# Product-B Level-C v8.2 — robust prospective field-calibration sampling plan

## Status

This is a **prospective sampling-plan hardening step performed before any Level-C field-calibration outcomes are entered or inspected**.

It changes the calibration collection target only. It does not change:

- retained candidates (`CREMV3-007`, `BELV3-012`);
- sensitivity threshold (`>= 0.80`);
- hard false-negative-rate threshold (`<= 0.20`);
- specificity threshold (`>= 0.95`);
- one-sided 95% exact Clopper-Pearson confidence rule;
- missingness/failure semantics;
- the v8.1 calibration evaluator;
- the biological endpoint or empirical ledger.

The canonical plan is `config/product_b_level_c_sampling_plan_v8_2.json`.

## Why v8.2 is needed

The historical v8.1 minimum design uses 30 resolved gold-positive and 60 resolved gold-negative calibration units per candidate. Under the frozen one-sided 95% exact specificity requirement, the 60-negative minimum is fragile: `60/60` known negatives must be classified correctly. `59/60` does not put the exact lower confidence bound at or above 0.95.

That fragility is a property of the already-frozen threshold/confidence rule, not evidence that the threshold should be relaxed.

Because no field-calibration outcomes have yet been inspected, the legitimate prospective response is to freeze a larger collection target before data collection rather than extend the sample after observing a failure.

## Frozen resolved targets

Per candidate:

- gold-positive target: **30 resolved units**;
- gold-negative target: **93 resolved units**.

The positive target remains 30 because the exact sensitivity rule already permits two false negatives at that target: `28/30` passes the one-sided 95% exact lower-bound requirement for sensitivity >= 0.80, whereas `27/30` does not.

The negative target is increased to 93 because:

- `92/93` has a one-sided 95% exact lower bound at or above 0.95;
- `91/93` does not.

Thus the frozen 93-negative target tolerates **one false positive**, but not two, without changing the scientific specificity threshold.

These exact boundaries are computed rather than copied into the implementation by `scripts/audit_level_c_sampling_plan_v8_2.py`.

## Operational gate

A config file alone is insufficient because the unchanged v8.1 evaluator correctly treats 30 positives and 60 negatives as its historical minimum. Therefore v8.2 adds an outer prospective sampling gate while reusing the v8.1 evaluator unchanged.

`evaluate_candidate_against_plan(...)` authorizes later endpoint opening only when both conditions hold:

1. the candidate has reached at least the prospectively frozen resolved targets (`30` positive, `93` negative); and
2. the unchanged v8.1 exact calibration evaluator returns `opening_authorized=true`.

Consequences:

- a clean `30 + 60` calibration can pass v8.1 but **cannot** pass the v8.2 operational gate because the prospective negative target has not been reached;
- `30/30` positives plus `92/93` correctly classified negatives can pass v8.2;
- two false positives among 93 negatives fail the unchanged exact specificity rule;
- no single-winner, threshold-relaxation, candidate-replacement, or post-failure sample-extension rescue is introduced.

## Missingness and failures

The target counts refer to **resolved calibration units**.

Rows marked as missing, device failure, observer failure, occlusion, or unresolved adjudication do not count toward the resolved positive or negative targets. They are not biological negatives. This preserves the existing separation between observation failure and biological absence.

If a planned unit is unresolved, another calibration unit may be collected to reach the prospectively declared resolved target. That is completion of the frozen sampling design, not a post-outcome extension. Once the resolved target has been reached and its biological calibration result is known, extending the target to rescue a failed calibration is forbidden.

## What the final CSV cannot prove

The evaluator can verify resolved counts, exact performance and missingness semantics from the submitted rows. It cannot reconstruct the full chronology of data access from a final CSV. Therefore two governance facts must be maintained prospectively in field records/workflow provenance:

- the 30/93 target was frozen before candidate calibration outcomes were inspected;
- the target was not increased after observing a failed result.

The repository freeze and commit history provide the pre-outcome design record; field acquisition records must preserve the corresponding collection chronology.

## Interpretation boundary

Passing this calibration gate is **not** a biological conclusion. It only authorizes the later candidate-specific Level-C endpoint to be opened under its already-frozen rules.

Accordingly v8.2:

- does not count as empirical evidence;
- does not count as an empirical conclusion;
- increments the empirical ledger by `0`;
- does not open focal cross-role values before calibration qualification.

## Machine checks

`tests/test_level_c_sampling_plan_v8_2.py` verifies:

- pre-outcome 30/93 target freeze;
- exact 28/30 sensitivity boundary;
- exact 92/93 specificity boundary;
- unchanged scientific thresholds and unchanged v8.1 evaluator;
- failure of the v8.2 gate at the historical 60-negative minimum;
- acceptance of one false positive at 93 negatives;
- rejection of two false positives at 93 negatives;
- exclusion of unresolved/failure rows from resolved target counts.

The focused CI also writes an outcome-blind audit receipt so the exact count implications are preserved independently of later field outcomes.
