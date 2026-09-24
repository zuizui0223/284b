# Frog climate-cue decoupling — fresh standalone incubator v0.1

This branch is a **new empirical programme** created from `main`, not from the closed RMNP stage-filtering branch. It cannot be used to rescue the RMNP null result.

## Question

> **When historically coupled breeding cues disagree, does frog calling become less predictable or shift toward one cue?**

The focal ecological idea is **climate-cue coherence**. Temperature, rainfall and seasonality often covary. Climate change and extreme weather can produce combinations such as anomalously warm but dry periods. A frog can then receive conflicting cues about whether conditions are suitable for breeding.

## Prior-art boundary

Thompson et al. (2022; DOI 10.1111/ddi.13634) used the first three years of FrogID and >150,000 records from 100 species to rank meteorological predictors of calling, including interactions. They found day-of-year and temperature were generally stronger predictors than rainfall and explicitly identified future uncoupling of historically associated cues as an unresolved problem.

Therefore this project does **not** claim novelty for showing that temperature, rainfall or day-of-year predict calling.

The target is different:

> **prospectively test the biological consequence of cue disagreement itself in later, held-out years.**

Reference years learn each species' expected cue response; later FrogID years test whether calling changes when temperature and rainfall cues disagree.

## Public data

Primary occurrence source:
- FrogID, Australian Museum
- DOI `10.15468/wazqft`
- GBIF dataset UUID `47c9fee2-619a-481c-a114-386bc4748256`
- ALA Darwin Core Archive endpoint `https://dwca-exports.ala.org.au/dr14760.zip`

FrogID dataset 7.0 spans 10 Nov 2017–9 Nov 2024 and contains >1 million expert-validated records of 228 species according to the Australian Museum release.

Sensitive records may be spatially buffered. The project therefore freezes a coarse 0.25° analysis grid and never interprets public coordinates as exact breeding-site locations.

## Frozen time split

FrogID project-years are defined as 10 November through 9 November of the following calendar year.

- **reference:** project-years 2018–2020
- **confirmatory:** project-years 2021–2024

The reference period overlaps the data era used by Thompson et al. (2022). The confirmatory years are reserved for the new cue-coherence test.

## Structural species gate

A species is eligible before any seasonal/cue outcome is opened only if it has:

- >=1,000 public records;
- >=6 project-years with >=50 records/year;
- >=20 occupied 0.25° cells;
- records in both the reference and confirmatory periods.

No species is selected because its cue-conflict result is strong.

## Current opening state

Only archive identity, fields, dates, project-year counts, species counts and coarse-cell coverage may be opened.

Calling-date distributions within years, climate values, cue directions and cue-conflict effects remain closed.
