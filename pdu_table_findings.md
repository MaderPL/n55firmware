# PDU descriptor table — analysis follow-up

Follow-up investigation requested by user: (a) find the parallel TX descriptor
table, (b) decode the type-0x60 PDU descriptors for sig 0x145.

## Correction to earlier finding

The signal descriptor table at `0x80052e7c` has **195 real entries** (sig 0..0xC2),
not 0..0x300 as I initially assumed.

Layout in flash:
```
0x80052e7c .. 0x80053187   signal descriptor table (195 × 4 bytes = 780 bytes)
0x80053188 .. 0x800531a7   length mask LUT          (16 × 2 bytes = 32 bytes)
0x800531a8 .. 0x80053213   intermediate data
0x80053214 ..              PDU registration table   (4 bytes per entry)
```

When I addressed "sig 0xE6+" through the descriptor table base I was actually
reading the PDU registration table that follows the mask LUT. The decoded data
is real and meaningful, but the index "sig 0x145" is misleading — it's not a
signal index, it's an offset into this *second* table at
`0x80053214 + ((0x145 - 0xE6) * 4) = 0x80053390`.

## PDU registration table @ ~0x80053214

Each entry is 4 bytes:
```
byte 0  pduSeq    sequence number, starts at 1, monotonically increasing
byte 1  flags     always 0x00 in real PDU entries
byte 2  txChan    TX channel index (0..0xFD observed)
byte 3  marker    always 0x58 in real PDU entries
```

The table is sequential: pduSeq increments by 1 per entry. txChan is mostly
monotonic but skips values (1..4-step gaps). 227 PDU entries observed before
the marker changes from 0x58 to 0x59 (probably a different group).

### The entry for CAN ID 0x145

Located at `0x80053390`:
```
0x80053390: 60 00 6c 58
              ^^ pduSeq = 96
                 ^^ flags = 0
                    ^^ txChan = 108 (0x6C)
                       ^^ marker = 0x58
```

PDU sequence #96 maps to TX channel 108.

### How to find the channel descriptor

TX channels live in RAM at `0xd000ed90 + chIdx * 0x20`. Channel 108 descriptor is at:
```
0xd000ed90 + 108*0x20 = 0xd000fb10
```

Channel descriptor layout (verified earlier in `can_architecture.md`):
```
+0x0c   uint32  enable flag
+0x14..0x17    payload bytes 4..7  (live, set via CAN_SetChannelPayload)
+0x18..0x1A    payload bytes 1..3  (set once at init from DAT_d000bf28..bf2a)
+0x1C..0x1F    additional config
```

Frame byte 0 comes from `parent_ctx[0x16]` (typically an alive counter).

So the **8-byte payload for CAN ID 0x145** has this static structure:
```
offset  0, length  8   alive/counter byte         (parent_ctx[0x16])
offset  8, length 24   3 bytes static at init     (ch[0x18..0x1A])
offset 32, length 32   4 bytes dynamic            (ch[0x14..0x17], one u32)
```

The 8-bit per-field bit semantics within these byte ranges are application-defined
and require either:
- the calling code (search for `CAN_SetChannelPayload` callers with channelIdx=108), or
- a DBC for this DME.

## On (a): a parallel TX descriptor table

**There is no separate "TX descriptor" flash table** equivalent to the 195-entry
RX descriptor table at `0x80052e7c`.

The TX path in this firmware doesn't have a bit-position descriptor structure
because **TX frames are assembled by direct API calls** (`CAN_SetChannelPayload`,
`CAN_Transmit`, `CAN_WriteMessageObject`) rather than a Com-layer signal
packer. Each TX frame's 8-byte payload is written into the channel descriptor's
`+0x14..+0x1A` fields directly by application code.

The closest thing to a TX descriptor is the PDU registration table above —
but it only stores the channel index, not bit positions.

## Implication for the user's five frames

| CAN ID | MsgCfgEntry | PDU# (if any) | TX channel | Layout |
|---|---|---|---|---|
| 0xA5 | [13], [26] | ? | ? | Channel-mode (see below) |
| 0xA6 | [14] | ? | ? | Channel-mode |
| 0xA7 | [76] | ? | ? | Channel-mode |
| 0x8F | [15], [18] | ? | ? | Channel-mode |
| 0x145 | [16] | 96 | 108 | Channel-mode |

All five use the channel-mode TX layout:
```
byte 0     = parent_ctx[0x16]                                  ← alive counter
bytes 1-3  = channel_desc[0x18..0x1A] (static after init)      ← header/config
bytes 4-7  = channel_desc[0x14..0x17] (via CAN_SetChannelPayload)  ← live data
```

To resolve which channel a specific MsgCfgEntry binds to, follow the
PDU sequence in the registration table — `MsgCfgEntry[N]` likely maps to
`PDU# = (N+1)` (the sequence is consistent with init order), giving txChan via
the table I dumped above.

Working hypothesis (verifiable with a RAM dump or one CAN trace):
- `MsgCfgEntry[16]` (canId 0x145) → PDU#96 → txChan 108 ✓ (consistent with `(N+1)*1 = pduSeq`)
- `MsgCfgEntry[13]` (canId 0xA5) → PDU#? → txChan ?
- `MsgCfgEntry[14]` (canId 0xA6) → PDU#? → txChan ?
- ...

## What this means for "frame format in (offset, length) pairs"

Static analysis can give the **structural** layout (alive byte + 3-byte header +
4-byte data) for each channel-mode TX frame, but the **per-bit signal semantics**
within those 4 dynamic bytes are encoded only at the call site of
`CAN_SetChannelPayload` — i.e., in application code that knows which physical
quantity it's writing. That information is per-frame and would need either:

1. A RAM dump showing live channel-descriptor bytes for our specific channels, or
2. Tracing each `CAN_SetChannelPayload(108, value)` caller to see how `value`
   is constructed from sensor RAM reads (similar to what we already did for
   `FUN_8030fc4a`).

Option (2) is feasible — find callers of `CAN_SetChannelPayload` and group them
by channel index, then trace each value-construction path. That would give a
full DBC-equivalent for the firmware's TX frames.
