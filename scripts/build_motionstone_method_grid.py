"""Build the four-example MotionStone-style method grid used in the paper.

The script crops immutable held-out all-method GIFs into four temporal frames
per method. Cells use the same landscape aspect ratio as MotionStone Fig. 4.
Only deterministic center cropping, Lanczos resizing, and concatenation are
applied; no sharpening, alignment, or color correction is performed.

Usage:
    python scripts/build_motionstone_method_grid.py --gif-root PATH
"""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

from PIL import Image


@dataclass(frozen=True)
class Case:
    dataset: str
    fold: str
    seed: int
    family: int
    family_name: str
    control: int
    control_value: str
    frames: tuple[int, int, int, int]


CASES = (
    Case("Lighting", "L3", 100, 13, "object 335", 4, "0.529", (4, 8, 12, 16)),
    Case("Lighting", "L3", 100, 10, "object 318", 4, "0.529", (4, 8, 12, 16)),
    Case("MEAD", "M0", 100, 8, "M003 happy-002", 1, "0.5", (2, 6, 10, 14)),
    Case("MEAD", "M0", 200, 20, "M005 angry-015", 1, "0.5", (1, 7, 12, 16)),
)
METHODS = (0, 2, 3, 4)  # Target, Pointwise shared-noise, endpoint interpolation, LFVD.
LABEL_WIDTH = 300
HEADER_HEIGHT = 62
TILE_WIDTH = 256
TILE_HEIGHT = 176
GUTTER = 6


def geometry(dataset: str) -> tuple[int, int]:
    if dataset == "Lighting":
        return 128, 9
    if dataset == "MEAD":
        return 192, 3
    raise ValueError(dataset)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--gif-root",
        required=True,
        type=Path,
        help="Root containing lighting/ and mead/ all-method GIF exports",
    )
    return parser.parse_args()


def source_path(root: Path, case: Case) -> Path:
    return (
        root
        / case.dataset.lower()
        / case.fold
        / f"seed_{case.seed}"
        / f"family_{case.family:03d}_all_methods.gif"
    )


def landscape_crop(image: Image.Image) -> Image.Image:
    crop_height = round(image.width * TILE_HEIGHT / TILE_WIDTH)
    top = (image.height - crop_height) // 2
    return image.crop((0, top, image.width, top + crop_height)).resize(
        (TILE_WIDTH, TILE_HEIGHT), Image.Resampling.LANCZOS
    )


def build_strip(path: Path, case: Case, method: int) -> Image.Image:
    cell, control_count = geometry(case.dataset)
    if not 0 <= case.control < control_count:
        raise ValueError((case.dataset, case.control))
    width = 4 * TILE_WIDTH + 3 * GUTTER
    strip = Image.new("RGB", (width, TILE_HEIGHT), "white")
    x0 = LABEL_WIDTH + case.control * cell
    y0 = HEADER_HEIGHT + method * cell
    with Image.open(path) as gif:
        for column, frame_index in enumerate(case.frames):
            gif.seek(frame_index)
            frame = gif.convert("RGB")
            square = frame.crop((x0, y0, x0 + cell, y0 + cell))
            strip.paste(landscape_crop(square), (column * (TILE_WIDTH + GUTTER), 0))
    return strip


def output_name(case: Case, method: int) -> str:
    return (
        f"{case.dataset.lower()}_{case.fold}_f{case.family:03d}_s{case.seed}"
        f"_m{method}_s{case.control:02d}_motionstone.png"
    )


def main() -> None:
    args = parse_args()
    output_root = Path("figures/qualitative")
    source_data = Path("figures/source_data/qualitative_motionstone_method_grid")
    output_root.mkdir(parents=True, exist_ok=True)
    source_data.mkdir(parents=True, exist_ok=True)

    manifest = {
        "description": "Four-example method grid matching the geometry of MotionStone Fig. 4.",
        "processing": "center crop to 256x176, Lanczos resize, concatenate; no sharpening, alignment, or color correction",
        "methods": {"0": "target", "2": "pointwise_shared_noise", "3": "endpoint_interpolation", "4": "lfvd"},
        "cases": [],
    }
    for case in CASES:
        source = source_path(args.gif_root, case)
        if not source.exists():
            raise FileNotFoundError(source)
        outputs = []
        for method in METHODS:
            destination = output_root / output_name(case, method)
            build_strip(source, case, method).save(destination, dpi=(300, 300), optimize=True)
            outputs.append(destination.as_posix())
            print(destination)
        manifest["cases"].append(
            {
                **asdict(case),
                "frames": list(case.frames),
                "source": source.relative_to(args.gif_root).as_posix(),
                "outputs": outputs,
            }
        )

    manifest_path = source_data / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(manifest_path)


if __name__ == "__main__":
    main()
