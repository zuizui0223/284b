# Meetnetten effort-schema receipt v0.1

The fixed downstream DwC-A v1.24 contains a MeasurementOrFact extension, but the current published archive does **not** expose a `number of sweeps` measurement type.

- exact `number of sweeps` label present: **false**
- events with non-empty `number of sweeps`: **0**
- `sampling effort type` is present on 399 events, but this is not a quantitative sweep count and does not satisfy the frozen exposure requirement.
- many MeasurementOrFact rows have blank `measurementType`; their values are **not reverse-engineered** because the pre-outcome gate did not authorize semantic recovery from outcome-adjacent value patterns.

No occurrence abundance was read by this audit.

## Decision

Under `HYLA_MODEL_CONTRACT_V0_1`, quantitative sweep-effort coverage had to reach 80% before the Meetnetten negative-binomial count analysis could open.

It does not.

Therefore the **Meetnetten confirmatory count model is structurally closed**. The 245 exact *Hyla arborea* site-years remain a useful feasibility result but cannot be rescued by:
- assuming constant sweep effort;
- replacing sweep count with qualitative sampling-effort type;
- inferring hidden measurement labels from values;
- switching to binary absence because the count model cannot open.

The next candidate is the already frozen fallback #2: **PINK within-programme adult-call / egg / larva transitions**.

Adult and larval abundance associations remain unopened.
