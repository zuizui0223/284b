# Paper 1 display final-QA v0.1

**Scope:** six-item v0.10 full-submission display route.  
**Scientific state:** unchanged; empirical ledger = 1.

## Route

1. `figure1_relation_endpoint_contract_v0_2.svg`
2. `figure2_level_a_empirical_anchor_v0_2.svg`
3. `figure3_relation_layer_and_event_function_v0_2.svg`
4. `figure4_parallel_openability_audits_v0_1.svg`
5. `figure5_invalid_state_decomposition_v0_3.svg`
6. `TABLE1_CLAIM_EVIDENCE_MATRIX_V0_2.md`

Canonical captions remain `FULL_SUBMISSION_FIGURE_CAPTIONS_V0_2.md`.

## Mechanical QA — guarded in CI

- all five SVG files parse as XML;
- every rectangle stays inside its declared canvas;
- every explicit text anchor stays inside its declared canvas;
- Figure 1 is deterministically reproducible from `build_paper1_v09_display_figures.py`;
- Figure 3 is deterministically reproducible from the same builder;
- Figure 2 retains the repaired 970-pixel canvas and explicitly states that the 283 evaluable cells are not independent successes;
- Figure 4 retains multiline STOP messages and states that no focal biological outcome is opened;
- Figure 5 retains the generalized `a1/a0` decomposition and unresolved-state-ablation wording;
- display count remains exactly six.

## Scientific-message QA

### Figure 1

Must show the downstream Method object rather than a Level A→E progression:

- five-part contract;
- `opening_rule_reference`;
- canonical deterministic JSON;
- SHA-256 fingerprint;
- calibrated soft and directional hard state logic;
- explicit unresolved state;
- hashing is not proof of outcome blindness.

### Figure 2

Must lead with biological replication:

- 12 independent held-out taxa;
- 288 repeated diagnostics;
- 283 evaluable;
- five unresolved;
- 0/12 taxa with an envelope exceedance;
- q95 is an empirical source-discordance envelope, not nominal 95% coverage.

### Figure 3

Must carry both parts of the conceptual argument:

- identical perfect marginals can support `v=0` and `v=0.5` under classical Fréchet–Hoeffding coupling bounds;
- the accepted hard object is an event-key relation `E(k) -> F(k)`;
- provider absence is not functional absence unless provider closure or an independent calibrated aggregate-function channel establishes it.

### Figure 4

Must remain a stopping-rule figure:

- Cremastra and Belonocnema shown in parallel;
- negative functional/resource state uncalibrated;
- hard endpoint opening false;
- no confirmed/falsified dependency language.

### Figure 5

Must retain:

- `FPR_zero-FPR_gated = 1-a1`;
- `TPR_zero-TPR_gated = 1-a0`;
- `1-a` only as equal-validity corollary;
- zero collapsing described as an ablation of the unresolved-state guard, not a state-of-the-art comparator.

## Manual export check still required

CI guards SVG geometry and content, but a final human visual check is still required after journal export/rescaling for:

- text legibility at the submitted physical size;
- line wrapping after any PDF/EPS conversion;
- symbol rendering (`→`, subscripts, Greek letters);
- journal-mandated font embedding;
- grayscale readability if required by production.

This manual export check is an administrative/production check and does not change scientific claims.
