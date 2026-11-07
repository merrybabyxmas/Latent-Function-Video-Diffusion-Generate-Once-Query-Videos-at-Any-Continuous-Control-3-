# Final Control and Function Audits (2026-11-06)

This revision replaces the weak Lighting Pointwise baseline with the frozen
control-token design selected on L0 validation and records the follow-up
exposure, sparse-control, query-path, and reader audits. Raw CSV and protocol
files are checked in under `results/final_audits_20261106/`.

## Main matched-update Lighting result

- Pointwise shared-noise: LPIPS 0.362986, PSNR 19.7780, SSIM 0.731837,
  control Spearman 0.930278.
- LFVD-Mix: LPIPS 0.321635, PSNR 21.1408, SSIM 0.752628,
  control Spearman 0.932569.
- Paired Pointwise-minus-LFVD LPIPS: +0.041351,
  95% CI [0.031561, 0.051147].
- Paired LFVD-minus-Pointwise control Spearman: +0.002292;
  the corresponding interval includes zero.

## Interpretation-changing audits

- Dense L0 validation, Pointwise at nine times the update count:
  0.326844 LPIPS / 20.7751 PSNR / 0.741307 SSIM / 0.997917 Spearman.
  LFVD on the same split: 0.336514 / 20.8640 / 0.748711 / 0.972917.
  This is a stress test, not the five-fold main protocol. It prevents an
  intrinsic-representation explanation for the matched-update quality gap.
- Sparse controls, Pointwise at nine times the main update count: Pointwise
  has lower unseen LPIPS (0.332197 vs. 0.341027); LFVD has higher unseen PSNR
  (21.2215 vs. 20.5849) and higher all-query ordering (0.990556 vs. 0.969097).
  The paper therefore reports a trade-off rather than uniform LFVD dominance.

## Direct functional evidence

- Target-relative adjacent-query LPIPS error: LFVD 0.030345 vs. shared-noise
  Pointwise 0.086728, independent Pointwise 0.119000, and endpoint
  interpolation 0.143885.
- Target-relative path-length log error: LFVD 0.134093 vs. 0.586638,
  0.510050, and 1.746024, respectively.
- With the sampled family code held fixed, the learned reader reaches
  0.326863 LPIPS vs. 0.407397 for adjacent latent interpolation.

## Naming and data lineage

- `lfvd_mix` is the paper's default LFVD result.
- `pointwise_shared` and `pointwise_independent` in the new Lighting export
  use the frozen control-token model.
- Older MEAD results are retained because the control token did not improve
  the MEAD validation gate.
- All reported test targets are official measured images; no interpolated
  image is used as ground truth.
