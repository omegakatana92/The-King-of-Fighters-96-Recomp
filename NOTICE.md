# Notices

## Project code

`LICENSE` (PolyForm Noncommercial License 1.0.0, confirmed 2026-10-26)
covers the code written for this port: `src/`, `tests/`, `scripts/`,
`packaging/`, `docs/` and the build files. See `LICENSE-STATUS.md` for scope.

## neogeorecomp

`neogeorecomp/` is a vendored copy of the neogeorecomp toolkit
(<https://github.com/sp00nznet/neogeorecomp>) at v0.2.0, commit
`af96b2b4b39b42b392b17bcaa6a74a5f27088202`. It is MIT licensed; the full text
is in `neogeorecomp/LICENSE`, and the upstream notices are in
`neogeorecomp/NOTICE` and `neogeorecomp/LICENSES/`. The generic hardware
fixes in the vendored copy are described in `docs/runtime-changes.md` and
are offered under the toolkit's MIT terms.

## SDL2

SDL2 is not vendored in the source tree. Builds with a window link against
SDL2 (<https://www.libsdl.org/>), zlib licensed. The Windows package ships
`SDL2.dll`; the AppImage bundles `libSDL2-2.0.so.0`.

## ROM data

No ROM images, BIOS images, generated recompiled C or entry-point lists are
part of the project source. The generator writes the C from the user's own
ROM files into the build directory, and `.gitignore` keeps the build, ROMs,
entry lists and captures out of version control. Executables in `dist/` are
built from the owner's dump and contain translated game code: do not
redistribute them.

The King of Fighters and Neo Geo are trademarks of SNK Corporation. This
project is not affiliated with or endorsed by SNK.
