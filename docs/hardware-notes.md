# Hardware notes

KOF '96 is a conventional MVS cart, so the port needed no title-specific
hardware work. The notes below record what the set uses and the generic
runtime behaviour that matters.

## Cart identity

MAME's `ROM_START(kof96)` is the plain MVS version:

* **P ROMs** are 1 MB + 2 MB, unencrypted (TC538200 / TC5316200). They are
  `ROM_LOAD16_WORD_SWAP`, hence the 16-bit swap in `src/game.c`.
* **Program banking** is the standard PROGBK1 arrangement: write the bank
  number to `$2FFFF0`, and `$200000-$2FFFFF` shows the selected 1 MB slice.
* **C ROMs** are eight 4 MB files in odd/even pairs (32 MB total), the
  CHA256 arrangement the renderer expects.
* **S ROM** is the plain 128 KB fixed layer. No extraction from graphics is
  needed.
* **M1** is 128 KB and plays the cart's own sound driver after the BIOS
  hands over from SM1.
* **V ROMs** are 4 + 4 + 2 MB of ADPCM-A samples.
* There is **no protection device** and no encryption. The alternate
  `kof96a`/`kof96h` sets in MAME are different dumps and are not this port.

## Program image and header

After the swap, `214-p1.p1` begins with the 68000 stack pointer and reset
vector, and carries `NEO-GEO` at `$100` plus the BIOS entry table at
`$122` (USER), `$128` (PLAYER_START), `$12E` (DEMO_END) and `$134`
(COIN_SOUND). The recompiler seeds discovery from both vector tables, those
four entry points, static call targets, jump tables and code pointers.

The banked 2 MB holds a mix of code and data. The recompiler discovers code
from the first banked MB, and the runtime's bank-window guard interprets
rather than dispatch if the cart ever selects another physical bank at the
same address. During the measured sessions the game kept bank 0 selected and
all banked execution stayed native. Banks 2/3 wrap to 0/1, the usual 2 MB
PROGBK1 mirroring.

## Boot and watchdog

The port uses the real `sp-s2.sp1` BIOS. It runs its RAM test, checksums
itself and the cartridge, initialises backup RAM and hands control to the
cart. The BIOS writes the watchdog port `$300001`; the generic board model
resets the whole machine if it is not kicked for about 1.62 M 68000 clocks,
keeping work/backup RAM. No delay or patch was added for KOF '96.

## Graphics

The per-scanline LSPC renderer handles the sprite list, sticky chains,
vertical/horizontal shrink, the 96-sprites-per-line limit, auto-animation,
the fix layer and both palette banks. KOF '96 uses raster effects (the HUD
and backgrounds change palettes/scroll mid-frame); these are driven by the
raster timer IRQ and the per-line renderer, not by title-specific code.

## Sound

The BIOS starts its SM1 driver; when the cart selects its own M1 through the
fix/Z80 ROM latch, the runtime restarts the Z80 at the M1 reset vector.
Commands go through the NMI/reply latch to the YM2610. ymfm synthesises FM,
SSG and ADPCM-A at the chip rate. KOF '96's M1 is 128 KB, within the plain
128 KB audio region; the generic M1 bank-mask fix is inert here but is
described in `docs/runtime-changes.md`.

## M1 bank offsets above 64 KB

The Z80 bank windows select offsets in the M1 image; the 128 KB KOF '96 M1
uses offsets `0x18000`–`0x1F000` for music data at character selection. The
mask must come from the M1 size (`(size - 1) & 0x3FFFF`, matching MAME's
`address_mask`), not from `size - 0x10000`. The latter is `0xFFFF` for a
128 KB M1 and truncates every bank above 64 KB, so the driver reads unrelated
bytes and the BGM goes silent while already-triggered ADPCM effects continue.
`docs/runtime-changes.md` has the full derivation and the regression check.

## Calendar and randomness

The board's uPD4990A real-time clock is driven from the host's local time, as
a real battery-backed calendar would be. KOF '96 reads it during boot and
uses it to vary some random choices (AI behaviour, menu paths). For
reproducible tests, `NG_RTC="YYYY-MM-DD HH:MM:SS"` freezes the calendar; all
coverage figures in this project use it. Without it, two runs can reach
different (correctly emulated) AI paths, which is why a given frame number
is only guaranteed identical when the clock is fixed.

## Input

MVS controller ports are active-low; the runtime inverts the `ng_input_t`
bits. Coin/start are BIOS-level credits. Standard SDL2 GameController
mapping: D-pad/left stick, A/B/X/Y -> Neo Geo A/B/C/D, Start, Back = coin,
left shoulder = select. Steam Input's default gamepad template works
unchanged; the AppRun enables fullscreen for Gaming Mode.
