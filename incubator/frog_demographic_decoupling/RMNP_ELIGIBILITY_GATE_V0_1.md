# RMNP eligibility gate v0.1

This gate is frozen before opening Pseudacris detection values or habitat values for analysis.

The confirmatory unit is `site_name × calendar_year` during 2003–2022.

A site-year is adult-confirmed only when at least one visit has `psma=1` and stage code `A`.

A reproductive observation visit is valid only when percent surveyed is available. Then:
- `psma=0` → y=0;
- `psma=1` with E or L → y=1;
- `psma=1` with A but no E/L → y=0;
- `psma=1` with only J/M/U/NA or blank stage → unresolved;
- `psma=NA` → invalid.

The model opens only if all three endpoint conditions hold:
1. >=50 adult-confirmed site-years;
2. >=30 adult-confirmed site-years with >=2 valid endpoint visits;
3. >=15 adult-confirmed site-years with at least one E/L detection.

Before fitting the primary depth model, complete process covariates must retain >=40 site-years and both depth classes must have >=10 site-years. Fish is secondary and is omitted—not replaced—if either Y or N has <10 complete site-years.

Duplicate `site_name × date` rows fail closed.

This audit may report only eligibility and covariate coverage. It may not fit or summarize ecological effects.
