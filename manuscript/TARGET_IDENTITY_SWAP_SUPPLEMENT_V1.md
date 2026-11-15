# Supplementary methods and results: frozen wrong-target identity controls

**Exploratory reanalysis — not the held-out Level-A result.**
Design pinned in `config/target_identity_controls_v1.json` before donor scores
on the focal grids were opened. However, all 12 taxon identities and their
original Level-A outcomes had already been opened in September 2026; the
experiment is **not** a new independent biological validation.

## Research question

Can a numerical soft-coherence criterion falsely appear to authorize an
agreement even when the two separately fitted models refer to *different*
biological target taxa? A valid relation endpoint requires that the target
identity and comparison row are both matched **before** a numerical agreement
test is admissible.

## Reanalysis protocol

The existing Level-A experiment compared two independent GBIF data modes:
PRESERVED_SPECIMEN and HUMAN_OBSERVATION. We retained the 12 original
held-out plant taxa, the original CHELSA bio1–19 grids of exactly 2,000
comparison-row IDs for each M=150,300,500 km, eight fixed modelling
procedures, and 24 prespecified procedure×M nearest-rank q95 source-discordance
reference ceilings.

For each taxon, a fixed ecologically or taxonomically similar **different
species** was chosen as the donor of the HUMAN_OBSERVATION model. The
12 complete target→donor assignments and 24 signed, immutable ZIP artifact
identities were frozen before the scoring run. The donor's preserved-specimen
records did not enter the focal model, and neither donor nor target model
was refitted. The donor model was evaluated on the target taxon's original,
identical CHELSA predictor rows; all 2,000 focal row IDs remained in order
for the subsequent Schoener-D calculation.

The workflow confirmed every artifact ZIP SHA-256, inner model-fit prediction
surface hash, and core19 frame hash. It then reconstructed each donor
HUMAN_OBSERVATION prediction on its **own** frame before applying the same
model to the focal frame; predictions had to agree with the original
stored model output to maximum absolute error ≤1e−10. A failed checksum or
prediction-reproduction check was a hard failure, not a replacement rule.

Only focal target cells with both original answers adequate and donor cells
with their own HUMAN_OBSERVATION answer adequate were evaluated; other
cases remained unresolved. A negative-control label meant exactly
**wrong target identity**, not proven biological niche mismatch or interaction
failure.

## Observed numerical agreement despite target substitution

Among **288 fixed target×M×procedure cells**, **280** met all adequacy gates
and were evaluated. Eight remained unresolved; no missing numeric score was
coerced into a zero.

| Diagnostic | Matching procedure×M ceiling | Single pooled reference q95 |
|---|---:|---:|
| Original same-target alerts on the 280 evaluable cells | 0/280 | 2/280 |
| Distinct-species target swaps flagged | **165/280 (58.9%)** | **148/280 (52.9%)** |
| Distinct-species target swaps still within ceiling | **115/280 (41.1%)** | **132/280 (47.1%)** |

Matched-q95 flags exceeded pooled-q95 flags in the aggregate by 17 cells
(6.1 percentage points), but this is an **exploratory**, correlated
comparison without true biological mismatch labels or out-of-sample taxa.
The 280 repeated cells are not independent replicates.

At the biologically relevant target level, 11 of 12 taxa had at least one
matched-q95 flag against their fixed wrong-species donor; one target
(*Laguncularia racemosa* paired with *Avicennia germinans*) had **0/24**
flagged. This result shows that the score-only test is not sufficient
to detect target-identity errors even when supplied with bona fide, independently
fitted ecological models. Eight constructed wrong-target scores were
**numerically closer** to the focal PRESERVED_SPECIMEN scores than the
legitimate same-target HUMAN_OBSERVATION score for the same cell.

## Interpretation and prior-art boundary

The strongest supported point is **a falsifying counterexample to the
*logical implication* "small prediction discordance certifies that two
answers describe the same biological target"**. Species identity is a
separately observed metadata condition; it cannot be inferred from a
numerical score-distance. The complete relation-endpoint contract should
reject all mismatched keys *before* evaluating whether score discordance is
inside its q95 envelope. That is an eligibility rule, not a 100%-accurate
numeric classifier.

This is not evidence that the q95 test is flawed when used on the domain
for which it was defined. Every swapped pair violates its precondition.
The deliberately illicit score-only evaluation shows why the precondition
must be explicit and audited.

The two error types must not be conflated: a wrong-species model can share
a real climatic niche with the target species; conversely the model may
extrapolate beyond its original geographic/environmental training domain.
The fixed donor species were not randomly sampled and do not represent
known biologically incompatible interacting species. Thus the reported
58.9% is an *alert frequency under selected constructed swaps*, **not**
true-positive rate for biological violations, process necessity, or a
prediction of detection power in nature.

## Scientific consequence

This creates a coherent three-part methodological argument:

1. **Correct key/target first** — demonstrated as necessary for the
   logical admissibility of the score-comparison by wrong-target controls.
2. **Then answer adequacy and conditional cross-source coherence** —
   demonstrated by the original 12-taxon held-out Level A (283 evaluable;
   five unresolved; 0/12 exceedance taxa).
3. **Then interpretation reliability** — limited separately by the exact
   M1 invalid-key decomposition and class-conditional FDF analysis.

No part proves that metadata validation is a novel ecological estimator or
that a higher-tier interaction mechanism has been identified. Claims about
general methods superiority still require fresh taxa, realistic negative
controls and strong spatial/temporal replication.

## Evidence location

- Fixed plan and artifact digests:
  `config/target_identity_controls_v1.json`
- Deterministic scoring and model integrity checks:
  `scripts/audit_target_identity_controls_v1.py`
- Machine-readable 12-taxon results:
  `results/target_identity_controls_v1/target_identity_results_v1.json`
- Full 288-cell diagnostic output:
  `results/target_identity_controls_v1/target_identity_cells_v1.csv`
- The original held-out empirical endpoint and original frozen reference
  remain untouched on `main`; empirical ledger increment for this
  reanalysis is **zero**.
