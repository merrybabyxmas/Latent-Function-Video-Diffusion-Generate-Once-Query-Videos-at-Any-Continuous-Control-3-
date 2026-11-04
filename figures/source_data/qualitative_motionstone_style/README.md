# Qualitative Figure Sources

These crops come from the latest immutable 50-step, three-seed held-out
evaluation package. `manifest.json` records the exact dataset, fold, seed,
family index, control index, temporal frame, source GIF geometry, and method
row used for every paper panel.

The paper figures apply only deterministic cell cropping, Lanczos resizing,
labels, and layout. They do not use sharpening, alignment, color correction,
or generated replacement imagery.

Rebuild the checked-in figures from the source crops:

```bash
python scripts/build_motionstone_qualitatives.py --compose-only
```

To re-extract the same crops from the full comparison GIF package, pass its
root directory:

```bash
python scripts/build_motionstone_qualitatives.py --gif-root /path/to/all_full_comparison_gifs_v1
```

The generated paper assets are:

- `figures/reviewer_defense/qualitative_method_comparison.png`
- `figures/reviewer_defense/qualitative_lighting_control.png`
- `figures/reviewer_defense/qualitative_mead_control.png`
- `figures/reviewer_defense/qualitative_control_sweeps.png` (combined archival layout)

## Typeset layout (2026-11-04)

The main paper no longer embeds the composited PNGs above. Figures 4 and 5 are
typeset in LaTeX (`figures/qualitative/fig_method_comparison.tex` and
`figures/qualitative/fig_control_sweeps.tex`) from label-free four-frame strips,
so row labels, frame indices, and panel titles use the paper font. Rebuild the
strips from the same source crops with:

```bash
python scripts/build_qualitative_strips.py
```

Grid macros (`\qsetup`, `\qrow`, `\qtitle`, `\qframes`, `\qpanel`) live in
`preamble.tex`. The former Figures 5 and 6 are merged into one 2x2 control
figure (`fig:control_sweeps`).
