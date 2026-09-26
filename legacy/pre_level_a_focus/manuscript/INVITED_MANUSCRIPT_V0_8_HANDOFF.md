# Invited manuscript v0.8 handoff

Purpose: make the transition from the frozen pre-invitation manuscript (`PREFIELD_FLAGSHIP_V0_7.md`) to the first invited Ecology Letters Method manuscript mechanical rather than interpretive.

This handoff is **noncanonical until an invitation/approved proposal is received**. It does not open new data, alter thresholds or increment the empirical ledger.

## Trigger

Promote v0.8 only after Ecology Letters invites/approves a full Method submission.

Until then:

- Stage-1 proposal title is **Relation endpoints for ecological inference: when independent answers can support joint biological claims**;
- canonical full manuscript remains `PREFIELD_FLAGSHIP_V0_7.md`;
- do not silently edit v0.7 in place.

## Deterministic build

Run:

`python scripts/build_prefield_flagship_v0_8_candidate.py`

This creates:

`manuscript/PREFIELD_FLAGSHIP_V0_8_CANDIDATE.md`

The builder must stop rather than guess if any frozen textual anchor in v0.7 has changed.

## Authorized v0.8 changes

Only the following scientific/editorial changes are authorized by the pre-invitation handoff:

1. **Title promotion**
   - old: `Prospective validation of ecological answers: from cross-source reproducibility to identifiable biological absence`
   - new: `Relation endpoints for ecological inference: when independent answers can support joint biological claims`

2. **Antecedent paragraph hardening**
   - explicitly acknowledge ecological data fusion (Pacifici et al. 2017);
   - explicitly acknowledge JSDM marginal versus joint prediction (Wilkinson et al. 2021);
   - add these to the list of established ingredients not claimed as novel.

3. **Relation-layer separation subsection**
   Insert before the existing soft/hard relation subsection:

   `### 2.2 Why accurate answers do not eliminate the relation layer`

   Required content:
   - hard relation `E -> F`;
   - violation probability `v=P(E=1,F=0)`;
   - classical bound `max(0,p_E-p_F) <= v <= min(p_E,1-p_F)`;
   - exact `p_E=p_F=0.5` counterexample with both `v=0` and `v=0.5`;
   - explicit statement that the probability result is classical and is used only as a separation argument;
   - JSDMs may estimate joint coupling, but statistical coupling does not choose the biological endpoint semantics;
   - relation-endpoint contract supplies relation, common key and contradiction rule.

4. **Reference additions**
   Add only the pre-audited references needed for the new paragraph:
   - Nelsen 2006, *An Introduction to Copulas*;
   - Wilkinson et al. 2021, JSDM marginal/joint prediction;
   - Galiana et al. 2024, co-occurrence/interaction distinction;
   - Pacifici et al. 2017, ecological data fusion.

## Changes explicitly not authorized by this handoff

The v0.8 promotion must **not**:

- open any focal Level-C cross-role value;
- convert Cremastra or Belonocnema non-detection into functional absence;
- alter the v8.1 sensitivity/specificity thresholds or calibration counts;
- change candidate identities;
- reinterpret five Level-A unresolved cells as failures;
- treat 283 diagnostics as independent replication;
- reinterpret q95 as nominal 95% predictive coverage;
- claim Fréchet–Hoeffding bounds as new mathematics;
- claim JSDMs, data fusion, occupancy, LIES, model adequacy, external validation or preregistration as inventions of this paper;
- add a seventh display item;
- change empirical ledger = 1.

## Display plan under v0.8

Keep the six-item full-submission display budget.

Recommended integration:

- **Figure 1:** unchanged executable contract overview;
- **Figure 2:** unchanged Level-A empirical anchor;
- **Figure 3:** retain event/function dependency as the main figure; optionally integrate the already-prepared `relation_layer_separation_inset_v0_1.svg` as a compact inset rather than creating Figure 6;
- **Figure 4:** unchanged parallel real-system openability audit;
- **Figure 5:** unchanged generalized invalid-state decomposition;
- **Table 1:** unchanged claim/evidence matrix except add the nonempirical separation result if the final table has space; otherwise place it in Supplement.

Do not use the separation inset as a second Stage-1 proposal attachment unless editors explicitly request it.

## Word-count strategy

No compensating deletion is currently required. The frozen v0.7 main text has substantial headroom below the 5,000-word Method ceiling, and CI must verify the generated v0.8 candidate remains <=5,000 words and abstract <=150 words.

The relation-layer paragraph should remain concise. Do not turn the manuscript into a copula/JSDM review.

## Promotion audit after invitation

Before renaming the candidate to canonical `PREFIELD_FLAGSHIP_V0_8.md`, verify all of the following:

- invitation/approved proposal exists;
- generated candidate passes `tests/test_invited_v08_candidate_builder.py`;
- abstract <=150 words;
- main text <=5,000 words;
- display count remains 6;
- title page and cover letter are synchronized to the promoted title;
- reference list contains the four added antecedents with verified metadata;
- claim/evidence ledger gets a new row for the relation-layer separation result marked **nonempirical method evidence**;
- full-display captions are synchronized only where Figure 3/Table 1 actually change;
- archive/DOI packaging still excludes any later Level-C focal outcome unless separately authorized.

## Frozen empirical boundary carried into v0.8

- Level A: sole completed empirical endpoint; 12 independent held-out taxa; 288 repeated diagnostics; 283 evaluable; five unresolved; 0/12 taxa with an envelope exceedance among evaluable cells.
- Level B: fresh empirical relation endpoint unopened.
- Level C: focal hard/soft/knockout outcomes remain sealed pending candidate-specific negative-state calibration.
- Empirical ledger: **1**.
- Relation-layer separation: **nonempirical**, ledger increment 0.

## Editorial interpretation

The purpose of v0.8 is not to add another result. It is to make the paper's logical object explicit:

> accurate ecological answers, and even statistical joint structure, do not by themselves determine which biological relation those answers are licensed to support. The relation-endpoint contract supplies that prospective biological authorization layer.
