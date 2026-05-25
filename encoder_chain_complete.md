# The full CAN TX encoder chain — as traced through ASW

This document closes out the encoder hunt with the complete call chain
that the firmware uses to broadcast a CAN signal. Each level adds
indirection; the per-frame byte/bit positions live at the deepest level,
in tables that resolve into the CAFD partition at runtime.

## The chain (top-down)

```
[Scheduler tick]
   |  0x8007acb6 / 0x8007b48e / 0x8007baba   (3 tick sites)
   v
CAN_BroadcastSignalGroupA    @ 0x800c5d06    (8 signal-writes per call)
CAN_BroadcastSignalGroupB    @ 0x800c6032    (7 signal-writes per call)
   |  Each issues calls of the form:
   |     d4 = sigIdx16 from flash table
   |     d5 = sub-value16 from flash table
   |     d6 = mask-bit from DAT_d00043a7
   |     d7 = 0x186A0
   |  call FUN_800ed734
   v
FUN_800ed734                  @ 0x800ed734    (per-signal wrapper)
   |  - increments DAT_c000054e (counter)
   |  - if d4 == 0: fallback path
   |  - else: call FUN_80085a02 (subscriber check)
   |          if not active: -> FUN_800cb816 (timeout path)
   |          else:         -> FUN_80082c10
   v
FUN_80082c10                  @ 0x80082c10    (central dispatcher, 261 callers)
   |  - subscriber bitmap check at [a9]+0x208
   |  - top4 of d4 (sigIdx) -> dispatch table at 0x80032580
   v
dispatch[top4]                e.g. handler[0] = 0x80082c9c
   |  - reads state at 0xd000eddc + (sigIdx<<2)
   |  - reads timeout config from flash table at 0x80051d3e
   |  - updates aging/validity bits in state word
   |  - manipulates per-signal counters
   v
returns to FUN_80082c10, which then unconditionally calls:
FUN_800cb6e6                  @ 0x800cb6e6    (signal state commit)
   |  - reads status byte at 0xd001a8c2 + sigIdx (the Com layer)
   |  - updates state words in DAT_d000eddc area
   |  - updates flag halfwords at 0xd0011692 area
   |  - calls FUN_80083e12
   v
FUN_80083e12                  @ 0x80083e12    (sub-signal commit, 349 callers)
   |  - reads status from 0xd001a8c2+subIdx
   |  - manipulates per-subfield quality bits
   |  - calls FUN_80085a74 / FUN_800848de
   v
FUN_80085a74 / FUN_800848de   (sub-signal bit writers)
   |  - access [a9]+0x208 (RX status bitmap)
   |  - access [a9]+0x1e0 (BYTE OFFSET table - CAFD-resident)
   |  - access [a9]+0x1e4 (BIT POSITION table - CAFD-resident)
   v
[Actual byte position in I-PDU RAM buffer is computed here, from
 byte-offset and bit-position tables that live in CAFD.]
```

## What we have extracted

| Item | Value | Notes |
|---|---|---|
| Broadcast signal indices | `0x0292`, `0x01df` (and 8 sub-IDs 0x36..0x3d) | from BroadcastA flash refs |
| Dispatch top4 for both | `0x0` | -> handler `0x80082c9c` |
| Signal state table | `0xd000eddc` | 4 bytes per signal |
| Signal status buffer | `0xd001a8c2` | 1 byte per sub-signal |
| Dirty-flag map | `0xd001187a` | 1 bit per sub-signal |
| Per-signal timeout LUT | `0x80051d3e` | ASW flash (verified) |
| Subscriber bitmap | `[a9]+0x208` | per-task RAM |
| Byte-offset table ptr | `[a9]+0x1e0` | -> CAFD |
| Bit-position table ptr | `[a9]+0x1e4` | -> CAFD |

## What we have NOT cracked

The actual `(canId, byteOffset, bitOffset, length)` mapping for a given
signal index lives in the byte-offset and bit-position tables that are
addressed through `[a9]+0x1e0` and `[a9]+0x1e4`. Those tables exist in
CAFD but we couldn't find a fingerprint that matches the user's claimed
A5/A6/A7 bit positions (`16/12, 28/12, 40/16` for A5 etc.).

The fundamental reason: **the encoding in CAFD is more abstract than
"plain (sb, len) byte pairs"**. The bit-position table is indexed not
by signal index directly, but by a sub-index that's computed from
several pointer hops through CAFD-resident structures. Without either
running the firmware or a DBC/A2L file, the static encoding is opaque.

## Verified facts (recap)

- All 5 user-requested IDs (`0x8F`, `0xA5`, `0xA6`, `0xA7`, `0x145`) are
  TX (`direction=0x01`, STT mode) with the MsgCfgEntries documented in
  `msgcfg_entries.md`.
- The 10 ms scheduler tick contains `CAN_BroadcastSignalGroupA` +
  `BroadcastSignalGroupB` back-to-back, broadcasting 15 signals total.
- The Com layer is fully decoded in **structure** (every function in the
  chain) but the **per-frame byte/bit positions** live in CAFD-resident
  tables behind a task-local pointer chain.

## How a runtime trace would close this

If a single 10 ms tick were captured with these data points logged:
- the 15 sigIdx values passed to `FUN_800ed734` in order,
- the 15 corresponding `value` parameters,
- the resulting bytes written to MO data registers at
  `0xF0005010 + hwMO*0x20`,

then a one-to-one mapping `(sigIdx, value) -> (canId, byte, bit)` is
immediately derivable for every TX signal in this 10 ms slot,
including the A5/A6/A7 set.

## Function inventory closeout

The full chain involves these functions, all now mapped and committed
to the repo:

```
0x800c5d06   CAN_BroadcastSignalGroupA       (signal-by-signal broadcaster)
0x800c6032   CAN_BroadcastSignalGroupB
0x800ed734   FUN_800ed734                    (per-signal wrapper)
0x80085a02   FUN_80085a02                    (subscriber active check)
0x800cb816   FUN_800cb816                    (timeout/fallback path)
0x80082c10   FUN_80082c10                    (central dispatcher, top4 split)
0x80032580   dispatch_table[16]              (per-group handler array)
0x80082c9c   handler[0] (top4=0)              (signal aging/timeout state)
0x800cb6e6   FUN_800cb6e6                    (signal state commit)
0x80083e12   FUN_80083e12                    (sub-signal commit, 349 callers)
0x80085a74   FUN_80085a74                    (sub-signal flag updater)
0x800848de   FUN_800848de                    (sub-signal byte writer)
0xd000eddc   per-signal state table
0xd001a8c2   sub-signal status buffer
0xd001187a   dirty-flag bitmap
0x80051d3e   per-signal timeout LUT (ASW flash)
```
