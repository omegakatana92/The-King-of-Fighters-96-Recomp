The King of Fighters '96 - Windows x64 static recompilation
==========================================================

This is a native Windows x64 program. The game's Motorola 68000 program was
translated ahead of time into C and runs on the neogeorecomp MVS board model;
the real MVS BIOS boots the cartridge. It is not an emulator frontend.

ROMs are NOT included
---------------------
You must supply your own legally obtained dump:

  From kof96.zip:
    214-p1.p1  214-p2.sp2  214-s1.s1  214-m1.m1
    214-c1.c1 .. 214-c8.c8
    214-v1.v1  214-v2.v2  214-v3.v3
  From neogeo.zip:
    sp-s2.sp1  sfix.sfix  sm1.sm1  000-lo.lo

Unzip those files (flat, no subfolders) into the "roms" folder next to
"kof 96.exe".

Run
---
  Play KOF96.cmd
or
  "kof 96.exe" --rom-path roms
or
  "kof 96.exe" --rom-path roms --fullscreen

F11 toggles fullscreen, Esc quits. The image keeps the Neo Geo's 4:3
aspect; fullscreen pillarboxes on a 16:9/16:10 display.

Controls
--------
  Arrows / left stick        move
  Z X C V / A B X Y          Neo Geo A B C D
  5 / Back                   insert coin
  1 / Start                  player 1 start
  2 / Start (P2)             player 2 start
  3 / left shoulder          select
  9                          service credit
  F2                         test switch
  F11                        fullscreen
  Esc                        quit

Insert a coin before Start does anything (MVS behaviour).

Notes
-----
* v0.1.1 fixes the M1 bank-mask bug that silenced music at character
  selection; music is continuous through select and the match.
* Built from the plain MAME "kof96" set (CRC/SHA1 verified). No decryption
  or protection patching is needed.
* Verified with the MVS sp-s2.sp1 BIOS. Other BIOS files may work but were
  not the test target.
* Windows 10/11 x64. SDL2.dll and the Microsoft Visual C++ runtime DLLs
  are included.
* This package contains code generated from SNK's ROM data. Use it only
  with ROMs you are legally allowed to use. No ROM or BIOS data is included,
  and no rights to SNK's game are granted. The project source (without ROMs
  or generated code) is separately licensed.
* The King of Fighters and Neo Geo are trademarks of SNK Corporation. This
  project is not affiliated with or endorsed by SNK.
