# Compatibility and ROM layout

## Identification

| | |
|---|---|
| Game | The King of Fighters '96 (NGM-214) |
| MAME set | `kof96` - "MVS VERSION" |
| MAME driver | `snk/neogeo.cpp`, `ROM_START(kof96)` |
| Hardware | MVS, standard PROGBK1 program banking, CHA256 graphics |
| BIOS used | `sp-s2.sp1` (MVS Asia/Europe v2) |
| Protection/encryption | none: plain P ROMs, plain C/S/M/V ROMs |

The supplied archive was hashed entry by entry. Every file's CRC32 and SHA1
match the MAME definition, so no decrypt step is needed:

| File | Size | CRC32 | Role |
|---|---:|---|---|
| `214-p1.p1` | 1,048,576 | `52755d74` | fixed program bank |
| `214-p2.sp2` | 2,097,152 | `002ccb73` | banked program (2 x 1 MB) |
| `214-s1.s1` | 131,072 | `1254cbdb` | fixed layer |
| `214-m1.m1` | 131,072 | `dabc427c` | Z80 driver |
| `214-v1.v1` | 4,194,304 | `63f7b045` | ADPCM-A |
| `214-v2.v2` | 4,194,304 | `25929059` | ADPCM-A |
| `214-v3.v3` | 2,097,152 | `92a2257d` | ADPCM-A |
| `214-c1.c1` .. `214-c8.c8` | 8 x 4,194,304 | see README | graphics, odd/even pairs |

The archive also contains `000-lo.lo`, `sfix.sfix`, `sm1.sm1`, `sp-s2.sp1`
and a range of alternate/Universe BIOS files. Only the four listed BIOS
files are used by default.

## Program image

```
$000000-$0FFFFF  fixed bank        214-p1.p1 after 16-bit byte swap
$200000-$2FFFFF  bank window       214-p2.sp2: bank 0 = file +$000000,
                                   bank 1 = file +$100000
```

`214-p1.p1` carries the `NEO-GEO` signature at `$100` after the swap, which
the loader checks by construction; the fixed bank holds the cartridge header
entry points the BIOS calls (USER `$122`, PLAYER_START `$128`, DEMO_END
`$12E`, COIN_SOUND `$134`). The cartridge writes the bank number to
`$2FFFF0`; the runtime maps it to a 1 MB slice of the 2 MB banked image.
Banks 2 and 3 wrap onto 0 and 1, as on a 2 MB PROGBK1 board.

The recompiler sees the fixed 1 MB plus the first banked MB. Code that the
BIOS executes from bank 1 address space is still compiled from bank 0 bytes,
which is safe because the runtime refuses native bank-window dispatch while
the selected bank is not 0 (see `docs/runtime-changes.md`); those paths fall
back to Musashi rather than running the wrong bytes. In the measured sessions
the cart kept bank 0 selected, so this fallback never cost a native block.

## Hardware behaviour exercised

| Feature | Status |
|---|---|
| 68000 fixed bank + 2 MB banked program | yes |
| Standard `$2FFFF0` PROGBK1 bank select | yes |
| 32 MB CHA256 graphics (odd/even pairs) | yes |
| 128 KB S ROM fixed layer | yes |
| 128 KB M1, Z80 banking, M1 bank mask, NMI/reply latches | yes (bank mask fixed in v0.1.1) |
| 10 MB ADPCM-A samples, YM2610 FM/SSG/ADPCM | yes |
| MVS BIOS boot, RAM/checksum tests, coin/start | yes |
| uPD4990A calendar | yes (host time; `NG_RTC` freezes it for tests) |
| Raster timer IRQ and per-scanline sprite rendering | yes |
| Watchdog reset | yes |
| SDL2 window, gamepads, keyboard, 4:3 fullscreen | yes |
| Memory card | no (toolkit scope) |
| AES/PAL variants | not tested |
| Two-player sessions | not tested |

## Coverage

Measured on the scripted sessions in `tests/`:

| Session | Native instructions | Interpreted | Native share |
|---|---:|---:|---:|
| Windows, 20,000 frames (`tests/play.txt`, fixed RTC) | 377,468,486 | 0 | 100.00% |
| Windows, 7,000-frame `--verify` | 133,013,234 | 0 | 100.00% |
| Linux, 20,000 frames (same RTC) | 377,468,486 | 0 | 100.00% |
| Linux, 7,000-frame `--verify` | 133,013,234 | 0 | 100.00% |

Coverage is per session, from the `[exec]` line, not a claim about every
path in the game. Later stages, other teams, two-player mode and the test
menu were not driven by the scripts.

## Unsupported / limitations

* No memory card, AES/PAL timing or link-up support.
* Audio continuity and signal level were checked; subjective mix/volume was
  not auditioned.
* Physical Steam Deck and physical controllers were not available.
* Release binaries embed translated ROM code and are provided for use with
  legally owned ROMs; no rights to SNK's game data are granted.
