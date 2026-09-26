# NAAMP secondary contract v0.1

This contract was frozen after the rainfall primary was opened, but **before any
temperature or seasonal-position effect was opened**. These secondary analyses were
declared in the fresh-programme protocol and cannot replace the primary rainfall result.

## Temperature

Each run receives a single temperature from the arithmetic mean of numeric
`AirTemp` values across non-skipped stops, after conversion using the run-level
`TempScale` metadata.

The secondary temperature model uses only runs with at least 8 valid stop temperatures:

```
multi-species stops / sampled stops
  ~ z(log1p DaysSinceRain)
  + z(mean AirTemp_C)
  + State + RunNumber + RouteType + z(year)
```

SEs remain cluster-robust by State × RouteNumber.

Directional hypothesis: **temperature coefficient > 0**.

## Seasonal shoulder test

NAAMP defines RunNumber as a state-specific seasonal sampling window. The last window
is frozen structurally as the maximum RunNumber observed for that State among
UnifiedProtocol runs; only states with a maximum of 3 or 4 are eligible.

A run is a **shoulder** when it is:
- RunNumber 1, or
- that state's final sampling window.

H3 is the interaction:

```
rain_z × shoulder
```

with the same primary adjustments. Because larger `DaysSinceRain` means less recent
rainfall, the predicted shoulder-synchrony hypothesis is **interaction < 0**.

No alternate shoulder definition may be tried after opening.

## H4

Network reconfiguration remains closed. Pair universe and topology metric must be
frozen separately before any species-pair effect is read.
