"""Build the MEAD endpoint-interpolation diagnostic strips used in the paper.

Each output strip contains the three measured controls for one method at a
fixed temporal frame. Source pixels are cropped directly from the immutable
all-method GIF exports; no sharpening, alignment, or color correction is
applied.

Usage:
    python scripts/build_mead_endpoint_qualitatives.py --gif-root PATH
"""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

from PIL import Image, ImageSequence


@dataclass(frozen=True)
class Case:
    seed: int
    family: int
    family_name: str
    temporal_frame: int


CASES = (
    Case(100, 8, "M003-happy-002", 2),
    Case(100, 13, "M003-happy-015", 13),
    Case(200, 4, "M003-angry-008", 2),
    Case(200, 20, "M005-angry-015", 7),
)
METHODS = (0, 2, 3, 4)  # Target, Pointwise, endpoint interpolation, LFVD.
LABEL_WIDTH = 300
HEADER_HEIGHT = 62
CELL_SIZE = 192
GUTTER = 6


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--gif-root",
        required=True,
        type=Path,
        help="Root containing mead/M0/seed_*/family_*_all_methods.gif",
    )
    return parser.parse_args()


def read_frame(path: Path, frame_number: int) -> Image.Image:
    with Image.open(path) as image:
        frames = [frame.copy().convert("RGB") for frame in ImageSequence.Iterator(image)]
    if not 1 <= frame_number <= len(frames):
        raise ValueError(f"{path}: frame {frame_number} outside 1..{len(frames)}")
    return frames[frame_number - 1]


def control_strip(frame: Image.Image, method: int) -> Image.Image:
    width = 3 * CELL_SIZE + 2 * GUTTER
    strip = Image.new("RGB", (width, CELL_SIZE), "white")
    y0 = HEADER_HEIGHT + method * CELL_SIZE
    for control in range(3):
        x0 = LABEL_WIDTH + control * CELL_SIZE
        crop = frame.crop((x0, y0, x0 + CELL_SIZE, y0 + CELL_SIZE))
        strip.paste(crop, (control * (CELL_SIZE + GUTTER), 0))
    return strip


def main() -> None:
    args = parse_args()
    out = Path("figures/qualitative")
    source_data = Path("figures/source_data/qualitative_mead_diagnostics")
    out.mkdir(parents=True, exist_ok=True)
    source_data.mkdir(parents=True, exist_ok=True)

    manifest = {
        "description": "Three measured controls cropped from immutable MEAD all-method GIFs.",
        "processing": "crop and concatenate only; no sharpening, alignment, or color correction",
        "methods": {"0": "target", "2": "pointwise_shared_noise", "3": "endpoint_interpolation", "4": "lfvd"},
        "cases": [],
    }
    for case in CASES:
        source = (
            args.gif_root
            / "mead"
            / "M0"
            / f"seed_{case.seed}"
            / f"family_{case.family:03d}_all_methods.gif"
        )
        frame = read_frame(source, case.temporal_frame)
        outputs = []
        for method in METHODS:
            name = (
                f"mead_M0_f{case.family:03d}_s{case.seed}_t{case.temporal_frame:02d}"
                f"_m{method}_controls.png"
            )
            destination = out / name
            control_strip(frame, method).save(destination, dpi=(300, 300), optimize=True)
            outputs.append(destination.as_posix())
            print(destination)
        manifest["cases"].append(
            {
                **asdict(case),
                "source": source.relative_to(args.gif_root).as_posix(),
                "outputs": outputs,
            }
        )

    manifest_path = source_data / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(manifest_path)


if __name__ == "__main__":
    main()
