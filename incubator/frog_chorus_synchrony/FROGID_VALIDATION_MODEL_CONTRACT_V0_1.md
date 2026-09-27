# FrogID external validation model contract v0.1

This contract is frozen **before ERA5 rainfall is retrieved**.

## Question

Does the weak NAAMP result recur in an independent continent and sampling design?

The FrogID response is defined per expert-validated recording:

- 0 = exactly one calling frog species;
- 1 = two or more calling frog species.

This is **conditional on a FrogID recording being submitted**. It is not an occupancy or absence model.

## Sample

The sample is fixed by `SHA256(eventID)[0] < 16` and cannot be changed after weather opening:

- 40,754 recordings
- 18,174 multi-species recordings
- 1,623 rounded ERA5 0.25-degree cells
- coordinate uncertainty <=25 km

## Rain metric

ERA5 daily precipitation is accessed through Open-Meteo.

A wet day is **>=1 mm/day**, following the standard ETCCDI convention.

The event day itself is excluded. Exposure is the number of consecutive dry days immediately preceding the recording date, capped at 30. Thus:

- 0 = yesterday was a wet day;
- larger values = a longer antecedent dry spell.

Primary predictor: `z(log1p(antecedent dry days))`.

Predicted direction: **negative**.

## Model

```
multi_species_recording
  ~ dry_z
  + State × Month
  + z(Year)
  + sin(local hour)
  + cos(local hour)
```

Binomial logit; cluster-robust covariance by ERA5 0.25-degree cell.

Support requires the dry-spell coefficient to be negative, two-sided p<0.05, and its 95% CI to exclude zero.

## Sensitivities

1. coordinate uncertainty <=10 km;
2. same point model but cluster-robust covariance by recorder.

No additional state/species/month search is authorized.

## Interpretation boundary

A matching negative coefficient would support **cross-system recurrence of rainfall-associated community temporal overlap**. It would not prove rainfall causally synchronizes frogs.
