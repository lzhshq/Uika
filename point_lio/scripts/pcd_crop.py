#!/usr/bin/env python3
import argparse
from pathlib import Path

import numpy as np


def read_pcd(path):
    header = {}
    with path.open("rb") as stream:
        while True:
            line = stream.readline()
            if not line:
                raise ValueError("PCD header ended before DATA")
            text = line.decode("ascii", errors="strict").strip()
            if text and not text.startswith("#"):
                parts = text.split()
                header[parts[0].upper()] = parts[1:]
            if text.upper().startswith("DATA "):
                data_offset = stream.tell()
                break

        fields = header["FIELDS"]
        sizes = [int(value) for value in header["SIZE"]]
        types = header["TYPE"]
        counts = [int(value) for value in header.get("COUNT", ["1"] * len(fields))]
        points = int(header["POINTS"][0])
        if header["DATA"][0].lower() != "binary":
            raise ValueError("Only binary PCD is supported")
        if any(size != 4 or kind != "F" or count != 1
               for size, kind, count in zip(sizes, types, counts)):
            raise ValueError("Only scalar float32 PCD fields are supported")
        stream.seek(data_offset)
        data = np.fromfile(stream, dtype=np.float32, count=points * len(fields))

    if data.size != points * len(fields):
        raise ValueError("Truncated PCD payload")
    return data.reshape(points, len(fields)), fields, sizes, types, counts


def write_pcd(path, data, fields, sizes, types, counts):
    header = (
        "# .PCD v0.7 - Point Cloud Data file format\n"
        "VERSION 0.7\n"
        f"FIELDS {' '.join(fields)}\n"
        f"SIZE {' '.join(str(value) for value in sizes)}\n"
        f"TYPE {' '.join(types)}\n"
        f"COUNT {' '.join(str(value) for value in counts)}\n"
        f"WIDTH {len(data)}\n"
        "HEIGHT 1\n"
        "VIEWPOINT 0 0 0 1 0 0 0\n"
        f"POINTS {len(data)}\n"
        "DATA binary\n"
    )
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("wb") as stream:
        stream.write(header.encode("ascii"))
        np.asarray(data, dtype=np.float32).tofile(stream)
    temporary.replace(path)


def main():
    parser = argparse.ArgumentParser(description="Crop a Point-LIO PCD in map XY.")
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--center-x", type=float, default=0.0)
    parser.add_argument("--center-y", type=float, default=0.0)
    parser.add_argument("--width", type=float, default=15.0)
    parser.add_argument("--height", type=float, default=15.0)
    args = parser.parse_args()

    data, fields, sizes, types, counts = read_pcd(args.input)
    x_index, y_index = fields.index("x"), fields.index("y")
    half_width, half_height = args.width / 2.0, args.height / 2.0
    finite = np.isfinite(data[:, [x_index, y_index]]).all(axis=1)
    inside = (
        finite &
        (data[:, x_index] >= args.center_x - half_width) &
        (data[:, x_index] <= args.center_x + half_width) &
        (data[:, y_index] >= args.center_y - half_height) &
        (data[:, y_index] <= args.center_y + half_height)
    )
    cropped = data[inside]
    if len(cropped) < 100:
        raise ValueError("Crop contains too few points")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    write_pcd(args.output, cropped, fields, sizes, types, counts)
    print(f"input points: {len(data)}")
    print(f"cropped points: {len(cropped)}")
    print(f"crop bounds: x=[{args.center_x - half_width}, {args.center_x + half_width}], "
          f"y=[{args.center_y - half_height}, {args.center_y + half_height}]")
    print(f"wrote: {args.output}")


if __name__ == "__main__":
    main()
