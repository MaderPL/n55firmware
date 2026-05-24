# Periodic task scheduler tables

Discovered while hunting for the actual encoders of the 10 ms TX frames
(0xA5, 0xA6, 0xA7 per user). The firmware uses a Bosch-style cyclic task
scheduler with multiple period-bucket tables of function pointers.

## Structure

Each table is a sequence of 4-byte function pointers in flash, bookended by:
- Start sentinel: `0x800aeb3c` (`LAB_800aeb3c` — common scheduler entry handler)
- End sentinel pattern: pair of `addr` words pointing to the next table start

`LAB_800aeb3c` is XREF'd by all scheduler tables (we see it referenced from
`0x80059080`, `0x80059204`, `0x80059284`, `0x8005955c`, `0x80059690`,
`0x80059be0`, `0x80059e3c`, `0x80059f7c`, ...). Each XREF marks the start
of one period bucket.

## Identified tables (region 0x80059800 .. 0x8005a800)

| Base addr   | Entries | Probable period | Notes |
|-------------|---------|-----------------|-------|
| 0x80059800  | 242     | Fast (1-5 ms?)  | Heavy with 0x803xxxxx app code |
| **0x80059be0** | **116** | **10 ms (candidate)** | Contains `FUN_8030fc4a` (sigs 0xA1..0xA9 status) |
| 0x80059e3c  | 37      | 20 ms?          | Smaller |
| 0x80059f7c  | 28      | 50 ms?          | Smaller |
| 0x8005a0bc  | 70      | 100 ms?         | |
| 0x8005a210  | 75      | 200 ms?         | |
| 0x8005a354  | 57      | 1000 ms?        | |
| 0x8005a498  | 8       | startup/init    | |

The 10 ms candidate is `0x80059be0` because:
- `FUN_8030fc4a` (signal status updater for `sigs 0xA1..0xA9`, which line up
  with the user's CAN IDs 0xA5/A6/A7) is at index 66 in this table.
- 116 entries × small periodic tasks is consistent with a 10 ms slot.

## Notable entries in the 10 ms table (subset)

Indices 60..80 of `0x80059be0`:
```
[60] 0x8030f764  — sig 0xAF status updater
[61] 0x8030757e  — ?
[62] 0x8030fc4a  — FUN_8030fc4a (sigs 0xA1..0xA9 status updater)
[63] 0x8032a3a4
[64] 0x8032a9e0
[65] 0x803804ae
[66] 0x80307f58
[67] 0x8030a944
[68] 0x803645a2
[69] 0x8030a096  — large state-machine (Lambda/torque governor pattern)
[70] 0x80309b54
[71] 0x80309ae2
[72] 0x80316028
[73] 0x80306b4c
[74] 0x80307d9c
[75] 0x8032c0da
[76] 0x80307d90
```

Any of these may contain (or call) the actual byte-level encoders for
frames 0xA5/0xA6/0xA7.

## Unsuccessful encoder fingerprints

The following static-analysis fingerprints turned up **nothing** for the
A5/A6/A7 encoders:

- `insert d_, d_, _, #0x10, #0xc` (12-bit pack at bit 16 for A5)
- `insert d_, d_, _, #0x1c, #0xc` (12-bit pack at bit 28 for A5)
- `insert d_, d_, _, #0x28, #0x10` (16-bit RPM pack at bit 40 for A5)
- `insert d_, d_, _, #0xc, #0xc` (12-bit pack at bit 12 for A6/A7)
- `mov d5, #0xa5/0xa6/0xa7` (canId as immediate to `CAN_Transmit`)
- `mov d4, #0x0d/0x0e/0x10/0x12/0x1a/0x4c` (MsgCfgEntry index for our IDs)
  — 14 hits found, all are DEM error code `0x1A`, not entry indices

The 11 `CAN_Transmit` call sites are all generic dispatchers that load
canId from a runtime context structure (`[a12]+0x2c`). No call site passes
a hardcoded canId for our IDs.

The `0x80043f90` table I initially thought was the TX scheduler turned out
to point to **blank flash** (`0x801c80xx = 0xff..ff`) — the loop's compare
at `0x80380bd8` (`d8 == 0x5dc` after `d15*25`) makes the dispatcher skip
all 40+ entries, so that table appears unused in this firmware variant.

## Two likely reasons for the encoder being hard to find

1. **Indirect encoding** — `CAN_Transmit` is called from a dispatcher that
   reads `canId` from a context structure populated at init time. The
   context structure may live in RAM and only be initialized at boot via
   pointer chains that aren't trivial to follow statically.

2. **Generic byte packer** — the encoder may not use `insert` at frame-bit
   positions but rather a generic function that takes `(buf, byteOffset,
   bitOffset, length, value)` parameters. In that case the bit positions
   wouldn't appear as immediates in the encoder code.

## Suggested next investigation paths

- Walk each function in the 0x80059be0 table looking for the pattern
  `ld.h <rpm_var>; sha #2; st.b` (load RPM, multiply by 4, store as bytes).
- Search for any function that takes 4 parameters and packs 12-bit fields
  into a byte stream (the generic packer hypothesis).
- Look for the engine RPM RAM global — once found, code that reads it and
  writes to a buffer is a candidate encoder.
- A RAM dump or live trace would resolve this in minutes — the runtime
  buffer addresses for the TX I-PDUs would be visible.
