"""Build paper qualitative figures from locked held-out comparison GIFs.

The script performs only deterministic cropping, resizing, and labeling. It
does not sharpen, align, color-correct, or otherwise alter result pixels.
Run once with --gif-root to extract the checked-in source crops; subsequent
runs may use --compose-only and depend only on those crops.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


BLUE = (28, 91, 165)
RED = (190, 54, 80)
ORANGE = (218, 107, 38)
GRAY = (85, 85, 85)
WHITE = (255, 255, 255)


@dataclass(frozen=True)
class Example:
    dataset: str
    fold: str
    seed: int
    family_index: int
    family_id: str

    @property
    def key(self) -> str:
        return f"{self.dataset.lower()}_{self.fold}_f{self.family_index:03d}_s{self.seed}"


METHOD_LIGHTING = Example("Lighting", "L3", 100, 13, "335")
METHOD_MEAD = Example("MEAD", "M0", 100, 7, "M003-happy-008")
LIGHTING_EXAMPLES = (
    Example("Lighting", "L3", 100, 10, "318"),
    Example("Lighting", "L3", 100, 8, "308"),
)
MEAD_EXAMPLES = (
    Example("MEAD", "M1", 100, 6, "M007-angry-015"),
    Example("MEAD", "M2", 100, 10, "M011-happy-007"),
)


def font(size: int, bold: bool = False, italic: bool = False) -> ImageFont.FreeTypeFont:
    windows = Path("C:/Windows/Fonts")
    if bold and italic:
        candidates = (windows / "timesbi.ttf", windows / "arialbi.ttf")
    elif bold:
        candidates = (windows / "timesbd.ttf", windows / "arialbd.ttf")
    elif italic:
        candidates = (windows / "timesi.ttf", windows / "ariali.ttf")
    else:
        candidates = (windows / "times.ttf", windows / "arial.ttf")
    candidates += (
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf")
        if bold
        else Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"),
    )
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def gif_path(root: Path, example: Example) -> Path:
    return (
        root
        / example.dataset.lower()
        / example.fold
        / f"seed_{example.seed}"
        / f"family_{example.family_index:03d}_all_methods.gif"
    )


def geometry(dataset: str) -> tuple[int, int, int, int, int]:
    if dataset == "Lighting":
        return 300, 62, 128, 9, 5
    if dataset == "MEAD":
        return 300, 62, 192, 3, 5
    raise ValueError(dataset)


def crop_cell(image: Image.Image, dataset: str, method: int, control: int) -> Image.Image:
    label_width, header, cell, control_count, method_count = geometry(dataset)
    if not (0 <= control < control_count and 0 <= method < method_count):
        raise ValueError((dataset, method, control))
    x0 = label_width + control * cell
    y0 = header + method * cell
    return image.crop((x0, y0, x0 + cell, y0 + cell)).convert("RGB")


def raw_path(raw_root: Path, example: Example, method: int, control: int, frame: int) -> Path:
    return raw_root / example.key / f"m{method}_s{control:02d}_t{frame:02d}.png"


def extract(
    gif_root: Path,
    raw_root: Path,
    example: Example,
    methods: tuple[int, ...],
    controls: tuple[int, ...],
    frames: tuple[int, ...],
) -> None:
    path = gif_path(gif_root, example)
    if not path.exists():
        raise FileNotFoundError(path)
    with Image.open(path) as gif:
        for frame in frames:
            gif.seek(frame)
            rgb = gif.convert("RGB")
            for method in methods:
                for control in controls:
                    output = raw_path(raw_root, example, method, control, frame)
                    output.parent.mkdir(parents=True, exist_ok=True)
                    crop_cell(rgb, example.dataset, method, control).save(output, optimize=True)


def load_crop(
    raw_root: Path,
    example: Example,
    method: int,
    control: int,
    frame: int,
    size: int,
) -> Image.Image:
    path = raw_path(raw_root, example, method, control, frame)
    if not path.exists():
        raise FileNotFoundError(path)
    return Image.open(path).convert("RGB").resize((size, size), Image.Resampling.LANCZOS)


def centered(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, face: ImageFont.ImageFont, fill=GRAY) -> None:
    box = draw.textbbox((0, 0), text, font=face)
    draw.text((xy[0] - (box[2] - box[0]) // 2, xy[1]), text, font=face, fill=fill)


def method_panel(
    raw_root: Path,
    example: Example,
    control: int,
    control_label: str,
    size: int = 164,
) -> Image.Image:
    methods = ((0, "Target", GRAY), (2, "Pointwise", RED), (3, "Endpoint interp.", GRAY), (4, "LFVD", BLUE))
    frames = (4, 8, 12, 16)
    label_width, title_h, frame_h, gap = 112, 40, 26, 5
    width = label_width + len(frames) * size + (len(frames) - 1) * gap
    height = title_h + frame_h + len(methods) * size + (len(methods) - 1) * gap
    canvas = Image.new("RGB", (width, height), WHITE)
    draw = ImageDraw.Draw(canvas)
    title = f"{example.dataset} held-out family  |  {control_label}"
    centered(draw, (width // 2, 4), title, font(21, bold=True), "black")
    for column, frame in enumerate(frames):
        x = label_width + column * (size + gap) + size // 2
        centered(draw, (x, title_h + 2), f"frame {frame}", font(15), GRAY)
    for row, (method, label, color) in enumerate(methods):
        y = title_h + frame_h + row * (size + gap)
        box = draw.textbbox((0, 0), label, font=font(16, bold=(method == 4)))
        draw.text((label_width - (box[2] - box[0]) - 9, y + (size - (box[3] - box[1])) // 2), label, font=font(16, bold=(method == 4)), fill=color)
        for column, frame in enumerate(frames):
            x = label_width + column * (size + gap)
            canvas.paste(load_crop(raw_root, example, method, control, frame, size), (x, y))
    return canvas


def control_panel(
    raw_root: Path,
    example: Example,
    controls: tuple[tuple[int, str], ...],
    size: int,
) -> Image.Image:
    frames = (4, 8, 12, 16)
    label_width, title_h, frame_h, gap = 92, 42, 25, 5
    width = label_width + len(frames) * size + (len(frames) - 1) * gap
    height = title_h + frame_h + len(controls) * size + (len(controls) - 1) * gap
    canvas = Image.new("RGB", (width, height), WHITE)
    draw = ImageDraw.Draw(canvas)
    title = f"{example.dataset}  |  held-out {example.family_id}"
    centered(draw, (width // 2, 4), title, font(21, bold=True), "black")
    for column, frame in enumerate(frames):
        x = label_width + column * (size + gap) + size // 2
        centered(draw, (x, title_h + 1), f"t={frame}", font(15), GRAY)
    for row, (control, label) in enumerate(controls):
        y = title_h + frame_h + row * (size + gap)
        box = draw.textbbox((0, 0), label, font=font(17, bold=True, italic=True))
        draw.text((label_width - (box[2] - box[0]) - 8, y + (size - (box[3] - box[1])) // 2), label, font=font(17, bold=True, italic=True), fill=ORANGE)
        for column, frame in enumerate(frames):
            x = label_width + column * (size + gap)
            canvas.paste(load_crop(raw_root, example, 4, control, frame, size), (x, y))
    return canvas


def join_panels(panels: tuple[Image.Image, ...], output: Path, gap: int = 24) -> None:
    width = sum(panel.width for panel in panels) + gap * (len(panels) - 1)
    height = max(panel.height for panel in panels)
    canvas = Image.new("RGB", (width, height), WHITE)
    x = 0
    for index, panel in enumerate(panels):
        canvas.paste(panel, (x, 0))
        x += panel.width
        if index + 1 < len(panels):
            ImageDraw.Draw(canvas).line((x + gap // 2, 4, x + gap // 2, height - 4), fill=(185, 185, 185), width=1)
            x += gap
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output, dpi=(300, 300), optimize=True)


def stack_panels(panels: tuple[Image.Image, ...], output: Path, gap: int = 20) -> None:
    width = max(panel.width for panel in panels)
    height = sum(panel.height for panel in panels) + gap * (len(panels) - 1)
    canvas = Image.new("RGB", (width, height), WHITE)
    y = 0
    for index, panel in enumerate(panels):
        x = (width - panel.width) // 2
        canvas.paste(panel, (x, y))
        y += panel.height
        if index + 1 < len(panels):
            ImageDraw.Draw(canvas).line((4, y + gap // 2, width - 4, y + gap // 2), fill=(185, 185, 185), width=1)
            y += gap
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output, dpi=(300, 300), optimize=True)


def write_manifest(raw_root: Path, gif_root: Path | None) -> None:
    manifest = {
        "protocol": "Latest 50-step held-out evaluation, seed 100; deterministic crop only.",
        "pixel_processing": "GIF cell crop and Lanczos resize for layout; no sharpening, alignment, or color correction.",
        "source_root": str(gif_root) if gif_root else "Source crops checked into this directory.",
        "gif_geometry": {
            "Lighting": {"label_width": 300, "header": 62, "cell": 128, "controls": 9, "methods": 5},
            "MEAD": {"label_width": 300, "header": 62, "cell": 192, "controls": 3, "methods": 5},
            "method_rows": {"0": "Target", "1": "Pointwise independent", "2": "Pointwise shared-noise", "3": "Endpoint latent interpolation", "4": "LFVD"},
        },
        "method_comparison": [METHOD_LIGHTING.__dict__, METHOD_MEAD.__dict__],
        "lighting_control": [item.__dict__ for item in LIGHTING_EXAMPLES],
        "mead_control": [item.__dict__ for item in MEAD_EXAMPLES],
        "temporal_frames": [4, 8, 12, 16],
        "lighting_controls": {"indices": [0, 4, 8], "labels": ["s=0.000", "s=0.529", "s=1.000"]},
        "mead_controls": {"indices": [0, 1, 2], "labels": ["s=0.0", "s=0.5", "s=1.0"]},
    }
    raw_root.mkdir(parents=True, exist_ok=True)
    (raw_root / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gif-root", type=Path)
    parser.add_argument("--raw-root", type=Path, default=Path("figures/source_data/qualitative_motionstone_style"))
    parser.add_argument("--output-root", type=Path, default=Path("figures/reviewer_defense"))
    parser.add_argument("--compose-only", action="store_true")
    args = parser.parse_args()

    if not args.compose_only:
        if args.gif_root is None:
            parser.error("--gif-root is required unless --compose-only is set")
        extract(args.gif_root, args.raw_root, METHOD_LIGHTING, (0, 2, 3, 4), (4,), (4, 8, 12, 16))
        extract(args.gif_root, args.raw_root, METHOD_MEAD, (0, 2, 3, 4), (1,), (4, 8, 12, 16))
        for example in LIGHTING_EXAMPLES:
            extract(args.gif_root, args.raw_root, example, (4,), (0, 4, 8), (4, 8, 12, 16))
        for example in MEAD_EXAMPLES:
            extract(args.gif_root, args.raw_root, example, (4,), (0, 1, 2), (4, 8, 12, 16))

    write_manifest(args.raw_root, args.gif_root)
    join_panels(
        (
            method_panel(args.raw_root, METHOD_LIGHTING, 4, "s=0.529"),
            method_panel(args.raw_root, METHOD_MEAD, 1, "s=0.5"),
        ),
        args.output_root / "qualitative_method_comparison.png",
    )
    lighting_control = tuple(
        control_panel(args.raw_root, example, ((0, "s=0.000"), (4, "s=0.529"), (8, "s=1.000")), 176)
        for example in LIGHTING_EXAMPLES
    )
    mead_control = tuple(
        control_panel(args.raw_root, example, ((0, "s=0.0"), (1, "s=0.5"), (2, "s=1.0")), 176)
        for example in MEAD_EXAMPLES
    )
    lighting_path = args.output_root / "qualitative_lighting_control.png"
    mead_path = args.output_root / "qualitative_mead_control.png"
    join_panels(lighting_control, lighting_path)
    join_panels(mead_control, mead_path)
    with Image.open(lighting_path) as lighting_image, Image.open(mead_path) as mead_image:
        stack_panels(
            (lighting_image.convert("RGB"), mead_image.convert("RGB")),
            args.output_root / "qualitative_control_sweeps.png",
        )


if __name__ == "__main__":
    main()
