/*
 * game.c - the King of Fighters '96 (kof96) ROM set, shared by the player
 * and the generator so both load the program identically.
 *
 * The supplied archive is the plain MVS set from MAME's neogeo.cpp
 * (ROM_START(kof96), NGM-214). Every file's CRC32 and SHA1 matches the MAME
 * entry, so there is no decryption, no protection device and no S-ROM
 * extraction step:
 *
 *   214-p1.p1   1 MB  TC538200  fixed bank (NEO-GEO header at $100)
 *   214-p2.sp2  2 MB  TC5316200 banked program, two 1 MB PROGBK1 banks
 *   214-c1..c8  8 x 4 MB CHA256 graphics, odd/even bitplane pairs
 *   214-s1.s1   128 KB fixed-layer tiles
 *   214-m1.m1   128 KB Z80 sound driver
 *   214-v1..v3  10 MB ADPCM-A samples
 *
 * P ROMs are stored byte-swapped (MAME's ROM_LOAD16_WORD_SWAP), hence
 * swap = 1. The two P files map in file order: p1 at $000000 (fixed) and
 * p2 at $100000 (the 2 MB banked area), which is the standard PROGBK1
 * arrangement the runtime already models at $2FFFF0.
 */
#include "game.h"

const ng_game_t k_kof96 = {
    .name = "kof96",
    .title = "The King of Fighters '96",
    .prom_size = 0x300000,
    .prom = {
        {"214-p1.p1",  0x000000, 0x000000, 0x100000, 1},
        {"214-p2.sp2", 0x000000, 0x100000, 0x200000, 1},
    },
    .crom_size = 0x2000000,
    .crom_pairs = {
        {"214-c1.c1", "214-c2.c2"},
        {"214-c3.c3", "214-c4.c4"},
        {"214-c5.c5", "214-c6.c6"},
        {"214-c7.c7", "214-c8.c8"},
    },
    .srom = "214-s1.s1",
    .m1 = "214-m1.m1",
    .vrom = {"214-v1.v1", "214-v2.v2", "214-v3.v3"},
};
