# Pre-field identifiability benchmark result v0.1

## Status

This is a synthetic, exact analytic benchmark. It reads **no focal Level-C biological values**, does not estimate candidate-specific detection performance, does not authorize endpoint opening, and increments the 284b empirical ledger by **0**.

Canonical implementation:

- `scripts/run_pre_field_identifiability_benchmark.py`
- `tests/test_pre_field_identifiability_benchmark.py`
- `results/pre_field_identifiability_benchmark_summary_v0_1.json`
- `results/pre_field_identifiability_benchmark_scenarios_v0_1.csv`

## Question

For a hard dependency

`E(k) -> F(k)`, 

what happens if an observation pipeline collapses incomplete, missing, or failed observations of `F` into `F=false`, rather than preserving them as `unresolved`?

Condition on an adequately positive dependent event `E(k)`. Define:

- `v = P(F=false | E=true)`, the true violation prevalence;
- `s = P(function detected | F=true, valid key)`, the key-level sensitivity;
- `sp = P(negative observed | F=false, valid key)`, specificity;
- `a = P(key is valid)`, the fraction with complete-window coverage and no missingness/device-observer failure.

Two rules are compared.

1. **Naive-zero:** any non-positive or invalid function observation is collapsed to `F=false` and can therefore trigger a hard violation.
2. **Identifiability-gated:** a hard violation is emitted only after the observation process passes the prospectively frozen sensitivity/specificity gate and the focal key itself is valid. Invalid keys remain `unresolved`.

## Exact result for a qualified observation process

For the naive rule:

`P(call violation | F=true) = 1 - a s`

`P(call violation | F=false) = 1 - a(1-sp)`

For the identifiability-gated rule:

`P(call violation | F=true) = a(1-s)`

`P(call violation | F=false) = a sp`

Therefore:

`naive false-violation rate - gated false-violation rate = 1 - a`

and

`naive true-violation sensitivity - gated true-violation sensitivity = 1 - a`.

This identity is the main benchmark result. **Every unit of apparent sensitivity gained by reclassifying invalid observation states as biological negatives is matched exactly by the same probability mass of additional false hard violations.**

The 8,748-condition deterministic grid verifies both identities to numerical error below `1.12e-16`.

## Full grid

The grid crosses:

- violation prevalence: 0.05, 0.10, 0.20, 0.50;
- per-opportunity event probability: 0.05, 0.20, 0.50;
- per-event detection sensitivity: 0.50, 0.80, 0.95;
- opportunities per key: 1, 5, 20;
- complete-window fraction: 0.50, 0.80, 1.00;
- missingness: 0, 0.10, 0.30;
- failure rate: 0, 0.05, 0.20;
- specificity: 0.80, 0.95, 0.99.

Total scenarios: **8,748**.

- calibration pass: **4,320**;
- calibration fail: **4,428**;
- gated hard-call mass in calibration-failing scenarios: **0**;
- maximum gated false-violation rate among passing scenarios: **0.20**;
- maximum naive false-violation rate among passing scenarios: **0.776**.

The equal-weight median false-violation rate over the full grid is 0.525 under naive-zero and 0 under the gated rule. This equal-weight grid median is a benchmark descriptor, not an ecological frequency estimate.

## Representative scenarios

### High missingness

With near-perfect key sensitivity but 30% missingness, `a=0.70`.

- naive false-violation rate: **0.300001**;
- gated false-violation rate: **0.0000011**;
- gated unresolved fraction: **0.30**.

The difference is exactly the 30% invalid-state mass.

### Device failure

With 20% device failure, `a=0.80`.

- naive false-violation rate: **0.200001**;
- gated false-violation rate: **0.0000013**;
- gated unresolved fraction: **0.20**.

### Incomplete observation window

With only 50% of keys having complete-window observation, `a=0.50`.

- naive false-violation rate: **0.500001**;
- gated false-violation rate: **0.0000008**;
- gated unresolved fraction: **0.50**.

### Mixed qualified regime

For the mixed scenario (`a=0.684`, key sensitivity 0.8653, specificity 0.95):

- naive false-violation rate: **0.4081**;
- gated false-violation rate: **0.0921**;
- naive true-violation sensitivity: **0.9658**;
- gated true-violation sensitivity: **0.6498**;
- unresolved fraction: **0.316**.

Again, both naive-minus-gated differences equal 0.316.

## A second result: qualification is not false-discovery control

Observation-process qualification is necessary for a hard test, but it does not by itself make every called violation reliable.

At the current threshold example (`s=0.80`, `sp=0.99`) and a true violation prevalence of 0.10, the gated false-discovery fraction among called violations is **0.6452** even with `a=1`. This follows from the base-rate term:

`FDF = (1-v)(1-s) / [(1-v)(1-s) + v sp]`.

This does **not** invalidate the v8 calibration gate. It clarifies its role: calibration is an **opening condition**, not a biological conclusion and not a posterior-error guarantee. Any future focal Level-C endpoint must separately freeze how evidence is aggregated across keys and how uncertainty in a putative violation is handled.

No v8 threshold is changed by this benchmark.

## Scientific interpretation

The benchmark turns the qualitative rule “non-detection is not absence” into an explicit decision-theoretic result for hard ecological dependency tests.

The gain from the identifiability gate is not that it manufactures higher apparent sensitivity. It deliberately gives up calls on invalid keys, converting them to `unresolved`. The exact identity shows why this is necessary: treating invalid keys as negative makes the test look more sensitive only by adding an equal amount of false contradiction risk.

The result is general to any ecological hard implication in which a dependent event is compared with a required function under an imperfect observation process. It is not specific to pollination, host dependence, Cremastra, or Belonocnema.
