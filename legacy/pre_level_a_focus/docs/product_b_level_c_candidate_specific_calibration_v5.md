# Product-B Level C v5 — candidate-specific calibration boundary

## Why v5 exists

Level-C v4 established that a conservative absence classifier can be qualified synthetically without turning sparse detections, missingness, or observer failure into biological negatives. That result does not validate either retained empirical observation process. v5 therefore asks a narrower question: **for each retained candidate, has the actual observation process been independently calibrated well enough that a zero/non-detection can identify `F(k)=false`?**

## Frozen candidates

No new candidate search is permitted. The only retained systems are:

- `CREMV3-007` — *Cremastra appendiculata* var. *variabilis*; function channel = effective pollinia transfer during the frozen flowering opportunity.
- `BELV3-012` — *Belonocnema treatae* / live-oak budbreak; function channel = required newly flushed host resource during the frozen dependent opportunity.

The same numerical qualification thresholds are used for both systems: sensitivity at least 0.80, hard false-negative rate at most 0.20, specificity at least 0.95, plus full-window coverage and explicit separation of observation failure from confirmed absence.

## Candidate-specific audit

### Cremastra

The 2026 sensor-camera study supplies strong positive validation: multi-year monitoring covered complete flowering periods and repeatedly detected *Bombus diversus* queens carrying pollinia. Recorded effective visits correspond strongly to pollinia removal and fruit development. But the paper explicitly notes that quantitative validation against continuous recording would be necessary to establish detection completeness. The present evidence therefore cannot estimate the probability that the sensor process detects an effective pollination event when one occurs but is rare, short, or otherwise missed. A zero camera record cannot be promoted to `F=false`.

### Belonocnema

The natural budbreak and adult-emergence streams are separate and biologically aligned. Budbreak is an appropriate resource-state signal because newly flushed tissue is the ephemeral resource required for reproduction. However, the available dataset metadata do not provide a candidate-specific repeated-observation or cross-observer calibration from which false-negative detection of the required budbreak state can be estimated. Missing or unobserved budbreak therefore cannot be promoted to confirmed resource absence.

## Operational consequence

Neither retained candidate passes C1-C6. Both terminate as `calibration_unavailable`, a nonbiological state. No focal event/function values, hard invariant, soft cross-check, or process knockout may be opened under v5. The v4 synthetic pass cannot substitute for candidate-specific calibration, and thresholds cannot be relaxed after inspecting focal outcomes.

## What would unlock a future empirical endpoint

For Cremastra, a prospective calibration must overlap sensor monitoring with a gold-standard observation stream over the same flowers and opportunity windows, define effective pollination labels independently of fruit outcome, and estimate sensitivity / false-negative performance while explicitly handling out-of-frame, knocked-over, malfunctioning, and incomplete-window cameras.

For Belonocnema, a prospective calibration must repeat budbreak/resource assessments through the complete dependent window, independently validate the resource-state threshold (e.g. repeated or cross-observer scoring), estimate sensitivity / false-negative performance, and distinguish a missed visit or missing record from confirmed pre-budbreak resource absence.

This closes v5 as an identifiability/calibration result, not a biological negative or empirical conclusion. The global 284b empirical ledger remains 1.
