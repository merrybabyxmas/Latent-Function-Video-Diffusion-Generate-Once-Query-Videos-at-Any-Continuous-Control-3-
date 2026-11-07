"""Replace Lighting Pointwise paper rows with the final control-token outputs.

The input ``videos.npz`` files are the immutable 50-step, seed-100 outputs
from the L3 held-out test fold. The script selects control index 4 and temporal
frames 4, 8, 12, and 16, writes the raw crops, and concatenates them with the
same geometry used by the checked-in MotionStone-style qualitative layout.
No sharpening, color correction, alignment, or model-side processing is used.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from PIL import Image


FRAMES = (4, 8, 12, 16)
CONTROL = 4
GUTTER = 6
SIZE = 256


def write_row(npz_path: Path, family: int, repo: Path) -> None:
    with np.load(npz_path) as data:
        prediction = data["prediction"]
    if prediction.shape[:3] != (9, 3, 17):
        raise ValueError(f"Unexpected prediction shape: {prediction.shape}")

    raw_dir = (
        repo
        / "figures"
        / "source_data"
        / "qualitative_controltoken_20261106"
        / f"lighting_L3_f{family:03d}_s100"
    )
    raw_dir.mkdir(parents=True, exist_ok=True)

    canvas = Image.new(
        "RGB", (len(FRAMES) * SIZE + (len(FRAMES) - 1) * GUTTER, SIZE), "white"
    )
    for column, frame in enumerate(FRAMES):
        pixels = prediction[CONTROL, :, frame].transpose(1, 2, 0)
        tile = Image.fromarray(pixels, mode="RGB")
        tile.save(raw_dir / f"m2_s{CONTROL:02d}_t{frame:02d}.png", optimize=True)
        canvas.paste(tile, (column * (SIZE + GUTTER), 0))

    output = (
        repo
        / "figures"
        / "qualitative"
        / f"lighting_L3_f{family:03d}_s100_m2_s{CONTROL:02d}_motionstone.png"
    )
    canvas.save(output, dpi=(300, 300), optimize=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--family-010", type=Path, required=True)
    parser.add_argument("--family-013", type=Path, required=True)
    args = parser.parse_args()
    write_row(args.family_010, 10, args.repo)
    write_row(args.family_013, 13, args.repo)


if __name__ == "__main__":
    main()
