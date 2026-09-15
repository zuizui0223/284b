# Paper 1 claim-evidence ledger v0.5 — v0.9 narrative sync

**Status:** noncanonical full-manuscript claim ledger. It reorganizes the reviewer-hardened v0.4 boundary around the v0.9 manuscript argument. No focal Level-C values are opened; empirical ledger remains **1**.

| ID | Manuscript claim | Evidence status | Canonical repository evidence | Allowed wording |
|---|---|---|---|---|
| M0 | Accurate role-specific marginal answers do not by themselves identify a directional biological relation. | Classical nonempirical method support | `manuscript/RELATION_LAYER_SEPARATION_V0_1.md`; `results/relation_layer_separation_v0_1.json` | For `v=P(E=1,F=0)`, classical Fréchet–Hoeffding bounds allow the same exact marginals `p_E=p_F=0.5` to support both `v=0` and `v=0.5`. This is a separation argument, not new probability theory. |
| M1 | A relation endpoint can be frozen as an executable, prospectively inspectable object. | Method implementation | `scripts/relation_endpoint_contract.py`; `scripts/freeze_relation_endpoint_contract.py`; committed contract receipt/examples | Freeze relation, key space, adapters, adequacy gates, opening rule and its immutable/versioned reference; canonical JSON + SHA-256 fingerprint makes later contract drift inspectable. |
| E1 | Same-target independently reconstructed ecological answers can satisfy a prospectively calibrated cross-source coherence relation on fresh held-out taxa when both answers pass adequacy. | **Empirical, closed** | `docs/product_b_same_target_core19_empirical_result.md`; `results/product_b_same_target_core19_v0_4_heldout_final_receipt.json`; `results/reviewer2_level_a_structure_audit_v0_1.json` | Independent biological replication is **12 held-out taxa**. Their prespecified matrices yielded 283 evaluable diagnostics and five unresolved cells; **0/12 taxa** contained an empirical-envelope exceedance among evaluable cells. |
| E2 | The Level-A nearest-rank q95 reference is a prospectively frozen empirical source-discordance envelope. | Design/interpretation boundary | Level-A reference receipt and reviewer-2 structure audit | Call it an empirical source-discordance envelope; do not call it nominal 95% predictive coverage or an alpha=0.05 test. |
| M2 | Same-target Level-A calibration cannot be exported as a universal cross-role tolerance. | Conceptual/design boundary | `docs/product_b_paired_answer_check_relation_ladder.md`; relation-endpoint contract | Cross-role comparisons require their own biological relation, common key and relation-specific calibration. |
| M3 | Directional dependency should be expressed at a biological event key and function level rather than inferred from raw distribution equality/containment. | Conceptual/methodological | Level-C event/function design; `docs/product_b_level_c_functional_pool_bridge.md`; Figure-3 logic | Different roles may differ upstream; compare them only after relation-space adaptation. Provider occurrence is not automatically the required function. |
| M4 | For a qualified hard endpoint, deleting the unresolved state has exact class-specific operating-characteristic costs under state-dependent validity. | Exact analytic/synthetic method result | `results/pre_field_state_dependent_invalidity_v0_2.json`; `scripts/relation_endpoint_contract.py` | With `a1=P(valid|F=true)` and `a0=P(valid|F=false)`, `FPR_zero-FPR_gated=1-a1` and `TPR_zero-TPR_gated=1-a0`; `a1=a0=a` gives the equal-validity `1-a` corollary. |
| M5 | Zero collapsing is an ablation of the unresolved-state guard, not a competing observation model. | Method interpretation | endpoint engine + generalized audit | Detection-aware models may supply an admissible negative if their observation design identifies it; the ablation isolates the cost of coercing invalid/nonidentified states into `F=false`. |
| Q1 | Fresh cross-role systems can satisfy relation/event/function architecture while remaining unqualified for a hard endpoint. | Prospective qualification result; **not focal biology** | `results/product_b_level_c_source_qualification_v3.json` | Cremastra and Belonocnema reached separated R/X/Y architectures but stopped before hard opening because functional absence was not independently calibrated. |
| Q2 | Existing identified supplementary/raw sources do not reconstruct the missing candidate-specific negative-state calibration for either retained system. | Closed source-audit result; **not biological endpoint** | `results/product_b_level_c_candidate_specific_calibration_audit_v5.json`; `results/product_b_level_c_raw_calibration_reconstruction_v6.json` | The next admissible information is prospective candidate-specific calibration or direct aggregate-function measurement, not reinterpretation of current non-detections. |
| Q3 | Observation-process qualification is an endpoint-opening condition, not final false-discovery control. | Exact analytic interpretation | original benchmark/base-rate calculation; v8/v8.1 design docs | A qualified negative may enter the endpoint, but final evidentiary reliability also depends on biological violation prevalence and separately frozen replication/aggregation rules. |
| P1 | The v8.1 confidence-bound repair was prospective and nonempirical. | Provenance/design | v8.1 docs/config/result/tests | v8 remains immutable history; v8.1 corrected the pre-data confidence-bound implementation without changing thresholds, candidate identities or minimum counts. Main text may relegate this detail to Supplement. |

## Prohibited manuscript inferences

1. `Level C confirmed dependency` or `Level C falsified dependency`.
2. `No record = no function`, or any conversion of missing/failed/unqualified observation into biological absence.
3. Treating 283 Level-A diagnostics as independent biological replication or as a binomial sample size.
4. Treating the five Level-A unresolved cells as failures.
5. Treating Level-A q95 as a nominal 95% predictive interval, alpha=0.05 test or general cross-role threshold.
6. Claiming process necessity, causality or mechanism knockout; the relevant intervention endpoints are unopened.
7. Claiming universal source invariance for specimen- and observation-based ecological models.
8. Claiming the Fréchet–Hoeffding bounds are new mathematics or that JSDMs cannot estimate joint statistical structure.
9. Claiming fingerprinting proves outcome blindness.
10. Claiming the relation-endpoint contract repairs upstream model misspecification.
11. Treating zero collapsing as a state-of-the-art occupancy/detection competitor.
12. Treating the equal `1-a` identity as universal when validity can depend on latent functional state.
13. Claiming process qualification guarantees that any individual called violation is biologically true.
14. Any post hoc candidate replacement, threshold relaxation or outcome-dependent rescue in the frozen pre-field paper.

## Manuscript-facing priority

The v0.9 full manuscript should expose claims in this order:

1. **M0** — why the relation layer is necessary;
2. **M1** — the executable/fingerprintable contract;
3. **E1/E2** — the 12-taxon empirical anchor;
4. **M4/M5** — the exact cost of deleting unresolved;
5. **Q1/Q2** — two real-system stopping-rule demonstrations.

Level labels remain useful implementation/scoping vocabulary, but they are not the narrative spine of Paper 1.

## Submission audit rule

Before promotion of the v0.9 candidate, every numerical or biological claim in the abstract, Results, Discussion, captions and Table 1 must map to a row above or to an explicitly nonempirical antecedent statement. Any new focal Level-C biological result requires a new ledger version and a separately authorized opening event.
