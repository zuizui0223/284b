# NAAMP synthesis receipt v0.1

The fresh frog chorus programme now has one positive primary, one strong robust secondary,
and two informative negative secondary endpoints.

## Supported

**Recent rainfall.** Across 9,399 standardized runs, multi-species calling was modestly
more common closer to recent rain (OR = 0.969 per +1 SD `log1p(DaysSinceRain)`,
p = 0.0388). The >=8-stop sensitivity passes; the complete-10-stop sensitivity is
directionally identical but narrowly crosses zero (p = 0.0580).

**Warm conditions.** The temperature association is much stronger. After excluding only
two runs outside the prospectively frozen [-10,45]°C plausibility range, OR = 1.474 per
+1 SD run-mean temperature (p = 9.62×10^-46). The association remains positive and
supported in both C-coded and F-coded source records.

**Not just seasonal progression.** In the joint model with a flexible day-of-year spline,
both recent rainfall (OR = 0.946, p = 5.44×10^-4) and temperature (OR = 1.492,
p = 1.21×10^-48) remain associated with greater multi-species calling overlap.

## Not supported

The preregistered seasonal-shoulder amplification is not supported (p = 0.082; four-window
state sensitivity p = 0.628).

Rainfall also does not measurably densify the pairwise co-calling network conditional on
the run-level species pool (p = 0.724; repeated-edge sensitivity p = 0.790).

## Current ecological interpretation

The cleanest current result is:

> Warm conditions and recent rainfall are associated with greater temporal overlap in
> frog calling activity, but the data do not support a corresponding reorganization of
> pairwise co-calling network structure.

One mechanism remains unresolved: greater multi-species overlap could occur simply because
more stops become acoustically active. The next frozen endpoint decomposes the observed
multi-species probability into `P(any call)` and
`P(multispecies | any call)`. This decomposition was frozen after the main findings and
is explicitly mechanistic/diagnostic, not a replacement confirmatory endpoint.

## External validation

The Sunshine Coast dataset remains unopened for weather effects. Its source explicitly says
frogs were counted by sightings or hearing their calls, but the archived short codes
(`HEA/SEE/SHD/HAN/OPP`) have not yet been authorized into call states by an explicit
source mapping. No code is guessed from its spelling.
