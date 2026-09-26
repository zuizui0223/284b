# Novelty positioning v0.1

## The paper must not claim that imperfect detection is new

The ecological literature already has mature methods for separating ecological state from observation error. Relevant anchors include:

- MacKenzie et al. (2004), *Journal of Animal Ecology*: co-occurrence with imperfect detection, DOI 10.1111/j.0021-8790.2004.00828.x.
- Dénes et al. (2015), *Methods in Ecology and Evolution*: false zeros and imperfect detection in abundance models, DOI 10.1111/2041-210X.12333.
- Koshkina et al. (2017), *Methods in Ecology and Evolution*: integrated SDMs combining presence-background and occupancy data with imperfect detection, DOI 10.1111/2041-210X.12738.
- Tobler et al. (2019), *Ecology*: JSDMs with species correlations and imperfect detection, DOI 10.1002/ecy.2754.
- Hogg et al. (2021), *Methods in Ecology and Evolution*: consequences of imperfect detection for JSDMs, DOI 10.1111/2041-210X.13614.
- Doser et al. (2023), *Ecology*: high-dimensional spatial JSDMs with imperfect detection, DOI 10.1002/ecy.4137.

These literatures establish that non-detection can differ from ecological absence and that observation models can be required for unbiased occurrence/co-occurrence inference.

## The novelty claim

The proposed contribution is **not another occupancy or detection model**. It is a prospective decision architecture for determining when independently generated ecological answers can be combined, and when a stronger biological dependency claim is identifiable at all.

The distinct pieces are:

1. **Relation-first design.** The expected relation is frozen before focal outputs are inspected. Same-target reproducibility, soft cross-role concordance, directional dependency, mutual dependency and life-stage coupling are treated as different inferential objects rather than variations of one output-overlap statistic.

2. **Role-specific upstream answers, common downstream relation space.** Different roles need not share estimators, predictor sets, accessible areas or raw output scales. Comparability is created only after each role has been estimated appropriately and projected to a prospectively frozen biological event key.

3. **Independent-answer architecture.** Evidence defining the biological relation is separated from the streams used to answer the dependent-event and required-function questions. This prevents the evidence used to define a dependency from also serving as its confirmatory endpoint.

4. **Functional rather than provider-specific hard relations.** A required function can be defined prospectively even when several providers can supply it, avoiding unjustified single-provider exclusivity.

5. **Negative-state identifiability as a gate on hard falsification.** A hard implication is not testable merely because positive event/function states can be estimated. The negative state needed to contradict the implication must itself be distinguishable from non-observation, incomplete coverage and failure.

6. **Fail-closed unresolved state.** Missing, unavailable, failed and insufficiently calibrated states remain unresolved rather than being forced into either agreement or biological violation.

7. **Exact invalid-state inflation result.** In the analytic benchmark, when a qualified observation process has valid-key fraction `a`, collapsing invalid states into negatives adds exactly `1-a` both to apparent true-violation sensitivity and to false hard-violation probability. The additional apparent power is therefore exactly mirrored by additional contradiction error.

8. **Empirical cross-validity anchor.** The framework is not purely conceptual: Level A closed prospectively on fresh held-out data, with 283/283 adequately observed cells inside the frozen successor-derived source-discordance envelope while five inadequate cells remained closed.

## Distinction from detection-aware occupancy/JSDM methods

Detection-aware occupancy and JSDM methods ask, roughly, how to estimate latent occurrence/co-occurrence or correlations when observations are imperfect.

This manuscript asks a different upstream question:

> Given two ecological answers that may have different targets, observation processes, models and biological roles, what relation is scientifically justified between them, and are the states required to test that relation actually identifiable?

A detection model can be one component used to satisfy that architecture. It is not the architecture itself.

This distinction is essential for Ecology Letters. The Method paper should be sold as a transferable inferential design that determines when ecological answer-combination is licensed, not as a new estimator for imperfect detection.

## Why the case study matters

The same-target held-out endpoint demonstrates that a prospectively frozen cross-check can terminate empirically without focal tuning.

The Level-C sequence then shows that a biologically stronger relation can fail for a different reason: not because the two ecological models disagree, but because the negative functional state required for falsification is not yet observationally licensed.

Together, these cases expose a hierarchy that ordinary model comparison does not distinguish:

`answer existence -> valid relation space -> cross-validity -> negative-state identifiability -> hard biological test -> process necessity`.

The paper stops before the final two steps and says so explicitly.
