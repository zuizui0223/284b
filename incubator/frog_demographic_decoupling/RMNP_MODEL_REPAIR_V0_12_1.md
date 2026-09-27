# RMNP model repair v0.12.1

The pre-effect estimability audit retained 113 eligible site-years and 110 with known fish state, enough for the frozen fish interaction test. Depth was known for only 59 eligible site-years, leaving 57 complete primary-model site-years.

Therefore, **before any coefficient sign or magnitude is opened**, depth is removed from the confirmatory adjustment set and retained only as a complete-case sensitivity analysis.

Nothing else changes.

Primary:
`evidence ~ reproductive_stage * fish_present + centered_year + max_effort + n_visits`

Primary estimand:
`reproductive_stage:fish_present`

Prespecified direction:
negative.

Secondary temporal model:
`evidence ~ reproductive_stage * centered_year + fish_present + max_effort + n_visits`

A high-effort sensitivity uses only site-years with maximum surveyed fraction >= 76–99%.

This repair is missingness-driven, not result-driven.
