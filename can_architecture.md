# CAN / COM Layer — reverse-engineering notes

Static analysis of `dump.txt` (Ghidra disassembly of `swfl_00000fef.bin.129_160_001`).
TriCore TC17xx with Infineon MultiCAN module.

## Memory map (deduced)

- Flash code/data: `0x80000000..0x803fffff`
- Internal RAM: `0xd0000000+`
- MultiCAN node base: `0xf0004000` (CAN_NCR0/NPCR0/NSR0/etc.)
- MultiCAN MO array: `0xf0005000`, 32 bytes per MO:
  - `+0x00` MOFCR, `+0x04` MOFGPR, `+0x08` MOIPR, `+0x0c` MOAMR
  - `+0x10` MODATAL, `+0x14` MODATAH, `+0x18` MOAR, `+0x1c` MOCTR

Global base registers (set at boot):
- `a0` = `0xd0009a00`  (small-data RAM)
- `a1` = `0x80037618`  (small-data flash, read-only)
- `a9` = per-task (set on context switch via `mov.a a9, d1` in `FUN_800d4166`)

## CAN driver — message-object configuration

`MsgCfgEntry_ARRAY_80042938` — 107 entries × 24 bytes:

```
offset 0x00..0x01  field0_0x0, field1_0x1
offset 0x02        moIndex (0 or 1; second instance when ID is mirrored across MOs)
offset 0x03        pad
offset 0x04..0x07  canIdPtr  -> uint32_t in flash holding the 11-bit CAN ID
offset 0x08..0x0b  canIdMask (0x7FF = exact match; 0x780 = FIFO bank)
offset 0x0c        frameType (0 = standard)
offset 0x0d        direction  (0x01 = TX, 0x02 = RX)
offset 0x0e        field8_0xe (typically 8)
offset 0x0f        moType
offset 0x10..0x11  adbLookupIdx (0xFFFF = unset)
offset 0x12        useMsiMask
offset 0x13        pad
offset 0x14..0x17  callback pointer
```

### Direction semantics — verified from `CAN_Init` (`0x800c738e`)

The init loop at `0x800c75b6..0x800c7732` sets MOFCR bits via the `direction` field:

- `direction == 0x01` → sets MOFCR bit 17 = **STT** (Single Transmit Trial) → **TX**
- `direction == 0x02` → sets MOFCR bit 16 = **OVIE** (Overflow Interrupt Enable) → **RX FIFO**

Distribution: 64 TX entries (direction=01), 43 RX entries (direction=02).

### Callback semantics

- For TX entries: callback at `+0x14` is the **tx-complete handler** (fired from `CAN_MessagePending_ISR` at `0x800c7e28`).
- For RX entries: callback at `+0x14` is the **rx-data handler** (fired from `CAN_Rx_ISR` at `0x800c7c82`). Receives `a4` = 8-byte payload pointer, `a5` = &DLC, `a6` = payload pointer (again), `d2` = MO data.

## CAN driver — TX worker

`CAN_WriteMessageObject` at `0x800c7eee`:
```
d4 = moIdx (MsgCfgEntry index)
d5 = canId (-1 = use MsgCfgEntry[moIdx].canIdPtr)
d6 = DLC (clamped to 8)
a4 = payload pointer (8 bytes copied to MODATAL/MODATAH)
```

`CAN_Transmit` at `0x800c7fa2` — same signature, wraps `CAN_WriteMessageObject` with a status check.

Sets `MOAR = canId << 18`, copies bytes to MO data regs, sets MOCTR.TXRQ.

## RX dispatch

`CAN_Rx_ISR` (`0x800c7c82`):
1. Polls `CAN_MSID4` for pending MO bitmap
2. `CAN_FindHighestPendingMO` returns `hwMO`
3. Maps to MsgCfgEntry via `DAT_d00114ee[hwMO]` (populated in `CAN_Init` at `0x800c7710`)
4. Copies 8 bytes from MO data regs to local stack buffer
5. Reads CAN ID from MOAR (bits 28..18)
6. Sets `channelTypeTab[entryIdx]` (`0xd0012c9d + idx`) = 8 or 1 (fresh-data flag)
7. Calls per-entry callback at `MsgCfgEntry+0x14` if non-null

`CAN_RxFrameDispatch` (`0x800ed7dc`): switch on message-group selector `d4-4`, dispatches to
`CAN_RxHandler_MsgType4/6/7`, `CAN_DecodeSignalGroupA/B/C`, `CAN_ProcessMeasurementFrameA/B`.

## TX paths — three mechanisms

### 1. Channel-mode TX (diag/event)
`CAN_TransmitChannelNow` (`0x800c8454`) + `CAN_TxDispatch` (`0x800c854c`)
- Channel descriptor at `0xd000ed90 + chIdx * 0x20`:
  - `+0x0c` enable flag
  - `+0x14..0x17` payload bytes 4..7 (written as one u32 via `CAN_SetChannelPayload` at `0x800c84d6`)
  - `+0x18..0x1a` payload bytes 1..3 (written byte-by-byte at init from `DAT_d000bf28..bf2a`)
- Frame byte 0 = `parent_ctx[0x16]` (typically an alive counter)
- Used for ID 0x580-range UDS responses, by `FUN_800eeb24` (callback for MsgCfgEntry[78]).

### 2. I-PDU-mode TX (periodic broadcasts — incl. 0x8F, 0xA5..0xA9, 0x145)
- App calls `FUN_80084f12(sigIdx, value)` (168 callers) to write a Com signal.
- Signal status bytes live at `0xd001a8c2 + subIdx` (sub-position from cumulative range table at `0x80050c70`).
- Periodic scheduler reads the assembled I-PDU buffer and calls `CAN_Transmit`.
- Encoder for 0xA1..0xA9 group: `FUN_8030fc4a` at `0x8030fc4a` — reads RAM globals like
  `DAT_d00013ab`, `DAT_d000142c`, `DAT_d00016d2`, `DAT_d0001707` and produces signal-value
  words (data bit at 0, dirty bit at 1, quality nibble at bits 8..11).

### 3. RX-triggered TX (request/response)
- `FUN_800eeb24` (callback for MsgCfgEntry[78], ID 0x580 mask 0x780) reads byte 0 of received
  frame and dispatches to `CAN_Transmit` for UDS service responses.

## COM layer — RX descriptor stack

Context pointer at `[a0]-0x7210` (= `0xd00027f0`) is set by `FUN_800ee312` (`0x800ee312`)
to flash address `0x8004d4e4`. Structure:

```
0x8004d4e4 +0x00  uint32  0x00000001 (count)
0x8004d4e4 +0x04  fnptr   CAN_RxFrameDispatch        (0x800ed7dc)
0x8004d4e4 +0x08  fnptr   FUN_800ed78a               (RX dispatch switch)
0x8004d4e4 +0x0c  fnptr   FUN_800ed846               (timeout dispatch switch)
0x8004d4e4 +0x10  ptr     0x8004d4f8                 -> sub-context
0x8004d4e4 +0x14  ptr     RAM state
0x8004d4e4 +0x18  ptr     0x8004d560                 -> buffer table
```

Sub-context at `0x8004d4f8`:
```
+0x00  ptr     0xd000fc74     (RAM state)
+0x04  uint32  0x8004d560     (buffer table base)
+0x08  ptr     0x80053174     (frame-type / direction tag table)
+0x0c  ptr     0x80052e7c     (SIGNAL DESCRIPTOR table)
+0x10  ptr     0x80052e2a     (CAN ID list for some frames)
```

## Signal descriptor table @ `0x80052e7c`

Each signal index is 4 bytes:
```
byte 0  type      (0 = normal bitfield; nonzero = special, see below)
byte 1  len_enc   (0..15 -> bit width 0..15 via LUT)
byte 2  bufIdx    (0..24)
byte 3  startBit  (0..63 within the buffer's data)
```

Length mask LUT at `0x80053188` (16 halfwords): `enc N -> (1<<N)-1`
```
enc 0  -> 0x0000
enc 1  -> 0x0001
enc 2  -> 0x0003
...
enc 8  -> 0x00ff
...
enc 15 -> 0x7fff
```

### Special signal types (sig index `0xE6+`)

Signals 0xE6..0x1A0+ have nonzero type, len_enc=0, varying bufIdx, constant startBit=0x58.
Pattern: `type = (sigIdx - 0xE6) + 1`. These look like **PDU-level descriptors** referencing
entire frames (not bitfields). Example:
- sig 0x145: `type=0x60 (=96), bufIdx=0x6C (=108), startBit=0x58`
  - means: PDU #96, references buffer-pool entry 108 — likely the TX side of CAN ID 0x145
  - (the literal `0x145` lives in `MsgCfgEntry[16].canIdPtr -> 0x8004366c`)

## Buffer descriptor table @ `0x8004d560`

25 entries × 12 bytes. Per entry:
```
+0x00..0x01  hdr_word     (probable CAN ID or PDU handle)
+0x02        last_byte    (DLC - 1)
+0x03        group        (CAN node / bus / type, 0..7)
+0x04..0x07  ext_word
+0x08..0x0b  dataPtr      (RAM 0xd001 47xx or 0xd00043xx, holds the 8-byte payload)
```

Per-buffer RAM data is the actual frame payload (RX side of the COM stack).
Full layout in `rx_signal_map.txt`.

## The five frames you asked about

All five are TX (direction = 0x01) in MsgCfgEntry:

| CAN ID | MsgCfgEntry | canIdPtr   | Notes |
|--------|-------------|------------|-------|
| 0xA5   | [13], [26]  | 0x80043678, 0x80043644 | TX, two MO mirrors |
| 0xA6   | [14]        | 0x80043674 | TX |
| 0xA7   | [76]        | 0x8004351c | TX |
| 0x8F   | [15], [18]  | 0x80043670, 0x80043664 | TX, two MO mirrors |
| 0x145  | [16]        | 0x8004366c | TX |

The RX descriptor table at `0x80052e7c` does **not** contain bit layouts for these IDs —
they go through the special "PDU descriptor" path (signal indices `0xE6+`) for TX
assembly, then through `CAN_Transmit`/`CAN_WriteMessageObject` for the actual MO write.

## Useful function addresses

```
CAN_Init                            0x800c738e
CAN_Rx_ISR                          0x800c7c82
CAN_MessagePending_ISR              0x800c7e28   (TX-complete)
CAN_WriteMessageObject              0x800c7eee
CAN_Transmit                        0x800c7fa2
CAN_TransmitChannelNow              0x800c8454
CAN_TxDispatch                      0x800c854c
CAN_SetChannelPayload               0x800c84d6
CAN_GetChannelData                  0x800c8502
CAN_InitChannelObject               0x800c82cc
CAN_FindListAndWrite                0x800c8190
CAN_FindHighestPendingMO            0x800c777a
CAN_RxFrameDispatch                 0x800ed7dc
CAN_DecodeSignalGroupA              (via switchD_800ed80a::caseD_e)
CAN_DecodeSignalGroupB              (caseD_18)
CAN_DecodeSignalGroupC              (caseD_3 in FUN_800ed78a)
CAN_ProcessMeasurementFrameA        (caseD_8 in FUN_800ed78a)
CAN_ProcessMeasurementFrameB        (caseD_c in FUN_800ed78a)
CAN_TxComplete_DequeueNext          0x800c7ebe
FUN_8030fc4a                        0xA1..0xA9 periodic encoder (Com signal updates)
FUN_8032855e                        0x8F-touching state updater
FUN_800ee4b6                        Com layer 1-byte signal getter (96 callers)
FUN_800ee51a                        Com layer 16-bit signal getter (50 callers)
FUN_800ee312                        Com context pointer publisher
FUN_800859f0                        TX context table publisher
FUN_80084e64                        signal status getter
FUN_80084f12                        signal value setter (168 callers)
FUN_80083e12                        sub-signal commit
FUN_80085a74                        sub-signal flag updater
FUN_800848de                        I-PDU byte writer
```

## Open questions / not yet decoded

- The exact buffer→canId mapping for the 25-buffer RX table (hdr_word looks like
  a CAN ID, but two buffers share `0x003c` and several values don't match known
  BMW PT-CAN IDs cleanly).
- The TX-side I-PDU buffer pool and its bit-position table (`[a9]+0x1e0`,
  `[a9]+0x1e4`) — `a9` is per-task and the tables aren't statically traceable
  without identifying which task runs the TX assembler.
- For the user-requested IDs (0x8F, 0xA5, 0xA6, 0xA7, 0x145), the per-byte/per-bit
  layout requires either a RAM snapshot of the TX context tables or runtime
  observation of `MODATAL`/`MODATAH` during transmit cycles.
