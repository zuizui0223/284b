# Reviewer attack matrix v0.1 — frog chorus synchrony

This matrix records the strongest foreseeable attacks on the validated programme and the permitted response. It is not a menu for post hoc result hunting.

| Attack | Evidence / response | Status |
|---|---|---|
| “Rainfall effects on frog calling are old.” | Agree. Hsu 2006, Xie 2017 and many species-level studies establish that antecedent. Novelty is event-level multispecies overlap plus independent conditional validation. | Addressed |
| “Brodie et al. 2025 already showed chorus synchrony after rain.” | Agree that rainfall can synchronize onset of chorusing. Their unit is species-specific nightly chorus onset/activity at three sites over two wet seasons; our response is same-window multispecies co-calling in two continental systems. | Must cite explicitly |
| “This is just species richness.” | NAAMP response is the fraction of standardized 5-min stops with >=2 positively calling species; FrogID is one vs multiple species within one short recording. It is an overlap probability, not seasonal/site richness. | Addressed |
| “Synchrony is too strong a word.” | Operationalize as **short-window co-calling synchrony/overlap**. Do not imply sub-second phase synchrony or coordinated individual behavior. | Wording guard |
| “NAAMP effect is tiny and borderline.” | State this openly: OR 0.969, p=0.0388; >=8-stop sensitivity passes, complete-10-stop sensitivity p=0.058. The cross-dataset claim relies on independent FrogID replication, not effect size inflation. | Addressed |
| “FrogID is opportunistic and biased.” | Validation is expert-validated, outcome-independent deterministic sample, conditional on >=1 calling species, adjusted for state×month/year/hour, and robust to weather-cell and recorder clustering. Site-selection bias remains a limitation. | Qualified |
| “Spatial species-pool differences could create the association.” | A post-opening robustness contract was frozen: NAAMP within-route diagnostic and FrogID within-ERA5-cell conditional analysis. Results must be reported regardless of direction. | **Pending robustness receipt** |
| “NAAMP and FrogID measure rainfall differently.” | Correct. NAAMP uses programme-reported DaysSinceRain; FrogID uses prospectively frozen ERA5 antecedent dry days. This is directional replication across measurement systems, not effect-size replication. | Addressed |
| “Rain merely activates all frogs; this is not community synchrony.” | FrogID conditions on recordings already containing >=1 calling species, so rain still predicts one-versus-multiple calling species among acoustically active recordings. | Major strength |
| “Rain changes particular species interactions.” | Prespecified NAAMP pairwise network-density effect is null (p=0.724). No individual edge effects were opened. | Claim rejected |
| “Effect is strongest at seasonal shoulders.” | Prespecified shoulder interaction is null (p=0.082; four-window sensitivity also null). | Claim rejected |
| “Temperature is the real driver.” | NAAMP temperature is secondary and not independently validated. Rain remains associated after joint weather/day-of-year adjustment in NAAMP and validates independently in FrogID. | Qualified |
| “Temperature QC was post hoc.” | The raw secondary exposed implausible values; physical plausibility QC was documented and all excluded counts reported. Temperature is never allowed to replace the rain primary and remains secondary. | Wording guard |
| “The two continental effects should be meta-analysed.” | Forbidden: sampling units, outcome conditioning, and rainfall metrics differ. Synthesis is directional/replicative only. | Addressed |
| “Rainfall causes the synchrony.” | Observational designs do not identify a causal effect. Use ‘associated with’ or ‘predicts’, not ‘causes’. | Hard boundary |

## Current strongest claim

> Across independent North American and Australian acoustic monitoring systems, more recent rainfall is associated with greater short-window overlap in frog calling across species; conditional FrogID validation indicates that the pattern is not explained solely by rainfall increasing the probability of any frog calling.

## Current mechanism boundary

The result is consistent with **shared environmental activation** at short timescales. It does not identify:
- interspecific facilitation;
- pairwise network rewiring;
- sub-second call synchronization;
- reproductive success;
- demographic consequences;
- a causal rainfall effect.
