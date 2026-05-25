# CAN Handler Re-analysis — TX path discovered

After revisiting the function inventory, identified the **TX-side encoder path**
that was hidden in the CAN driver region. This is the chain that broadcasts
signal groups (and likely produces frames like 0xA5/0xA6/0xA7).

## Newly-traced TX encoder chain

### Top-level: CAN_BroadcastSignalGroupA / B (in driver)

```
CAN_BroadcastSignalGroupA @ 0x800c5d06    (called from 0x8007acb6, 0x8007b48e, 0x8007baba)
CAN_BroadcastSignalGroupB @ 0x800c6032    (paired RX/TX functions; symmetric to DecodeSignalGroupA/B)
```

These are TX broadcast encoders called by scheduler ticks. They follow the
template (illustrating one signal):

```
movh    d7, #0x2
ld.h    d4, [a15]+0                  ; d4 = signal index (16-bit, from flash)
lea     a15, [a1]<offset_B>
ld.hu   d5, [a15]+0                  ; d5 = value (from RAM)
lea     a15, [a1]<offset_C>           ; another lookup
call    FUN_800ed734                 ; wrapper -> core signal write
```

Each broadcast invocation writes one signal (d4 = sigIdx, d5 = value).

### Signal-write wrapper: FUN_800ed734 @ 0x800ed734

```
FUN_800ed734(d4, d5, d6, d7):
  saves d5 to local_4
  d0 = d4 & 0xffff                   (effective signal index)
  if d0 == 0:
    -> fallthrough path to FUN_80082c10
  else:
    call FUN_80085a02 (subscriber active check)
    if d2 == 0 -> call FUN_800cb816 (timeout path)
    else       -> tail-call FUN_80082c10
```

### Core dispatcher: FUN_80082c10 @ 0x80082c10 (261 callers — the central API)

```
FUN_80082c10(d4=sigIdx16, d5=value, d6, d7):
  st.h  [a10]+4, d4                  ; save sigIdx
  call  FUN_800866d6                 ; common pre-amble
  d4 = sigIdx
  insert d15, d15, d4, #2, #12       ; pack 12 bits of sigIdx
  a2 = [a9]+0x208                    ; per-task state base
  a15 = a2 + d15                     ; subscriber bitmap lookup
  d15 = *a15                         ; load 32-bit flag word
  d2 &= d15                          ; AND with subscriber active mask
  ...
  extr.u  d15, d4, #12, #4           ; TOP 4 BITS of sigIdx -> dispatch group
  a15 = 0x80032580 + d15*4           ; index into 16-entry dispatch table
  a15 = *a15                          ; load handler function pointer
  d4 = sigIdx & 0xffff
  calli a15                           ; dispatch!
```

So the **signal index is a 16-bit value**, split as:
- **bits 15..12 (top 4 bits)**: dispatch group ID — selects a handler from table
- **bits 11..0 (bottom 12 bits)**: sub-index within that group

### Dispatch table @ `0x80032580` (16 handlers)

```
[ 0] 0x80082c9c  — handles sigIdx 0x0xxx
[ 1] 0x800cae28  — handles sigIdx 0x1xxx
[ 2] 0x80082f0a  — handles sigIdx 0x2xxx
[ 3] 0x800cb296  — handles sigIdx 0x3xxx
[ 4] 0x80083272  — handles sigIdx 0x4xxx
[ 5] 0x800cb29c  — handles sigIdx 0x5xxx
[ 6] 0x80082f04  — handles sigIdx 0x6xxx
[ 7] 0x800cb06e  — handles sigIdx 0x7xxx
[ 8] 0x800cb690  — handles sigIdx 0x8xxx
[ 9] 0x800853a6  — handles sigIdx 0x9xxx
[10] 0x800854ca  — handles sigIdx 0xAxxx
[11] 0x8008542a  — handles sigIdx 0xBxxx
[12] 0x80085468  — handles sigIdx 0xCxxx
[13] 0x8008544e  — handles sigIdx 0xDxxx
[14] 0x80085558  — handles sigIdx 0xExxx
[15] 0x8008567e  — handles sigIdx 0xFxxx
```

Most of the higher-numbered handlers (0x80085xxx, 0x80083xxx) are in the
COM-layer signal-handler family we already knew about. The lower-numbered
ones (0x800cb...) are in the CAN driver itself, suggesting frame-specific
write paths.

## What this means for the A5/A6/A7 encoder hunt

To pin down the encoder for canId 0xA5:

1. Find the broadcast function that calls `FUN_800ed734` (or `FUN_80082c10`
   directly) with a signal index whose **top 4 bits** route to a handler
   that ultimately writes to MO data registers for the entry indexed in
   `MsgCfgEntry[13]` / `MsgCfgEntry[26]` (both canId 0xA5).
2. The exact sigIdx for "A5 byte 2-3 (12-bit torque)" / "A5 byte 5-6 (RPM*4)"
   is consumed by the broadcast function as a 16-bit literal loaded from
   a flash table.
3. Look at the broadcast function bodies (`CAN_BroadcastSignalGroupA` /
   `B`) — they contain the SEQUENCE of sigIdx writes that build a frame.

## Periodic-tick callers

The three call sites of `CAN_BroadcastSignalGroupA` are:
- `0x8007acb6`
- `0x8007b48e`
- `0x8007baba`

These three call sites are at fixed offsets within the multi-period tick
dispatcher in the OS layer (likely 5ms / 10ms / 20ms slots, given the
linear spacing). The 10 ms call would be the one that produces the
A5/A6/A7 broadcast batch.

## Key function addresses summary

```
0x800c5d06   CAN_BroadcastSignalGroupA       (TX encoder, 3 callers @ tick handlers)
0x800c6032   CAN_BroadcastSignalGroupB       (TX encoder, sibling)
0x800ed734   FUN_800ed734                    (per-signal write wrapper)
0x80082c10   FUN_80082c10                    (CENTRAL signal-write dispatcher)
0x80032580   dispatch_table[16]              (signal-write handler functions)
0x80085a02   FUN_80085a02                    (subscriber-active check)
0x800cb816   FUN_800cb816                    (signal timeout / fallback path)
0x800866d6   FUN_800866d6                    (signal-write pre-amble)
```

## Next concrete step

To get the per-frame sigIdx list for 0xA5 specifically:
- Disassemble the full body of `CAN_BroadcastSignalGroupA` (it has many
  signal-write calls in sequence — each is one signal of one frame).
- Map each `ld.h d4, [a15]+0` to its source address; that address holds
  the constant 16-bit sigIdx.
- Cross-reference the sigIdx top4 with the dispatch table to confirm
  which "frame group" each signal belongs to.
- The user's bit layouts for A5/A6/A7 then correspond to specific
  contiguous runs of sigIdx in the broadcast function body.
