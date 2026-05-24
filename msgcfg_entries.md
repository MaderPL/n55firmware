# MsgCfgEntry table — TX/RX configuration for all CAN message objects

Table address: `0x80042938` (`MsgCfgEntry_ARRAY_80042938`)
Entry size: 24 bytes
Total: 107 entries

## Entry layout

```
+0x00  uint8   field0_0x0
+0x01  uint8   field1_0x1
+0x02  uint8   moIndex            // 0 or 1 (instance, when an ID has two MOs)
+0x03  uint8   pad
+0x04  ptr32   canIdPtr           // -> uint32_t in flash with the 11-bit CAN ID
+0x08  uint32  canIdMask          // 0x7FF = exact; 0x780 = FIFO bank (matches 0x5_x range)
+0x0c  uint8   frameType          // 0 = standard 11-bit
+0x0d  uint8   direction          // 0x01 = TX (STT), 0x02 = RX (FIFO/OVIE)
+0x0e  uint8   field8_0xe         // typically 8 (related to DLC?)
+0x0f  uint8   moType
+0x10  uint16  adbLookupIdx       // 0xFFFF = unused
+0x12  uint8   useMsiMask
+0x13  uint8   pad
+0x14  fnptr   callback           // TX: tx-complete handler; RX: rx-data handler
```

## Distribution

- 64 entries with direction = 0x01 (TX)
- 43 entries with direction = 0x02 (RX)

## Entries for the user-requested CAN IDs

All five are TX. Two of them are mirrored across two message objects:

| CAN ID  | MsgCfgEntry idx | Entry address  | canIdPtr     | direction | callback   |
|---------|-----------------|----------------|--------------|-----------|------------|
| 0xA5    | [13]            | 0x80042a70     | 0x80043678   | 0x01 TX   | null       |
| 0xA5    | [26]            | 0x80042ba8     | 0x80043644   | 0x01 TX   | null       |
| 0xA6    | [14]            | 0x80042a88     | 0x80043674   | 0x01 TX   | null       |
| 0xA7    | [76]            | 0x80043058     | 0x8004351c   | 0x01 TX   | null       |
| 0x8F    | [15]            | 0x80042aa0     | 0x80043670   | 0x01 TX   | null       |
| 0x8F    | [18]            | 0x80042ae8     | 0x80043664   | 0x01 TX   | null       |
| 0x145   | [16]            | 0x80042ab8     | 0x8004366c   | 0x01 TX   | null       |

`canIdPtr` is dereferenced by `CAN_Init` (line `0x800c7658`) to read the 11-bit ID
and write `MOAR = canId << 18`.

## Example entry [78] — non-trivial direction=02 RX

Useful counter-example showing that direction=0x02 is RX with callback:

```
[78] @ 0x80043088 :
  field0_0x0       = 0x4e
  field1_0x1       = 0x00
  moIndex          = 0x01
  pad              = 0x00
  canIdPtr         -> 0x80043514 (= 0x00000580)
  canIdMask        = 0x00000780  (matches IDs 0x580..0x5FF — diagnostic bank)
  frameType        = 0x00
  direction        = 0x02       (RX FIFO)
  field8_0xe       = 0x08
  moType           = 0x01
  adbLookupIdx     = 0xFFFF
  useMsiMask       = 0x01
  pad              = 0x00
  callback         -> FUN_800eeb24 (0x800eeb24)
```

`FUN_800eeb24` reads byte 0 of the received payload (the UDS service ID) and dispatches
to handlers like `CAN_Transmit` for response, `FUN_800e23c2`, etc. This confirms
direction=0x02 entries are RX with dispatch callbacks (typical UDS request bank).

## How direction bits were verified

In `CAN_Init` at `0x800c76a6..0x800c76e6`:

```
ld.bu  d15, [a3]+0xd        ; d15 = MsgCfgEntry[i].direction
jne    d15, #0x2, LAB1       ; if direction != 2 goto LAB1

  ; direction == 0x02 branch:
  ld.w     d15, [a2]          ; load current MOFCR
  insert   d15, d15, #0xf, #0x10, #0x1   ; set MOFCR bit 16 (OVIE)
  st.w     [a2], d15
  ...
  or       d15, #0x02         ; MOIPR low nibble = 0x02
  j        LAB2

LAB1:                          ; direction == 0x01 branch
  ld.w     d15, [a2]          ; load current MOFCR
  insert   d15, d15, #0xf, #0x11, #0x1   ; set MOFCR bit 17 (STT)
  st.w     [a2], d15
  ...
  or       d15, #0x10         ; MOIPR field = 0x10

LAB2:
  st.w     [a15], d15          ; store MOIPR
```

TC17xx MOFCR layout:
- bit 13 = TXIE
- bit 15 = RXIE
- bit 16 = OVIE (Overflow Interrupt Enable) — set when direction = 0x02 -> RX FIFO mode
- bit 17 = STT (Single Transmit Trial) — set when direction = 0x01 -> single-shot TX

The `0xC00E00` (direction=0x02) and `0xE400000` (direction=0x01) constants written to
MOCTR (offset 0x1c) at `0x800c76e8..0x800c7706` are SET-bit patterns that select
RX-FIFO vs TX MMC modes respectively.
