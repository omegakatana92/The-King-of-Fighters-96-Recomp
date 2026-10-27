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

## 4. M1 bank mask from the M1 file size (`src/audio.c`)

This is the KOF '96 audio fix. MAME's `neogeo_base_state::init_audio()`
builds each Z80 bank entry as

```
bank_address = 0x10000 + ((bank << (11 + window)) & address_mask);
```

in the audio region. `ROM_RELOAD` places the first byte of the M1 file at
region offset `0x10000`, so the **file** offset is the masked value alone.
`address_mask` comes from the region length (`M1 size + 0x10000`):

```
address_mask = (region_len - 0x10000 - 1) & 0x3FFFF
             = (M1 size - 1) & 0x3FFFF      (for files up to 512 KB)
```

so a 64 KB M1 masks with `0xFFFF`, a 128 KB M1 with `0x1FFFF`, and 256/512 KB
M1s with `0x3FFFF`. The old code used `(size - 0x10000 - 1)`, which gives
`0xFFFF` for a 128 KB M1.

KOF '96's driver selects M1 banks `0x18000`–`0x1F000` when it loads its music
data at character selection. With `0xFFFF`, those offsets were truncated to
`0x8000`–`0xF000`, so the Z80 read unrelated bytes (code/data) and the BGM
went silent. ADPCM sound effects already triggered by the 68000 kept playing,
which exactly matches the reported symptom. The same failure occurs in
`--interp` mode because this code is shared. The fix derives the mask from
the M1 file size, as MAME does, and is generic for all M1 sizes.

Evidence: `NG_AUDIO_TRACE=1` showed banks `1F000/1E000/1C000/18000` at the
silent section; a MAME 0.242 capture of the same input sequence has
continuous music there. After the fix the WAV is continuous from 56 s
(character select) through 200 s (match), and the new `audio-check` target
guards it. The old "second 0x10000" bug for 512 KB M1s is also covered by the
same formula.

## 5. Frame-boundary Z80 sync (`src/audio.c`)

`audio_take_samples()` now calls `audio_sync()` before generating samples.
The Z80 previously advanced only when the 68000 touched the sound latches,
so a game that stopped polling could starve the sound CPU and its YM2610
timers. Syncing once per frame keeps the Z80 in step with `ng_cycles`
regardless of 68k polling. This is generic; it does not alter the 68000
timeline or the recompiled code.

## 6. Fullscreen and 4:3 presentation (`src/window_sdl.c`,
`src/platform.c`, `src/neogeo.c`)

`--fullscreen` creates a desktop-fullscreen window, and F11 toggles it. The
320x224 framebuffer is drawn into a 4:3 rectangle centred in the output
(1280x800 -> 1066x800), never stretched to 16:10. This is required for a
sensible Steam Deck image.

## 7. Optional cart features (not used by KOF '96)

These are configuration fields, not hacks, and are zero/NULL for this game:

* `ng_game_t.bank_map` / `bank_write_addr`: a cart-supplied bank table and
  select port for non-standard mappers (e.g. NEO-SMA at `$2FFFE4`).
* `ng_game_t.prot_read_addr` / `prot_value`: a protection read that returns
  a constant (e.g. `$2FE446 = $9A37`).
* `ng_game_t.fix_bank_type`: 512 KB fixed-layer S ROMs that take two extra
  tile-code bits from VRAM (`NG_FIX_BANK_KOF2000`).

`docs/hardware-notes.md` describes the underlying behaviour.

## 8. Optional fixed calendar for reproducible tests (`src/io.c`)

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
