# License status

The **original project code** in this repository (the game host in `src/`,
the build files, the test scripts, the packaging scripts and the
documentation) is licensed under the **PolyForm Noncommercial License 1.0.0**.
The full text is in `LICENSE`.

Status: **confirmed by the project owner on 2026-10-26** for this title. No
other PolyForm variant applies.

Required Notice: Copyright (c) 2026 omegakatana92.

What this license does **not** cover
------------------------------------
* `neogeorecomp/` is the upstream toolkit by sp00nznet, MIT licensed. Its
  `LICENSE`, `NOTICE` and `LICENSES/` directory are preserved. Do not
  relicense those files under PolyForm. The vendored copy carries generic
  runtime fixes (see `docs/runtime-changes.md`); those changes are offered
  under the toolkit's MIT terms.
* Musashi (MIT), superzazu/z80 (MIT) and ymfm (BSD-3-Clause) are vendored
  under `neogeorecomp/ext/`; their notices are preserved.
* SDL2 is zlib licensed. The Windows package includes `SDL2.dll` and the
  AppImage bundles `libSDL2-2.0.so.0` under that license. The AppImage
  runtime and appimagetool are build/packaging tools under their own
  licenses.
* The game ROMs, the Neo Geo BIOS, and everything generated from them
  (recompiled C, entry-point lists) are **not** part of the project's
  licensed source. Users supply their own legally obtained dumps. Release
  binaries built from a dump contain translated game code; they are provided
  for use with ROMs the user is legally entitled to use and grant no rights
  to SNK's game code. No ROM or BIOS data is included in the release assets.
* Game screenshots and captures contain SNK's copyrighted imagery and are
  not distributed. The local test run wrote them under `shots/`, which is
  ignored by `.gitignore`.

PolyForm Noncommercial is not a free/open-source license and does not permit
commercial redistribution. Do not assume otherwise. If you need commercial
terms, contact the project owner.

See `THIRD_PARTY_NOTICES.md` for the complete attribution list and
`NOTICE.md` for a short summary.
