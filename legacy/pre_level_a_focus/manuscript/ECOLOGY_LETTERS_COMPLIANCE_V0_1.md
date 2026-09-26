# Ecology Letters Method compliance checklist v0.1

Checked against current journal guidance on 2026-09-11.

## Proposal stage

- Article type: Method.
- Unsolicited proposal required before full submission.
- Proposal maximum: 300 words.
- Proposal must describe nature/novelty and contribution to ecology.
- Current draft: `ECOLOGY_LETTERS_300WORD_PITCH_V0_1.md`.

## Full manuscript constraints if invited

- Main text maximum: 5,000 words.
- Maximum display items: 6 total figures/tables/text boxes.
- Abstract maximum for Method: 150 words.
- Method paper must focus on the method itself and demonstrate it in a case study.
- Quantitative methods require high-quality code and sufficient transfer information.
- Title page must include article type, running title (<45 characters), keywords, word counts, reference count and display-item counts.
- Data/code availability statement required; final public archival DOI(s) should be supplied before publication.
- Cover letter must explain novelty, general ecological interest and how the paper differs from recent work by the authors/coauthors.

## Internal go/no-go checks before sending proposal

1. The novelty must be stated as a new prospective inference architecture / negative-state identifiability principle, not as an SDM workflow.
2. Figure 1 must demonstrate transfer beyond species-distribution modelling.
3. Level-C candidate names should support the method, not dominate the title/abstract.
4. The 283/283 result must remain conditional on adequacy and five unopened cells must remain unresolved.
5. No Level-C focal biological value may be opened to strengthen the proposal.
6. Add or surface a compact synthetic benchmark showing the false-inference cost of uncalibrated non-detection if this can be done without touching focal Level-C values.
7. Ensure all code used for figures and benchmarks has a stable command-line entry point and frozen test coverage.
8. Archive a submission release with immutable hashes before final submission.

## Editorial-risk diagnosis

Highest risk: editors may view the framework as a workflow rather than a sufficiently novel Method. The manuscript must therefore lead with the inferential object and the new stopping/identifiability rule, not with implementation details.

Second risk: editors may view the Level-C sequence as incomplete empirical research. Counter this by clearly separating completed empirical Level A from the prospective Level-C stress test, and by making the Level-C contribution the identification of a general measurement boundary rather than an unfinished biological result.

Third risk: case-study breadth. Counter this with the same-target multi-taxon held-out benchmark, two biologically distinct Level-C architectures, synthetic qualification, and explicit transfer examples across pollination, host dependence, trophic interactions, stage coupling and sensor ecology.