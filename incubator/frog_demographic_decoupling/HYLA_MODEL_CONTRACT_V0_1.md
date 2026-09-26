# Hyla pre-outcome model contract v0.1

This contract is frozen **after the structural overlap audit but before any abundance association or environmental-effect direction is opened**.

## Focal system

The confirmatory Meetnetten analysis is now *Hyla arborea* only.

- exact shared location-species-years: 245
- *Pelobates fuscus*: 2 shared units → structurally rejected from the confirmatory analysis
- downstream primary stage: larva
- metamorph: secondary only

## Temporal unit

The response remains at the **downstream sampling-event level**.

For each larval survey event, adult breeding effort is:

`A_pre = max(calling-male count among chorus visits at the same location and year occurring on or before that downstream event)`.

This is fixed now so later analyses cannot use a future chorus count to explain an earlier larval survey or choose mean/max after seeing the association.

## Count model

If the effort-schema audit shows `number of sweeps` is populated on at least 80% of otherwise eligible Hyla downstream events, the primary response model is negative-binomial with a log link and `log(number of sweeps)` as an exposure offset.

Baseline:

`larval count ~ offset(log sweeps) + z(log1p A_pre) + centered year + (1 | locationID)`

If effort coverage is below 80%, the Meetnetten confirmatory count analysis **fails**. It will not be rescued by converting missing effort into a constant or by treating a single observed absence as true reproductive failure.

## Habitat-dependent conversion

The paper needs more than a positive adult→larva association. The confirmatory ecological estimand is the interaction between adult breeding effort and **one habitat modifier chosen only from structural variation**.

Priority is frozen:

1. fish present;
2. permanent water column;
3. water quality;
4. maximum depth.

The first modifier with enough structural variation is used. No larval count or effect estimate may enter this choice.

This ordering is biologically motivated because fish can directly remove anuran larvae, while hydroperiod/water state constrain successful aquatic development. Earlier work already shows fish can strongly affect *H. arborea* reproductive success, so the novelty is not a generic “fish are bad” claim. The target is whether habitat changes the **conversion of observed breeding effort into offspring production**.

## Confirmatory claim

If the interaction is supported, the allowed claim is:

> Pond context modifies how strongly observed adult breeding effort is translated into larval production.

It is still an observational association. It is not a causal management effect, adult recruitment estimate, population-growth estimate, ecological trap, or extinction early-warning signal.

## Outcome-blind fallback

If the effort gate fails, move to the already frozen PINK structural fallback. Do not weaken the Meetnetten effort requirement after seeing that 245 Hyla site-years are available.
