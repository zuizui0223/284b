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

Primary display unit: 12 held-out taxa.

Panel A: taxon-level maximum observed discordance / frozen envelope.
- range 0.509-0.988
- horizontal line at 1
- all 12 below 1

Panel B: design accounting.
- 288 prespecified diagnostics
- 283 evaluable
- 5 unresolved
- 0/12 taxa with exceedance

Inset: closest *Nothofagus betuloides* cell, 0.38625 observed vs 0.39085 envelope.

Do not display 283 cells as independent replicates.

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

Plot FDF against **population** true-violation prevalence, explicitly distinguishing equal-validity and class-dependent-validity cases using the same illustrative `q=.80, sp=.99`.

Mark at `pi_all=.10`:
- equal validity (`a1=a0>0`): FDF≈.645;
- class-dependent validity (`a1=.70, a0=.90`): `pi_valid=.125`, FDF≈.586.

The original single-curve expression uses `pi_valid` (prevalence among valid keys), not automatically `pi_all`.

Message: admissible measurement is distinct from reliable endpoint-level attribution; aggregation/replication remains a separate layer.

## Supporting information

- all 12 taxon ratios;
- five unresolved cells;
- 8,748-scenario benchmark grid;
- exact mathematical audit;
- endpoint fingerprints and receipt hashes.
