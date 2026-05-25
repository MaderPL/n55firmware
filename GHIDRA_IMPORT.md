# Importing the symbol list into Ghidra

Two equivalent files are provided:

1. **`ghidra_symbols.txt`** — plain `NAME ADDRESS` per line, importable
   via Ghidra's built-in `ImportSymbolsScript.java`.
2. **`ghidra_rename.py`** — Jython script. Paste into the Ghidra Script
   Manager (or save it under your Ghidra scripts directory) and run it.

Both contain the same 110 names: function renames + a few data-label
renames for the key flash tables and RAM globals.

## Option A — `ghidra_symbols.txt`

1. In Ghidra, open the firmware program.
2. **Window → Script Manager**.
3. Search for `ImportSymbolsScript`.
4. Click *Run*. It will prompt for a file — pick `ghidra_symbols.txt`.
5. Each line in the file is `NAME ADDRESS`; the script creates a label
   at each address. Function addresses become function names; non-code
   addresses become data labels.

The bundled `ImportSymbolsScript` accepts both `NAME ADDR` and
`ADDR NAME` per line; this file uses the former.

## Option B — `ghidra_rename.py` (recommended)

1. Open the firmware program in Ghidra.
2. **Window → Script Manager**.
3. Click the green `+` (New Script) → choose **Jython**.
4. Replace the template with the contents of `ghidra_rename.py`.
5. Save and click *Run*.

The script renames existing functions in place and creates labels for
non-function addresses. It prints a tally at the end like:
```
Renamed 78 functions, created 32 data labels, skipped 0
```

## What the names cover

- **Com layer signal-write chain** (10+ functions: `Com_WriteSignal`,
  `Com_SignalDispatch_*`, etc.)
- **Signal-write dispatch table** at `0x80032580` and its 16 handlers.
- **CAN driver internals** that weren't already symbolised.
- **Scheduler tables** (Table A..G) and tick-call sites.
- **MsgCfgEntry / BaudCfgEntry / buffer descriptor table** addresses.
- **Key RAM globals** used by the CAN/Com runtime
  (`PerSignal_State_Table`, `SubSignal_StatusBuffer`,
  `moHw_to_msgCfgIdx_table`, `channelTypeTab`, etc.).
- **Application-layer encoders** identified during the broadcast-chain
  analysis.

Existing Ghidra symbols (e.g. `CAN_Transmit`, `CAN_Rx_ISR`, etc.) are
left untouched.

## Modifying / extending

If you want to add more names later, append lines to `ghidra_symbols.txt`
in the same format and re-run. Or edit `ghidra_rename.py`'s `symbols`
list and re-run.

## A note about RAM addresses

Several entries are RAM addresses in the `0xd000xxxx` range. Ghidra
treats them as data labels and will add the label at that exact
location in your RAM memory block, provided the block exists in the
project. If not, you can create it via *Memory Map → Add Block* before
running the import.
