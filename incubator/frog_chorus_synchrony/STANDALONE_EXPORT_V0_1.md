# Standalone reproducibility export v0.1

The public frog article should not expose the whole 284b development tree.

The export is deliberately limited to:
- the JAE-formatted anonymized manuscript;
- final claim boundary and cross-dataset synthesis;
- frozen NAAMP and FrogID contracts;
- primary, secondary and robustness receipts;
- scripts needed to regenerate final analyses and figures;
- a SHA-256 file manifest.

Raw NAAMP, FrogID and ERA5 data are not redistributed. Source identifiers and retrieval contracts are preserved instead.

Run:

```
python incubator/frog_chorus_synchrony/scripts/build_standalone_export.py
```

Output:

```
build/frog-chorus-synchrony-standalone/
```

This directory is the intended content for a future standalone public repository and Zenodo snapshot.
