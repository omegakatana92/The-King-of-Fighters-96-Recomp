# Runtime changes in the vendored toolkit

The project vendors neogeorecomp v0.2.0 at commit
`af96b2b4b39b42b392b17bcaa6a74a5f27088202` (MIT). On top of that baseline it
carries the generic fixes below. There are **no title-specific addresses,
patches or ROM checks** in the runtime; the only KOF '96-specific file is
`src/game.c`, which describes the ROM layout.

The fixes are offered under the toolkit's MIT license.

## 1. Native bank-window guard (`src/exec.c`)

`lookup()` refuses a native entry in `$200000-$2FFFFF` while the cart's bank
window is not at bank 0:

```c
if ((a & 0xFE0000) == 0x200000 && ng_bank_base != 0) return NULL;
```

The recompiled bank table describes the first banked MB only. If a cart maps
another physical bank at the same 68k address, the same address means
different bytes, so the block is interpreted instead of running stale native
code. This makes flat dispatch safe for multi-bank carts. For KOF '96 the
measured sessions kept bank 0 selected, so nothing was interpreted.

`bus.c` exports `ng_bank_base` and keeps the same value through bank writes
and resets.

## 2. Instruction accounting (`src/exec.c`)

`exec_native_instrs` counts instructions executed inside native blocks (from
the `ng_icount` delta). `exec_report()` prints native **and** interpreted
instruction counts plus a measured native share:

```
[exec] native blocks ..., native instructions ..., interpreted instructions ...
       (100.00% native), ... uncovered entry points
```

This replaces the old "blocks" only line and is what the coverage numbers in
the README come from.

## 3. Watchdog reset in the board, not the I/O device

The `$300001` watchdog kick and the ~1.62 M 68000-clock deadline moved from
`io.c` into `neogeo.c`. On expiry the whole board is reset (bus, LSPC,
palette, video blanking, video latch, audio ROM select, Z80, CPU) while work
RAM and battery-backed RAM keep their contents. The reset asserts IRQ3 like
the BIOS expects. This is the generic MVS behaviour and several games use a
watchdog reset as a protection check during backup-RAM initialisation.

## 4. YM2610 M1 bank mask (`src/audio.c`)

The Z80 bank ports address `0x10000 + ((bank << shift) & mask)` in the MAME
audio region. Because the region's `0x10000` base is the start of the M1
file (`ROM_RELOAD`), the file offset is the masked value alone. The old code
added a second `0x10000`, which on 512 KB M1 carts read `$FF` padding as
sample tables. KOF '96 has a 128 KB M1 where the difference is inert, but the
fix is generic. `NG_AUDIO_TRACE=1` prints command/reply and bank diagnostics.

## 5. Fullscreen and 4:3 presentation (`src/window_sdl.c`,
`src/platform.c`, `src/neogeo.c`)

`--fullscreen` creates a desktop-fullscreen window, and F11 toggles it. The
320x224 framebuffer is drawn into a 4:3 rectangle centred in the output
(1280x800 -> 1066x800), never stretched to 16:10. This is required for a
sensible Steam Deck image.

## 6. Optional cart features (not used by KOF '96)

These are configuration fields, not hacks, and are zero/NULL for this game:

* `ng_game_t.bank_map` / `bank_write_addr`: a cart-supplied bank table and
  select port for non-standard mappers (e.g. NEO-SMA at `$2FFFE4`).
* `ng_game_t.prot_read_addr` / `prot_value`: a protection read that returns
  a constant (e.g. `$2FE446 = $9A37`).
* `ng_game_t.fix_bank_type`: 512 KB fixed-layer S ROMs that take two extra
  tile-code bits from VRAM (`NG_FIX_BANK_KOF2000`).

`docs/hardware-notes.md` describes the underlying behaviour.

## 7. Optional fixed calendar for reproducible tests (`src/io.c`)

The uPD4990A calendar keeps following the host's local time by default, which
is what hardware does. `NG_RTC="YYYY-MM-DD HH:MM:SS"` freezes it for a run.
KOF '96 derives some random choices from the calendar, so without the hook
the same scripted session can take a slightly different (still correct) AI
path on a later run. All coverage numbers use a fixed RTC; five different
dates and the host clock reached 0 interpreted instructions with the final
entry list. This is a diagnostics/test hook, not a title setting.

## Regression checks

The toolkit's own conformance harness still passes 59/60 (the same as the
reference interpreter) when built separately. The project's `--verify` runs
checked 4.1 M native blocks against Musashi with 0 mismatches on both
Windows and Linux.
