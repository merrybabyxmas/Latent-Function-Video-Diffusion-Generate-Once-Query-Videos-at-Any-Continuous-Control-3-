# Changes from the user-supplied ZIP

Canonical input:
`Latent_Function_Video_Diffusion__Generate_Once__Query_Videos_at_Any_Continuous_Control__2_.zip`

This directory is the active revision derived from that archive. The original
extraction is preserved separately in `outputs/paper_zip_baseline_20261102_v1`.

## Scientific revisions

- Reframed the central contribution as family-valued diffusion, with LFVD as a
  learned-coordinate realization and JointConcat-LQ as a minimal fixed-grid
  realization.
- Added five-fold measured unseen-control results, identity-encoder
  comparisons, synchronized wall-clock timing, analytical transformer FLOPs, and
  an explicit representation-bottleneck analysis.
- Restored a method pipeline figure and retained only figures backed by actual
  experiment outputs.
- Added multi-view joint-diffusion related work and narrowed the novelty claim.
- Added explicit limitations for code size, amortization crossover, the ordinal
  MEAD control axis, and the remaining family-code sampling gap.
- Added a locked 28-frame learned-coordinate ablation: 24.3% fewer family
  tokens than native 37-frame packing, with exact-code and sampled-code results
  reported separately and without changing the main five-fold model.
- Recast direct JointConcat-LQ as LFVD-Identity, the exact $\lambda=0$, $P=I$
  instance of the family encoder. The learned-coordinate default is named
  LFVD-Mix and the shorter representation LFVD-Compact.
- Replaced sparse-control validation numbers with a no-training, locked-test
  re-evaluation of all five existing checkpoints (20 objects, 80 families,
  three seeds, 50 steps). LFVD-Mix improves unseen LPIPS by 0.0693 and PSNR by
  2.409 dB over shared-noise Pointwise.
- Added the matching locked-test LFVD-Identity sparse re-evaluation. Identity
  and Mix are tied overall; Mix has a 0.0505 dB unseen-PSNR edge, while all
  other sparse encoder intervals include zero.
- Verified the three-control family code shape as 48x13x16x16: 64.9% fewer
  latent frames than the dense 37-frame Lighting code, but 2.6x an ordinary
  five-frame video latent.
- Added paired MEAD confidence intervals to the encoder comparison, quantified
  the compact-code loss against the matched full-length L0 record, and stated
  that the 13-frame sparse model retains 0.3271 all-control LPIPS versus 0.3216
  for dense LFVD-Mix at a 2.37-query analytical crossover.

## Submission-compliance revisions

- Added the mandatory CVPR 2027 `LLM Usage Statement` after the main text and
  before the references.
- Added a human-subject data-use statement for the pre-existing MEAD dataset.
- Kept the main scientific text within eight pages and the supplement as a
  separate document.

The synchronized timing table and cost-scaling plot include the directly
measured $M=7$ crossover point and MEAD timing. The split-matched
LFVD-Identity comparison covers all five Lighting folds, three sampling
seeds, and paired object-bootstrap intervals for complete and sparse-control
protocols. The full-grid comparison uses the same locked test records for all
methods; an earlier mixed-split aggregate is excluded from the canonical
package.

Legacy public keys are documented without rewriting immutable records:
`joint_concat_learned_query = LFVD-Identity` and `lfvd = LFVD-Mix`.
