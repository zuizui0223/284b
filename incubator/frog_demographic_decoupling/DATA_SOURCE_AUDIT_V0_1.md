# Public-data source audit v0.1

## Decision

The project is **feasible enough to continue**, but the original single-dataset framing was too optimistic.

### 1. Flanders Natterjack is the strongest primary dataset
The publisher states that monitoring is at the site level, with three nocturnal visits per site, and all relevant life stages are counted: egg strings, tadpoles, terrestrial juveniles (<2 cm and >2 cm), observed adults and calling males. The reproductive period is April–August.

This is the only currently identified source that directly supports a same-programme full-chain candidate:
`adult breeding activity -> egg -> larva -> terrestrial juvenile`.

Dataset: https://www.gbif.org/dataset/099911ec-84c6-453f-995a-3ad064ec9d71  
DOI: 10.15468/2xfw8y.

### 2. Mohonk is not authorized as the primary juvenile-recruitment endpoint
Mohonk is extremely valuable because it pairs repeated amphibian observations with weather/water conditions across 11 vernal pools and a very long time span. The occurrence table contains chorus, adult, amplectant-pair, egg-mass, juvenile and tadpole/larval fields.

However, monitoring is concentrated in spring. Until raw date distributions demonstrate that `Juv_n` represents juveniles from the same breeding cycle for a focal species, current-year juvenile recruitment is not identified. Mohonk is therefore restricted prospectively to:
- adult/call -> egg;
- egg -> larva;
- hydroclimate modulation of those transitions.

Dataset DOI: 10.15468/dypfbs.  
Data paper DOI: 10.3897/BDJ.8.e50121.

### 3. PINK provides broad independent replication
PINK covers 243 ponds near the Belgian coast, >10 amphibian species, and standardized repeated surveys from 2007–2016. The protocol records calling adults and searches for eggs/larvae, including dedicated larval netting.

It is a good independent multi-species test of upstream stage coupling, but is not assumed to contain a full juvenile-recruitment endpoint.

Dataset DOI: 10.15468/jvtefa.

### 4. Additional Meetnetten programmes may provide cross-programme linkage
Separate public datasets exist for:
- chorus counts: DOI 10.15468/d4bu8j;
- larvae/metamorph counts: DOI 10.15468/swgure.

These are useful only if fixed site/time identities can be joined without coordinate-nearest matching or other post hoc reconstruction.

### 5. CROA is promising but short
The CROA urban-amphibian programme in southern France has standardized repeated surveys since 2023 and records adult, juvenile, egg, tadpole and calling behaviour. It is useful for later external replication, not yet for a long-term temporal claim.

Dataset DOI: 10.15468/xfz3uy.

## Closest prior art

Greenberg, Zarnoch & Austin (2017) used 22 years of continuous amphibian trapping at eight ephemeral wetlands and directly tested effects of adult breeding effort, weather and hydroregime on juvenile recruitment across six anuran species (DOI 10.1002/ecs2.1789). They found that breeding effort was important for some species but not others and that hydroregime/rainfall strongly affected recruitment.

Therefore the new project must **not** claim novelty for the observation that breeding effort can fail to predict recruitment.

## Remaining novelty target

The prospective novelty is:

> Localize demographic decoupling to explicit life-cycle transitions, estimate the observation process rather than treating non-detection as failure, and test whether the same stage-specific bottleneck recurs across independent standardized monitoring programmes.

This target remains empirically unopened. No raw stage outcome distribution has been used to select a favourable transition.

## Next gate

Obtain raw DwC-A / EDI exports and run the estimability audit. No hypothesis coefficient or sign is to be opened before:
1. site-year replication is counted;
2. stage positives are counted;
3. explicit absence vs missingness is audited;
4. stage timing is examined;
5. a source-specific deterministic life-stage normalizer is frozen.
