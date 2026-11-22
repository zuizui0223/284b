# Invited M1+M2 figures — signed data and rendered-file QA (2026-11-22)

**Disposition:** Figure source, tests and 12 rendered display files complete on draft PR #74; overall manuscript remains `HOLD_FOR_SENSITIVITY_REVIEW`. This is a figure-production receipt, **not a new biological endpoint**, new analysis or journal submission.

## Rendered package

- GitHub Actions figure run: [45032223808](https://github.com/zuizui0223/284b/actions/runs/45032223808), **success** on branch head `382bb0bb65d94b746d7d2a93a5b7eb3e87b78bf4`.
- Artifact ID: `14758595402`, `invited-m1-m2-figures-restored-v2`, ZIP digest `sha256:4ac5980a12f57201bb9659c9061c73d24ca389a26ecfb3c67c9bd2792b2dfdaa`.
- Contents: figures 1–4 in each of **PDF, SVG, and 300 dpi PNG** (12 plot files), plus `FIGURE_README.md`. Archive ZIP integrity test passed and all 13 entries were present.
- Output builder: `scripts/build_invited_m1_m2_figures.py`. Reproducible contract tests: `tests/test_invited_m1_m2_figures.py`; dedicated figure CI `.github/workflows/invited-m1-m2-figures.yml`.
- The 4 PNGs were inspected visually after rendering. The first version of Figure 2 had a legend/data overlap; the first version of Figure 3 had overprinted panel headers. These were corrected and the **second rendered artifact** was inspected. The final PDF versions of Figures 2 and 4 were separately rasterized at 150 dpi and reviewed for layout parity.
- Captions and alt text: `manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_FIGURE_CAPTIONS_V1.md`.

## Figure 2: signed Level-A statement, not unqualified robustness

- Historical original endpoint (9,705 Parquet objects): **12 taxa; 288 prespecified diagnostics; 283 evaluable and 5 unresolved; 0/12 taxa with calibrated q95 exceedance**.
- Retrospectively restored 10,215-object source: **same 12 taxa; 285 evaluable and 3 unresolved; 0/12 taxa with exceedance**. All 24 reference q95 conditions were recalibrated separately from restored 47-taxon reference data.
- The original 283 evaluable cells split into **282 still evaluable + 1 lost**. The original 5 unresolved cells split into **3 newly evaluable + 2 still unresolved**. Consequently, the predeclared strict 283/283 retention condition **failed**. Do not call repaired-source replication independent or fully robust.
- The repaired 288-key table and all 24 reference thresholds were parsed and compared key by key: 12 distinct taxa × 24 conditions; 288 unique keys; no missing reference threshold; all 285 open cells have internally consistent observed discordance, threshold and signed margin; all margins at or below zero; all 3 closed cells have no observed discordance. Max restored taxon-wise observed/reference ratio was **0.9502954933** for *Eucalyptus globulus*; historical maximum was **0.988232** for *Nothofagus betuloides*.
- Figure 2 panel A depicts **two source-version-specific maxima** per taxon, each normalized to its own corresponding q95 threshold; connecting markers are descriptive, not estimates of biological change. Panel B shows the exact 2×2 cell-state transition matrix (282, 1, 3, 2).

## Figure 4: mathematical result, not observational estimation

- Plot uses the qualified-call FDF `(1-pi)a1(1-q) / [(1-pi)a1(1-q)+pi*a0*sp]`, with unconditional violation prevalence `pi`.
- At `pi=.10, q=.80, sp=.99`, three mathematical examples are plotted: equal positive validity **0.645161**; `a1=.70,a0=.90` **0.585774**; `a1=.90,a0=.70` **0.700389**.
- If no qualified violation calls are possible, FDF is undefined. Source-validity fractions are illustrative **synthetic inputs**, not measured detection rates or a Level-C result.
- The exact original identities `ΔFPR=1-a1` and `ΔTPR=1-a0` are preserved.

## Remaining manuscript gates

- **Not yet journal-ready:** final-width (e.g. ~173 mm if required by target journal) typesetting proof and its minimum lettering sizes, complete M1+M2 supplement assembly, reference/word-count conformity, archive DOI, author metadata and author approval.
- **Human scientific decision still outstanding:** coauthors must explicitly approve reporting taxon-level non-exceedance under a source-repair sensitivity where one historically evaluable cell becomes unresolved.
- Do not merge PR #74, release as submitted, modify frozen q95 or Level-A historical evidence, or count this figure package as an additional empirical endpoint merely because CI completed.
