# The King of Fighters '96: static recompilation

**The King of Fighters '96 (SNK, 1996 / NGM-214) running as a native PC
program: its Motorola 68000 program is recompiled to C and runs on the
[neogeorecomp](https://github.com/sp00nznet/neogeorecomp) MVS board model.**

The real MVS system ROM boots the cartridge, checks its own RAM and
checksum, and starts the game exactly as on hardware. There is no BIOS HLE
and no emulator frontend. The only interpreter is the toolkit's Musashi
fallback, used while bringing the port up and as the `--verify` oracle.

> **No ROM or BIOS data is included.** You need your own legally obtained
> dumps of the MAME `kof96` set and the `neogeo` system ROMs. The recompiled
> C is generated from your dump on your machine into the build directory; it
> is never committed. The prebuilt release binaries contain code translated
> from the game's program ROM and are provided for use with those dumps.

## Download

Prebuilt packages are attached to the [v0.1.1 release](https://github.com/omegakatana92/The-King-of-Fighters-96-Recomp/releases/tag/v0.1.1):

| Platform | Asset |
|---|---|
| Windows x64 | `kof.96-Windows-x64.zip` (contains `kof 96.exe`, SDL2 and the VC++ runtime) |
| Steam Deck / Linux x86_64 | `KOF96-AudioFixed-x86_64.AppImage` |

These are the exact release-asset names; GitHub replaced the space in the
local `kof 96...` filenames with a dot. Neither package contains ROMs or BIOS
files. Put your unzipped ROM files in a `roms` folder next to the
executable/AppImage.

## Deliverables

| Platform | Artifact |
|---|---|
| Windows x64 | `dist/windows/kof 96-Windows-x64/kof 96.exe` (+ `SDL2.dll`) |
| Steam Deck / Linux x86_64 | `dist/steamdeck/KOF96-AudioFixed-x86_64.AppImage` |

The Windows package contains no ROMs. The AppImage contains no ROMs. Put
your unzipped ROM files in a `roms` folder next to the executable/AppImage.

## Status

**v0.1.1. Boots through the real BIOS, reaches gameplay, runs 100% native
on the measured sessions, and the native code matches Musashi with 0
mismatches. v0.1.1 fixes the M1 bank-mask bug that silenced the music at
character selection.**

| Area | State |
|---|---|
| Boot | Real MVS BIOS (`sp-s2.sp1`): RAM test, eyecatcher, `INSERT COIN`, attract, title |
| Input / credits | Coin, Start, directions and A/B/C/D tested by scripted sessions |
| Gameplay | Member select, order select, a full 3-on-3 match against the King team, continue screen and the next stage |
| Graphics | Sprites, backgrounds, fix layer, palettes, HUD, animation |
| Audio | Continuous music through character select and the match after the v0.1.1 M1 bank-mask fix; 337.9 s capture is non-silent (peak 26,937 at 55,555 Hz stereo), every 1 s window 56-200 s above 100 RMS. Not auditioned subjectively |
| Native coverage | **100.00%** of executed 68k instructions over a 20,000-frame scripted session (377,468,486 native, 0 interpreted); five fixed RTC dates and host time all reached 0 interpreted |
| `--verify` | **4,102,741 blocks, 0 mismatches**, 100% native over 7,000 frames of coin/start/select/match |
| Windows | Release x64 built with MSVC 19.51 (Visual Studio 2026) + SDL2 2.32.10; windowed and `--fullscreen` launches exit 0 |
| Steam Deck | AppImage built and run under WSL2 Ubuntu 22.04, including windowed/fullscreen on a 1280x800 Xvfb display; **physical Deck hardware not tested** |

Separate Windows and interpreter-only builds were made. The recompiled and
interpreter builds produced **pixel-identical frames** at 600, 1,200, 1,800
and 2,399 (boot, eyecatcher, attract, title).

## The ROM set

The supplied archive was hashed file by file and matches MAME's
`ROM_START(kof96)` (MVS, NGM-214) exactly. It is the plain unencrypted set:
no NEO-SMA/NEO-CMC, no protection read, no S-ROM extraction.

| File | Size | CRC32 | SHA1 (prefix) | Role |
|---|---:|---|---|---|
| `214-p1.p1` | 1,048,576 | `52755d74` | `4232d627` | fixed program bank |
| `214-p2.sp2` | 2,097,152 | `002ccb73` | `3ae8df68` | banked program, 2 x 1 MB |
| `214-c1.c1` | 4,194,304 | `7ecf4aa2` | `f773c4c1` | graphics plane 0/1 |
| `214-c2.c2` | 4,194,304 | `05b54f37` | `cc31653f` | graphics plane 2/3 |
| `214-c3.c3` | 4,194,304 | `64989a65` | `e6f3749d` | graphics plane 0/1 |
| `214-c4.c4` | 4,194,304 | `afbea515` | `ae875052` | graphics plane 2/3 |
| `214-c5.c5` | 4,194,304 | `2a3bbd26` | `7c1a7e50` | graphics plane 0/1 |
| `214-c6.c6` | 4,194,304 | `44d30dc7` | `c8ae001e` | graphics plane 2/3 |
| `214-c7.c7` | 4,194,304 | `3687331b` | `2be95caa` | graphics plane 0/1 |
| `214-c8.c8` | 4,194,304 | `fa1461ad` | `6c71a7f0` | graphics plane 2/3 |
| `214-s1.s1` | 131,072 | `1254cbdb` | `fce5cf42` | fixed layer |
| `214-m1.m1` | 131,072 | `dabc427c` | `b76722ed` | Z80 sound driver |
| `214-v1.v1` | 4,194,304 | `63f7b045` | `1353715f` | ADPCM-A |
| `214-v2.v2` | 4,194,304 | `25929059` | `6a721c4c` | ADPCM-A |
| `214-v3.v3` | 2,097,152 | `92a2257d` | `5064aec9` | ADPCM-A |

BIOS files used: `sp-s2.sp1` (MVS Asia/Europe v2, CRC `9036d879`),
`sfix.sfix`, `sm1.sm1`, `000-lo.lo`. The archive also carried other BIOS
sets; they are not the test target.

## Build

Requirements: CMake 3.21+, a C/C++ toolchain, and SDL2 for the window.
Headless builds need no SDL2.

### Windows x64 (MSVC)

```powershell
cmake -S . -B build-windows -G "Visual Studio 18 2026" -A x64 `
      -DKOF96_ROM_DIR="C:\path\to\roms" `
      -DSDL2_DIR="C:\path\to\SDL2-2.32.10\cmake"
cmake --build build-windows --config Release --target kof96 --parallel
```

or, in one step:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\build-windows.ps1 `
    -RomDir C:\path\to\roms -SdlDir C:\path\to\SDL2-2.32.10\cmake
```

Output: `build-windows\Release\kof 96.exe` and `SDL2.dll`.

Without `-DKOF96_ROM_DIR` the player is interpreter-only, which is the
quickest way to validate a dump and the board model:

```powershell
cmake -S . -B build-interp -DCMAKE_DISABLE_FIND_PACKAGE_SDL2=ON
cmake --build build-interp --config Release --target kof96
build-interp\Release\"kof 96.exe" --headless --interp --rom-path roms --frames 1200
```

### Linux x86_64

```bash
sudo apt install build-essential cmake libsdl2-dev
JOBS=4 ./scripts/build-linux.sh "$PWD/roms"
./build-linux/"kof 96" --rom-path roms
```

### Steam Deck AppImage

```bash
JOBS=4 ./packaging/appimage/build-appimage.sh "$PWD/roms"
```

Output: `dist/steamdeck/KOF96-AudioFixed-x86_64.AppImage` (set
`KOF96_APPIMAGE_NAME` to change the file name). The AppRun script
looks for ROMs in `~/.local/share/kof96/roms-clean`,
`~/.local/share/kof96/roms`, a `roms` folder next to the AppImage, and the
usual Deck locations; if the selected folder has no BIOS it uses
`~/.local/share/kof96/roms` as `--bios-path`. It bundles SDL2 and adds
`--fullscreen` unless told otherwise. The image is 4:3 pillarboxed on the
Deck's 16:10 panel.

## Run

```
"kof 96.exe" --rom-path roms
```

Useful flags: `--headless`, `--frames N`, `--input FILE`,
`--screenshot N:FILE`, `--wav FILE`, `--interp`, `--verify`,
`--dump-misses FILE`, `--scale N`, `--fullscreen`, `--mute`.

### Controls

| Key | Action |
| --- | --- |
| Arrows / left stick | move |
| Z / X / C / V (A/B/X/Y on a pad) | Neo Geo A / B / C / D |
| 5 / Back | insert coin |
| 1 / Start | player 1 start |
| 2 / Start (P2) | player 2 start |
| 3 / left shoulder | select |
| 9 | service credit |
| F2 | test switch |
| F11 | fullscreen |
| Esc | quit |

Insert a coin before Start does anything, as on an MVS cabinet. SDL2
gamepads use the toolkit's fixed GameController mapping; a pad SDL does not
know can be described with `SDL_GAMECONTROLLERCONFIG`.

## Verification

The generator translated **1,093,471 instructions into 19,148 routines and
31,213 dispatch entries** on both Windows and Linux. A fresh clone starts at
**1,077,293 instructions / 30,595 entries**: the extra 605 entry points are
runtime-only, found by the `profile` target from your own dump, and are not
committed. Run `cmake --build build-windows --config Release --target
profile` once and rebuild to reach the published count. Details and logs are
in `docs/TESTING.md`.

```text
# 20,000-frame soak: boot, coin, start, select, a full match
[exec] native blocks 12232598, native instructions 377468486,
       interpreted instructions 0 (100.00% native), 0 uncovered entry points

# replay every native block in Musashi and compare registers, flags and bus writes
[verify] 4102741 blocks checked, 0 mismatches
```

The MVS calendar is seeded from the host clock by default (as on hardware),
which can change the AI's random choices slightly. For reproducible tests,
`NG_RTC="1996-01-01 00:00:00"` freezes it. The measurements above use that
seed; five different fixed dates and the host clock all also ran at 0
interpreted instructions.

The Linux build produced the same coverage and 0 mismatches
(`4,102,741 blocks`, `133,013,234` native instructions), and its
fixed-RTC 19,999-frame screenshot is byte-identical to the Windows one.

## Known limitations

* **Subjective audio quality was not auditioned.** The Z80 driver runs, the
  YM2610 is programmed, the 56-200 s windows are continuous, and the
  automated regression check passes, but mix/volume balance and every track
  were not checked by ear.
* **Physical Steam Deck hardware was not available.** The AppImage was built
  and launched under WSL2 Ubuntu 22.04 (headless, and windowed/fullscreen at
  1280x800 on an Xvfb virtual display). SteamOS 3 uses a compatible glibc
  2.35, but Deck LCD/OLED, Steam Input and Gaming Mode remain unvalidated on
  real hardware.
* **Physical gamepads were not tested**; the SDL2 mapping is the toolkit's
  existing tested path.
* **AES/PAL variants, memory cards, two-player sessions and later stages**
  were not part of the measured sessions. The toolkit does not implement
  memory cards.
* **Scripted sessions can diverge at late frames between builds.** Native
  code takes interrupts at recompiled-block boundaries while Musashi checks
  them between instructions; a button press can therefore land on a slightly
  different frame. The host RTC also seeds the game's random choices and can
  change the AI path. This is an upstream toolkit/hardware property, not a
  translation error; `--verify` found no mismatches in any run. Fix
  `NG_RTC` when byte-for-byte reproducible runs are needed.
* **The release binaries contain translated game code.** The executable and
  AppImage embed a recompilation of SNK's program ROM. No ROM or BIOS data is
  included, but the underlying game remains SNK's; use the builds only with
  ROMs you are legally entitled to use. The project source is the licensed
  part; the binaries are provided as-is for that purpose.

## Project layout

```
CMakeLists.txt              build: recompiler generator + player
src/game.c, game.h          verified ng_game_t ROM layout
src/main.c                  player (ng_main)
src/recomp_main.c           generator (ng_recomp_main)
neogeorecomp/               toolkit v0.2.0 (MIT) + generic fixes
tests/play.txt              20,000-frame coin/start/select/match session
tests/coin_start.txt        shorter session for --verify
tests/check_audio.py        audio continuity regression check (`audio-check`)
scripts/build-linux.sh      Linux Release build
scripts/build-windows.ps1   Windows Release build
packaging/appimage/         AppImage build, AppRun, desktop file, icon, README
packaging/windows-README.txt  text shipped in the Windows folder
docs/                       compatibility, build, test and runtime notes
dist/windows/               Windows release folder (no ROMs)
dist/steamdeck/             AppImage + README (no ROMs)
```

## License

The project's own source is licensed under the **PolyForm Noncommercial
License 1.0.0** (see `LICENSE`; confirmed by the project owner on
2026-10-26, scope in `LICENSE-STATUS.md`). Copyright (c) 2026
omegakatana92. `neogeorecomp/` remains MIT;
Musashi and z80 are MIT, ymfm is BSD-3-Clause, SDL2 is zlib. Full
attribution is in `THIRD_PARTY_NOTICES.md` and in the preserved
`neogeorecomp/LICENSE`, `NOTICE` and `LICENSES/` files.

No SNK ROMs, BIOS images, generated C or entry lists are distributed. The
King of Fighters and Neo Geo are trademarks of SNK Corporation. This project
is not affiliated with or endorsed by SNK.
