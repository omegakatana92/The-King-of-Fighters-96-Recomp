The King of Fighters '96 - Steam Deck / Linux x86_64 AppImage
=============================================================

This is a native Linux x86_64 build. The game's Motorola 68000 program was
statically recompiled to C and runs on the neogeorecomp MVS board model with
the real MVS BIOS. It is not an emulator wrapper.

Quick start
-----------
1. Copy this AppImage and your "roms" folder anywhere on the Deck.
   The players look for ROMs in these places, in order:
     - ~/.local/share/kof96/roms-clean (the standard location)
     - ~/.local/share/kof96/roms
     - a "roms" folder next to the AppImage
     - ~/Emulation/roms/kof96
     - ~/roms/kof96
     - ~/roms
2. chmod +x "KOF96-AudioFixed-x86_64.AppImage"
3. Desktop Mode: double-click it.
   Gaming Mode: add it as a non-Steam game and launch it.

The AppRun script adds --fullscreen automatically. Pass --scale 2 or
--headless to override; F11 toggles fullscreen and Esc quits. If the chosen
ROM folder has no BIOS files, AppRun uses ~/.local/share/kof96/roms as
--bios-path automatically.

ROMs are NOT included
---------------------
Supply your own legally obtained dump, unzipped flat into "roms":

  From kof96.zip:
    214-p1.p1  214-p2.sp2  214-s1.s1  214-m1.m1
    214-c1.c1 .. 214-c8.c8
    214-v1.v1  214-v2.v2  214-v3.v3
  From neogeo.zip:
    sp-s2.sp1  sfix.sfix  sm1.sm1  000-lo.lo

Controls
--------
  D-pad / left stick         move
  A B X Y (Xbox layout)      Neo Geo A B C D
  Back                       insert coin
  Start                      player 1 start
  Left shoulder              select
  Keyboard: arrows, Z X C V = A B C D, 5 = coin, 1 = start, 3 = select,
  9 = service, F2 = test, F11 = fullscreen, Esc = quit.

Steam Input: the toolkit uses SDL2's GameController mapping. A pad SDL does
not recognise can be described with SDL_GAMECONTROLLERCONFIG. A standard
Xbox-layout pad works without extra configuration.

Display
-------
The game runs at its native 320x224 and is presented at 4:3 in fullscreen
(1280x800 -> 1066x800 pillarboxed), so it is not stretched to 16:10. The
internal refresh rate is the MVS 59.1856 Hz and frames are paced to it.

Verification
------------
Built and run under Ubuntu 22.04 (glibc 2.35) under WSL2: headless boot,
attract mode, coin/start, member select, a full match, --verify with 0
mismatches, 100% native instructions over a 20,000-frame scripted session,
and the AppImage launched windowed and fullscreen at 1280x800 on an Xvfb
virtual display (SDL2 X11 path), exiting 0.

This is the audio-fixed build (v0.1.1). The previous build went silent from
character selection; the M1 bank mask truncated music banks above 64 KB. The
fix is in the bundled binary and the source tree. A 20,000-frame capture has
continuous music from 56 s through 200 s, and native and interpreter modes
match.

Physical Steam Deck LCD/OLED hardware, Steam Input and Gaming Mode were not
available in this environment, so those are not claimed as tested. SteamOS 3
is glibc 2.35-compatible with the build host.

Licensing
---------
The project's own source is PolyForm Noncommercial 1.0.0. The bundled
neogeorecomp toolkit and Musashi/z80/ymfm keep their MIT/BSD licenses; see
the LICENSES folder in this AppImage. The AppImage contains code generated
from SNK's ROM data: use it only with ROMs you are legally allowed to use.
No ROM or BIOS data is included, and no rights to SNK's game are granted.
The King of Fighters and Neo Geo are trademarks of SNK Corporation. This
project is not affiliated with or endorsed by SNK.
