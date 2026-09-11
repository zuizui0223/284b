# Pre-field flagship submission readiness v0.1

## Primary target

**Ecology Letters — Method**

Current journal constraints checked during manuscript preparation:

- main text <= 5,000 words;
- <= 6 figures, tables or text boxes;
- unsolicited Method requires an approved proposal before full submission;
- proposal <= 300 words and should describe nature, novelty and disciplinary contribution;
- strong Method proposals may include quantitative information or a conceptual figure;
- a successful Method should present a specific generalizable technique rather than a taxon-specific result.

## Repository readiness

### Green — already closed

- Level-A empirical anchor is terminal and deduplicated: 283/283 eligible held-out cells within frozen ceilings; 5 adequacy failures remain unresolved.
- Level-B fresh empirical endpoint remains explicitly unopened.
- Level-C focal biological endpoint remains explicitly unopened.
- Exact synthetic benchmark is implemented and tested with no focal Level-C values.
- v8.1 exact-confidence repair was performed prospectively before field-calibration data entry.
- calibration operating characteristics are audited prospectively.
- manuscript automated tests enforce the Ecology Letters word/display limits and Level-C claim closure.
- current PR head CI has passed.
- <=300-word proposal v0.3 is drafted.
- proposal email is drafted.
- compact proposal figure is drafted.
- claim/evidence ledger and prohibited-inference list exist.
- literature-positioning audit explicitly concedes prior imperfect-detection, co-occurrence and independent-validation literature.

### Yellow — finish before sending proposal

1. **Notation cleanup.** Use `a` for valid-key fraction and `pi` for biological violation prevalence throughout benchmark-facing manuscript/figures. Do not reuse `v` for both concepts.
2. **Author qualifications.** Freeze final author list and add one concise directly relevant qualification sentence per necessary contributor. Do not inflate biography.
3. **Proposal figure visual QA.** Export the SVG to the format preferred for email attachment and verify legibility at ordinary page width.
4. **Current manuscript canonicalization.** After notation cleanup and base-rate insertion, designate one manuscript version as canonical and point submission-boundary tests to it.
5. **Closer-antecedent search.** Complete the targeted search around ecological model adequacy, preregistration/Registered Reports and inference from negative evidence. This is a novelty stress test, not an excuse to broaden the paper.

### Yellow — finish before full manuscript submission, but not required for the proposal enquiry

- render final Figures 1–4 and Table 1;
- finalize references and journal style;
- create immutable archival release / DOI and insert exact code/data availability identifiers;
- freeze authorship contribution statement;
- verify all numerical manuscript sentences against `CLAIM_EVIDENCE_LEDGER`;
- perform final language and figure-legibility pass.

## Explicitly not required for Paper 1

- Level-C field calibration data;
- opening Cremastra or Belonocnema focal cross-role values;
- a hard Level-C biological result;
- process knockout;
- Level-B empirical completion.

Adding any of these before Paper 1 is submitted would change the paper's prospective boundary and should require a new claim-evidence ledger rather than silent insertion.

## Separate pre-data decision for future Level-C work

The v8.1 operating-characteristic audit shows that the 30-positive / 60-negative minima are feasibility minima rather than power-optimized sample sizes. No sample-size change is authorized in the current manuscript branch. If larger calibration samples are desired for the future Level-C study, they must be frozen before collection or outcome inspection, ideally in a separately versioned field-design decision or Registered Report Stage 1 package.

## Go / no-go rule for sending the Ecology Letters proposal

**Go** once the five proposal-level yellow items above are closed. The proposal does not need new biological data.
