# LFVD Overleaf package (2026-11-02)

This revision is derived only from the user-supplied archive
`Latent_Function_Video_Diffusion__Generate_Once__Query_Videos_at_Any_Continuous_Control__2_.zip`.
Its SHA-256 and local provenance are recorded in `CANONICAL_SOURCE.txt`; the
untouched extraction is preserved separately in
`outputs/paper_zip_baseline_20261102_v1`.

1. In Overleaf select **New Project -> Upload Project** and upload the source
   ZIP. The archive has no enclosing parent directory.
2. Select **pdfLaTeX**.
3. Set the main document to `main.tex` for the manuscript.
4. Set it to `supplement.tex` for the supplementary material.

All active figures are either schematic panels from the supplied ZIP or plots
and qualitative panels rebuilt from the archived LFVD experiment outputs. The
paper does not use example images as experimental evidence. Plot source data
and scripts are retained under `figures/source_data/` when applicable.

The revision adds object/actor-disjoint main evaluation, five-fold measured
unseen-control evaluation, LFVD-Identity encoder ablations, synchronized timing,
analytical transformer FLOPs, representation diagnostics, and a locked compact
coordinate ablation. Exact changes from the supplied ZIP are summarized in
`CHANGES_FROM_USER_ZIP.md`.

The scientific body occupies eight pages. The required CVPR 2027 LLM Usage
Statement follows the body, and references follow that statement. The
supplement compiles independently.
