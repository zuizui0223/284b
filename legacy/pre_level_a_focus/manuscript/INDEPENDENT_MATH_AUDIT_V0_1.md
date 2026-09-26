# Independent mathematical audit v0.1

Purpose: independently verify the central quantitative claims used in the pre-field manuscript and Ecology Letters Method proposal. This audit is performed from the declared equations and frozen thresholds; it does not read focal Level-C biological values and does not change the empirical ledger.

## 1. Exact invalid-key identity

Let:

- `a` = probability an event key is valid for negative inference;
- `q` = probability of detecting the required function on a valid key when the function is truly present;
- `sp` = probability of a negative observation on a valid key when the function is truly absent.

For a biologically compatible key (`F=true`):

- zero-collapsing false-violation probability = `1 - a q`;
- gated false-violation probability = `a(1-q)`.

Therefore

`(1-aq) - a(1-q) = 1-a`.

For a true violation (`F=false`):

- zero-collapsing true-violation sensitivity = `1 - a(1-sp)`;
- gated true-violation sensitivity = `a sp`.

Therefore

`[1-a(1-sp)] - a sp = 1-a`.

Both identities are exact algebraic consequences of the two decision rules. No simulation assumption is required.

## 2. Conditional key sensitivity

With per-opportunity true-event probability `r`, per-event detection probability `s`, and `n` opportunities:

- `P(at least one true event) = 1-(1-r)^n`;
- `P(at least one detected true event) = 1-(1-rs)^n`.

Because detection implies a true event, conditional key sensitivity is

`q = [1-(1-rs)^n] / [1-(1-r)^n]`.

This matches the benchmark implementation.

## 3. False-discovery fraction among gated calls

Let `π` be true violation prevalence. For qualified valid keys:

- false-call mass = `(1-π) a (1-q)`;
- true-call mass = `π a sp`.

Thus

`FDF = (1-π)(1-q) / [(1-π)(1-q) + π sp]`.

The factor `a` cancels. Therefore observation-process qualification and endpoint-level false-discovery reliability are distinct quantities; preserving invalid keys as unresolved removes invalid-key mass from both numerator and denominator but does not solve the base-rate problem.

## 4. Exact one-sided 95% Clopper–Pearson boundaries

Frozen thresholds:

- sensitivity >= 0.80;
- specificity >= 0.95;
- one-sided 95% exact lower bound must also meet the corresponding threshold;
- minimum known-positive count = 30;
- minimum known-negative count = 60.

Independent beta-quantile calculation gives:

- 27/30 sensitivity successes: lower bound `0.7614021427` — fails;
- 28/30: lower bound `0.8046739563` — passes;
- 59/60 specificity successes: lower bound `0.9233600051` — fails;
- 60/60: lower bound `0.9512970867` — passes.

Therefore the manuscript's critical counts of **28/30** and **60/60** are correct.

## 5. Independent pass-probability checks at the frozen minima

For sensitivity with `n=30`, critical count 28:

- true sensitivity 0.80 -> `0.0441789852`;
- 0.85 -> `0.1514006073`;
- 0.90 -> `0.4113512396`;
- 0.95 -> `0.8121788131`;
- 0.98 -> `0.9782821655`;
- 0.99 -> `0.9966822907`.

For specificity with `n=60`, critical count 60:

- true specificity 0.95 -> `0.0460697990`;
- 0.97 -> `0.1608066690`;
- 0.98 -> `0.2975531427`;
- 0.99 -> `0.5471566424`;
- 0.995 -> `0.7402609577`;
- 0.999 -> `0.9417362622`.

These match the repository operating-characteristic audit to rounding.

## 6. Independent 80% nominal pass-probability checks

First sample size at or above 80% nominal pass probability, using the same exact rule:

Sensitivity threshold 0.80:

- true sensitivity 0.85 -> `n=365`, critical 305, pass probability `0.8017786275`;
- true sensitivity 0.90 -> `n=82`, critical 72, pass probability `0.8057063960`;
- true sensitivity 0.95 -> `n=30`, critical 28, pass probability `0.8121788131`.

Specificity threshold 0.95:

- true specificity 0.97 -> `n=601`, critical 580, pass probability `0.8001953127`;
- true specificity 0.98 -> `n=234`, critical 228, pass probability `0.8091388318`;
- true specificity 0.99 -> `n=124`, critical 122, pass probability `0.8715535097`;
- true specificity 0.995 -> `n=93`, critical 92, pass probability `0.9206112641`;
- true specificity 0.999 -> `n=60`, critical 60, pass probability `0.9417362622`.

These also match the repository audit.

## 7. Audit conclusion

No mathematical discrepancy was found in the central pre-field quantitative claims. The exact benchmark identity, conditional sensitivity equation, false-discovery expression, minimum critical counts and reported operating characteristics are mutually consistent.

This audit does not validate candidate-specific field performance and does not authorize any Level-C endpoint opening.
