# FrogID external validation model contract v0.4

This is the final weather-transport freeze before any FrogID rainfall value or validation effect is opened.

## Frozen sample

- 40,754 deterministic FrogID recordings
- 18,174 multi-species recordings
- 1,623 rounded 0.25-degree weather cells
- event selection: first byte of SHA-256(eventID) < 16
- coordinate uncertainty <=25 km

## ERA5 exposure

Weather comes from Earthmover's public Icechunk ERA5 temporal layout.

Exact variable:
- `tp` = Total precipitation
- units = metres
- each value is a 1-hour accumulation ending at `valid_time`
- chunks = 8,736 hours × 12 latitude cells × 12 longitude cells

The frozen sample requires 470 unique chunks (about 2.37 GB uncompressed upper bound), so the transport gate passes.

For each event:
1. map the rounded coordinate to the nearest ERA5 grid cell;
2. resolve timezone from the original event coordinate;
3. assign each hourly accumulation to a local day using the **midpoint of the accumulation interval** (`valid_time - 30 min`);
4. sum to local daily precipitation in mm;
5. exclude the event day;
6. count consecutive prior days with <1 mm precipitation, stopping at the first wet day, capped at 30;
7. analyse `z(log1p(dry days))`.

No missing required weather hour is imputed. Tiny negative ERA5 values from [-1e-8,0) m may be set to zero; more negative values fail closed.

## Frozen validation model

```
multi_species_recording
  ~ dry_z
  + State × Month
  + z(calendar year)
  + sin(local hour)
  + cos(local hour)
```

Primary cluster = ERA5 weather cell.

Directional validation hypothesis: **dry_z < 0**.

The NAAMP result is not replaced by this validation, regardless of outcome.
