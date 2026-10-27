# Building

## Prerequisites

| Tool | Windows | Linux |
|---|---|---|
| Compiler | Visual Studio 2022/2026, Desktop C++ | gcc/g++ 11+ |
| Build system | CMake 3.21+ | CMake 3.21+, make |
| SDL2 | SDL2 2.x MSVC development package (2.32.10 used) | `libsdl2-dev` |
| Other | Git only if you use a submodule checkout | `strip`, `wget` for the AppImage |

The toolkit source is vendored under `neogeorecomp/` (MIT), including
Musashi, superzazu/z80 and ymfm. No network access is needed to build;
`wget` is only used by the AppImage script to fetch appimagetool.

## ROM files

The build reads the unencrypted MAME `kof96` set plus the `neogeo` system
files from `KOF96_ROM_DIR` (one flat directory, no subfolders):

```
kof96 set:  214-p1.p1 214-p2.sp2 214-s1.s1 214-m1.m1
            214-c1.c1 .. 214-c8.c8
            214-v1.v1 214-v2.v2 214-v3.v3
neogeo set: sp-s2.sp1 sfix.sfix sm1.sm1 000-lo.lo
```

The project never downloads ROMs and never modifies the originals. The
generator reads them and writes C into the build directory; neither the ROMs
nor the generated C are part of the source tree.

## Windows x64 (MSVC)

From the project root (PowerShell):

```powershell
$sdl = "C:\path\to\SDL2-2.32.10\cmake"
cmake -S . -B build-windows -G "Visual Studio 18 2026" -A x64 `
      -DKOF96_ROM_DIR="C:\path\to\roms" `
      -DSDL2_DIR="$sdl"
cmake --build build-windows --config Release --target kof96 --parallel
```

Result: `build-windows\Release\kof 96.exe`, with `SDL2.dll` copied beside it.

The same steps are in `scripts/build-windows.ps1`:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\build-windows.ps1 `
    -RomDir C:\path\to\roms -SdlDir C:\path\to\SDL2-2.32.10\cmake
```

Notes:

* The generated C is about 160 MB of very large functions. The project
  compiles those files with `/bigobj;/O1`; `/O2` makes MSVC's optimizer take
  tens of minutes per file. The runtime and 68000 helpers still build
  optimized.
* `SDL2_DIR` must point at an **MSVC** SDL2. A MinGW SDL2 earlier on `PATH`
  can make MSVC include MinGW headers and fail with `stdio.h` errors.
* A headless-only build works without SDL2: omit `SDL2_DIR` and add
  `-DCMAKE_DISABLE_FIND_PACKAGE_SDL2=ON`. `--screenshot` and `--wav` still
  work.

### Interpreter-only check

```powershell
cmake -S . -B build-interp -DCMAKE_DISABLE_FIND_PACKAGE_SDL2=ON
cmake --build build-interp --config Release --target kof96
build-interp\Release\"kof 96.exe" --headless --interp --rom-path roms `
    --frames 1200 --screenshot 600:bios.png --screenshot 1199:title.png
```

This tests the board model without the recompiler. Expect the NEO-GEO
eyecatcher at frame 600 and `INSERT COIN`/attract by frame 1,200.

## Linux x86_64

```bash
sudo apt install build-essential cmake libsdl2-dev
JOBS=4 ./scripts/build-linux.sh "$PWD/roms"
```

or manually:

```bash
cmake -S . -B build-linux -DCMAKE_BUILD_TYPE=Release -DKOF96_ROM_DIR="$PWD/roms"
cmake --build build-linux --parallel 4 --target kof96
```

The generated files are compiled with `-O1` after the Release `-O3`, to keep
memory within reach of an 8 GB machine (an `-O2` build of the largest files
was killed by the OOM killer). The runtime, CPU helpers and audio path are
still `-O3`. Use `JOBS` to limit parallelism; the largest translation units
need roughly 1.5-2 GB each.

Run:

```bash
./build-linux/"kof 96" --rom-path roms
```

## Steam Deck AppImage

```bash
JOBS=4 ./packaging/appimage/build-appimage.sh "$PWD/roms"
```

This configures/builds `build-linux`, assembles an AppDir, copies the
player, `libSDL2-2.0.so.0`, the desktop entry, the icon and the licenses,
then runs `appimagetool` (downloaded on first use, run with
`--appimage-extract-and-run` so FUSE is not required).

Output:

```
dist/steamdeck/kof 96-SteamDeck-x86_64.AppImage
```

The AppRun script:

* adds `usr/lib` to `LD_LIBRARY_PATH`;
* finds ROMs in `~/.local/share/kof96/roms-clean`,
  `~/.local/share/kof96/roms`, a `roms` folder beside the AppImage,
  `~/Emulation/roms/kof96`, `~/roms/kof96` or `~/roms`;
* if the selected folder has no BIOS, uses
  `~/.local/share/kof96/roms` as `--bios-path`;
* adds `--fullscreen` unless `--headless`, `--scale` or `--fullscreen` is
  already present.

Test without a physical Deck:

```bash
./dist/steamdeck/"kof 96-SteamDeck-x86_64.AppImage" \
    --appimage-extract-and-run --headless --frames 700 --rom-path build-linux/roms
```

## WSL2

The Linux build and AppImage in this project were produced in Ubuntu 22.04
under WSL2, building the project directory on `/mnt/c`:

```powershell
wsl -d Ubuntu-22.04
cd "/mnt/c/.../releases/kof 96"
JOBS=4 bash scripts/build-linux.sh "$PWD/roms"
JOBS=4 bash packaging/appimage/build-appimage.sh "$PWD/roms"
```

WSLg can run the windowed/fullscreen binary if a display is available.
