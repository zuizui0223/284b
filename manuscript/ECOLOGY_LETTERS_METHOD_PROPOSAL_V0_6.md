# Ecology Letters — unsolicited Method proposal package v0.6

## Working title

**Prospective validation of ecological answers: from cross-source reproducibility to identifiable biological absence**

## Article type

**Method**

The proposal presents an executable, estimator-agnostic technique for authorizing relations among independently generated ecological answers. It is not a new occupancy estimator, observation-process typology, preregistration framework or taxon-specific biological study.

## Proposal text

Use the exact body frozen in `ECOLOGY_LETTERS_300WORD_PITCH_V0_6.md` (255 words under the repository word-count rule).

## The methodological object

The central object is a five-part **relation-endpoint contract** frozen before focal comparison:

1. biological relation;
2. biological event/key space;
3. role-specific adapters;
4. answer-adequacy gates;
5. calibration/opening rule.

The reference implementation `scripts/relation_endpoint_contract.py` makes the technique executable. A soft calibrated key returns `consistent`, `attention_required` or `unresolved`. A directional hard key returns `hard_violation_authorized`, `no_observed_violation`, `noninformative_for_implication` or `unresolved`. Inadequate answers and unqualified negatives cannot become biological contradictions.

## Position relative to antecedents

- **Occupancy/detection models:** may supply a role-specific answer or satisfy part of the negative-state gate when sampling identifies the observation process; this paper is not another occupancy model.
- **Chadwick et al. (2024) LIES:** already systematizes Latency, Identifiability, Effort and Scale in ecological observation processes. Observation-process identifiability is an input to relation-endpoint authorization, not the novelty claim.
- **Getz et al. (2018) model adequacy:** addresses whether a model and its data are adequate. The relation endpoint asks what joint biological relation individually defensible answers may test.
- **External validation:** established. Level A is a controlled empirical anchor, not the invention of held-out testing.
- **Preregistration / Registered Reports:** established. Prospectivity is an enforcement mechanism for freezing the endpoint, not the contribution itself.

## Quantitative performance without a straw-man method comparison

The synthetic comparison is explicitly an **ablation of one guardrail**: zero collapsing removes the rule that invalid observation remains unresolved. It is not presented as a competitor to detection-aware models.

Allow key validity to differ by latent function state:

- `a1 = P(valid | F=true)`;
- `a0 = P(valid | F=false)`;
- `q` = key sensitivity on valid compatible keys;
- `sp` = specificity on valid true-violation keys.

Then exactly:

`FPR_zero - FPR_gated = 1-a1`

and

`TPR_zero - TPR_gated = 1-a0`.

The previously reported identity in which both increments equal `1-a` is the equal-validity special case `a1=a0=a`. The original 8,748-scenario benchmark evaluates that controlled case; `pre_field_state_dependent_invalidity_v0_2` audits the generalized form. No focal Level-C biological values are used.

A separate base-rate result shows that process qualification is not false-discovery control:

`FDF = (1-pi)(1-q) / [(1-pi)(1-q) + pi sp]`.

## Empirical anchor without pseudoreplication

The independent held-out biological units are **12 taxa**, not 283 cells. Each taxon had a prespecified 3 accessible-area × 8 procedure matrix, yielding 288 cell diagnostics. Of these, 283 were evaluable and five stayed unresolved; no held-out taxon contained an envelope exceedance among its evaluable cells.

The nearest-rank q95 references are described as **prospectively frozen empirical source-discordance envelopes**, not nominal 95% prediction intervals or alpha=0.05 tests. The 283/283 result is a cell-level diagnostic summary and is never used as an independent binomial sample size.

## Real-system stress test

Two biologically different Level-C architectures independently reached the same stopping point after relation, key alignment, answer directness and evidence separation succeeded: functional absence lacked candidate-specific calibration. They are used only as **pre-outcome openability audits**. Paper 1 contains no Level-C biological dependency result.

## Why this fits Method

The package now includes:

- a specific executable contract and state machine;
- exact class-conditional operating characteristics;
- outcome-blind calibration operating-characteristic analysis;
- open tested code;
- a fresh 12-taxon held-out empirical demonstration;
- two real-system openability stress tests spanning pollination and host-resource dependence.

## Quantitative figure to attach

Use `manuscript/figures/ecology_letters_method_proposal_figure_v0_5.svg`.

The figure explicitly distinguishes biological replication (12 taxa) from repeated cell diagnostics and shows the generalized `a1/a0` decomposition. It contains no focal Level-C biological values.

## Editorial-risk sentence

The remaining desk-review risk is conceptuality. If the editors judge relation-endpoint authorization too conceptual for Method despite the executable engine, exact performance decomposition and case study, invite advice on another Ecology Letters article type rather than changing the scientific endpoint post hoc.

## Proposal-readiness boundary

No new Level-C field data are required. Remaining pre-send fields are final author list, affiliation, corresponding email and coauthor qualification sentences.
