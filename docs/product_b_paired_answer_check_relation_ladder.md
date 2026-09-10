# Product-B paired answer-check relation ladder

## Central question

Product-B asks:

> When two ecological answers are obtained independently, but external biology says they should cohere in a declared way, do they actually agree closely enough under the *appropriate relation* to trust the combined interpretation?

The relation, biological event, relation-space adapter, comparison metric, and any soft threshold are frozen before focal outcomes are opened.

A crucial distinction is now explicit:

- **same-target replication** may deliberately use the same estimator/procedure and the same accessible-area frame as an experimental control;
- **cross-species or cross-role checks must not require one universal estimator, one universal M, or one raw output scale.**

For cross-role checks, each answer is constructed with a role-appropriate estimator first, then both answers are projected onto a common **relation space** where the biological dependency is meaningful.

## Relation ladder

### Level A — same target, independent observation source

Examples: the same taxon modeled independently from preserved-specimen records and human-observation records, or from two genuinely independent observation systems.

Expected relation: broad environmental support should be concordant at a declared spatial/temporal scale, but exact identity is not required because detectability and sampling bias differ.

Default interpretation: **soft cross-check**. Excess divergence is `attention_required`, not a biological violation.

This level is intentionally a controlled reconstruction experiment. The core19 v0.4 endpoint held fixed:

- the biological target;
- the ecological estimand;
- the estimator/procedure identity;
- M/background semantics within a procedure × M cell;
- the comparison rows;
- the active `bio1`–`bio19` predictor universe;
- the adequacy and successor-reference rules.

Only the observation source changed. This is where a same-estimator requirement is scientifically justified.

**Empirical status:** Level A now has a prospectively frozen fresh held-out result. Successor calibration froze 24/24 procedure-by-M nearest-rank q95 reference cells. In the held-out 12-taxon matrix, 283/288 paired cells were eligible to open and **283/283 remained within the frozen successor ceiling**, with zero `attention_required` cells. Five cells stayed closed because one source-specific answer failed its predeclared adequacy gate. Process knockout remained closed.

Canonical endpoint:

`same_target_cross_source_reproducibility_heldout12_core19_v0_4`

Canonical interpretation: **same-target cross-source answer reproducibility conditional on answer adequacy**.

This is the first empirical closure of the cross-validity layer in the ladder. It is not yet a cross-role or biological-process result.

### Level B — expected biological concordance

Examples: independently estimated ecological responses that external experimental or natural-history evidence predicts should rank a declared biological opportunity similarly.

The upstream estimators may differ when the roles differ. A relation-space adapter must state what common event/units are being compared.

Default interpretation: **soft cross-check** with relation-specific calibration.

Current status: **unopened as a fresh empirical relation endpoint in this ladder**. Level-A success cannot serve as its tolerance by default. A Level-B test needs its own prospectively frozen reference design because two different biological roles or estimands can have legitimate discordance that is absent from the controlled same-target experiment.

### Level C — directional dependency

Example: `Y requires X` for reproduction or persistence.

The hard or soft statement applies to a declared **dependency event**, not automatically to raw occurrence or raw suitability surfaces.

For a plant requiring an obligate pollinator, adult plant occupancy need not be contained within current pollinator occupancy because plants can persist after local pollinator loss. A stronger hard candidate is instead something such as:

`pollinator-dependent successful reproduction at plant site × flowering window requires pollinator visitation/reachability at that same opportunity`.

Plant and pollinator answers may therefore use different estimators and different accessible areas. They are compared only after projection to the same site/time interaction-opportunity keys.

Interpretation: may be a **hard invariant** when dependency, event and scale are genuinely mandatory; otherwise it is prospectively a soft directional cross-check.

Current status: the relation form is defined, but the first fresh Level-C empirical endpoint must still be prospectively frozen. Level-A reproducibility establishes that the independent-answer machinery can close empirically; it does not establish the dependency itself.

### Level D — mutual dependency

Example: `X requires Y` and `Y requires X`, but possibly for different role-specific events.

Mutuality does **not** imply that X and Y should have identical raw distribution surfaces. Each direction gets its own biologically meaningful event/adapter. A complete admissible failure of either mandatory direction can falsify mutual compatibility under the frozen contract.

### Level E — life-stage coupling

Examples: larval habitat versus adult breeding support, host-resource stage versus dispersing adult stage, or other stages whose movement and persistence processes differ.

Different stages may require different model classes, M definitions and temporal grains. Hard/soft status is declared from external biology, then answers are projected to the stage-transition relation space.

## Relation-space principle

Cross-role comparability is created **after** answer construction:

`role-specific estimator A -> answer A`

`role-specific estimator B -> answer B`

`answer A + answer B -> frozen relation-space adapter -> biological cross-check`

The common relation space can be, for example:

- plant site × flowering window;
- breeding patch × reproductive season;
- host patch × dispersal generation;
- larval site × transition interval.

The relation-space keys, biological event and both projections must be frozen before the focal comparison is opened.

Level A did not require a nontrivial cross-role adapter because both independent answers referred to the same target, estimand and matched comparison rows. Levels B–E do require explicit adaptation and therefore represent a real scientific step beyond the completed Level-A result.

## What must not be forced across roles

Unless external biology itself justifies it, cross-role checks must not require:

- the same estimator family;
- the same predictor universe;
- the same accessible area `M`;
- the same spatial mobility model;
- the same observation model;
- equality of raw suitability/probability values.

This follows the same separation already used elsewhere in the research program: EOG separates local viability, reachability, persistence and observation support; SDMR explicitly refuses a single universal M and treats transfer across taxa/life forms/dispersal contexts as something to test rather than assume.

## One common language: discordance — only after adaptation

Soft relation metrics are converted to non-negative discordance where smaller means more coherent, but only after the two answers are on a valid common relation space.

Examples:

- directional containment `C` -> `1 - C`;
- reciprocal containment -> worst-direction discordance;
- same-target Schoener's D -> `1 - D`;
- relation-specific rank or opportunity-profile discordance.

These do **not** share one universal threshold.

## Calibration boundaries

The same-target independent-source panel estimates reconstruction disagreement when the **target, estimand, estimator and M/background are controlled** and only the observation source changes.

The completed core19 v0.4 endpoint gives this calibration an empirical held-out check: all 283 opened fresh cells remained within the successor-derived q95 ceiling. The closest opened cell was *Nothofagus betuloides*, M=150 km, `predictive_forward|logit_l2_C1_degree2`, with discordance `0.3862496` versus a frozen ceiling of `0.3908492`.

Therefore the q95 ceiling is empirically useful for the Level-A same-target calibration problem. It is **not automatically a tolerance for plant-versus-pollinator, host-versus-dependent, life-stage, or movement-versus-persistence comparisons**.

Cross-role soft checks require their own reference design, such as prospectively matched non-obligate controls, shuffled partners, or another relation-specific external calibration. Hard obligacy uses the dedicated biological invariant rather than importing the same-target q95.

The same-target result now does two things: it quantifies one source of reconstruction instability and demonstrates that a prospectively frozen independent-answer cross-check can produce a clean fresh terminal result. It still does not define how much disagreement is biologically acceptable between different estimands.

## Process intervention extension

Process intervention is also role-specific. Removing a plant environmental process and removing a pollinator movement/accessibility process are not required to be the same intervention.

The general question becomes:

> Which frozen process intervention in either role makes a previously coherent biological relation cease to hold after both answers are re-projected to the same relation space?

No process knockout may change the baseline estimator, adapter, relation event or comparison keys after the focal baseline has been opened.

The completed Level-A endpoint intentionally stopped before this step. Its empirical conclusion is cross-validity, not necessity. The next process-level claim requires a separately frozen intervention after a valid baseline relation has been established.