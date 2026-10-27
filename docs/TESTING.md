# Testing

All runs used the owner's `kof96` dump (CRC/SHA1 matched against MAME) and
the MVS `sp-s2.sp1` BIOS. Frame numbers are 59.1856 Hz video frames from
power-on. Test artifacts (logs, WAVs, screenshots) live in `shots/` and are
not part of the source.

## 1. ROM validation

Every file in the archive was hashed and compared with MAME's
`ROM_START(kof96)`: all 15 game files and `sp-s2.sp1` match (CRC32 and
SHA1). The fixed bank shows `NEO-GEO` at `$100` after the 16-bit swap, and
the P ROM image is 3 MB (1 MB fixed + 2 MB banked). No encryption or
protection is present.

## 2. Interpreted boot (board model only)

```
build-interp\Release\"kof 96.exe" --headless --interp --rom-path roms \
    --frames 2400 --screenshot 600:i0600.png --screenshot 2399:i2399.png
```

Frames observed:

| Frame | Screen |
|---:|---|
| 300 | black / BIOS self-test |
| 600 | NEO-GEO eyecatcher, "MAX" |
| 1,200 | `INSERT COIN`, LEVEL-4, CREDIT 00 |
| 1,800 | AGAIN... / INSERT COIN |
| 2,399 | attract artwork with `INSERT COIN` |

This verifies the board model independently of the recompiler.

## 3. Native build and coverage

```
cmake --build build-windows --config Release --target kof96 --parallel
build-windows\Release\"kof 96.exe" --headless --rom-path roms --frames 2400
```

Boot result: 30,595 recompiled entry points, 99.80% native (89,184
interpreted instructions in the first run), 60 uncovered entry points.

The recompiled and interpreter builds rendered **byte-identical PNGs** at
frames 600, 1,200, 1,800 and 2,399 (SHA-256 equal).

### Profile passes

`NG_PROFILE=1` plus `--dump-misses` identified a few hot interpreted entry
points, all short copy/loop tails in the fixed bank:

```
[profile] 456702 interpreted from $009B30  move.w (A0)+,(A1)
[profile] 235039 interpreted from $009B48  move.w (A0)+,(A1)
[profile] 128362 interpreted from $009694  move.w (A0)+,($2,A1)
...
```

Two profile/dump passes added 219, then 220 entry points; the 9,000-frame
session then reported **100.00% native, 0 uncovered**. A 20,000-frame
gameplay soak added 205 more (later match/continue paths) and 64 fixed/bank
entries.

The first repeated soaks then exposed a source of run-to-run variation: the
MVS calendar is seeded from the host clock and the game uses it to vary its
random choices. The same binary could reach a different (still correct) AI
path on a later run. A generic `NG_RTC="YYYY-MM-DD HH:MM:SS"` test hook now
freezes the calendar. Profiling fixed dates added 71 more entries for one
seed, then 1 + 45 for two others. With the union of **605 runtime entries**,
five different fixed dates and the host clock all reported 0 interpreted
instructions.

Final Windows generator: **1,093,471 instructions, 19,148 routines, 31,213
dispatch entries** (identical Linux numbers).

### Final Windows soak

```
set NG_RTC=1996-01-01 00:00:00
build-windows\Release\"kof 96.exe" --headless --rom-path roms \
    --frames 20000 --input tests/play.txt
```

```
[exec] native blocks 12232598, native instructions 377468486,
       interpreted instructions 0 (100.00% native), 0 uncovered entry points
```

A second identical run produced the same block/instruction counts and a
byte-identical frame 19,999 (SHA-256 equal), as did runs with the dates
1996-02-14, 2000-12-31, 1980-01-01, 2026-10-26 and host time.

`tests/play.txt` starts at power-on, inserts a credit at frame 1,300,
starts at 1,500, confirms the default team on the member-select screen, and
plays through order select and a full match against the King team. At frame
14,000 the run reaches the CONTINUE screen; at 19,999 it is in the next
stage. Screenshots at 6,000, 9,000, 14,000 and 19,999 show the HUD, health
bars, sprites, backgrounds, fix layer and palettes rendering correctly.

## 4. `--verify` (native vs Musashi)

Boot:

```
[verify] 169946 blocks checked, 0 mismatches
[exec] native blocks 169946, native instructions 13348453, ... 100.00% native
```

Coin/start/member-select/first match (`tests/coin_start.txt`, 7,000 frames):

```
[verify] 4102741 blocks checked, 0 mismatches
[exec] native blocks 4102741, native instructions 133013234,
       interpreted instructions 0 (100.00% native), 0 uncovered entry points
```

`--verify` replays every native block in Musashi with the same bus values
and compares registers, flags and the complete write sequence. 0 mismatches
over 4.1 million blocks.

## 5. Timing and determinism

With a fixed `NG_RTC`, two Windows runs and a Linux run of the same 20,000-
frame script produced the same block/instruction counts and byte-identical
frame-19,999 PNGs. Boot and attract frames are also pixel-identical between
the native and interpreter builds.

With the default host clock, two runs minutes apart can reach a different
AI path because the game derives random choices from the calendar. Each
path still runs natively (0 interpreted after the seed coverage above), but
the frame at a given number can differ. Native code also takes interrupts
at block boundaries while Musashi takes them between instructions, so a
scripted button can land on a different frame in a verify/oracle run. This
is not a translated-instruction mismatch: `--verify` reports none.

## 6. Audio

The KOF '96 audio failure was caused by the M1 bank mask truncating music
banks above 64 KB (see `docs/runtime-changes.md`). Before the fix, a
12,000-frame capture was silent from about 61 s to 88 s, with only isolated
ADPCM blips, exactly matching the reported symptom. A MAME 0.242 capture of
the same input sequence has continuous music through that section.

After the fix:

```
# 20,000 frames, fixed RTC
NG_RTC=1996-01-01 ./build-linux/"kof 96" --headless --rom-path roms \
    --frames 20000 --input tests/play.txt --wav fixed.wav
```

337.9 s, 55,555 Hz stereo, peak 26,937. Every 1-second window from 56 s
(character select) through 200 s (match) is above 100 RMS; the minimum in
56-90 s is 1,780, 90-130 s is 746, and 130-200 s is 1,696. The later short
gaps at ~208/217/239 s are the normal round/continue transitions; the
280-298 s gap is the game-over -> title transition, after which the attract
match music resumes.

Native and `--interp` captures have the same 56-200 s continuity, and the
Windows build matches the Linux RMS values. Subjective quality (mix, volume,
every track) was not auditioned.

## 7. Audio regression test

`tests/check_audio.py` checks the 56-90, 90-130 and 130-200 s windows for
silence. The `audio-check` CMake target runs a 12,000-frame capture and the
check:

```
cmake --build build-linux --target audio-check
```

It fails the pre-fix WAV (silent windows at 61-88 s) and passes the fixed
one:

```
 56- 90 s: min RMS  1780.2  mean RMS  2449.0
 90-130 s: min RMS   746.5  mean RMS  3608.9
130-200 s: min RMS  1696.1  mean RMS  3513.7
PASS: continuous audio through character select and the match (peak 26937)
```

## 8. Windows window

```
"kof 96.exe" --rom-path roms --frames 240 --scale 2      -> exit 0
"kof 96.exe" --rom-path roms --frames 120 --fullscreen    -> exit 0
```

Both opened the SDL2 window, rendered frames and exited cleanly. The
`--fullscreen` path letterboxes the 4:3 Neo Geo image inside the desktop
resolution.

## 9. Linux x86_64

Built with gcc 11.4 / CMake 4.4.4 on Ubuntu 22.04 under WSL2, generated
files at `-O1`.

```
NG_RTC="1996-01-01 00:00:00" ./build-linux/"kof 96" --headless --rom-path roms \
    --frames 20000 --input tests/play.txt
[exec] native blocks 12232598, native instructions 377468486,
       interpreted instructions 0 (100.00% native), 0 uncovered entry points

NG_RTC="1996-01-01 00:00:00" ./build-linux/"kof 96" --headless --verify \
    --rom-path roms --frames 7000 --input tests/coin_start.txt
[verify] 4102741 blocks checked, 0 mismatches
[exec] ... 100.00% native, 0 uncovered entry points
```

The Linux fixed-RTC frame-19,999 screenshot is byte-identical to the
Windows one, and the block/instruction counts match exactly. `ldd` shows
SDL2 plus normal system libraries; the AppImage bundles SDL2.

## 10. AppImage

```bash
JOBS=4 ./packaging/appimage/build-appimage.sh "$PWD/roms"
```

Verified after building:

* file is executable and has the AppImage magic/type-2 header;
* `--appimage-extract-and-run --headless --frames 700` boots, renders and
  exits 0;
* the AppImage's own 20,000-frame fixed-RTC session reported
  `12232598` native blocks / `377468486` native instructions / 0
  interpreted, and its frame-19,999 PNG is identical to the Windows build's;
* the windowed/fullscreen AppImage was launched at 1280x800 on an Xvfb
  virtual X display (SDL2 X11 path) and exited 0;
* an X11 capture of that fullscreen output shows the 4:3 image pillarboxed
  (1066x800) with black side bars, not stretched to 16:10;
* `ldd` of the extracted binary resolves SDL2 from the AppImage's
  `usr/lib` (when run with the AppRun environment);
* no ROM/BIOS data is inside the AppImage (`usr/bin/kof96`,
  `usr/lib/libSDL2-2.0.so.0`, desktop/icon/licenses only).

Physical Steam Deck LCD/OLED, Steam Input and Gaming Mode were not
available. See `dist/steamdeck/README.txt`.

## 11. Not tested

* Physical Steam Deck hardware, Gaming Mode, Steam Input, Deck speakers.
* Physical Xbox/Steam controller (SDL mapping inherited from the toolkit).
* Subjective audio mix, volume balance, every music track.
* Two-player sessions, later stages, boss/ending paths, test menu, memory
  card, AES/PAL variants.
