# Paper 1 reviewer-attack matrix v1

**Purpose:** pre-empt the closest conceptual objections without widening the scientific claim boundary or altering the frozen Ecology Letters Stage-1 package.

**Current paper object:** an executable prospective **relation-endpoint authorization layer** that specifies which biological relation independently generated ecological answers are licensed to test, on which biological key/event space, and under what adequacy and observation conditions that relation may be opened or contradicted.

**Scientific boundary:** Level A is the sole completed empirical endpoint; Level B remains unopened; focal Level-C outcomes remain sealed; empirical ledger = 1.

## Reviewer objection 1 — “This is just preregistration.”

### Closest antecedent
Gould et al. (2026) develop Adaptive Preregistration for model-based ecology. Their method is explicitly designed to constrain researcher degrees of freedom, improve transparency, and prospectively register flexible modelling decisions.

### What we concede
Preregistration, outcome-blind freezing, registered decision rules and auditability are prior art. The present paper does not claim to invent any of them.

### Remaining distinct object
Preregistration governs **when analytic decisions are declared**. A relation endpoint governs **what joint biological proposition separately generated ecological answers are authorized to evaluate** and which observation state is logically sufficient to support or contradict it.

A preregistration can freeze a biologically invalid comparison perfectly. Conversely, a correctly specified relation endpoint can itself be preregistered. The two layers are therefore complementary, not competing.

### Safe manuscript sentence
> Preregistration protects analysis choices from outcome-dependent revision; the relation endpoint specifies the biological proposition those protected analyses are entitled to test together.

## Reviewer objection 2 — “A JSDM or multispecies occupancy model already solves the joint problem.”

### Closest antecedents
Wilkinson et al. (2021) distinguish marginal, joint and conditional predictions from JSDMs. Rota et al. (2016) model the joint occurrence of two or more potentially interacting species while accounting for imperfect detection.

### What we concede
Joint models can estimate statistical coupling that separate marginal models leave unidentified. A multispecies occupancy model can also estimate latent joint occurrence under an explicit observation model.

### Remaining distinct object
The endpoint question is downstream: whether the joint structure is licensed to represent co-occurrence, directional dependency, mutual dependency, life-stage transition, effective pollination, host-dependent development, or another biological relation. The model does not by itself choose the biological semantics or the observation state sufficient for a hard contradiction.

The Fréchet–Hoeffding counterexample is therefore used only to show why **marginals alone** are insufficient. It does not imply that joint distributions are statistically unknowable.

### Safe manuscript sentence
> Joint models can estimate coupling; the endpoint contract specifies which biological relation that coupling is supposed to represent and what state can open or contradict it.

## Reviewer objection 3 — “Co-occurrence-to-interaction caveats already say this.”

### Closest antecedents
Blanchet et al. (2020) show that spatial association is a poor proxy for ecological interaction. Galiana et al. (2024) show the complementary point that co-occurrence can nonetheless contain information about network-level interaction structure under explicit assumptions.

### What we concede
The generic warning that co-occurrence is not interaction is established. Co-occurrence is not biologically meaningless, either.

### Remaining distinct object
The relation endpoint is not a warning about one proxy. It is an executable authorization rule that forces the user to state the biological relation, common event/key, role-specific adapters, answer-adequacy gates and opening rule before focal comparison values are opened.

### Safe manuscript sentence
> Statistical joint structure can be informative without being identical to the biological relation being claimed; the endpoint makes that mapping explicit and testable.

## Reviewer objection 4 — “LIES / occupancy already handles identifiability and non-detection.”

### Closest antecedents
Chadwick et al. (2024) formalize Latency, Identifiability, Effort and Scale as properties of ecological observation processes. Occupancy and detection models explicitly separate latent ecological state from observation.

### What we concede
Imperfect detection, latent-state modelling and the principle that non-detection is not automatically absence are prior art.

### Remaining distinct object
The paper asks what happens **after** an upstream answer has been constructed: can that answer supply the specific positive or negative premise required by the declared relation endpoint? If the observation process does identify the required state, the endpoint consumes that qualified answer. If it does not, the endpoint remains unresolved.

The exact `1-a1` / `1-a0` result characterizes the decision consequence of deleting this unresolved state; it is not presented as a replacement for detection-aware modelling.

### Safe manuscript sentence
> Detection-aware models may satisfy the endpoint’s negative-state gate; when they do not identify the required state, the endpoint cannot manufacture a hard negative from non-detection.

## Reviewer objection 5 — “Model adequacy already asks whether the data support the model.”

### Closest antecedent
Getz et al. (2018) argue that ecological models should be assessed for adequacy, including whether data determine the chosen model detail and whether analyses are sensitive and valid.

### What we concede
Answer adequacy and model-data compatibility are established upstream responsibilities.

### Remaining distinct object
A relation endpoint assumes that multiple answers may each be adequate on their own terms. It asks whether those adequate answers can be **composed into one joint biological claim**. Thus answer adequacy is a gate inside the endpoint contract, not the endpoint’s novelty claim.

### Safe manuscript sentence
> Model adequacy asks whether an answer is supported; relation authorization asks what biological claim multiple supported answers can jointly license.

## Reviewer objection 6 — “Data fusion already combines independent sources.”

### Closest antecedent
Pacifici et al. (2017) integrate heterogeneous data sources into a common species-distribution inference.

### What we concede
Multi-source integration can improve estimation of a shared latent target and is not novel here.

### Remaining distinct object
Data fusion combines sources to estimate one target. Relation endpoints allow different roles to remain modelled on role-appropriate scales and estimands, then require explicit mapping only at the biological event where a relation is predicted.

### Safe manuscript sentence
> Data fusion solves how evidence streams contribute to an answer; relation authorization solves what separately defensible answers may claim together.

## Reviewer objection 7 — “This is just a DAG or causal model.”

### Closest antecedent
Structural causal models and DAGs encode causal assumptions and provide formal identification criteria for causal effects in ecology (e.g. Arif 2023).

### What we concede
Encoding biological assumptions prospectively and making them inspectable is not unique to relation endpoints. DAGs provide a much richer calculus for causal identification than anything claimed here.

### Remaining distinct object
The present Method does **not** claim causal-effect identification. A relation endpoint may encode a non-causal dependency, same-target cross-source relation, life-stage compatibility rule or functional requirement. Its output is authorization of an endpoint state, not an intervention effect or causal estimand.

Where the scientific claim is causal, a DAG/SCM can supply the causal assumptions and estimand upstream; the relation endpoint still governs how the resulting answers are mapped to the declared joint endpoint.

### Safe manuscript sentence
> DAGs formalize causal identification; relation endpoints govern prospective composition of ecological answers and do not, by themselves, identify causal effects.

## Reviewer objection 8 — “The Level-A result is just reproducibility.”

### What we concede
The 12-taxon same-target experiment is a controlled empirical anchor, not a universal theorem of source invariance.

### Remaining distinct object
Its role is to demonstrate that a prospectively declared endpoint can actually close when adequacy and calibration are satisfied. Replication is **12 taxa**, not 283 cells. The 283 evaluable cells are repeated diagnostics under a prespecified procedure-by-area matrix.

### Safe manuscript sentence
> Level A demonstrates endpoint closure under a frozen same-target relation; it does not establish universal cross-source reproducibility.

## Reviewer objection 9 — “The Level-C examples are negative results dressed up as a method.”

### What we concede
No focal Level-C dependency is confirmed or falsified.

### Remaining distinct object
Both systems independently pass relation/event/function architecture gates and stop at the same missing requirement: candidate-specific identification of functional absence. The result is therefore a **measurement-boundary/stopping-rule demonstration**, not a biological negative.

### Safe manuscript sentence
> The Level-C demonstrations identify the next admissible measurement rather than convert an ambiguous zero into a biological conclusion.

## Reviewer objection 10 — “The framework is only a checklist.”

### Response
It is executable rather than purely verbal. The contract validates required fields, freezes an `opening_rule_reference`, serializes canonically, fingerprints semantic identity, preserves explicit unresolved states and produces defined endpoint states. The manuscript also includes a classical separation argument, an exact error-cost ablation, a held-out empirical closure and two real-system stopping-rule demonstrations.

The defensible novelty is therefore **not** any one ingredient. It is the operational composition of these pieces around a specific missing inferential object: prospective authorization of a joint biological relation among independently generated ecological answers.

## Strongest defensible novelty sentence

> Existing methods can estimate ecological states, correct observation error, fuse sources, encode causal assumptions, model joint distributions and preregister analyses. We introduce an executable prospective contract for the logically subsequent composition step: specifying which biological relation independently generated ecological answers are authorized to test, on which biological key, and under what adequacy and observation conditions that relation may be opened or contradicted.

## Claims explicitly not made

- not a new occupancy or detection model;
- not a new JSDM;
- not a new data-fusion method;
- not a new causal-identification calculus;
- not a new preregistration framework;
- not a new probability theorem;
- not proof that co-occurrence is biologically uninformative;
- not proof of universal source invariance;
- not a confirmed or falsified Level-C dependency;
- not permission to treat non-detection as biological absence.

**Empirical ledger increment from this audit:** 0.
