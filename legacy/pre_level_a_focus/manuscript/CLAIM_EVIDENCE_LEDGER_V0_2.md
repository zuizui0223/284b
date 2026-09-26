# Pre-field flagship claim-evidence ledger v0.3

All empirical biological claims remain bounded to repository state `bdc81d0`. Later synthetic benchmarks and v8.1 pre-data implementation/design audits are method evidence only and read no focal Level-C values.

| ID | Manuscript claim | Evidence status | Canonical repository evidence | Allowed wording |
|---|---|---|---|---|
| C1 | Same-target independently reconstructed ecological answers can satisfy a prospectively calibrated cross-source coherence relation on fresh held-out taxa when both answers pass adequacy. | Empirical, closed | `docs/product_b_same_target_core19_empirical_result.md`; `results/product_b_same_target_core19_v0_4_heldout_final_receipt.json` | 283/283 opened held-out cells were within frozen successor ceilings; 5 cells remained closed at adequacy. |
| C2 | Level-A same-target calibration does not provide a universal tolerance for cross-role comparisons. | Design/conceptual boundary | `docs/product_b_paired_answer_check_relation_ladder.md` | Cross-role tolerances require relation-specific calibration. |
| C3 | Cross-role biological dependency should be expressed at a frozen biological event key rather than inferred from raw equality/containment of occurrence or suitability surfaces. | Conceptual/methodological | `docs/product_b_paired_answer_check_relation_ladder.md`; Level-C event/set/function design files | Role-specific answers may differ upstream and are compared only after relation-space adaptation. |
| C4 | Functional-pool semantics repair the single-named-provider exclusivity problem but do not by themselves create a confirmatory endpoint. | Prospectively documented design result | `docs/product_b_level_c_functional_pool_v2_hard_stop.md` | v2 moved the bottleneck from single-provider exclusivity to independent same-key measurement of the required function. |
| C5 | Fresh cross-role systems can satisfy relation/event/function source architecture while remaining unqualified for a hard endpoint. | Prospectively documented qualification result, not focal biology | `results/product_b_level_c_source_architecture_hard_stop_v3.json`; `results/product_b_level_c_source_qualification_v3.json` | Cremastra and Belonocnema reached separated R/X/Y architectures but stopped at unresolved hard functional absence. |
| C6 | Positive function observations do not license a negative functional state from non-detection without candidate-specific calibration. | Prospectively documented identifiability result | `results/product_b_level_c_absence_candidate_audit_v4.json`; `results/product_b_level_c_candidate_specific_calibration_audit_v5.json` | Existing observation processes did not validate zero/non-detection as `F(k)=false`. |
| C7 | Existing identified supplementary/raw sources do not reconstruct the missing candidate-specific absence calibration for the two retained systems. | Closed source-audit result, not biological endpoint | `results/product_b_level_c_raw_calibration_reconstruction_v6.json` | The next admissible information is new calibration measurement rather than reinterpretation of existing non-detections. |
| C8 | The Level-C pre-field workflow is operationally frozen, but no focal cross-role endpoint is open. | Current process state | v7-v8 receipts plus v8.1 pre-data repair | Field calibration remains unexecuted; empirical ledger remains 1. |
| C9 | Under a qualified observation process, collapsing invalid keys into zero adds exactly invalid-key mass `1-a` to both apparent violation sensitivity and false-violation probability. | Exact synthetic/mathematical method result | `scripts/run_pre_field_identifiability_benchmark.py`; `results/pre_field_identifiability_benchmark_summary_v0_1.json`; `manuscript/SYNTHETIC_BENCHMARK_RESULT_V0_1.md` | For calibration-passing scenarios, `FPR_zero - FPR_gated = 1-a` and `TPR_zero - TPR_gated = 1-a`; identities hold across the exact grid. |
| C10 | A process that fails the frozen sensitivity/specificity gate should not generate hard negative calls under the identifiability-gated rule. | Exact synthetic method result | same benchmark artifacts as C9 | Across all 4,428 calibration-failing grid points, gated hard-call mass is zero by the frozen decision rule. |
| C11 | The 0.80 sensitivity / 0.95 specificity calibration floor is an opening qualification, not a universal final single-key falsification standard. | Interpretation boundary | v8/v8.1 operational package; benchmark result | A later focal endpoint must separately freeze aggregation/replication and evidentiary rules before values are opened. |
| C12 | Passing the observation-process gate does not itself control the false-discovery fraction among called violations. | Exact analytic interpretation | representative benchmark scenarios; `manuscript/SYNTHETIC_BENCHMARK_RESULT_V0_1.md` | With true violation prevalence `pi`, sensitivity `q` and specificity `sp`, `FDF=(1-pi)(1-q)/[(1-pi)(1-q)+pi sp]`; e.g. `pi=0.10`, `q=0.80`, `sp=0.99` gives FDF≈0.645. This is a base-rate property, not a candidate-specific result. |
| C13 | The v8.1 exact-confidence repair is prospective and nonempirical. | Pre-data implementation repair | `docs/product_b_level_c_v8_1_exact_confidence_repair.md`; v8.1 config/result/tests | v8 remains immutable history; v8.1 changes the confidence-bound implementation only, before any calibration data were entered. |
| C14 | The frozen 30-positive / 60-negative calibration counts are feasibility minima rather than power guarantees. | Pre-data design audit | `docs/product_b_level_c_v8_1_operating_characteristics.md`; operating-characteristic result | Nominal pass probabilities may be low near threshold; no sample-size change is authorized by the audit. |

## Prohibited manuscript inferences

1. `Level C confirmed dependency` — forbidden.
2. `Level C falsified dependency` — forbidden.
3. `No record = no function` — forbidden unless future candidate-specific calibration and endpoint rules authorize the classification.
4. `Level-A q95 is a general cross-role threshold` — forbidden.
5. `Process X is necessary/causal` — forbidden; process knockout is unopened.
6. `All specimen- and observation-based ecological models are source-invariant` — forbidden.
7. `Five unopened Level-A cells were failures` — forbidden; they are unresolved adequacy cases.
8. Any candidate replacement or post hoc threshold rescue — forbidden for the frozen pre-field paper.
9. The equal-weight synthetic grid estimates how common observation regimes are in nature — forbidden; it is a stress-test grid.
10. Synthetic benchmark outputs estimate Cremastra or Belonocnema detection performance — forbidden.
11. A v8/v8.1 calibration pass would itself increment the empirical ledger or prove/falsify a dependency — forbidden.
12. The v8.1 operating-characteristic audit authorizes outcome-dependent sample-size extension — forbidden.
13. Observation-process qualification guarantees that an individual called violation is true — forbidden; final evidentiary reliability also depends on base rate and the separately frozen endpoint rule.
14. 284b invented imperfect detection, external validation, preregistration or ecological model adequacy — forbidden; these are established antecedents.

## Notation rule

For manuscript-facing benchmark notation:

- `a` = valid-key fraction;
- `pi` = biological violation prevalence;
- `q` = key-level sensitivity;
- `sp` = specificity.

Do not use `v` for both observation validity and violation prevalence.

## Submission audit rule

Before submission, every abstract/result/discussion sentence containing a numerical or biological claim must map to one row above. New empirical Level-C data, if collected later, require a new ledger version rather than silent insertion into this pre-field manuscript state.
