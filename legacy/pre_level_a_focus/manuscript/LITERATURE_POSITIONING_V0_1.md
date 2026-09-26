# Literature positioning audit v0.1

Purpose: prevent the pre-field flagship from claiming novelty for ideas that are already established, and isolate the contribution that is actually distinctive.

## The paper must explicitly concede these established results

### 1. Imperfect detection and false absence are established problems

Occupancy modelling has long separated ecological occurrence from detection. MacKenzie, Bailey & Nichols (2004) showed that false absences can distort species co-occurrence inference and developed a co-occurrence model with imperfect detection. Guillera-Arroita (2016) reviewed species-distribution and community modelling under imperfect detection and emphasized that data must be informative about the observation process, for example through repeat surveys, observers or detection methods. Guillera-Arroita et al. (2017) further treated false-positive and false-negative errors as an identifiability problem requiring additional information.

**Therefore we must not claim:**
- that 284b discovered imperfect detection;
- that 284b discovered that non-detection can differ from absence;
- that repeat or gold-standard observation is a new idea.

Core references:
- MacKenzie DI, Bailey LL, Nichols JD. 2004. *Investigating species co-occurrence patterns when species are detected imperfectly*. Journal of Animal Ecology 73:546–555. DOI: 10.1111/j.0021-8790.2004.00828.x.
- Guillera-Arroita G. 2017 [online 2016]. *Modelling of species distributions, range dynamics and communities under imperfect detection: advances, challenges and opportunities*. Ecography 40:281–295. DOI: 10.1111/ecog.02445.
- Guillera-Arroita G et al. 2017. *Dealing with false-positive and false-negative errors about species occurrence at multiple levels*. Methods in Ecology and Evolution. DOI: 10.1111/2041-210X.12743.

### 2. Multispecies co-occurrence under imperfect detection is established

Rota et al. (2016) generalized multispecies occupancy models to arbitrary numbers of interacting species while accounting for imperfect detection. This literature estimates statistical dependence in occupancy while separating the observation process.

MacKenzie et al. (2004) are especially useful for our positioning because they explicitly distinguish their statistical use of “interaction” from a claim about a specific biological mechanism.

**Therefore we must not claim:**
- that 284b is the first way to analyse two biological entities jointly under imperfect detection;
- that statistical co-occurrence or occupancy dependence is itself a new target.

Core reference:
- Rota CT et al. 2016. *A multispecies occupancy model for two or more interacting species*. Methods in Ecology and Evolution. DOI: 10.1111/2041-210X.12587.

### 3. Missed ecological interactions are an established inferential problem

Weinstein & Graham (2017) explicitly framed unobserved interactions as ambiguous between missed sampling and true non-occurrence and used hierarchical models to separate detectability from interaction intensity.

**Therefore we must not claim:**
- that 284b first noticed that an unobserved plant–pollinator interaction may simply have been missed;
- that detection-aware interaction modelling is absent from the literature.

Core reference:
- Weinstein BG, Graham CH. 2017. *On comparing traits and abundance for predicting species interactions with imperfect detection*. Food Webs 11:17–25. DOI: 10.1016/j.fooweb.2017.05.002.

### 4. Independent external validation of ecological models is established

Independent datasets are already used to evaluate species-distribution models. Matutini et al. (2021) compared internal cross-validation with external citizen-science evaluation and showed that internal evaluation could be optimistic. Gaier & Resasco (2023) used iNaturalist as a truly independent external evaluation source for a herbarium-trained rare-plant SDM.

**Therefore we must not claim:**
- that 284b invented independent validation;
- that specimen versus observation data have never been compared;
- that the existence of a held-out source is itself sufficient novelty.

Core references:
- Matutini F et al. 2021. *How citizen science could improve species distribution models and their independent assessment*. Ecology and Evolution 11:3028–3039. DOI: 10.1002/ece3.7210.
- Gaier AG, Resasco J. 2023. *Does adding community science observations to museum records improve distribution modeling of a rare endemic plant?* Ecosphere 14:e4419. DOI: 10.1002/ecs2.4419.

### 5. Specimen and observation sources have different biases; this is established

Large biodiversity databases combine observation and specimen processes with different spatial, temporal and taxonomic biases. Erickson & Smith (2021) adapted occupancy concepts to museum/herbarium collection processes. Comparative work has also documented distinct bias structures between specimen and observation records.

**Therefore we must not claim:**
- that source-specific bias is newly discovered by the Level-A result;
- that 283/283 means the two source processes are identical.

Core reference:
- Erickson KD, Smith AB. 2021. *Accounting for imperfect detection in data from museums and herbaria when modeling species distributions: combining and contrasting data-level versus model-level bias correction*. Ecography 44:1341–1352. DOI: 10.1111/ecog.05679.

## What 284b contributes beyond those literatures

These contributions should be presented as the manuscript's novelty package rather than as isolated slogans.

### A. Relation-specific prospective validation rather than generic model validation

The framework freezes **what kind of agreement is biologically expected** before focal values are opened. Same-target source reproducibility, soft cross-role concordance and hard directional dependency are different relations with different admissible calibrations. In particular, a Level-A source-discordance tolerance is prohibited from silently becoming a Level-B/C biological tolerance.

This is not merely “external validation”: the object being validated is a predeclared relation between independently constructed ecological answers.

### B. Cross-role comparability is created after answer construction

Role-specific estimators, predictor universes and accessible areas are allowed upstream. The answers are compared only after projection onto a prospectively frozen common relation space. This avoids treating identical raw suitability or occupancy surfaces as the default biological expectation.

### C. Hard dependency is an event-to-function implication, not statistical co-occurrence

The Level-C object is a biologically justified implication

`E(k) -> F(k)`

at a frozen biological opportunity key. `F(k)` is the required function rather than generic occurrence of a named provider. This distinguishes the target from multispecies occupancy models whose statistical interaction need not identify a biological mechanism.

### D. Evidence architecture is separated prospectively

For a hard cross-role endpoint, the evidence defining the biological relation (`R`), the dependent-event answer (`X`) and the required-function answer (`Y`) are separated before focal opening. A relation-defining experiment cannot simply be reused as the focal function answer, and candidate hunting stops at a frozen finite cap.

This turns evidence independence from an informal preference into an endpoint-admission property.

### E. Negative-state identifiability is an authorization condition for biological falsification

Detection-aware models estimate latent states from imperfect observations. 284b's additional question is procedural and inferential: **when is a hard biological contradiction allowed to be opened at all?** A non-detection can participate in `F(k)=false` only after the actual candidate-specific observation process has been prospectively calibrated and missing/failure states are separable.

When that condition is not met, the terminal state is `unresolved`, not a fitted negative and not a biological conclusion.

### F. The cost of collapsing invalid states is quantified exactly

For a qualified process with valid-key mass `v`, key sensitivity `q` and specificity `sp`, the pre-field benchmark derives

`FPR_naive - FPR_gated = 1-v`

and

`TPR_naive - TPR_gated = 1-v`.

Thus an apparent gain in hard-violation sensitivity from converting invalid observations into zero is exactly matched by a structural increase in false violations. This result is about endpoint decision semantics rather than estimation of occupancy or detection probability.

### G. The complete method is exercised at two different inferential levels

- Level A supplies a fresh held-out empirical demonstration: 283/283 eligible cells satisfy prospectively frozen source-discordance ceilings while 5 inadequate cells remain unresolved.
- Level C supplies a prospectively documented real-system stress test: relation/function semantics and independent evidence architecture can succeed while hard inference remains sealed because the falsifying negative state is not identified.

The contrast is scientifically useful because it shows that successful independent answer construction is not sufficient for a biological dependency claim.

## Recommended novelty sentence

Use a formulation close to:

> We do not introduce another model for imperfect detection or species co-occurrence. We introduce a prospective validation architecture for deciding which relation independent ecological answers are entitled to test, and—when that relation is a hard biological dependency—whether the negative state required to falsify it is identifiable enough for the endpoint to be opened.

## Recommended contrast paragraph for the Introduction

Occupancy and interaction models already show why ecological non-detection cannot generally be equated with absence, and independent external datasets are widely recognized as stronger tests of predictive models. Our target is different. We ask how independently constructed ecological answers can be promoted from model outputs to a prospectively testable biological relation. This requires specifying whether the intended claim is same-target reproducibility, soft cross-role concordance or a hard dependency; mapping role-specific answers to the event at which biology makes that claim; and withholding hard falsification when the negative state required for contradiction is not independently identifiable.

## Reviewer attacks this positioning should pre-empt

1. **“This is just occupancy modelling.”** Response: occupancy models estimate latent occurrence under imperfect detection; this framework governs relation choice, evidence separation and endpoint authorization across independently constructed answers. Cite MacKenzie/Rota and state the difference directly.
2. **“Non-detection is not absence is obvious.”** Agree. Novelty is the event/function endpoint architecture plus the exact decision consequence and prospectively enforced stopping rule, not the aphorism.
3. **“Independent validation already exists.”** Agree. Level A is not claimed as the invention of external validation; its contribution is a fresh controlled demonstration inside the broader prospectively frozen relation framework.
4. **“The algebra is tautological.”** Do not sell the identity alone. Its value is that it exposes exactly which apparent gain from a common zero-collapsing endpoint rule is observation invalidity rather than biological information, and it is coupled to the operational gate and real-system stopping point.
5. **“Why not fit a latent-state model instead of declaring unresolved?”** A latent-state model is appropriate when the available sampling design identifies detection and state parameters. The Level-C source audits ask precisely whether candidate data provide that information. When they do not, a fitted latent negative would import identification from assumptions rather than candidate-specific evidence; the framework records that as a measurement requirement.

## Status

This is a literature-positioning document, not a systematic review. Before submission, expand the citation search around prospective/preregistered model validation, ecological falsification, and decision-theoretic treatment of unresolved observations to test whether any closer antecedent already combines these elements.
