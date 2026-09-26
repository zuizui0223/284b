# Closer-antecedent novelty audit v0.4 — relation-layer separation update

Purpose: strengthen the September 2026 novelty audit by testing the relation-endpoint object against two additional close literatures: joint species distribution modelling and inference of interactions from co-occurrence.

This audit does not widen the empirical claim boundary and does not claim new probability theory.

## 1. Closest established layers

The pre-field Method paper explicitly concedes the following as prior art:

- imperfect-detection and occupancy models;
- LIES / observation-process identifiability;
- model adequacy and data determinacy;
- external validation and held-out testing;
- preregistration / outcome-blind design;
- multi-source data fusion;
- joint species distribution modelling and joint prediction;
- the generic warning that co-occurrence does not automatically equal interaction;
- the generic warning that non-detection does not automatically equal absence.

The novelty claim therefore cannot rest on any of these ingredients alone.

## 2. JSDMs are a genuinely close antecedent, but at a different inferential layer

Wilkinson et al. (2021), *Defining and evaluating predictions of joint species distribution models* (*Methods in Ecology and Evolution* 12:394–404; DOI 10.1111/2041-210X.13518), explicitly distinguish marginal predictions from joint predictions. That literature is directly relevant because it shows that separately correct marginal predictions are not the same object as a joint ecological prediction.

This overlap should be acknowledged rather than evaded.

The remaining boundary is biological authorization. A JSDM may estimate a joint distribution or residual co-occurrence structure. The relation-endpoint method asks a subsequent question:

> Which joint biological relation is scientifically licensed for these answers — co-occurrence, directional dependency, mutual dependency, stage transition, reproductive opportunity, or another relation — and what observation state is sufficient to open or contradict that endpoint?

Thus the relation-endpoint method does not replace a JSDM. A JSDM can be one upstream answer-construction engine or can supply part of the joint/event alignment required by the endpoint contract.

## 3. Co-occurrence is not automatically the biological relation

Galiana et al. (2024), *Power laws in species' biotic interaction networks can be inferred from co-occurrence data* (*Nature Ecology & Evolution* 8:209–217; DOI 10.1038/s41559-023-02254-y), emphasizes that species co-occurrences do not reliably map one-to-one onto pairwise biotic interactions; in their analysed systems only a minority of co-occurrences corresponded to observed interactions, even though network-level co-occurrence structure remained informative.

This is aligned with the relation-endpoint motivation: statistical association can be informative without being the same claim as a mandatory biological dependency.

The Method paper should therefore never imply that co-occurrence/JSDM work is biologically meaningless. The narrower point is that statistical joint structure does not itself choose the endpoint semantics.

## 4. Formal separation: exact marginals do not identify a hard implication

Let `E` be a dependent event and `F` a required function on a common key population. The hard relation is `E -> F` and its violation probability is

`v=P(E=1,F=0)`.

Suppose the role-specific answers are perfect and return exact marginals

`p_E=P(E=1)` and `p_F=P(F=1)`.

Classical Fréchet-Hoeffding bounds imply

`max(0,p_E-p_F) <= v <= min(p_E,1-p_F)`.

For `p_E=p_F=0.5`, both of the following are compatible with exactly the same marginal answers:

- `v=0`: `E` and `F` are perfectly aligned and the hard implication holds;
- `v=0.5`: every `E=1` key has `F=0` and the implication is maximally violated.

Therefore perfect marginal answer quality does not generally identify the hard relation. This is a classical coupling fact, not new mathematics. Its role is to demonstrate that a relation layer cannot be eliminated merely by improving the upstream marginal estimators.

Canonical executable audit:
- `scripts/run_relation_layer_separation_v0_1.py`;
- `results/relation_layer_separation_v0_1.json`;
- `manuscript/RELATION_LAYER_SEPARATION_V0_1.md`.

## 5. What a JSDM repairs — and what it does not choose

A correctly specified joint model can estimate the coupling that separate marginals leave unidentified. This means the relation-endpoint paper must not claim that all joint relations are statistically unknowable without its framework.

Instead, the exact distinction is:

1. marginal models estimate role-specific states;
2. joint models can estimate statistical coupling;
3. **external biology and the endpoint contract specify which biological relation that coupling is supposed to represent and what counts as an admissible contradiction.**

Layer 3 remains even when layers 1 and 2 are solved perfectly.

## 6. Updated strongest novelty claim

The strongest defensible novelty statement after adding JSDM and co-occurrence antecedents is:

> Existing methods can estimate ecological states, correct observation error, fuse sources and model joint distributions. We introduce an executable prospective contract for the logically subsequent step: specifying which biological relation independently generated ecological answers are authorized to test, on which biological key, and under what adequacy and observation conditions that relation may be opened or contradicted.

This formulation is narrower than claiming a new theory of joint distributions and stronger than presenting the work as a checklist for good modelling practice.

## 7. Editorial consequence

The formal two-world counterexample directly answers the likely reviewer objection that better upstream models would make the relation-endpoint layer redundant. They do not: perfect marginal answers can have opposite hard-relation status under different couplings, and even a perfect joint distribution still requires biological semantics to determine whether the scientific endpoint is co-occurrence, functional dependency or another relation.

The counterexample is therefore worth a concise manuscript-facing statement if it can be added without destabilizing the reviewer-hardened claim boundary. It should be presented as a **separation argument using classical probability bounds**, not as a new theorem.

Empirical ledger increment: **0**.
