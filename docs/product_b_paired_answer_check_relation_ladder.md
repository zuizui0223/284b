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

This level is intentionally a controlled reconstruction experiment. The current calibration therefore holds fixed:

- the biological target;
- the ecological estimand;
- the estimator/procedure identity;
- M/background semantics within a procedure × M cell;
- the comparison rows.

Only the observation source changes. This is where a same-estimator requirement is scientifically justified.

### Level B — expected biological concordance

Examples: independently estimated ecological responses that external experimental or natural-history evidence predicts should rank a declared biological opportunity similarly.

The upstream estimators may differ when the roles differ. A relation-space adapter must state what common event/units are being compared.

Default interpretation: **soft cross-check** with relation-specific calibration.

### Level C — directional dependency

Example: `Y requires X` for reproduction or persistence.

The hard or soft statement applies to a declared **dependency event**, not automatically to raw occurrence or raw suitability surfaces.

For a plant requiring an obligate pollinator, adult plant occupancy need not be contained within current pollinator occupancy because plants can persist after local pollinator loss. A stronger hard candidate is instead something such as:

`pollinator-dependent successful reproduction at plant site × flowering window requires pollinator visitation/reachability at that same opportunity`.

Plant and pollinator answers may therefore use different estimators and different accessible areas. They are compared only after projection to the same site/time interaction-opportunity keys.

Interpretation: may be a **hard invariant** when dependency, event and scale are genuinely mandatory; otherwise it is prospectively a soft directional cross-check.

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

Therefore its q95 ceiling is valid for that same-target calibration problem. It is **not automatically a tolerance for plant-versus-pollinator, host-versus-dependent, life-stage, or movement-versus-persistence comparisons**.

Cross-role soft checks require their own reference design, such as prospectively matched non-obligate controls, shuffled partners, or another relation-specific external calibration. Hard obligacy uses the dedicated biological invariant rather than importing the same-target q95.

The same-target result remains useful diagnostically: it quantifies one source of reconstruction instability. It does not define how much disagreement is biologically acceptable between different estimands.

## Process intervention extension

Process intervention is also role-specific. Removing a plant environmental process and removing a pollinator movement/accessibility process are not required to be the same intervention.

The general question becomes:

> Which frozen process intervention in either role makes a previously coherent biological relation cease to hold after both answers are re-projected to the same relation space?

No process knockout may change the baseline estimator, adapter, relation event or comparison keys after the focal baseline has been opened.
