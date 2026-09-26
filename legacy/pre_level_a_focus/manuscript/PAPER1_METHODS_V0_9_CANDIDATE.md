# Paper 1 Methods candidate v0.9

**Status:** noncanonical manuscript prose for integration after editorial review. No focal Level-C values are opened and the empirical ledger remains unchanged.

## Methods

### Relation-endpoint contract

We treat the relation joining independently generated ecological answers as an explicit inferential object rather than an implicit consequence of upstream model choice. Before focal comparison values are viewed, a relation-endpoint contract freezes five scientific components: (1) the biological relation, (2) the biological event or key space at which it applies, (3) role-specific adapters mapping each answer into that space, (4) adequacy gates determining whether each answer exists for a key, and (5) an opening rule defining which relation states are admissible. The implementation also stores an `opening_rule_reference` identifying the frozen calibration artifact or negative-state qualification protocol that instantiates the opening rule.

The reference engine (`scripts/relation_endpoint_contract.py`) validates a complete contract, serializes it to deterministic canonical JSON and returns a SHA-256 fingerprint. Unknown or missing fields are rejected. Fingerprinting is used only as an audit device: it permits later comparison between the endpoint specification frozen before opening and the object actually used at evaluation, but does not itself prove outcome blindness.

The current implementation directly evaluates calibrated soft relations (same-target Level A and relation-specific Level B checks) and directional hard implication (Level C). Soft keys return `consistent`, `attention_required` or `unresolved`. Directional hard keys return `hard_violation_authorized`, `no_observed_violation`, `noninformative_for_implication` or `unresolved`. Mutual dependency and life-stage coupling are composition-only in the present implementation and require separately frozen primitive contracts.

### Why answer accuracy does not identify the relation

For a directional dependency `E -> F`, let `p_E=P(E=1)` and `p_F=P(F=1)` be exact role-specific marginal probabilities and let `v=P(E=1,F=0)` be the hard-violation probability. Classical Frechet-Hoeffding coupling bounds imply

`max(0,p_E-p_F) <= v <= min(p_E,1-p_F)`.

At `p_E=p_F=0.5`, the same exact marginals admit both `v=0` and `v=0.5`. We use this established result only as a separation argument: marginal answer accuracy does not determine the downstream hard relation. A joint model can estimate statistical coupling, but the ecological relation being tested and the event at which support or contradiction is defined must still be declared biologically.

### Controlled same-target empirical anchor

We evaluated whether a fully prespecified soft relation could close on fresh held-out taxa using independent preserved-specimen and human-observation reconstructions. Within each procedure-by-accessible-area cell, target identity, ecological estimand, `bio1-bio19` predictor universe, estimator/procedure identity, accessible-area semantics, a fixed 2,000-row comparison frame, adequacy logic and the successor-derived reference rule were held fixed.

The held-out outcomes were not used to choose taxa, procedures, accessible areas or rescue paths. A successor audit sealed 2,255 of 2,256 fit cells and retained the unresolved cell. Each reference cell required at least 30 prospectively adequate successor taxa; all 24 procedure-by-accessible-area cells satisfied this rule, with 34-47 distinct adequate successor taxa per cell. The nearest-rank q95 reference was frozen before held-out opening and is interpreted only as an empirical source-discordance envelope, not as a nominal 95% predictive interval or an alpha=0.05 test.

The independent biological units were 12 held-out taxa. Each taxon contributed a prespecified 3 accessible-area x 8 procedure matrix, for 288 repeated cell diagnostics. A cell was evaluable only when both source-specific answers passed predeclared adequacy. Discordance was `1 - Schoener D` and was compared with the corresponding frozen empirical envelope. Cells are repeated diagnostics nested within taxa and are not treated as 288 independent replications.

### Directional dependency and negative-state identifiability

For a hard relation we write `E(k) -> F(k)`, where `E(k)` is the dependent event and `F(k)` is the required biological function at opportunity key `k`. A hard contradiction requires an adequately positive event state and an adequately negative function state at the same key. When several providers can satisfy the requirement, `F` is defined at the aggregate function level rather than as occurrence of one named provider.

A detected function, calibrated functional absence, unresolved non-detection and observation failure/missingness are therefore distinct states. Only calibrated functional absence can supply `F(k)=false`. Under the frozen Level-C design, process qualification requires key-level sensitivity >=0.80, hard false-negative rate <=0.20 and specificity >=0.95, together with explicit quality-control and missingness rules. These thresholds qualify whether a negative state may enter an endpoint; they are not universal final evidentiary standards for a biological conclusion.

### Exact unresolved-state ablation

To isolate the decision consequence of deleting the unresolved state, we compared an identifiability-gated hard rule with a zero-collapsing ablation. The ablation deliberately treats invalid observation or valid non-detection as `F=false` when `E=true`; it is not presented as a competitor to occupancy, interaction or other detection-aware models.

Let `q` denote key-level sensitivity for a true function on a valid key and `sp` specificity for a true violation on a valid key. Allow observation validity to depend on latent function state:

`a1 = P(valid key | F=true)`

`a0 = P(valid key | F=false)`.

For biologically compatible keys,

`FPR_zero = 1 - a1 q`

and

`FPR_gated = a1(1-q)`,

so

`FPR_zero - FPR_gated = 1-a1`.

For true violations,

`TPR_zero = 1 - a0(1-sp)`

and

`TPR_gated = a0 sp`,

so

`TPR_zero - TPR_gated = 1-a0`.

The earlier common `1-a` identity is therefore the controlled special case `a1=a0=a`. The original 8,748-scenario grid evaluates this equal-validity case; a separate outcome-blind audit verifies the generalized state-dependent decomposition. When process calibration fails, the gated rule returns no hard negative calls.

Because process qualification is not equivalent to endpoint-level reliability, we also distinguish it from false-discovery control. For violation prevalence `pi`, the false-discovery fraction among called violations is

`FDF = (1-pi)(1-q) / [(1-pi)(1-q) + pi sp]`.

Thus final biological evidence requires separately frozen replication or aggregation rules even after the observation process qualifies.

### Prospective cross-role openability audit

We then tested whether real cross-role systems could satisfy the information requirements of a directional endpoint without opening their focal biological outcomes. Each candidate required three prospectively separated evidence channels: external evidence defining the biological relation (`R`), an independent dependent-event stream (`X`) and an independent required-function stream (`Y`). Independence was defined by observation generation rather than publication label.

Candidate discovery was finite and response-blind. Gates required a common biological key, direct role estimands, provenance separation and no post hoc redefinition. Unavailable sources, failed downloads, missing records and uncalibrated zeros were never permitted to count as biological absence. Two systems survived the architecture gates: `CREMV3-007` (*Cremastra appendiculata* var. *variabilis*) and `BELV3-012` (*Belonocnema treatae* / live-oak budbreak). Paper 1 uses them only to evaluate endpoint openability. Their focal hard invariant, soft cross-check and process-knockout outcomes remain sealed.