# Product-B paired answer-check relation ladder

## Central question

Product-B now asks a broader validation question than whether one obligate pair is recovered correctly:

> When two ecological answers are obtained independently, but external biology says they should cohere in a declared way, do they actually agree closely enough to trust them?

The two answers must not tune, define, or fit one another. The relation, scale, comparison metric, and any soft discordance threshold are frozen before the focal comparison is opened.

## Relation ladder

The framework distinguishes relation types by how strongly biology constrains the expected agreement.

### Level A — same target, independent observation source

Examples: the same taxon modeled independently from preserved-specimen records and human-observation records, or from two genuinely independent observation systems.

Expected relation: broad environmental support should be concordant at a declared spatial/temporal scale, but exact identity is not required because detectability and sampling bias differ.

Default interpretation: **soft cross-check**. Excess divergence is `attention_required`, not a biological violation.

Primary use: calibrate how much disagreement is normal when the biological target is the same but the observation process changes.

### Level B — expected biological concordance

Examples: two independently estimated ecological responses that external experimental or natural-history evidence predicts should rank environments similarly.

Expected relation: symmetric or ordered concordance, with a relation-specific tolerance.

Default interpretation: **soft cross-check**.

### Level C — directional dependency

Example: `Y requires X` for persistence or reproduction.

Expected relation: Y support should be contained within X support at the declared persistence scale. X may be broader than Y.

Interpretation: may be a **hard invariant** when dependency and scope are genuinely mandatory; otherwise it can be downgraded prospectively to a soft directional cross-check.

### Level D — mutual dependency

Example: `X requires Y` and `Y requires X` at the same declared persistence scale.

Expected relation: both directed constraints must hold.

Interpretation: strongest **hard positive-control** class. A complete admissible failure in either direction falsifies compatibility under the frozen contract.

### Level E — life-stage coupling

Examples: independently modeled breeding/larval and adult/resource-linked stages where external biology declares a directional or symmetric persistence relation.

Interpretation: hard or soft must be declared prospectively from natural-history evidence; it is not inferred from observed overlap.

## One common language: discordance

Soft relation metrics are converted to a non-negative discordance quantity where smaller means more coherent. Examples:

- directional containment `C` -> `1 - C`;
- reciprocal containment -> worst-direction discordance `max(1-C(B|A), 1-C(A|B))`;
- Schoener's D -> `1 - D`;
- taxon-specific rank profiles -> joint-support-weighted rank-profile discordance.

These transformations do **not** imply that all discordance metrics share one universal numerical threshold. Each relation contract freezes its own metric and reference ceiling independently of the focal outcome.

## Calibration before confirmatory use

A soft `attention_required` flag needs an empirical reference rather than a post-hoc convenient cutoff.

The preferred first calibration is **same-target independent-source replication**:

1. choose an engineering calibration panel without inspecting paired model discordance;
2. fit each taxon independently under two disjoint observation modes;
3. compute the predeclared discordance metric;
4. freeze a predeclared quantile of the calibration distribution as the reference ceiling;
5. evaluate later held-out taxa against that ceiling without retuning it.

The calibration panel cannot be used as confirmatory evidence that its own members are coherent.

## Why same-target replication comes first

It is an unusually strong calibration case because the biological target is literally the same while the observation process changes. Therefore it estimates the amount of disagreement created by sampling and model reconstruction alone. This provides a baseline for interpreting more interesting cross-species biological relations.

If two independently adequate models of the same target diverge strongly, the first diagnosis is observation/model sensitivity. If same-target replication is stable but a biologically coupled pair diverges, the case for a relation-specific ecological problem becomes stronger.

## Process knockout extension

After a baseline pair is coherent, freeze process removals and recompute the same paired discordance.

A process is interesting when its removal creates or amplifies disagreement between answers that were previously coherent. This reframes process importance from single-model predictive contribution to **maintenance of biological cross-coherence**.
