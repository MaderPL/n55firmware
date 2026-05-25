# CAN_BroadcastSignalGroup{A,B} — full body analysis

Disassembled the full bodies of both broadcast functions and extracted the
signal index / value flash addresses.

## Periodic-tick context (where both broadcasts are called)

Three scheduler tick sites call BOTH broadcasts together:

```
0x8007acb6  call CAN::CAN_BroadcastSignalGroupA
0x8007acba  call CAN::CAN_BroadcastSignalGroupB        <- back to back!
```

Same pattern at `0x8007b48e/b492` and `0x8007baba/babe`. So `BroadcastA + B`
together produce one round of TX signals per tick.

The surrounding context in the tick handler `(0x8007ac9e..)`:
```
call FUN_800ed8dc            (CAN RX dispatcher prep)
call FUN_800edcbc            (RX work)
call FUN_800eafd6            (something CAN-related)
call FUN_800c1694
call FUN_800c2792
call FUN_800c52ee
call CAN_BroadcastSignalGroupA   <-- HERE
call CAN_BroadcastSignalGroupB   <-- AND HERE
call FUN_800dfa62
call FUN_800aecd0
...
```

## CAN_BroadcastSignalGroupA (`0x800c5d06` .. `0x800c5e4e`)

8 signal-write calls to `FUN_800ed734(d4=sigIdx, d5=value, d6=ctrl-bit, d7=0x186A0)`.

Flash addresses referenced (`a1 = 0x80037618`):

| Address | Value (LE u16) | Used as |
|---|---|---|
| `[a1]-0x75aa` = `0x8003006e` | `0x0292` (658) | sigIdx for call #1 |
| `[a1]-0x7444` = `0x800301d4` | `0x01df` (479) | sigIdx for call #2 |
| `[a1]-0x76a0` = `0x8002ff78` | `0x003d` (61) | "value" for call #1 |
| `[a1]-0x769e` = `0x8002ff7a` | `0x003c` (60) | "value" |
| `[a1]-0x769c` = `0x8002ff7c` | `0x003b` (59) | "value" |
| `[a1]-0x769a` = `0x8002ff7e` | `0x003a` (58) | "value" |
| `[a1]-0x7698` = `0x8002ff80` | `0x0039` (57) | "value" |
| `[a1]-0x7696` = `0x8002ff82` | `0x0038` (56) | "value" |
| `[a1]-0x7694` = `0x8002ff84` | `0x0037` (55) | "value" |
| `[a1]-0x7692` = `0x8002ff86` | `0x0036` (54) | "value" |

The "value" slots `0x002ff78..0x8002ff86` hold 8 consecutive descending IDs
`0x36..0x3d`. These are sub-indices into a deeper Com layer (they're passed
as `d5` to `FUN_800ed734`, which forwards them to `FUN_80082c10`'s top-4
dispatch).

The control-bit `d6` for each call is bit N of a status byte at
`DAT[a0]-0x5799` (i.e. `0xd00043a7`), with N = 0..6 (first call uses
a different control source at `DAT[a0]-0x5c1b`).

## CAN_BroadcastSignalGroupB (`0x800c6032` .. `0x800c6126`)

7 signal writes. Same call template, different flash addresses (note:
neighboring addresses to A's — likely the same data section).

```
lea a15,[a1]-0x75a8   ; 0x80030070  (= sigIdx ?)
lea a15,[a1]-0x76a2   ; 0x8002ff76
lea a15,[a1]-0x7446   ; 0x800301d2
lea a15,[a1]-0x7690   ; 0x8002ff88
lea a15,[a1]-0x768e   ; 0x8002ff8a
lea a15,[a1]-0x768c   ; 0x8002ff8c
lea a15,[a1]-0x768a   ; 0x8002ff8e
```

So A and B together access an interleaved block in `0x8002ff72..0x8002ff8f`
(the "value" sub-index ID array) and `0x8003006e/70, 0x800301d4/d2` (the
"main" sigIdx values).

## Per-call `d6` control-bit source

In `CAN_BroadcastSignalGroupA`, after the first call all calls extract
sequential bits from byte at `[a12]` (`a12 = a0 - 0x5799 = 0xd00043a7`):

```
Call 1: d6 = DAT[a0-0x5c1b].bit0           (different control byte)
Call 2: d6 = DAT[a0-0x5799].bit0
Call 3: d6 = DAT[a0-0x5799].bit1
Call 4: d6 = DAT[a0-0x5799].bit2
Call 5: d6 = DAT[a0-0x5799].bit3
Call 6: d6 = DAT[a0-0x5799].bit4
Call 7: d6 = DAT[a0-0x5799].bit5
Call 8: d6 = DAT[a0-0x5799].bit6  (tail-called via 'j')
```

So each bit of `0xd00043a7` gates one signal write. This is a *broadcast
selector mask*: each bit decides whether that particular signal is sent
this cycle.

## What's in the d4 vs d5 fields

Looking at `FUN_800ed734`'s body:

```
extr.u  d0, d4, #0, #0x10        ; d0 = d4 & 0xffff
if d0 == 0:
    ; fallback path
    d4 = d5 & 0xffff
    d5 = 0
    d6 = 0
    -> j FUN_80082c10
else:
    call FUN_80085a02(d4)        ; "is subscriber active?"
    if d2 (= subscriber bit) == 0 -> path A
    else                          -> path B
```

So `d4` IS the primary signal index. `d5` is a secondary
identifier used in the fallback path (when `d4 == 0`).

For our extracted data:
- `BroadcastA` calls all use a non-zero `d4` (0x292 and 0x1df dominate),
  so they take the subscriber-checked path.

## Dispatch routing — where the bits actually land

`FUN_80082c10` splits the 16-bit `sigIdx` (d4) into top-4 dispatch and
bottom-12 sub-index. For `0x0292` and `0x01df`:
- top-4 = `0x0` → dispatch handler `[0]` = `0x80082c9c`
- bottom-12 = `0x292` and `0x1df` respectively

Handler `0x80082c9c` is in the COM-layer 0x80082xxx family. Following its
body would lead to the actual byte/bit positions in the I-PDU buffer.

## Why this isn't the A5/A6/A7 encoder

Both `BroadcastA` and `BroadcastB` together produce **15 signal writes**
per tick. The user said A5/A6/A7 = 3+4+2 = 9 signals. So these two
functions could be the A5/A6/A7 encoders *plus* some other frames'
signals.

However, looking at the addresses used:
- The `value` sub-indices are tiny (0x36..0x3e) — too small to be CAN IDs.
- The `sigIdx` values 0x292, 0x1df are NOT the user's claimed bit positions
  (16, 28, 40).

So `BroadcastSignalGroupA/B` are broadcasting *some* group of signals, but
the signal indices don't obviously map to "frame 0xA5 byte 2-3 torque etc."
The CAN-ID-to-encoder mapping is still one indirection away (likely
inside handler `0x80082c9c`).

## Three caller locations

```
0x8007acb6 / 0x8007acba   in tick handler block starting at 0x8007ac9e
0x8007b48e / 0x8007b492   in another block
0x8007baba / 0x8007babe   in third block
```

The pattern `(broadcastA, broadcastB)` always appears as a pair. The three
caller blocks are likely 5ms / 10ms / 20ms scheduler slots.

## Next step (where the rabbit hole continues)

To extract concrete A5/A6/A7 bit positions, the productive trail is:
disassemble handler `0x80082c9c` (the top-4=0 dispatch target). Its body
must contain either:
- Direct byte writes to MO data registers, with embedded bit positions, or
- A lookup table indexed by the bottom-12 of the signal index, where each
  entry describes a `(canId, byteOffset, bitOffset, length)` tuple.

That would close the loop from "broadcast tick → signal index → byte/bit
in CAN frame".
