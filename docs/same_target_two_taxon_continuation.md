# Explicit continuation of two timeout-censored executions

The original attempt (run 34032659571, SHA 5d16212538d8b25d12235d2bb11b9a5e184a113b)
is permanently recorded as cancelled. The terminal audit recovered 45 artifacts;
only index 8 (Alisma plantago-aquatica) and 35 (Populus tremula) are missing.

This continuation authorizes exactly six jobs: both missing taxa at each original
M = 150, 300, 500 km. Completed original taxa are never refitted, and unresolved
fits in their saved artifacts are never rescued. All 47 taxa, 2,256 source cells,
and 1,128 paired cells remain in the experiment.

## What changes, and what does not

The original runner is checked out at its execution SHA and checked against its
Git blob. Its AST is executed with only two inserted statements: a shallow,
in-memory restriction of the M loop and an input fingerprint. The original
fitting body, both evidence views, background sampling, spatial blocks, 43
predictors, eight procedures, four-fold adequacy, and candidate-derived background
seed are unmodified. No original source or scientific contract is edited.

Each partition reconstructs the shared source-blind geometry. Fingerprints of
prepared source covariates, geometry, block assignments, predictors, keyset and
background seed must agree across a taxon's three partitions before assembly.
These hashes do not persist raw coordinates or record IDs. Per-partition package
versions are recorded. The original installation recipe is reused, but all its
transitive dependencies were not locked: byte-for-byte environment identity is
not asserted.

The original liblinear model uses random_state=None. The continuation preserves
that setting, rather than silently assigning a new seed. Separate processes do
not replay the interrupted process's RNG trajectory. This is continuation of the
same statistical procedure, **not bitwise reproduction** of lost computations.
There is one recorded continuation attempt; no outcome-dependent retry or choice
among alternative fits is allowed. Failure or further timeout remains visible.

## Mixed provenance and prediction boundary

A pre-execution receipt validates the original cancelled attempt and the exact
45 original archive identities against terminal audit artifact 10002365752
(SHA256 ee03b5ef5bad16fa16456ed1ad8c3324f4e812a15aa184c44c332e6a08221df7).
Six successful partition artifacts (including retained scientific fit failures)
are required. Three partitions per taxon are assembled using opaque byte copies,
not prediction decoding or model deserialization. The prediction path is a
Parquet dataset directory, which the existing authorized Arrow reader accepts.
Part-specific hashes replace a fictitious single-file hash; original 45 artifacts
remain unchanged. An entirely empty partition is preserved, and a nonempty
partition is placed first for schema discovery when available.

This explicitly supersedes the **execution-completeness** requirement for this
continuation: 45 immutable originals plus two fully accounted continued taxa,
not a claim that the first attempt succeeded. The old controller remains intact.
The complete mixed-provenance bundle is sealed before the unchanged aggregate
and reference-feasibility scripts run. Existing strict q95 calibration can run
only after this complete continuation, with at least 30 eligible taxa in each
procedure/M cell. All 24 cells remain; unavailable references stay unresolved.
No threshold, taxon panel, or paired outcome is selected from the terminal audit.

Outputs are artifacts only. Held-out predictions and process interventions stay
closed until reference outputs are independently reviewed and committed. A PR
runs only validation. A separate explicit trigger commit on the continuation
branch starts the six real jobs after review; merging this implementation does
not restart anything by itself.
