# Level A: retrospective reference-transfer and discriminability audit (2026-11-15)

**Status:** exploratory diagnostic of already opened, signed historical artifacts. This is
**not a new positive empirical endpoint**, a Level-C result, or a new
confirmatory test. The frozen main endpoint is unchanged.

## Question and source chain

Does the q95 relation-endpoint rule ever flag an independently evaluated taxon,
or is the 0/12 held-out closure effectively guaranteed by its design?
How sensitive is the held-out finding to a simpler pooled comparator?

Pinned artifacts (original audit / reference):
- heldout run 34439487385; artifact 10137399646, opened 2026-09-10
- successor-reference run 34439012066; artifact 10137248940
- original receipt `results/product_b_same_target_core19_v0_4_heldout_final_receipt.json`
- original reviewer audit `results/reviewer2_level_a_structure_audit_v0_1.json`
- script `scripts/audit_level_a_discriminability_v1.py`

The workflow re-downloads those exact artifacts and checks **inner CSV SHA-256**
before using them. It archives sufficient already-opened scalar comparison
data, without refitting ecological models or altering the original artifacts.

## Reanalysis results

1. Original held-out: **12 taxa, 288 predeclared procedure×M cells, 283 adequate,
   5 unresolved, and 0/12 taxa with any exceedance** of the frozen matching
   reference ceiling. The original nearest-rank q95 values are recovered
   exactly for all 24 procedure×M reference cells.
2. Reference leave-one-taxon-out diagnostic: among the **47 calibration taxa**,
   **11/47 taxa** (65/1024 evaluable cells) exceed a re-frozen reference
   nearest-rank q95 built from *other reference taxa only* within the same
   procedure×M. The other **36/47** do not exceed. Therefore the method is
   not an all-pass rule, but this result does **not** estimate external
   specificity or nominal false-alarm probability.
3. Cell-weighted mean discordance (1−Schoener D) is **0.1865** in the held-out
   panel versus **0.2498** in the reference panel; this indicates a
   potential taxon-composition / ease shift and **is not** a treatment effect
   or an independent-replicate comparison.
4. A single pooled nearest-rank q95 calculated over 1,024 correlated
   reference cells flags **2/283 held-out cells** (2/12 taxa), whereas the
   frozen procedure×M-specific ceilings flag none. The two taxa are
   *Nothofagus antarctica* and *N. betuloides*. Without ground-truth labels
   these are **not demonstrably false positives** of the pooled comparator.
   The pooled procedure ignores the heterogeneity of calibration cells.

The machine-readable audit includes all 47 reference taxon-level
leave-one-out summaries and all 12 held-out taxon-level summaries.

## Post-hoc stress test (not biological discrimination)

Adding a fixed synthetic increment to the *already measured* held-out scalar
discordance and applying the unchanged frozen reference rule produces:

| Synthetic distance increment | Cells over ceiling | Taxa with ≥1 exceedance |
|---|---:|---:|
| 0.025 | 1 | 1 |
| 0.05 | 6 | 4 |
| 0.10 | 22 | 5 |
| 0.20 | 115 | 10 |

These illustrate the headroom of the existing thresholds; they **do not**
reconstruct source-specific surfaces, mimic real mechanisms, or estimate
detection power for a genuine biological incompatibility.

## Critical inferential boundaries

- The 47 reference taxa are not a fresh random test set; the reference
  distribution is refitted 47 times on the same pool. The q95 boundary is not a
  95% predictive interval or a formal alpha=0.05 test.
- Successor and held-out taxa need not be exchangeable. Species selection,
  phylogenetic relatedness, observational coverage and geographic
  differences could explain the distance shift.
- 283/288 and 1024/1128 are repeated cells; **12** and **47** are biological
  units in the respective panels, not the individual cells.
- This audit does not estimate accuracy because there are no independently
  verified *negative* instances of biologically incompatible source answers,
  nor a gold-standard ecological process-necessity label.
- This audit is **post-hoc**. All contrasts and perturbation values here are
  descriptive and do not change the original predeclared held-out result.

## Consequence for publication

The defensible addition is: *the original Level-A frozen comparison is
non-vacuous (some independent, leave-one-out reference taxa exceed), but the
held-out all-pass result is conditioned on a reference panel with higher
discordance and does not establish superiority over simpler SDM
source-comparison methods.*

Before claiming method superiority or biological discriminability, a new,
prospectively specified experiment needs independently verified negative
controls (e.g. correctly aligned versus deliberately misaligned
source-specific prediction surfaces on the same common cell IDs) and a
strictly separated calibration and test panel. Such a contrast must not
reinterpret 1−Schoener D alone as a gold-standard biological violation.
