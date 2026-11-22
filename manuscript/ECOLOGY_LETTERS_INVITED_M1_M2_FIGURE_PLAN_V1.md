# Ecology Letters invited positive-core figure plan v1

Maximum main-text goal: four display items.

## Figure 1 — Evidence-bounded relation endpoint

Panels:
A. Independently generated ecological answers.
B. Prospective relation endpoint: common key, adequacy gates, opening rule.
C. Three states for a soft comparison: consistent, attention, unresolved.
D. Hard-negative logic: only an identified negative on a valid key can contradict a directional relation.

Message: unresolved is an inferential state, not a failed biological result.

## Figure 2 — Positive Level-A held-out closure

Primary biological replication unit: 12 held-out taxa. Source-restoration sensitivity uses the **same 12 taxa** and is not another independent replication.

Panel A: taxon-level maximum observed discordance / frozen envelope.
- range 0.509-0.988
- horizontal line at 1
- all 12 below 1

Panel B: original versus source-repaired *accounting* of the same prespecified design.
- Historical original input: **288** prespecified diagnostics, **283** evaluable, **5** unresolved, **0/12** taxa with exceedance.
- Repaired input (510 restored GBIF Parquet objects; 59 original taxa refitted; 24 new q95 envelopes): **288** prespecified diagnostics, **285** evaluable, **3** unresolved, **0/12** taxa with exceedance.
- **282 original evaluable cells retained, one original evaluable cell lost, three original unresolved cells gained**. Use a compact two-row accounting flow that makes the *failed full-retention criterion* explicit. Do not connect 283 and 285 as if they were independent replicates.

Inset: closest **historical** *Nothofagus betuloides* cell, 0.38625 observed vs 0.39085 envelope (margin −0.00460). The **restored** closest is *Eucalyptus globulus* at M=500 km (margin −0.01691), using its separately recalibrated q95.

Do not display 283 or 285 cells as independent biological replicates. **0/12 is conditional on evaluability**; do not label the source-repair result as a full robustness pass.

## Figure 3 — Exact cost of deleting unresolved states

Panel A:
`FPR_zero - FPR_gated = 1-a1`.

Panel B:
`TPR_zero - TPR_gated = 1-a0`.

Panel C:
equal-validity diagonal `a1=a0=a` where both increments are `1-a`.

Panel D:
representative frozen scenario:
- false violation 0.035 -> 0.335
- apparent true-violation sensitivity 0.891 -> 0.991

Message: added decisiveness is not free.

## Figure 4 — Qualification versus reliability

Plot FDF against true violation prevalence for representative q/sp combinations.

Mark:
`pi=.10, q=.80, sp=.99 -> FDF≈.645`.

Message: admissible measurement is distinct from reliable endpoint-level attribution; aggregation/replication remains a separate layer.

## Supporting information

- all 12 historical taxon ratios and the original five unresolved cells;
- source-completeness sensitivity flow table showing 283 → 282 retained + 1 lost, and 5 → 3 gained + 2 still unresolved; 285 repaired evaluable total;
- all four original/repaired eligibility-transition keys and original frozen four-fold lower-bound diagnostics, including *Nothofagus antarctica* 0.5070 → 0.4945 across the 0.50 threshold;
- complete **24-row** original/repaired reference q95 comparison; q95 recalibrated from 47 original reference taxa without using held-out scores;
- descriptive **282 common opened-cell** comparison of original vs repaired discordance and margin (median changes +0.000698 and +0.000744), with explicit ranges and non-independent sampling;
- 8,748-scenario structural benchmark grid and exact mathematical audit;
- separate historical and restored source manifest/artifact digests and endpoint fingerprints; label retrospective data repair **not independent validation**.
