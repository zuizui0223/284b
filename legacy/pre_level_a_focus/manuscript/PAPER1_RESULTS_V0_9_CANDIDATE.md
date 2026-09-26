# Paper 1 Results candidate v0.9

**Status:** noncanonical manuscript prose for integration after editorial review. No focal Level-C biological endpoint is opened.

## Results

### A prospectively frozen same-target relation closed on 12 fresh taxa

The 12 prospectively held-out taxa generated 288 prespecified cell diagnostics. Both independently reconstructed answers passed adequacy in 283 cells; five remained unresolved. Each taxon contributed 22-24 evaluable cells. No held-out taxon contained an empirical-envelope exceedance among its evaluable cells: the taxon-level result was therefore **0 of 12 taxa with an exceedance**.

The 283/283 cell count is a diagnostic summary rather than an independent sample size. The closest opened cell was *Nothofagus betuloides* under the 150-km accessible area and `predictive_forward|logit_l2_C1_degree2`, with discordance 0.38625 against a frozen envelope of 0.39085, a margin of 0.00460. One of 283 evaluable cells lay within 0.025 of its envelope and six lay within 0.05. The result supports same-target cross-source coherence conditional on answer adequacy and the prespecified empirical envelopes; it does not imply exact source invariance or nominal 95% coverage.

### The hard relation is not determined by accurate marginals

The relation-layer separation result is structural rather than empirical. For `E -> F`, exact marginals constrain but do not identify `v=P(E=1,F=0)`. At `p_E=p_F=0.5`, the classical bounds permit the full range from `v=0` to `v=0.5`. Thus even perfect marginal answers can be compatible with both no hard violations and maximal violation among positive `E` keys. The endpoint contract therefore contains information not supplied by marginal answer accuracy alone: the biological relation, common key and contradiction rule.

### Removing the unresolved state creates exact class-specific error increments

For state-dependent observation validity, the zero-collapsing ablation increased false violations by exactly `1-a1` and apparent sensitivity to true violations by exactly `1-a0`. The increments are unequal whenever validity differs between compatible keys and true violations. For example, with `a1=0.70`, `a0=0.90`, `q=0.95` and `sp=0.99`, the false-violation probability increased from 0.035 under the gated rule to 0.335 under zero collapsing, an increment of 0.30, while apparent true-violation sensitivity increased from 0.891 to 0.991, an increment of 0.10.

The original 8,748-scenario equal-validity grid contained 4,320 calibration-passing and 4,428 calibration-failing combinations. Across every passing combination, both increments equalled `1-a` to floating-point error below `1.2 x 10^-16`. Under the frozen `q >= 0.80` process-qualification floor, gated key-level false-violation probability did not exceed 0.20 in that grid, whereas the zero-collapsing ablation reached 0.776 because invalid keys were relabelled as biological negatives. When calibration failed, the gated rule emitted no hard negative calls.

Process qualification did not by itself imply high reliability of a called violation. For example, with violation prevalence `pi=0.10`, `q=0.80` and `sp=0.99`, the false-discovery fraction among called violations is approximately 0.645. This separates authorization of a negative state from the later aggregation or replication rule required for a biological conclusion.

### Two real systems independently stopped at the same measurement boundary

Finite response-blind screening retained two biologically different systems with separated relation, event and function evidence streams. `CREMV3-007` combined external breeding-system evidence, same-inflorescence fruit outcome and pollinia-carrying camera observations for *Cremastra appendiculata* var. *variabilis*. `BELV3-012` combined independent host-specificity evidence, natural adult emergence and live-oak budbreak observations for *Belonocnema treatae*.

Both systems passed source materialization, common-key alignment, direct event/function estimands, provenance separation and no-post-hoc-redefinition gates. Both then stopped before focal endpoint opening because the negative functional state was not independently calibrated. Positive pollinia-carrying contacts were directly informative in Cremastra, but camera non-detection was not validated as absence of effective pollination. In Belonocnema, emergence and budbreak were separately observed, but an unrecorded usable-resource state could not be distinguished from incomplete observation.

Candidate-specific calibration audits found no independent existing stream sufficient to estimate the required sensitivity and specificity without conditioning on focal outcomes, and identified supplementary/raw sources did not reconstruct the missing calibration. These stops are therefore measurement-boundary results, not biological negatives. No focal Level-C dependency is confirmed or falsified in Paper 1; the next admissible information for either system is new candidate-specific calibration or direct measurement of the required aggregate function.