# Fixed target-identity swap controls: design and interpretation

**Protocol frozen 2026-11-15 before reading any cross-target model predictions.**
This is a retrospective methodological experiment using previously opened Level-A
data, not a new prospective holdout of taxa and not a biological-process endpoint.

## Scientific question

Can a purely numerical measure of cross-source species-distribution agreement
mistake a *wrong species* for an agreement about the **same biological target**?
The exact common target/key is a required part of the 284b relation contract.
We distinguish **identity authorization** from **numerical mismatch detection**.

## Freeze and control logic

The complete fixed target→donor mapping for all 12 existing held-out taxa,
including machine-verified identities for 12 model-fit ZIPs and 12 CHELSA frame
ZIPs, resides in `config/target_identity_controls_v1.json`.

Donors are distinct species chosen for ecological or taxonomic similarity
(arid shrubs, mangroves, conifers, *Nothofagus*, *Eucalyptus*). This is **not**
a random matched-species design, and not a claim that donor niches are
identical. There will be **no substitution** of taxa or models after scoring.

For each 12×3 accessible-area radii×8 procedure cell:

1. The original valid-key control uses PRESERVED_SPECIMEN prediction of target
   vs HUMAN_OBSERVATION prediction of the *same* target (2,000 identical
   `comparison_row_id` values). Keep all original inadequacies unresolved.
2. The constructed wrong-target control uses the target's PRESERVED_SPECIMEN
   model score vs a fixed **different species** HUMAN_OBSERVATION model,
   reevaluated on the target's *same 2,000 CHELSA bio1–bio19 rows*.
3. All ZIP artifact digests, per-frame parquet digests, original source
   prediction digests and original held-out cell CSV hashes must match frozen
   receipts. Re-scoring the donor on **its own frame** must reproduce the
   stored original surface to maximum absolute error ≤1e−10. Any mismatch
   stops the run; it cannot be used to select another model.
4. Only cells with both original target scores adequate and the donor
   HUMAN_OBSERVATION answer adequate are numerically evaluated. Others
   remain unresolved; the full 288 denominator is reported.
5. Compare target-specific frozen procedure×M q95 with a single pooled
   nearest-rank q95 derived from the untouched reference. The 24 thresholds,
   12 donor assignments, eligible-score criterion and original row identities
   are all fixed before wrong-target scoring. No posthoc threshold adjustments.

**The unambiguous known label** in the constructed negative control is
*"the donor source belongs to a different target taxon"*.
An identity-aware contract should **reject this pair before scoring**, rather
than claim a biological contradiction. The diagnostic question is how often
a score-only rule nevertheless gives a plausible agreement verdict.

## What cannot be inferred

- A swapped model evaluated outside its own geographic area is not a
  biologically validated absence or suitable counterfactual; it may extrapolate.
- This cannot estimate sensitivity for real obligate interactions, or show
  that cross-source observations have different underlying ecological truth.
- Target identity is known by metadata. Catching it with an identity gate is
  logically necessary but not itself a novel numerical method.
- All 12 target taxa were previously opened; evaluation is *post hoc* as a
  scientific claim, despite this local predeclared donor assignment.
- Methods and biological taxa are correlated. Cells are not independent
  biological replicates.
- No new empirical conclusion should be added to 284b's frozen ledger.
- A convincing stronger test requires truly fresh taxa and a biologically
  meaningful known-outcome comparison.

## A decision threshold for publication

If many wrong-target scores nevertheless fall *inside* the original q95
coherence envelope, the paper should explicitly state that numerical
coherence alone cannot establish shared biological target identity; the
formal key check is not optional. If almost all swaps exceed, that demonstrates
only a diagnostic ability to reject these constructed mismatches. In neither
case does it establish biological causality or universal superior prediction.

The files in this branch support a source-backed Methods/Supplement
diagnostic; they must not be silently promoted into the invited paper's
confirmatory Level-A results.
