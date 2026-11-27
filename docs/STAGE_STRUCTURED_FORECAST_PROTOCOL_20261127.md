# Stage-structured leading indicators of later forest replacement — three-census pilot

2026-11-27. Outcome-blind specification for a new temporal endpoint. Existing 9-state regional results and the original M1/M2 invited manuscript remain immutable. The previous ecological hypothesis of universally increasing demographic opposition with niche similarity was not supported; this is a different question, motivated by it. This is exploratory and not a registered independent confirmation.

## Ecological question

Can a juvenile cohort's relative abundance and change reveal forthcoming changes in adult tree composition **before the adult community itself changes**? Is this a genuine leading indicator beyond existing adult trends and static juvenile stocks, or largely immediate growth of already observed large saplings into the adult inventory class? Distinguish local juvenile/adult disequilibrium from a climatic niche shift. Predictions are not evidence of competition, reproduction, climate-change effects or population replacement at reproductive maturity.

## Fixed data and temporal design

- Reuse the SHA-256-locked FIA PLOT, COND, SUBPLOT, TREE archives and WorldClim normals used in the earlier pilot, all 37 input hashes recorded. Regions fixed: northeast (ME,NH,VT), central Appalachia (PA,WV,VA), Great Lakes (MI,WI,MN). No substitute regions, outcome-driven species selections or archive version changes.
- Three linked same-physical-plot censuses t0 (2004–2012), t1, t2 (through 2024), both intervals 4–8 years, PREV_PLT_CN link for each. Choose earliest eligible triple per physical plot. Only national four-subplot design, single accessible forest condition occupying all subplot AND microplot area, all four subplots sampled, no recorded nonzero treatment codes on the three visits. Reject visits with invalid live tree size, species, subplot or incompatible expansion factors rather than interpreting those stems as missing zeros. These restrictions select persistently sampled forest, not all forests.
- Adult-sized stems: live DBH >=5 inches on 4 subplots (TPA_UNADJ near 6.018046); early saplings: 1–<3 inches and late saplings: 3–<5 inches on 4 microplots (TPA near 74.965282). Counts within each fixed sampled stratum; never compare raw juvenile versus adult density as though sampled areas are the same. Size classes are operational, not reproductive maturity. No seedling claims. USDA FIESTA data summaries: https://usdaforestservice.github.io/FIESTA/articles/FIESTA_datSum_examples.html .
- Plot identity split via prior deterministic hash: arm 0 contributes only earliest 2004–2012 reference visit, arm 1 contributes forecasting triples. Reference stage climatic occupancy (WorldClim bio1 2°C and bio12 200-mm bins) is a secondary test, not necessary for primary local juvenile forecasts. Only bins with >=10 reference plots, species >=40 occupied reference plots in each stage. This is historical realized occurrence, not fundamental niche; public coordinates displaced. No temporal climate exposure is used.

## Primary comparison (frozen)

At t1, retain all adult species with >=2 sampled stems, at least two eligible species per plot, including observed absence in the future t2. Each species-plot is one row, centered within its plot on the same fixed t1 species set. Response: 5-year scaled change in log adult counts with +0.5 offset, from t1 to t2, minus its within-plot mean. No conditioning on the t2 change direction. This describes changes in relative adult-sized composition, not all species colonization.

Prediction models fitted independently within each region, 5 spatial folds assigned by stable hash of 1° geographic blocks (train and heldout blocks disjoint; no random row split), equal total weight per plot, fixed ridge penalty 0.01 times total training weight after weighted RMS scaling from training only. Species fixed effects are plot-centered; baseline includes current adult log counts, preceding 5-year-scaled adult change, current mean adult diameter, small-adult fraction, and adult abundance/history interactions with stand density. No future values in features, no tuning. Record performance against the same test rows:
- A adult-only baseline.
- S A + early and late sapling stock at t1 (log1p counts).
- H S + each stage's preceding 5-year-scaled log1p count change t0→t1.
- Secondary E/L: A + early-only or late-only stock and preceding change.
Primary contrast H vs A and important mechanistic contrast H vs S: paired heldout plot-equal mean squared error reduction. Report absolute and percentage reductions, conditional spatial-block bootstrap intervals (500, fixed seed), all regions separately. Stable-adult subgroup: total variation distance of complete adult count proportions between t0 and t1 <=0.10, defined using no future data. Evaluate on same heldout predictions (not refit or select thresholds).
 
## Mechanism and climate sensitivity (secondary, fixed)

- For each t2 live adult stem whose PREV_TRE_CN points to a t1 live microplot sapling with same physical plot/species/subplot, count directly tracked sapling-to-adult crossings. Predict relative adult change with those exact observed crossings removed from t2; this removes only identified carryover, not all ingrowth outside microplots or unlinked transitions.
- Separately for species-plot groups whose t1 adult stems ALL have unique same-plot/species/subplot t2 links with explicit status live/dead/removed, predict relative fraction of baseline adults dead or removed (never assign missing link to death). Require >=2 eligible species in a plot. Report support, no interpretation as mortality-only or causal competition. Use same spatial folds, A/S/H. A positive juvenile signal for total adult change but not either control would support a limited size-transition explanation; absence of gain in controls is not proof of mediation.
- Secondary climate-reference test: for heldout species/plots with adequate stage reference occupancy, calculate log ratio of juvenile-to-adult occurrence probability in climate bin minus the same species' overall reference log occurrence ratio (+0.5 smoothing of occupied plot count; identical denominators within bin); compare H plus this mismatch versus H on identical eligible rows. No extrapolation, no causal warming claim.

## Decision rule

Report all effects and uncertainties, including adverse results. A meaningful predictive gain is a positive error reduction replicated geographically and evident in stable adult plots; history-specific signal requires H outperforming S, not merely H outperforming A. If no support, do not change definitions after outcome opening. If gains vanish after identified crossing removal or do not predict linked losses, report endpoint specificity and limits of links. This pilot uses related source material and repeated taxa; no increment to prior confirmatory ledger. 
