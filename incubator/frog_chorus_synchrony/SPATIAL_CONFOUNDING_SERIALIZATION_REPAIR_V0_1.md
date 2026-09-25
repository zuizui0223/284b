# FrogID within-cell artifact serialization repair v0.1

The repaired within-cell estimator completed and printed its full effect payload before
the workflow failed.

The opened diagnostic effect was:

- beta (within-cell probability scale): **-0.04264901148705781**
- 95% CI: **[-0.05175442812124915, -0.033543594852866475]**
- p = **4.298613216030537e-20**
- informative ERA5 cells: **1,071**
- recordings: **40,020**

The failure occurred **after those values were produced**, when the wrapper attempted
to parse the base validation JSON file. The base script terminates its JSON text with
the two literal characters `\n`, rather than a newline, so `json.loads()` raised
`Extra data`.

This repair removes only that literal trailing marker before JSON parsing. It does not:

- rerun a different estimator;
- change the sample;
- change the rainfall metric;
- change any adjustment;
- change the opened within-cell coefficient;
- change the frozen spatial-robustness classification rule.

The rerun is solely to emit the already-opened diagnostic as a durable workflow artifact.
