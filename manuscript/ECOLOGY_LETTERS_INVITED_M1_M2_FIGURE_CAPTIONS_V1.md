# Invited Ecology Letters M1+M2 — figure captions and accessibility text v1

These captions apply only to the completed positive-core method and empirical results. They do not imply that the held-out comparison proves a causal ecological interaction.

## Figure 1. Prospective same-target relation endpoint

Preserved-specimen and human-observation records are separated before fitting independent source-specific distribution models. Both models address the same taxon and comparison frame. A separate successor-taxon panel calibrates 24 empirical discordance envelopes across procedure-by-accessible-area conditions; those envelopes are frozen before the 12 focal held-out taxa are opened. Cells lacking adequate answers from either source remain unresolved. This diagram is a schematic, not an additional empirical result.

**Alt text:** Four connected stages show independent record sources, source-specific ecological models, an independently frozen discordance reference, and a held-out evaluation with an unresolved option. An annotation states that held-out outcomes did not choose the procedures, accessible areas or thresholds.

## Figure 2. Cross-source reproducibility across prospectively held-out taxa

For each of 12 held-out plant taxa, the maximum ratio of observed `1 − Schoener's D` discordance to its procedure-specific and accessible-area-specific frozen empirical reference ceiling is shown across evaluable cells. A dashed vertical line denotes equality to the reference ceiling (ratio 1). All 12 taxon maxima are below 1; the largest is 0.988 for *Nothofagus betuloides*. The 12 taxa, rather than the 283 evaluable procedure-by-area cells, are the independent biological replication units. Of 288 prespecified diagnostics, 283 were evaluable and five remained unresolved because a source-specific answer was inadequate or missing. The nearest-rank 95th-percentile reference is an empirical calibration, **not** a nominal 95% prediction interval or `α=0.05` test.

**Alt text:** Horizontal bars show 12 species ranked by the highest ratio of cross-source disagreement to a predeclared ceiling. Every bar ends to the left of a dashed ceiling at 1. The highest bar belongs to *Nothofagus betuloides* at 0.988. Five out of 288 procedure-by-area comparisons were unresolved and are excluded from the plotted maxima.

## Figure 3. Exact class-conditional cost of collapsing invalid observation keys into biological zero

The first two panels compare the gated and zero-collapsed false-violation and true-violation rates in the frozen illustrative state-dependent scenario. With `a₁ = P(valid key | F=true)=0.70`, `a₀ = P(valid key | F=false)=0.90`, valid-key sensitivity `q=0.95` and specificity `sp=0.99`, false-violation rate increases from 0.035 to 0.335 and true-violation sensitivity increases from 0.891 to 0.991. The third panel illustrates the exact identities `ΔFPR=1−a₁` and `ΔTPR=1−a₀`. Both increments are `1−a` **only if** validity is class independent (`a₁=a₀=a`). Values are analytical consequences of a specified observation model, not empirical estimates of missingness or ecology.

**Alt text:** Two paired bar charts show that coding invalid keys as zero increases both false-violation calls and apparent true-violation sensitivity. A third panel plots the downward line 1 minus valid-key fraction, marking increments of 0.30 and 0.10 for two different classes. The difference between those marks emphasizes class-dependent validity.

## Figure 4. Qualified-call reliability and prevalence conditioning

The false-discovery fraction (FDF) among qualified hard-violation calls is
plotted against the true-violation prevalence `π_all` **before** the validity
gate. The two curves use illustrative valid-key sensitivity `q=0.80` and
specificity `sp=0.99`. The solid curve assumes equal nonzero class validity
(`a₁=a₀`), in which case `π_valid=π_all` and
`FDF=(1−π_all)(1−q)/[(1−π_all)(1−q)+π_all sp]`. The dashed curve allows
class-dependent validity (`a₁=0.70,a₀=0.90`), for which the corresponding
population-prevalence formula must retain `a₁,a₀` in both terms. At
`π_all=0.10`, the respective FDF values are 0.645 and 0.586; the latter
has `π_valid=0.125`. The curves are analytical illustrations, not estimates
of natural missingness, false discovery or focal Level-C interactions.
Qualified observations are necessary for admissible negative inference, but
do not automatically guarantee attribution reliability.

**Alt text:** Two descending theoretical FDF curves are plotted against
population true-violation prevalence. A solid equal-validity curve and a
dashed class-dependent-validity curve are highlighted at population prevalence
0.10, with FDF values of 0.645 and 0.586 respectively. The caption explains
that the difference comes from how validity changes the composition of
qualified calls rather than from any new biological observations.
