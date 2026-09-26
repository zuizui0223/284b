# Journal of Animal Ecology scientific adaptation v0.1

This is an **anonymized scientific routing document**, not a title page and not a submission.
Human authorship, affiliations and declarations are intentionally absent.

## Proposed title

**Recent rainfall predicts transient temporal niche compression in frog communities across continents**

Alternative more literal title:

**Recent rainfall predicts greater short-window co-calling in frog communities across continents**

The first is conceptually stronger; the second is safer if editors consider "temporal niche
compression" too interpretive.

## Numbered abstract — JAE format

1. **Environmental cues can align animal activity, but community temporal niches need not be fixed.** Rainfall-driven frog calling is well established at species and seasonal scales. We tested whether recent rainfall is also associated with greater overlap among species within the same short acoustic observation window.

2. **We used two independent continental monitoring systems under prospectively specified analysis rules.** In the North American Amphibian Monitoring Program, the response was the proportion of standardized 5-min route stops containing at least two calling species. We independently validated the directional prediction in expert-verified Australian FrogID recordings linked to ERA5 precipitation, conditional on a recording already containing at least one calling species.

3. **Recent rainfall predicted greater short-window multispecies co-calling in both systems.** Across 9,399 NAAMP runs and 93,383 sampled stops, co-calling declined weakly with increasing time since rain (OR per 1 SD increase in log-transformed days since rain = 0.969, 95% CI 0.941–0.998). In 40,754 FrogID recordings, increasing antecedent dry-spell duration likewise reduced the odds of multiple calling species (OR = 0.853, 95% CI 0.827–0.879).

4. **The direction persisted when static spatial differences were removed.** Within-route NAAMP analysis remained negative (beta = -0.0137 on the probability scale, 95% CI -0.0200 to -0.00737), as did within-ERA5-cell FrogID analysis (beta = -0.0426, 95% CI -0.0518 to -0.0335). Prespecified analyses did not support stronger rainfall effects at seasonal shoulders or rainfall-driven pairwise network densification.

5. **These results show that community temporal structure can be environmentally elastic at short timescales.** Shared rainfall cues are associated with transiently greater overlap in species' reproductive acoustic activity across independent systems, without evidence that particular species-pair relationships are reorganized. The observational design supports shared environmental activation, not a causal rainfall effect or interspecific facilitation.

## Keywords

acoustic community; anurans; ecoacoustics; environmental cue; rainfall; temporal niche; synchrony; weather

## General ecological contribution

The manuscript should open and close on this principle:

> **Temporal niche partitioning is not only a persistent property of communities; shared environmental pulses can transiently compress behavioural separation without changing which pairwise relationships are privileged.**

This is broader than frogs, but it is still directly supported only at the short acoustic
observation scale. Examples from birds, insects or other chorusing animals belong in the
Discussion as testable extensions, not as demonstrated generality.

## Novelty paragraph for editor screening

Rainfall effects on frog calling are not new, and rainfall-triggered chorus onset has been
documented directly. The advance here is a different scale of ecological organization:
whether multiple species occupy the same brief behavioural window. The same directional
relationship emerged in a standardized North American monitoring programme and an
independent Australian recording system. In the latter, the test was conditional on at
least one species already calling, separating multispecies overlap from simple activation
of any frog. Within-route and within-weather-cell analyses further show that static spatial
species-pool differences are insufficient to explain the replicated direction.

## Results hierarchy

### Primary
- NAAMP rain recency -> short-window multispecies co-calling.
- FrogID independent directional validation.

### Robustness
- NAAMP within-route.
- FrogID within-ERA5-cell.
- NAAMP >=8-stop and complete-route sensitivities.

### Mechanistic boundaries
- seasonal-shoulder amplification: unsupported.
- pairwise network densification: unsupported.

### Secondary
- NAAMP temperature association only; no independent validation.

## Mandatory wording boundaries

Use:
- "associated with";
- "predicts";
- "short-window co-calling overlap";
- "consistent with shared environmental activation";
- "temporal niche compression at the observation-window scale".

Do not use:
- "rainfall causes";
- "first evidence that rainfall synchronizes frogs";
- "interspecific facilitation";
- "network rewiring";
- "phase synchrony";
- "reproductive success";
- "demographic consequence".

## Data statement scaffold

Final submission should cite and archive:

- NAAMP USGS source data, DOI 10.5066/F7G44NG0;
- FrogID occurrence/call source, DOI 10.15468/wazqft;
- the exact FrogID weather linkage contract and pinned ERA5 daily-weather digest;
- analysis code and immutable result receipts from the extracted standalone repository.

The frog programme should be extracted from the 284b incubator before public submission so
Paper 1 relation-endpoint development is not mixed with this independent ecology article.
