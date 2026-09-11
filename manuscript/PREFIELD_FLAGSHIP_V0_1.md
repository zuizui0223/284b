# When ecological answers can be combined: prospective cross-validity and the identifiability of biological absence

**Target:** Ecology Letters — Method  
**Stage:** pre-field manuscript v0.1  
**Frozen repository boundary:** `bdc81d0`  
**Main-text target:** <= 5,000 words  
**Display-item target:** <= 6

## Abstract

Ecologists increasingly combine answers reconstructed from different observation sources and biological roles, but reproducibility and biological dependency are not the same inferential problem. We develop a prospective framework that freezes the relation, comparison event, relation-space adapter, adequacy gates and calibration before focal outcomes are opened. In a same-target held-out test, 283/283 adequately observed cells reconstructed independently from specimen and human-observation records remained within prospectively calibrated source-discordance ceilings; five inadequate cells remained unresolved. We then stress-tested escalation to hard cross-role dependency. Two fresh systems achieved separated relation, dependent-event and required-function evidence streams but could not identify functional absence from non-detection, and existing raw sources did not repair the missing calibration. We derive a negative-state identifiability principle: hard ecological dependencies are falsifiable only when the negative required-function state is itself observable under a calibrated process. This separates cross-source reproducibility from cross-role biological inference.

## 1. Introduction

Ecological inference increasingly depends on combining answers that were not produced by the same observation process. Species distributions are reconstructed from museum specimens, opportunistic observations and sensors; interacting species are modelled from different data streams; host, pollinator and life-stage responses are estimated using distinct spatial grains, accessible areas and observation models. The attractive intuition is that independently reconstructed answers should agree when they describe the same ecology, and that biologically dependent roles should occupy compatible environmental or spatiotemporal opportunity. The dangerous step is treating those two statements as interchangeable.

Agreement has no scientific meaning until the expected relation has been specified. Two reconstructions of the same target can be compared as a controlled cross-source problem because the target and estimand can be held fixed. Two different biological roles cannot generally be required to have identical suitability surfaces, fitted values or accessible areas. A plant may persist after local pollinator loss, an adult stage may disperse beyond larval habitat, and a dependent consumer may be observed outside the window in which its required resource was measured. Cross-role inference therefore requires a relation defined at the biological event where the dependency actually applies.

A second problem appears when the relation is hard rather than approximate. Suppose a dependent event `E(k)` requires a function `F(k)` at biological opportunity `k`. Observing `E(k)` together with `F(k)=false` can falsify the proposed dependency. But a recorded zero is not automatically `F(k)=false`: it may instead reflect imperfect detection, missingness, sensor failure, observer failure or incomplete coverage. Hard dependency inference therefore depends not only on independent answer construction and a valid relation space, but on whether the negative state needed for falsification is itself identifiable.

Here we develop a prospective ecological answer-check framework that separates these requirements before focal outcomes are opened. We first test the controlled same-target case using independently reconstructed answers from preserved-specimen and human-observation records. We then use prospectively frozen cross-role candidate screens to ask how far the same logic can be extended toward directional biological dependency without importing same-target tolerances or converting non-detection into biological absence. This yields a general negative-state identifiability principle for ecological cross-checks and a practical stopping rule for deciding when additional modelling is no longer informative and new measurement is required.

## 2. A prospective relation ladder for independent ecological answers

### 2.1 Freeze the relation before seeing the focal comparison

The framework begins by defining the biological relation, comparison event, relation-space adapter, adequacy gates and any soft calibration before focal outcomes are opened. This reverses a common workflow in which two fitted outputs are first inspected and their biological meaning is decided afterwards.

We distinguish five relation levels: (A) same target reconstructed from independent observation sources; (B) different biological roles expected to show soft concordance; (C) directional dependency, `Y requires X`; (D) mutual dependency; and (E) life-stage coupling. The levels differ in what may legitimately be held constant and what relation can be expected.

### 2.2 Same-target and cross-role comparisons require different invariances

For Level A, holding the biological target, estimand, estimator family, accessible-area semantics and comparison rows fixed is a deliberate experimental control. The focal perturbation is observation source.

For Levels B-E, enforcing the same estimator, predictor set, accessible area or raw output scale can be biologically wrong. Each role is estimated using an appropriate model first and only then projected onto a common relation space. Candidate relation spaces include plant site × flowering window, breeding patch × reproductive season, host patch × developmental interval and larval site × transition window.

### 2.3 Soft coherence and hard dependency are different tests

Soft checks quantify discordance after valid adaptation and require relation-specific calibration. Hard dependency instead asks whether a mandatory biological implication is violated at an adequately observed event key. A same-target source-discordance ceiling is therefore not a universal biological tolerance.

## 3. Controlled empirical closure at Level A

### 3.1 Prospectively frozen design

We constructed independent ecological answers for the same taxa from preserved-specimen and human-observation records while holding fixed the target identity, ecological estimand, active `bio1-bio19` predictor universe, estimator/procedure identity within each cell, accessible-area semantics, exact 2,000-row comparison frame, adequacy logic and successor-derived reference rule.

The focal held-out outcome was not used to select procedures, accessible areas, taxa or rescue paths. A repaired successor audit sealed 2,255/2,256 fit cells and retained the unresolved cell rather than dropping or rescuing it. The predeclared reference rule required at least 30 prospectively adequate successor taxa per procedure-by-accessible-area cell. All 24 reference cells met that requirement and were frozen using the unchanged nearest-rank q95 rule before held-out paired discordance was opened.

### 3.2 Fresh held-out result

The held-out matrix contained 12 taxa × 3 accessible-area definitions × 8 procedures = 288 cells. Both independently constructed answers passed their predeclared adequacy gates in 283 cells; five cells remained closed. All 283 opened cells remained within the corresponding frozen successor-derived discordance ceiling and none triggered `attention_required`.

The closest opened result to its ceiling was *Nothofagus betuloides* under the 150-km accessible area and the `predictive_forward|logit_l2_C1_degree2` procedure: observed discordance (`1 - Schoener D`) was 0.38625 versus a frozen ceiling of 0.39085. The result therefore supports conditional cross-source reproducibility, not trivial or unlimited source invariance.

### 3.3 What Level A establishes

The controlled experiment closes cross-validity for adequately observable same-target answers: fresh held-out reconstructions from two independent source classes can satisfy a prospectively calibrated coherence relation without focal-outcome tuning. It does not imply equality of observation processes, equality of raw suitability values, a universal tolerance across biological roles, or process necessity.

## 4. Why cross-role dependency cannot be tested as raw surface containment

### 4.1 Dependency attaches to events, not adult occurrence surfaces

Consider obligate pollination. Adult plant occupancy can remain positive after local pollinator loss because established plants persist. Requiring current plant occupancy to be contained within current pollinator occupancy would therefore encode a stronger and often false biological statement. The relevant hard relation instead concerns the event at which the dependency operates, for example:

`pollinator-dependent successful reproduction at plant site × flowering window -> effective pollination function at the same site × flowering window`.

This event-key formulation permits different estimators and accessible areas upstream while preserving a hard relation where biology actually requires it.

### 4.2 Functional pools replace unjustified single-provider exclusivity

A hard dependency need not name one exclusive provider species. We therefore define the Level-C relation as `E(k) -> F(k)`, where `F(k)` is the required biological function at event key `k`. Effective pollination, compatible host resource or another prospectively defined function can be supplied by one or several providers. Provider occurrence, richness or suitability is not itself the function.

A prospectively frozen 12-candidate functional-pool screen produced no fully admitted endpoints. Seven candidates failed the exact event-to-function relation gate, three passed the relation, space, time and estimand gates but stopped at focal evidence independence, one could not freeze the exact relation population/site and one was excluded because it had been screened previously. This moved the binding problem from single-provider exclusivity toward independent same-key measurement of the required function.

## 5. Stress-testing Level C without opening focal biological outcomes

### 5.1 Separated evidence architecture can be achieved

A new prospectively frozen finite screen evaluated 12 candidates under a three-channel architecture: external evidence defining the hard biological relation (`R`), a dependent-event answer (`X`) and a required-function answer (`Y`). Two fresh systems qualified at the architecture stage.

`CREMV3-007` (*Cremastra appendiculata* var. *variabilis*) used an external breeding-system relation, same-inflorescence fruit outcome and pollinia-carrying camera observations. `BELV3-012` (*Belonocnema treatae* / live-oak budbreak) used independent host-specificity evidence, natural adult emergence and live-oak budbreak streams. Candidate hunting stopped at the frozen cap rather than continuing until a favourable endpoint was found.

### 5.2 The remaining blocker is not evidence independence

Both systems passed source materialization, common-key alignment, direct event/function estimands, provenance separation and the no-post-hoc-redefinition rule. Neither passed the gate required to infer hard functional absence.

For Cremastra, positive pollinia-carrying contacts are direct observations of the relevant function, but a zero camera record has not been calibrated as absence of effective pollination. For Belonocnema, budbreak and emergence are separately observed, but metadata do not establish that an unrecorded usable-resource state is a true biological absence rather than incomplete observation.

Thus the architecture can support direct positive states while still failing to identify the negative state required for a hard falsification.

### 5.3 Existing data do not repair the calibration gap

Candidate-specific calibration audits found no independent calibration stream capable of estimating known-positive sensitivity and known-negative specificity for either retained system without conditioning on the focal outcome. A subsequent response-blind audit of available supplementary and raw sources also failed to reconstruct such a stream.

The resulting stopping point is an external-data boundary. Further candidate hunting, threshold relaxation or reinterpretation of non-detection would change the question after seeing where the design failed. The next admissible information is new candidate-specific calibration measurement.

## 6. The negative-state identifiability principle

For a frozen hard dependency `E(k) -> F(k)`, a biological violation requires an event key for which `E(k)` is adequately positive and `F(k)` is adequately negative. The second condition is not satisfied by an observational zero unless the observation process has prospectively demonstrated that the required function, when present, would have been detected with adequate performance and that failure/missingness states are separable from biological negatives.

This creates four conceptually distinct states that should not be collapsed: detected function, calibrated functional absence, unresolved non-detection and observation failure/missingness. Only the second can supply `F(k)=false` for a hard invariant.

The principle is simple but consequential. Increasing model complexity cannot identify a biological negative that the measurement process does not distinguish from non-observation. At that point, the inferential bottleneck has moved from modelling to measurement.

## 7. Implications across ecology

The same structure appears in many ecological problems. Host-dependent development requires a compatible resource during a specific developmental interval, not generic host occurrence. Trophic dependency concerns accessible prey at a relevant foraging opportunity, not equality of predator and prey distribution surfaces. Life-stage coupling concerns transition-compatible habitat at the transition event, not identical adult and juvenile niches. Sensor-based interaction studies require calibrated detection before a zero can indicate absence of interaction. Distribution models used for process attribution require explicit separation between lack of predicted support and failure to observe the process itself.

The practical consequence is a three-part hierarchy. First, independent answers must be constructible and adequate. Second, they must be mapped to a biologically justified relation space. Third, the states needed to falsify the relation must be identifiable under the observation process. Passing an earlier layer does not license inference at a later one.

## 8. Discussion

The framework clarifies why apparently strong ecological comparisons can fail for different reasons. Level-A same-target reconstruction provides a controlled case in which cross-source discordance can be calibrated and tested prospectively. The fresh held-out result shows that this layer can close empirically: every adequately observable held-out comparison satisfied its frozen source-discordance ceiling. The five inadequate cases remained unresolved, preserving the distinction between failure to construct an answer and evidence of ecological disagreement.

Cross-role inference is harder not because it necessarily requires the same models to agree more closely, but because it requires a different relation. Once dependency is defined at the biological event and provider identity is replaced by the required function, the dominant obstacle changes again. Independent positive streams can be available while the negative functional state remains observationally unidentified. Treating uncalibrated non-detection as absence would manufacture the very falsifying evidence that the test is supposed to discover.

This boundary suggests a stopping rule for ecological modelling. When the candidate relation, evidence architecture and positive estimands are adequate but the negative state cannot be separated from non-observation, additional fitting of the same data cannot complete the hard inference. New calibration measurement is required. Conversely, obtaining that calibration does not itself prove or falsify the dependency; it only makes the focal endpoint identifiable and eligible to be opened under a separately frozen stage.

The broader lesson is that ecological answer checking should be prospective and relation-specific. Reproducibility across observation sources, concordance across biological roles and falsification of a hard dependency occupy different inferential levels. A defensible workflow freezes the relation before viewing focal comparisons, allows biologically appropriate role-specific models, preserves unresolved states, and asks explicitly whether the negative state required for contradiction is something the observation process can actually see.

## Data and code availability

Repository artifacts, code, frozen protocols and terminal receipts supporting the completed Level-A result and the pre-field Level-C design/audit sequence are maintained in the project repository. Final archival DOI(s) and immutable release identifiers will be inserted before submission.

## Display-item plan

- Figure 1. Relation ladder and prospective answer-check architecture.
- Figure 2. Level-A calibration/held-out design and empirical result.
- Figure 3. Raw-surface containment versus event-to-function dependency.
- Figure 4. Level-C v2-v8 identifiability funnel.
- Figure 5. Negative-state identifiability matrix.
- Box/Table 1. Allowed and forbidden inferences across Levels A-C.
