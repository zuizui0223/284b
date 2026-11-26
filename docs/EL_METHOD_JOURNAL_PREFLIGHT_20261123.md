# Ecology Letters invited Method — journal-format preflight (2026-11-23)

**Scope:** current repository Markdown manuscript and integrated SI, not the final Word/PDF proof or a journal portal submission. **Decision:** `HOLD_FOR_SENSITIVITY_REVIEW`.  
**Official guidance checked:** [Ecology Letters, Author Guidelines (Wiley)](https://onlinelibrary.wiley.com/page/journal/14610248/homepage/ForAuthors.html), sections 2 (article type), 9 (presentation), 11 (specifications), 19 (data/code availability), 21 (Supporting Information).

## Preliminary quantitative checks

| Check | Current source | Guidance | Status |
|---|---:|---|---|
| Article type | Invited Method candidate | Method is a commissioned/proposed article type | Invitation/proposal reference still needs verified human metadata |
| Abstract | **135 words** | ≤150 for Method | Within limit in this Markdown preflight |
| Main manuscript (sections 1–7, headings included) | **2,392 whitespace-separated words** | ≤5,000 for Method, excluding abstract, legends, references, title | Within limit in this Markdown preflight; refresh in formatted derivative |
| Figures | **4** main items | ≤6 total figures, tables or boxes | Within limit; vector PDF and print-width preflight already passed |
| Main-text tables / text boxes | **0 / 0** | Count together with figures | Within limit |
| Supporting Information | **11 sections**, including **2 tables** | Ancillary SI, referenced in main manuscript; author supplies final intended format | Scientifically assembled; upload/format proof outstanding |
| Running title | **29 characters** | <45 characters including spaces | Within limit |
| Keywords | **8** | Up to 10 | Within limit |
| Reference list | **9 entries** | Count required on title page | Count checked; formatting and citation accuracy require final human review |

**Counting method:** derived from the 2026-11-23 source Markdown. The abstract is the block between `## Abstract` and `## 1.`; main-text counts cover section headings 1–7 through, but not including, `## References`. Markdown markup and backtick delimiters are removed and whitespace-separated tokens counted. This is a **provisional reproducibility count**, not a guarantee that Microsoft Word, LaTeX or the submission portal will use identical tokenisation; final word counts must be updated from the actual journal-formatted derivative.

## Author/publisher controls not yet passed

1. The title page requires the **final author names/order, affiliations and e-mails**, verified corresponding author's full mailing/contact details, current word/reference/figure counts, and validated article type/invitation reference. The current title page deliberately contains placeholder metadata.
2. The journal requests **double-spaced text, consecutive page numbering**, consecutively cited figures, figure legends grouped at the end or separate, and a final compiled reviewer-facing PDF/proof. The source Markdown is not this compiled product.
3. Official guidance says **Supporting Information is published as supplied and no SI proof is provided**. The current integrated Markdown must therefore be converted to and checked in a publisher-accepted final format, with descriptive legends, tables and references intact.
4. The data/code accessibility statement and archival DOI(s) are **required at initial submission**. Public GitHub visibility and signed model artifacts alone are not a substitute for a permanent versioned DOI and any applicable data-source access obligations.
5. Funding/COI, contributor roles, permissions and AI disclosure require factual verification; any recommended/opposed reviewers must be chosen by the authors rather than invented.
6. The scientific pre-submission **coauthor decision** remains outstanding: the restored-source same-taxon 0/12 pattern recurs, yet **only 282/283** of the historically evaluable comparisons stay eligible. The predeclared strict retention result is **false** and must not be silently upgraded.

## What may be supplied for coauthor scientific review now

- Main manuscript: `manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_V1.md`
- Complete SI: `manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_COMPLETE_SI_V1.md`
- Cover letter and placeholders: `manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_COVER_LETTER_V1.md`, `manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_TITLE_PAGE_V1.md`
- Four vector figure PDFs and associated source-verified PNG/SVG, built through `.github/workflows/invited-m1-m2-figures.yml`
- Claim ledger and scientific decision: `manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_CLAIM_LEDGER_V1.md`, `manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_COAUTHOR_DECISION_MEMO_20261123.md`

The review-only ZIP produced by `scripts/build_el_invited_review_bundle_v1.py` bundles the exact checked evidence, figures and placeholders, without implying approval, archive DOI, acceptance or submission.

## No alteration of science

The historical held-out endpoint remains 12 taxa, 283 evaluable cells and 0/12 source-discordance exceedance taxa. GBIF source repair has 285 evaluable cells and 0/12 exceedance taxa but **failed** all-original-283 retention because one originally opened cell became unresolved. The integrated SI has added no independent empirical endpoint. M1 is mathematical/synthetic, not observed natural detection-rate estimation.

**Preflight state:** quantitative journal size and inventory **within source-text limits**, but **submission remains HOLD** for coauthor approval, final metadata, DOI and final-formatted/compiled proof.
