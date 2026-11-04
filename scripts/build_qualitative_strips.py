"""Build label-free frame strips for the LaTeX-typeset qualitative figures.

Each strip is one row of a qualitative grid: four temporal frames of a single
(method, control) pair, joined with thin white gutters. All labels, headers,
and highlights are typeset in LaTeX (figures/qualitative/*.tex) so that text
matches the paper font at any print size.

Only deterministic Lanczos resizing and concatenation are applied to the
checked-in source crops; no sharpening, alignment, or color correction.

    python scripts/build_qualitative_strips.py
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image

RAW = Path("figures/source_data/qualitative_motionstone_style")
OUT = Path("figures/qualitative")
FRAMES = (4, 8, 12, 16)
SIZE = 256      # per-frame pixels in the strip
GUTTER = 6      # white gutter between frames, in pixels

# (source directory, methods, controls)
JOBS = (
    ("lighting_L3_f013_s100", (0, 2, 3, 4), (4,)),       # method comparison, s=.529
    ("mead_M0_f007_s100", (0, 2, 3, 4), (1,)),           # method comparison, s=.5
    ("lighting_L3_f010_s100", (4,), (0, 4, 8)),          # Lighting sweep, object 318
    ("lighting_L3_f008_s100", (4,), (0, 4, 8)),          # Lighting sweep, object 308
    ("mead_M1_f006_s100", (4,), (0, 1, 2)),              # MEAD sweep, M007-angry-015
    ("mead_M2_f010_s100", (4,), (0, 1, 2)),              # MEAD sweep, M011-happy-007
)


def strip(directory: str, method: int, control: int) -> Image.Image:
    width = len(FRAMES) * SIZE + (len(FRAMES) - 1) * GUTTER
    canvas = Image.new("RGB", (width, SIZE), (255, 255, 255))
    for column, frame in enumerate(FRAMES):
        path = RAW / directory / f"m{method}_s{control:02d}_t{frame:02d}.png"
        tile = Image.open(path).convert("RGB").resize((SIZE, SIZE), Image.Resampling.LANCZOS)
        canvas.paste(tile, (column * (SIZE + GUTTER), 0))
    return canvas


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for directory, methods, controls in JOBS:
        for method in methods:
            for control in controls:
                name = f"{directory}_m{method}_s{control:02d}.png"
                strip(directory, method, control).save(OUT / name, dpi=(300, 300), optimize=True)
                print(OUT / name)


if __name__ == "__main__":
    main()
