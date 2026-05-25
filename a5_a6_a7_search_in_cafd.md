# A5/A6/A7 signal layout search in CAFD — status

The maps file (`maps/swfl_00000ff2.bin`) is confirmed as the CAFD partition
for MEVD17.2.6-N55. The ASW (`dump.txt`) makes **14,171 references** into
this CAFD region (`0x80180000..0x801FFFFF`).

This document records what was searched for in CAFD when looking for the
explicit bit layouts of CAN frames 0xA5, 0xA6, 0xA7 (provided by user as
Intel/LE bit positions: A5 = (16,12),(28,12),(40,16); A6 = 4×(12-bit) at
12/24/36/48; A7 = (12,12),(32,16)).

## Patterns searched, no direct hits

The following byte/halfword patterns were searched across the full 512 KB
CAFD payload and returned **no matches**:

- A5 start-bit sequence: `10 1c 28` (byte triple), or with lengths: `10 0c 1c 0c 28 10`
- A6 start-bit sequence: `0c 18 24 30` (byte quad), or with lengths
- A5 signals as (sb16, len16) LE pairs: `10 00 0c 00  1c 00 0c 00  28 00 10 00`
- A6 signals as (sb16, len16) LE pairs
- (canId 0xA5 LE u16, DLC 8, period 10): `a5 00 08 0a`
- (canId 0xA5 LE u16, period 10 LE u16): `a5 00 0a 00`
- All 5 IDs as consecutive halfwords (A5..A9)
- Frame descriptor with canIdMask 0x7FF or 0xFFFF surrounding canId 0xA5
- canId u32 LE 0xA5 followed by various period bytes

## What was found

- **One canonical TX descriptor** at `0x801835a8` matches a recognizable
  Bosch format for **canId 0x8F**:
  ```
  0x801835a0:  33 33 33 01  00 00 00 00  8f 00 8f 00  00 00 ff ff
  0x801835b0:  b8 0b 40 1f  00 00 00 00  00 00 00 00  00 00 67 26
  ```
  → `canId=0x8F`, duplicate (filter), padding, mask=`0xFFFF`,
    field `0x0BB8` (= 3000), field `0x1F40` (= 8000). The `3000`/`8000`
    look like periods or limits but don't match the 10 ms cycle.
  But searching for the same `(canId, canId, 0000, FFFF)` pattern across
  all CAN IDs yielded only 6 matches total (most being 0x005, 0x064 —
  unlikely canIds). So this isn't the universal frame-descriptor format.

- **Calibration map data** is present in characteristic Bosch format,
  e.g., axis vectors and value arrays around `0x801a77a9+` (16-bit
  values that look like RPM thresholds).

## Hypotheses for why the A5/A6/A7 layout isn't visibly there

1. **Encoded / packed format** — bit positions and lengths may be
   packed into shared bytes (e.g., `(sb<<4)|len`, `(len<<4)|sb`, lookup
   indices into a separate length table). I tested the obvious such
   packings and didn't find them, but more elaborate encodings exist.

2. **Per-signal entries in a flat table with non-contiguous frame
   grouping** — signals for A5/A6/A7 might not appear in a contiguous
   block. They'd be interleaved with other signals, only resolvable by
   following the ASW's runtime index chain.

3. **Another partition exists** — the OEM image may have additional
   `swfl_*` partitions (one common pattern is BTLD + ASW + multiple
   CAFD sub-partitions). The CAN matrix could be in a partition not
   yet provided.

4. **Compressed CAFD section** — though the XML claims
   `COMPRESSION-STATUS="UNCOMPRESSED"`, individual data sections inside
   the payload could still be application-encoded (e.g., delta-encoded
   bit positions, or referenced by symbol via a separate symbol table).

## What is unambiguously true

- The unresolved pointer chains from the ASW analysis (`[a9]+0x1e0`,
  `[a9]+0x1e4`, `[a9]+0x210`, `[a0]-0x7e20`) **do** terminate inside
  this CAFD partition. So the data for A5/A6/A7 *is* in CAFD; we just
  haven't decoded the format yet.

- The cleanest path forward is to trace the runtime init that loads
  CAFD addresses into `a9` for the 10 ms TX task, then read the table
  there directly. The base pointer is set up by an ASW function
  reachable from `FUN_800ee312` or `FUN_800859f0`; identifying its
  one-time CAFD address would resolve the format.

- Failing that, a side-by-side dump of CAFD + RAM after the firmware
  has booted would expose the runtime tables in their fully-populated
  form. The CAFD-static encoding is the harder problem; the
  RAM-resolved data is the same content, easier to recognize.
