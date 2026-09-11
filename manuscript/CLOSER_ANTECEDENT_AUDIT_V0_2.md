# Closer-antecedent novelty audit v0.2

Purpose: stress-test the Ecology Letters Method novelty claim against work closer than standard imperfect-detection papers, including explicit observation-process identifiability frameworks.

## 1. Observation-process identifiability is already explicitly systematized

Chadwick et al. (2024), *LIES of omission: complex observation processes in ecology* (*Trends in Ecology & Evolution* 39:368–380; DOI 10.1016/j.tree.2023.10.009), proposes the LIES framework: **Latency, Identifiability, Effort and Scale**. Its central message is that ecological observation processes can be as complex as the biological processes being studied and that failure to represent those observation processes can bias inference and prediction.

**Overlap with 284b:** both treat identifiability of the observation process as a prerequisite for biological interpretation; both reject the conversion of observation failure into biological state; both connect field design to inferential authorization.

**Remaining distinction:** LIES is a typology of observation-process problems and inferential solutions. The 284b pre-field method has a different formal object: a **relation endpoint between independently generated ecological answers**. It asks (i) which relation two role-specific answers are entitled to test, (ii) which biological key makes that relation meaningful, (iii) whether independent relation/event/function evidence streams exist, and (iv) whether the negative state needed to contradict a hard relation is authorized at that endpoint. The exact benchmark then decomposes the endpoint-level consequence of coercing invalid keys into negatives: for a qualified process with valid-key fraction `a`, both the apparent true-violation gain and the excess false-violation probability equal `1-a`.

**Manuscript action:** cite Chadwick et al. early and explicitly state that observation-process identifiability is not the novelty claim. Use LIES as an antecedent that motivates why an endpoint authorization layer is needed above individual observation models.

## 2. Ecological model adequacy is already an explicit research programme

Getz et al. (2018), *Making ecological models adequate* (*Ecology Letters* 21:153–166; DOI 10.1111/ele.12893), argues that ecological models should be evaluated through explicit adequacy protocols, including state/control variables, data determinacy, sensitivity and validity.

**Overlap with 284b:** both reject the idea that model fitting alone licenses interpretation and both treat data determinacy/adequacy as a scientific constraint.

**Remaining distinction:** the pre-field framework is not a general adequacy checklist for one ecological model. It composes independently generated answers into a declared relation endpoint, separates same-target reproducibility from cross-role dependency, and distinguishes answer inadequacy from relation discordance.

**Manuscript action:** retain Getz et al. as a conceptual ancestor and avoid claiming that 284b invented model adequacy or data determinacy.

## 3. Imperfect detection and latent-state modelling are established

Occupancy, co-occurrence, integrated SDM and JSDM approaches already model imperfect observation when the sampling design identifies state and detection parameters. Interaction-network methods likewise distinguish missed interactions from true non-occurrence.

**Overlap with 284b:** a candidate-specific latent-state or detection model can satisfy part of the negative-state identifiability requirement.

**Remaining distinction:** the relation-endpoint method is upstream of estimator choice. It permits a detection-aware model as one role-specific answer, but still asks whether the two answers refer to a common biological event and whether the relation being tested is actually implied by external biology. If detection is not identified by the design, adding a latent-state model cannot create the missing information.

## 4. Preregistration and Registered Reports already establish prospectivity

Preregistration and Registered Reports freeze hypotheses, methods, sampling and analyses before outcomes. Adaptive preregistration extends this logic to model-based ecological research.

**Overlap with 284b:** relation, gates, candidate caps and analysis decisions are frozen before focal outcomes and post-hoc rescue is prohibited.

**Remaining distinction:** prospectivity is the enforcement mechanism, not the method's novelty. The methodological object being frozen is the **relation-endpoint contract**: relation, biological key, adapters, adequacy gates and calibration/opening rule.

## 5. Negative evidence is an old epistemic problem

The proposition that failure to observe something is not automatically evidence of absence is much older than this project.

**Overlap with 284b:** negative evidence is meaningful only when the observation process would have detected the relevant state with adequate performance.

**Remaining distinction:** 284b embeds this constraint inside a hard ecological implication `E(k) -> F(k)`, retains invalid keys as `unresolved`, and quantifies the endpoint-level cost of coercing them into `F(k)=false`.

**Manuscript action:** never market “absence of evidence is not evidence of absence” as the discovery. Market relation-endpoint authorization plus the exact invalid-key error decomposition.

## 6. Independent external validation is already established

Independent datasets and source-disjoint evaluation are established tools for ecological predictive validation, including species-distribution modelling.

**Overlap with 284b:** Level A uses specimen and human-observation sources plus fresh held-out taxa.

**Remaining distinction:** Level A is an empirical anchor for a broader method. The contribution is not independent validation itself, but a prospective relation endpoint in which answer existence/adequacy remains separate from cross-source disagreement and the tolerance is frozen before held-out opening.

## 7. Strongest defensible novelty claim after the LIES audit

The safest high-level claim is:

> We introduce a relation-endpoint authorization method for independent ecological answers. It prospectively fixes the biological relation, common event space, role-specific adapters, answer-adequacy gates and opening rule; distinguishes same-target reproducibility from cross-role dependency; and withholds hard contradiction until the negative state required by that relation is identifiable under the observation design.

The strongest quantitative addition is:

> For a qualified hard-dependency observation process with valid-key fraction `a`, coercing invalid keys into biological negatives increases apparent true-violation sensitivity and false hard-violation probability by the same exact amount, `1-a`.

The novelty claim therefore explicitly excludes:

- imperfect-detection modelling;
- observation-process identifiability as a general concept;
- model adequacy/data determinacy;
- preregistration/prospectivity;
- external validation;
- the generic principle that non-detection is not absence.

## 8. Editorial implication

The LIES paper is the closest conceptual antecedent found so far and should be named, not hidden. Doing so sharpens the desk-review question to the one the paper can answer: **is relation-endpoint authorization a sufficiently specific and transferable technique above observation-model choice?**

The strongest evidence that it is a method rather than workflow philosophy is the combination of:

1. a formally specified relation-endpoint contract;
2. the exact `1-a` decision decomposition;
3. an executable calibration/opening gate;
4. a fresh Level-A held-out empirical closure;
5. a real-system Level-C stress test that reaches a measurement boundary without opening focal biological outcomes.

If this package is kept central, the strongest comparison is not “284b versus occupancy/LIES.” It is “LIES and detection-aware methods characterize or solve observation processes; 284b decides when independently constructed answers may be composed into a biological relation endpoint and when that endpoint must remain sealed.”
