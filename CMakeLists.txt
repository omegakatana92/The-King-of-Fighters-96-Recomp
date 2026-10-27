cmake_minimum_required(VERSION 3.21)
project(kof96 VERSION 0.1.1 LANGUAGES C CXX)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)

# The neogeorecomp toolkit: the vendored copy, or a checkout next to this
# repo. The vendored copy is v0.2.0 plus the generic runtime fixes recorded
# in docs/runtime-changes.md (no title-specific addresses).
if(EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/neogeorecomp/CMakeLists.txt)
    set(ng_default ${CMAKE_CURRENT_SOURCE_DIR}/neogeorecomp)
else()
    set(ng_default ${CMAKE_CURRENT_SOURCE_DIR}/../neogeorecomp)
endif()
set(NEOGEORECOMP_DIR ${ng_default} CACHE PATH "neogeorecomp checkout")
add_subdirectory(${NEOGEORECOMP_DIR} neogeorecomp_build)

# Your ROM files (the "kof96" set plus the "neogeo" system ROMs, unzipped).
# Without it the player builds interpreter-only, which is also the quickest
# way to check a dump and the BIOS before recompiling.
set(KOF96_ROM_DIR "" CACHE PATH "Directory with your kof96 and Neo Geo BIOS ROM files")
# Optional: entry points a previous run found at runtime (--dump-misses).
set(KOF96_ENTRIES "${CMAKE_BINARY_DIR}/entries.txt" CACHE FILEPATH "Extra entry points for the recompiler")

# Stage 1: the generator.
add_executable(kof96_recomp src/recomp_main.c src/game.c)
target_link_libraries(kof96_recomp PRIVATE m68krecomp_core)
target_include_directories(kof96_recomp PRIVATE src)

# Stage 2: the player, with the generated C when ROMs are available.
set(GAME_SOURCES src/main.c)
set(GEN_DIR ${CMAKE_BINARY_DIR}/generated)
set(GEN_FILES 16)
if(KOF96_ROM_DIR)
    set(GEN_SOURCES ${GEN_DIR}/recomp_table.c)
    math(EXPR last "${GEN_FILES} - 1")
    foreach(i RANGE ${last})
        if(i LESS 10)
            list(APPEND GEN_SOURCES ${GEN_DIR}/recomp_0${i}.c)
        else()
            list(APPEND GEN_SOURCES ${GEN_DIR}/recomp_${i}.c)
        endif()
    endforeach()
    # The entry list starts empty. The `profile` target fills it from
    # scripted sessions; the next build regenerates with it.
    if(NOT EXISTS ${KOF96_ENTRIES})
        file(WRITE ${KOF96_ENTRIES} "")
    endif()
    file(MAKE_DIRECTORY ${GEN_DIR})
    add_custom_command(
        OUTPUT ${GEN_SOURCES} ${GEN_DIR}/recomp_common.h
        COMMAND kof96_recomp --rom-path ${KOF96_ROM_DIR} --out ${GEN_DIR} --files ${GEN_FILES}
                --entries ${KOF96_ENTRIES}
        DEPENDS kof96_recomp ${KOF96_ENTRIES}
        COMMENT "Recompiling kof96 from ${KOF96_ROM_DIR}")
    list(APPEND GAME_SOURCES ${GEN_SOURCES})
endif()

add_executable(kof96 ${GAME_SOURCES} src/game.c)
target_link_libraries(kof96 PRIVATE neogeorecomp)
target_include_directories(kof96 PRIVATE src ${GEN_DIR})
set_target_properties(kof96 PROPERTIES OUTPUT_NAME "kof 96")
if(KOF96_ROM_DIR)
    # Play scripted sessions and record the entry points that only show up at
    # runtime (computed jumps into unrolled code), then rebuild.
    add_custom_target(profile
        COMMAND $<TARGET_FILE:kof96> --headless --rom-path ${KOF96_ROM_DIR} --frames 6000
                --dump-misses ${KOF96_ENTRIES}
        COMMAND $<TARGET_FILE:kof96> --headless --rom-path ${KOF96_ROM_DIR} --frames 20000
                --input ${CMAKE_CURRENT_SOURCE_DIR}/tests/play.txt --dump-misses ${KOF96_ENTRIES}
        DEPENDS kof96
        COMMENT "Profiling scripted KOF '96 sessions for runtime-only entry points")
    target_compile_definitions(kof96 PRIVATE KOF96_HAVE_RECOMP)
    if(MSVC)
        # Generated routines are large; /bigobj lifts the section limit and
        # /O1 keeps the optimizer from taking tens of minutes per file.
        set_source_files_properties(${GEN_SOURCES} PROPERTIES COMPILE_OPTIONS "/bigobj;/O1")
    else()
        # Same trade-off with gcc: the generated C is over 100 MB of very
        # large functions. -O1 keeps compile time and memory within reach of
        # an 8 GB build machine; the runtime builds at -O3.
        set_source_files_properties(${GEN_SOURCES} PROPERTIES COMPILE_OPTIONS "-O1")
    endif()
endif()
if(MSVC)
    target_compile_definitions(kof96 PRIVATE _CRT_SECURE_NO_WARNINGS)
    target_compile_definitions(kof96_recomp PRIVATE _CRT_SECURE_NO_WARNINGS)
endif()

# Optional regression test: capture a scripted session and check that the
# sound driver keeps producing music through character selection and the
# match. Requires Python 3 and the user's ROMs.
find_package(Python3 COMPONENTS Interpreter QUIET)
if(KOF96_ROM_DIR AND Python3_Interpreter_FOUND)
    add_custom_target(audio-check
        COMMAND ${CMAKE_COMMAND} -E env "NG_RTC=1996-01-01"
                $<TARGET_FILE:kof96> --headless --rom-path ${KOF96_ROM_DIR}
                --frames 12000 --input ${CMAKE_CURRENT_SOURCE_DIR}/tests/play.txt
                --wav ${CMAKE_BINARY_DIR}/audio-check.wav
        COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tests/check_audio.py
                ${CMAKE_BINARY_DIR}/audio-check.wav
        DEPENDS kof96
        COMMENT "Checking KOF '96 audio through character select and the match")
endif()

# Ship the SDL2 DLL (when the window is built) next to the executable.
if(WIN32 AND TARGET SDL2::SDL2)
    add_custom_command(TARGET kof96 POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_if_different $<TARGET_RUNTIME_DLLS:kof96> $<TARGET_FILE_DIR:kof96>
        COMMAND_EXPAND_LISTS)
endif()
