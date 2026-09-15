# Table 1. Claim/evidence matrix for the relation-endpoint Method

**Status:** full-manuscript v0.9 display candidate. This table reorganizes existing evidence; it opens no new empirical endpoint.

| Paper claim | Evidence type | Completed evidence | What the paper may say | What the paper must not say |
|---|---|---|---|---|
| **A relation layer is needed even when upstream answers are accurate.** | Classical nonempirical separation | For `v=P(E=1,F=0)`, Fréchet–Hoeffding bounds give `max(0,p_E-p_F) <= v <= min(p_E,1-p_F)`. At exact `p_E=p_F=0.5`, the same marginals admit `v=0` and `v=0.5`. | Accurate marginals alone do not identify a directional biological relation; the relation semantics must be declared separately. | The coupling bounds are new mathematics; JSDMs cannot estimate joint structure. |
| **The relation endpoint can be frozen as an executable, auditable object.** | Method implementation | Five-part contract stores relation, key space, role-specific adapters, adequacy gates and opening rule; `opening_rule_reference` is part of deterministic canonical JSON and SHA-256 fingerprinting. | Endpoint drift can be made inspectable before focal opening. | Hashing proves investigators were outcome-blind; the contract repairs misspecified upstream models. |
| **A prospectively declared same-target relation can close on fresh data.** | Empirical anchor | 12 independent held-out taxa; 288 prespecified repeated diagnostics; 283 evaluable; five unresolved; **0/12 taxa with an envelope exceedance among evaluable cells**. | Same-target cross-source reproducibility was supported conditional on answer adequacy and the frozen empirical source-discordance envelopes. | 283 cells are independent replicates; q95 is a nominal 95% predictive interval or universal cross-role threshold; five unresolved cells are failures. |
| **Preserving `unresolved` prevents an exact class-specific error increment.** | Exact analytic/synthetic method result | With `a1=P(valid|F=true)` and `a0=P(valid|F=false)`, `FPR_zero-FPR_gated=1-a1` and `TPR_zero-TPR_gated=1-a0`; `1-a` is the equal-validity special case. | Coercing invalid observations into biological negatives creates quantifiable false-violation inflation and apparent sensitivity gain. | Zero collapsing is a modern occupancy-model competitor; the common `1-a` identity is universal under state-dependent validity. |
| **The method can refuse a tempting hard biological conclusion for a measurable reason.** | Prospective real-system qualification | Cremastra and Belonocnema each reached separated relation/event/function architectures, but candidate-specific functional-absence calibration was unavailable and could not be reconstructed from identified existing sources. | Both systems reached the same negative-state measurement boundary; the next admissible information is new calibration/direct functional measurement. | Either dependency is confirmed or falsified; camera non-detection or unrecorded budbreak is functional absence; unavailable data are biological negatives. |

## Boundary carried into the v0.9 full-manuscript candidate

- **Sole completed empirical endpoint:** Level A same-target cross-source relation on 12 held-out taxa.
- **Level B:** relation class only in this paper; fresh empirical endpoint unopened.
- **Level C:** architecture/openability evidence only; focal hard/soft/process-knockout outcomes remain sealed.
- **Empirical ledger:** **1**.
- **Final endpoint reliability:** observation-process qualification is necessary for a hard negative to enter the endpoint, but base rates, replication and aggregation require separately frozen rules.
