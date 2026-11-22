# Relation endpoints for ecological inference: when independent answers can support joint biological claims

**Target:** Ecology Letters — invited Method manuscript  
**Scientific core:** M1 exact invalid-state decomposition + M2 Level-A held-out empirical closure  
**Status:** invited positive-core candidate, revised after the 2026-11-22 GBIF source-completeness sensitivity; **submission HOLD_FOR_SENSITIVITY_REVIEW**  
**Empirical ledger:** 1 historical completed empirical endpoint; retrospective data repair adds 0 independent endpoints

## Abstract

Combining ecological answers from distinct observation processes requires explicit rules for joint inference. We formalize relation endpoints with prespecified comparison keys, answer-adequacy gates and unresolved states. In 12 prospectively held-out plant taxa, 283 of 288 specimen-versus-human-observation comparisons were evaluable; none exceeded independently calibrated source-discordance envelopes. After retrospective restoration of 510 missing GBIF Parquet objects, all 59 taxa were refitted and 24 reference envelopes recalibrated. Again, no held-out taxon exceeded its envelope among 285 evaluable comparisons, but only 282 of the original 283 evaluable cells remained evaluable: strict full-coverage robustness was not established. For hard negative inference, coercing invalid keys into zeros increases false-violation rate by exactly `1-a1` and apparent true-violation sensitivity by `1-a0`. Even after qualification, false-discovery risk depends on violation prevalence and state-dependent validity. Relation endpoints permit evidence-bounded positive conclusions without concealing unresolved comparisons.

## 1. Introduction

Ecological models increasingly combine data streams that differ in sampling process, detectability, scale and provenance. Preserved specimens, human observations, structured surveys and sensors can each generate defensible ecological answers, but agreement or disagreement among those answers does not automatically identify the biological claim they can support. Occupancy and detection models address latent ecological state under imperfect observation; data-fusion methods integrate heterogeneous sources; joint species-distribution models estimate statistical dependence; model-adequacy and LIES frameworks make data limitations explicit. These are established contributions. Our focus is the downstream inferential boundary: **when are independently generated ecological answers licensed to compose into a joint endpoint?**

Two failure modes motivate this boundary. The first is outcome-dependent comparison. If taxa, procedures, spatial extents or tolerances are selected after source agreement is viewed, apparent reproducibility can be manufactured. The second is invalid-state coercion. If incomplete, missing or failed observation is converted into biological zero, an endpoint can gain apparent sensitivity by creating unsupported contradictions.

We therefore treat the **relation endpoint** as an explicit object. Before focal outcomes are opened, the endpoint specifies the relation, common comparison key, answer-adequacy requirements and the rule that distinguishes an admissible conclusion from an unresolved state. The aim is not to make inference maximally conservative. It is to make the evidentiary boundary auditable and asymmetric: missed conclusions are permitted when evidence is insufficient, whereas unsupported attribution is not.

The present paper uses two completed positive contributions rather than unresolved biological case studies. First, we test whether independently fitted distribution predictions from preserved-specimen and human-observation records satisfy a calibrated cross-source relation in a prospectively held-out taxon panel, and we separately audit sensitivity to a subsequently repaired upstream GBIF extract. Second, we derive the exact error consequences of deleting the unresolved state and show why observation-process qualification is distinct from reliability of the final biological call.

## 2. Relation-endpoint principle

A relation endpoint contains four scientific commitments fixed before focal opening:

1. **Target relation** — what joint statement is being evaluated.
2. **Common key** — the biological or comparison unit on which the relation is meaningful.
3. **Adequacy rule** — when each independently generated answer exists strongly enough to enter the relation.
4. **Opening rule** — which combinations of answer states authorize a conclusion and which remain unresolved.

For same-target cross-source reproducibility, the relation is a calibrated soft-coherence statement. Both answers refer to the same target and comparison frame, and the opening rule compares source discordance with a prospectively calibrated empirical envelope.

For a hard directional relation, a contradiction requires a positive antecedent and an identified negative consequent on the same valid key. If the negative state is not identified, the endpoint remains unresolved. This distinction is not a new estimator; it is a rule for what existing estimators and observations are allowed to imply jointly (Fig. 1).

## 3. Positive empirical closure across biodiversity data sources

### 3.1 Prospectively separated source answers

We constructed independent species-distribution answers from GBIF records classified as `PRESERVED_SPECIMEN` and `HUMAN_OBSERVATION`. Response occurrences from one mode could not enter the likelihood, predictor selection or prediction fitting of the other mode.

The two source-specific fits nevertheless answered the same ecological question. Within each taxon and accessible-area setting they used the same source-blind comparison geometry, the same 2,000-row comparison frame, the same CHELSA bio1-bio19 predictor universe and the same prespecified modelling-procedure library.

### 3.2 Frozen sensitivity matrix and reference envelopes

The focal held-out design used 12 prospectively frozen plant taxa. Each taxon retained all three accessible-area radii (150, 300 and 500 km) and all eight procedures, yielding 24 repeated diagnostics per taxon. These cells were sensitivity diagnostics, not 288 independent biological replicates.

Source-discordance envelopes were calibrated independently from the held-out panel. Each of the 24 procedure-by-area cells required at least 30 adequate successor taxa; all cells met this rule with 34-47 adequate taxa. The nearest-rank q95 value was frozen before held-out paired discordance was opened. We use q95 only as an empirical source-discordance envelope, not as a nominal 95% predictive interval or alpha=0.05 test.

A held-out cell was evaluable only when both independently fitted answers passed their predeclared adequacy rules. Otherwise it remained unresolved. Discordance was `1 - Schoener D` on the common comparison frame.

### 3.3 Held-out result

The 12 taxa generated 288 prespecified diagnostics. Both source-specific answers were adequate in 283 cells; five remained unresolved. No held-out taxon contained an envelope exceedance among its evaluable cells, giving a taxon-level result of **0 of 12 taxa with an exceedance**.

The closest evaluable condition occurred for *Nothofagus betuloides* at 150 km under the predictive-forward, C=1, degree-2 procedure. Observed discordance was 0.38625 against a frozen envelope of 0.39085, a margin of 0.00460 and an observed-to-envelope ratio of 0.988. Thus the result was not obtained only because all envelopes were far from the held-out observations.

This result supports same-target cross-source reproducibility **conditional on answer adequacy**. It does not establish universal source invariance, identical observation processes or a general tolerance transferable to other biological relations.

### 3.4 Post-freeze GBIF source-completeness sensitivity

The original frozen experiment used 9,705 Parquet objects from the nominal 2026-08-01 GBIF source export. A later source-integrity audit identified **510 additional objects** belonging to that same snapshot, bringing the complete input to **10,215 objects**. Because the restored records could alter fitted answers in both the 47-taxon reference panel and the 12-taxon held-out panel, the original result could not automatically be treated as source-completeness robust.

We conducted a separate **retrospective sensitivity analysis**, maintaining all 59 original taxonomic concepts, the original 12 spatial-block centres per taxon, the three frozen 2,000-row comparison frames, 19 predictors, eight procedures, three accessible-area radii, and the original prediction-adequacy rule. All **2,832 source-specific fit cells** (2,256 reference and 576 held-out) completed without unresolved model fits. Before viewing restored held-out comparisons, all 24 reference settings independently passed the minimum of 30 adequate calibration taxa (35–47 per cell). Recalibration with the unchanged nearest-rank q95 rule opened **1,033 of 1,128** eligible reference taxon-by-setting pairs; the others remained closed under the original adequacy rule.

Under these separately recalibrated thresholds, **285 of 288 held-out cells were evaluable**, and none of the 12 taxa had an envelope exceedance. This repeats the taxon-level **0/12** non-exceedance pattern under the repaired upstream input. However, evaluability was not identical: **282 of the original 283 evaluable cells remained evaluable**, one became unresolved, and three previously unresolved cells became evaluable. Thus, the pre-opening source-repair audit's stricter criterion requiring retention of *all* 283 original evaluable cells **was not met**. The resulting terminal state is *zero exceedances with reduced original-cell coverage*, not full robustness.

The lost cell was *Nothofagus antarctica* at 150 km under `niche_forward|logit_l2_C0.1_degree1`. Its preserved-specimen mean outer-fold presence rank increased (0.6045 to 0.6105), but its standard error also increased (0.0975 to 0.1160), lowering mean minus SEM from 0.5070 to 0.4945 across the unchanged 0.50 adequacy boundary. The three newly evaluable cells were explained by corresponding source-specific adequacy-bound crossings. Across the **282 comparisons evaluable in both source versions**, median repaired-minus-original discordance `1−D` was **+0.00070** (range −0.09646 to +0.17331); the median change across 24 q95 thresholds was **+0.00027** (range −0.07180 to +0.04700). These medians do not imply universally small cell-wise changes. The restored panel's closest observed discordance remained below q95 by **0.01691**, for *Eucalyptus globulus* at 500 km.

This analysis does **not** constitute a new independent biological replication: it refits the same frozen taxon panel after repairing input provenance. The original signed 283/288, 0/12 endpoint is retained unchanged, and the restored-source result is reported as a distinct coverage-limited sensitivity finding. No adequacy threshold, taxon, procedure, accessible-area radius or reference rule was changed to recover the lost cell. The taxon-level source-version maxima and exact 288-key eligibility transitions are displayed in Fig. 2.

## 4. Exact consequence of deleting the unresolved state

Consider a hard endpoint in which `F=true` denotes a biologically compatible required function and `F=false` a true violation. Let

- `a1 = P(valid key | F=true)`;
- `a0 = P(valid key | F=false)`;
- `q` = sensitivity on a valid key when `F=true`;
- `sp` = specificity on a valid key when `F=false`.

Under an identifiability-gated rule, invalid keys remain unresolved. Under a zero-collapsing ablation, invalid keys are forced into the biological negative state.

For compatible keys,

`FPR_zero = 1 - a1 q`

and

`FPR_gated = a1(1-q)`.

Therefore

`FPR_zero - FPR_gated = 1-a1`.

For true violations,

`TPR_zero = 1 - a0(1-sp)`

and

`TPR_gated = a0 sp`.

Therefore

`TPR_zero - TPR_gated = 1-a0`.

These are exact algebraic identities for rates **per original latent biological class**, with unresolved keys contributing no gated violation call (not treated as known biological negatives). The rates are not conditional error rates among classified keys. When validity is class-independent (`a1=a0=a`), both increments equal `1-a`. The apparent gain in sensitivity obtained by zero collapsing is therefore purchased by a precisely quantified increase in unsupported calls; with state-dependent validity, the two increments are indexed by their own invalid-state masses.

A representative frozen audit with `a1=0.70`, `a0=0.90`, `q=0.95` and `sp=0.99` gives false-violation rate 0.035 under gating and 0.335 under zero collapsing, while apparent true-violation sensitivity rises from 0.891 to 0.991 (Fig. 3).

## 5. Qualification is not endpoint reliability

Observation-process qualification answers whether a negative state is admissible. It does not determine whether a called violation is likely to be true.

Let `pi = P(F=false)` be the **unconditional prevalence** of true biological violations across all candidate keys. Because only valid keys may produce gated violation calls, the unconditional probability of a false call is `(1-pi)a1(1-q)` and that of a true call is `pi a0 sp`. Among *issued qualified violation calls*, the false-discovery fraction is therefore

`FDF = (1-pi)a1(1-q) / [(1-pi)a1(1-q) + pi a0 sp]`,

provided the denominator is positive; when no qualified violation calls can occur, FDF is undefined, not zero. **Validity cancels only if `a1=a0>0`.** Equivalently, the shorter expression `(1-pi_valid)(1-q) / [(1-pi_valid)(1-q) + pi_valid sp]` holds if `pi_valid=P(F=false | valid key)` is explicitly the violation prevalence *among valid keys*. In general `pi_valid = pi a0 / [(1-pi)a1 + pi a0]` (when that denominator is positive); selection on validity can change this prevalence.

With equal positive valid-key fractions, `pi=0.10`, `q=0.80`, `sp=0.99` gives `FDF=0.645` as in the original illustrative case. For **unequal** fractions, keeping the same unconditional `pi`, `q` and `sp`, `a1=0.70, a0=0.90` gives `FDF=0.586`, whereas `a1=0.90, a0=0.70` gives `FDF=0.700`. These are exact illustrative calculations, not estimated ecological frequencies. A measurement gate is necessary for admissible negative inference but cannot by itself guarantee reliable endpoint attribution; both the base rate and class-dependent observability matter (Fig. 4).

## 6. Discussion

The two contributions address opposite sides of the same inferential problem. The historical held-out experiment shows that preserving adequacy gates and unresolved states does **not** merely prevent conclusions. When the relevant answers exist and the comparison rule is frozen prospectively, an empirical endpoint can close positively on fresh taxa: none of the 12 held-out taxa exceeded its original reference envelope among evaluable cells. The later source-repair audit again found no exceedances under fully recalibrated reference thresholds, but correctly kept one now-inadequate original cell unresolved. The distinction between taxon-level non-exceedance and complete retention of cell-level evaluability is itself central to the proposed endpoint logic.

The exact decomposition explains why the unresolved state is not optional bookkeeping. Converting invalid keys into biological zeros always contributes an error term equal to the invalid-state mass for the relevant latent class. The operation can make a procedure look more decisive because it simultaneously increases apparent sensitivity and unsupported negative calls.

There is a further selection consequence even after inadmissible keys have been rejected. If valid-key probabilities differ between compatible and violating biological states (`a1≠a0`), qualification changes the prevalence composition of the keys on which a violation can be called. The equal-validity FDF expression therefore cannot be generalized without specifying whether prevalence refers to all keys or to valid keys alone. Two hypothetical observation regimes with identical conditional `q` and `sp` can have different fractions of false qualified violation calls solely because their state-dependent validity differs. This is an analytic implication, **not** a field-estimated biological effect.

This suggests a general design principle for ecological synthesis: **separate answer construction from endpoint authorization**. Better upstream models can improve ecological answers, but the joint claim still requires a declared relation and an observation state capable of supporting or contradicting it. The relation endpoint therefore complements, rather than replaces, occupancy models, data fusion, JSDMs, model-adequacy analysis and preregistration.

The empirical result should be interpreted narrowly. The independent biological replication is 12 taxa, not 283 cells. The original five unresolved cells were not treated as biological failures; likewise, the repaired-source panel's three unresolved cells must not be silently replaced by its three newly adequate comparisons. Although both versions produced 0/12 taxa with an envelope exceedance, the full original-283-cell retention condition failed and individual source-paired discordance or q95 values sometimes shifted appreciably. The historical experiment and retrospective data-repair analysis are not independent biological replications. Empirical q95 envelopes are not nominal prediction intervals. The exact invalid-state identities are structural results, not estimates of how often missingness or observation failure occurs in nature.

The broader value of the framework is asymmetrical error control. An endpoint may remain unresolved when the evidence required for a claim is absent, but it cannot manufacture the missing state. Conversely, when the required answers are adequate and a prospective relation is satisfied, the framework permits a positive conclusion. In this sense, evidence-bounded inference is not a rule for saying less; it is a rule for saying exactly what the available evidence authorizes.

## 7. Open research statement

The source code, frozen contracts, held-out endpoint receipts and mathematical audits are maintained in the public 284b repository. The original Level-A empirical endpoint is recorded in `results/product_b_same_target_core19_v0_4_heldout_final_receipt.json` and `results/reviewer2_level_a_structure_audit_v0_1.json`. The separately signed retrospective source-completeness outcome, all 288 comparison cells, independently recalibrated 24 q95 thresholds, 282-cell matched comparison and four outer-fold adequacy flips are retained in `results/gbif_repaired_heldout12_sensitivity_v1.json`, `results/gbif_repaired_heldout12_sensitivity_cells_v1.csv`, `results/gbif_repaired_reference47_q95_ceiling_v1.csv`, `results/gbif_repaired_heldout12_postterminal_score_drift_v1.json`, and `results/gbif_repaired_heldout12_postterminal_cv_switch_v1.json`. The decision and caveat are documented in `docs/GBIF_REPAIRED_LEVEL_A_TERMINAL_DECISION_20261122.md`. The exact invalid-state result is reproduced by `scripts/relation_endpoint_contract.py`, `scripts/audit_state_dependent_invalidity_v0_2.py` and the accompanying frozen result files. The class-dependent FDF definition, special-case derivation, exact examples and zero-call boundary are independently recorded in `docs/M1_CLASS_DEPENDENT_FDF_AUDIT_20261122.md` and guarded by `tests/test_m1_fdf_validity_asymmetry_20261122.py`. A permanent archival DOI should be inserted before submission.

## References

Blanchet, F.G., Cazelles, K. & Gravel, D. (2020). Co-occurrence is not evidence of ecological interactions. *Ecol. Lett.*, 23, 1050–1063.

Chadwick, F.J., Haydon, D.T., Husmeier, D., Ovaskainen, O. & Matthiopoulos, J. (2024). LIES of omission: complex observation processes in ecology. *Trends Ecol. Evol.*, 39, 368–380.

Erickson, K.D. & Smith, A.B. (2021). Accounting for imperfect detection in data from museums and herbaria when modeling species distributions: combining and contrasting data-level versus model-level bias correction. *Ecography*, 44, 1341–1352.

Gaier, A.G. & Resasco, J. (2023). Does adding community science observations to museum records improve distribution modeling of a rare endemic plant? *Ecosphere*, 14, e4419.

Getz, W.M., Marshall, C.R., Carlson, C.J., Giuggioli, L., Ryan, S.J., Romañach, S.S. et al. (2018). Making ecological models adequate. *Ecol. Lett.*, 21, 153–166.

Guillera-Arroita, G. (2017). Modelling of species distributions, range dynamics and communities under imperfect detection: advances, challenges and opportunities. *Ecography*, 40, 281–295.

Matutini, F., Baudry, J., Pain, G., Sineau, M. & Pithon, J. (2021). How citizen science could improve species distribution models and their independent assessment. *Ecol. Evol.*, 11, 3028–3039.

Pacifici, K., Reich, B.J., Miller, D.A.W., Gardner, B., Stauffer, G.E., Singh, S. et al. (2017). Integrating multiple data sources in species distribution modeling: a framework for data fusion. *Ecology*, 98, 840–850.

Wilkinson, D.P., Golding, N., Guillera-Arroita, G., Tingley, R. & McCarthy, M.A. (2021). Defining and evaluating predictions of joint species distribution models. *Methods Ecol. Evol.*, 12, 394–404.
