#!/usr/bin/env python3
"""Regression check for the KOF '96 audio fix.

Run the player with tests/play.txt (coin at frame 1300, start at 1500,
character select around frame 4100, match around frame 5600), write a WAV,
then check that the music is continuous from character selection through
the match instead of going silent with only isolated samples.

Usage: tests/check_audio.py <capture.wav>

The 56-200 s windows cover character select, order select and the match.
A broken M1 bank mask leaves these windows nearly silent (<50 RMS); the
fixed build has every 1 s window above 100 RMS.
"""
import sys
import wave

import numpy as np

MIN_RMS = 100.0
MIN_PEAK = 1000


def fail(msg):
    print(f"FAIL: {msg}")
    return 1


def main(path):
    w = wave.open(path, "rb")
    rate, channels = w.getframerate(), w.getnchannels()
    if rate < 8000 or channels not in (1, 2):
        return fail(f"unexpected WAV format: {rate} Hz, {channels} ch")
    n = w.getnframes()
    data = np.frombuffer(w.readframes(n), dtype="<i2").astype(np.float32)
    if channels == 2:
        data = data.reshape(-1, 2).mean(axis=1)
    peak = float(np.max(np.abs(data))) if len(data) else 0.0
    if peak < MIN_PEAK:
        return fail(f"capture is silent (peak {peak:.0f})")

    win = rate
    secs = []
    for start in range(0, len(data) - win + 1, win):
        block = data[start:start + win]
        secs.append((start // win, float(np.sqrt(np.mean(block * block)))))

    windows = [(56, 90), (90, 130), (130, 200)]
    for a, b in windows:
        seg = [r for t, r in secs if a <= t < b]
        if not seg:
            return fail(f"capture is shorter than {b} s")
        quiet = [t for t, r in secs if a <= t < b and r < 50.0]
        minimum = min(seg)
        if quiet:
            return fail(f"{a}-{b} s has silent windows at {quiet}")
        if minimum < MIN_RMS:
            return fail(f"{a}-{b} s minimum RMS {minimum:.0f} is below {MIN_RMS}")
        print(f"{a:3d}-{b:3d} s: min RMS {minimum:7.1f}  mean RMS {sum(seg)/len(seg):7.1f}")

    print(f"PASS: continuous audio through character select and the match (peak {peak:.0f})")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: tests/check_audio.py <capture.wav>")
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
