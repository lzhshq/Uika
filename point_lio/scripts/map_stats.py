#!/usr/bin/env python3
import argparse
from pathlib import Path

import numpy as np


def read_pgm(path):
    with path.open("rb") as f:
        magic = f.readline().strip()
        if magic != b"P5":
            raise ValueError(f"{path} is not a binary PGM file")

        line = f.readline()
        while line.startswith(b"#"):
            line = f.readline()
        width, height = map(int, line.split())
        max_value = int(f.readline())
        if max_value != 255:
            raise ValueError(f"Unsupported PGM max value: {max_value}")

        data = np.frombuffer(f.read(), dtype=np.uint8)
        if data.size != width * height:
            raise ValueError(f"Expected {width * height} pixels, got {data.size}")
        return data.reshape(height, width)


def main():
    parser = argparse.ArgumentParser(description="Print simple occupancy statistics for a Nav2 PGM map.")
    parser.add_argument("pgm", type=Path)
    args = parser.parse_args()

    data = read_pgm(args.pgm)
    free = int((data > 250).sum())
    occupied = int((data < 10).sum())
    other = int(data.size - free - occupied)

    print(f"size: {data.shape[1]} x {data.shape[0]}")
    print(f"pixels: {data.size}")
    print(f"free: {free} ({free / data.size:.3f})")
    print(f"occupied: {occupied} ({occupied / data.size:.3f})")
    print(f"other: {other} ({other / data.size:.3f})")


if __name__ == "__main__":
    main()
