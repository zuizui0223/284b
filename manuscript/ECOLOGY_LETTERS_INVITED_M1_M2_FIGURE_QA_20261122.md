# Invited M1+M2 figures — signed data and rendered-file QA (2026-11-22)

**Disposition:** Figure source, tests and 12 rendered display files complete on draft PR #74; overall manuscript remains `HOLD_FOR_SENSITIVITY_REVIEW`. This is a figure-production receipt, **not a new biological endpoint**, new analysis or journal submission.

## Rendered package

- GitHub Actions figure run: [45032824094](https://github.com/zuizui0223/284b/actions/runs/45032223808), **success** on branch head `54d47342ac122ff7ef87b0866bdb8b88dec7ffc2`.
- Artifact ID: `14758348052`, `invited-m1-m2-figures-restored-v2`, ZIP digest `sha256:2a97feb9e090c39f49bdba7560cbeec421a306c52af2d673a9b5ebd13fe10aea`.
- Contents: figures 1–4 in each of **PDF, SVG, and 300 dpi PNG** (12 plot files), plus `FIGURE_README.md`. Archive ZIP integrity test passed and all 13 entries were present.
- Output builder: `scripts/build_invited_m1_m2_figures.py`. Reproducible contract tests: `tests/test_invited_m1_m2_figures.py`; dedicated figure CI `.github/workflows/invited-m1-m2-figures.yml`.
- The 4 PNGs were inspected visually after rendering. The first version of Figure 2 had a legend/data overlap, and the first version of Figure 3 had overprinted panel headers. These were corrected; one final right-panel label in Figure 3 was shortened after a 173-mm print proof. All final figures were visually inspected, and vector PDFs were rendered as print proofs.
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

## 173-mm print-size proof (vector, not raster enlargement)

The [Ecology Letters author guidelines](https://onlinelibrary.wiley.com/page/journal/14610248/homepage/ForAuthors.html) describe standard output widths of 82, 110 and 173 mm and prefer vector PDF/EPS for line art. The four final vector PDFs were each transformed to a **173-mm-wide PDF page** without rasterizing the plot, rasterized separately at 200 dpi for visual QA, and checked for readable labels and non-overlapping annotations. The source PDF was not modified to change the underlying data.

Minimum font sizes read from the vector PDFs *after* scaling to 173 mm (an internal approximate 6-pt legibility preflight, not a journal-stated minimum): **Figure 1 7.056 pt; Figure 2 6.004 pt; Figure 3 6.096 pt; Figure 4 6.118 pt**. The final standalone PDF figures are vector and the visible 173-mm proofs have no detected overlaps. The actual compiled journal portal proof, however, still must be checked after figures are placed alongside text and captions.

## Remaining manuscript gates

- **Not yet submission-ready:** full M1+M2 supplement assembly, final journal manuscript/portal proof and reference/word-count conformity, archive DOI, verified author metadata and approval.
- **Human scientific decision still outstanding:** coauthors must explicitly approve reporting taxon-level non-exceedance under a source-repair sensitivity where one historically evaluable cell becomes unresolved.
- Do not merge PR #74, release as submitted, modify frozen q95 or Level-A historical evidence, or count this figure package as an additional empirical endpoint merely because CI completed.
