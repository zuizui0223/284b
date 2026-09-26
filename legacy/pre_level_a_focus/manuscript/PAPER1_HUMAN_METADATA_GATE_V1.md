# Paper 1 human/editor metadata gate v1

**Purpose:** convert the remaining RED submission blockers into one explicit, machine-validated handoff without inferring human-authored metadata from repository state.

## Why this gate exists

The scientific manuscript, Ecology Letters submission derivative, figure-production route and content-addressed archive candidate are already frozen. The remaining blockers are human/editor facts: invitation/approval, final authorship/order, affiliations, corresponding email, ORCID status, contributions, funding, acknowledgements, competing interests, all-author approval, simultaneous-submission status and related-work disclosure.

These facts must not be guessed from old files, account metadata or prior drafts. The committed template is therefore intentionally incomplete and must fail validation.

## Input

Copy:

`manuscript/PAPER1_HUMAN_METADATA_V1.template.json`

into a working metadata file and replace every `__REQUIRED__` sentinel with verified information. Do not edit the frozen scientific manuscript to store these fields.

Required gates include:

- Ecology Letters full Method invitation/approved-proposal state = true;
- a nonblank authorization reference and ISO date;
- final ordered author list;
- every author's final affiliation mapping;
- ORCID explicitly marked `confirmed` or `not_required`;
- at least one verified contribution/CREDIT role per author;
- a listed corresponding author with verified email;
- author order confirmed;
- all-author approval confirmed;
- not-under-consideration-elsewhere confirmed;
- explicit competing-interest statement;
- explicit related-work disclosure;
- explicit funding statement;
- explicit acknowledgements statement.

An explicit none/no-funding statement is acceptable where factually correct; an empty field is not.

## Validation

Run:

```bash
python scripts/finalize_paper1_human_metadata_v1.py path/to/PAPER1_HUMAN_METADATA_V1.json --validate-only
```

The script returns non-zero and prints all blockers until every gate passes.

## Finalization

After validation passes:

```bash
python scripts/finalize_paper1_human_metadata_v1.py path/to/PAPER1_HUMAN_METADATA_V1.json
```

The default output directory is `manuscript/final_submission/`. It creates:

- `ECOLOGY_LETTERS_TITLE_PAGE_FINAL.md`;
- `ECOLOGY_LETTERS_COVER_LETTER_FINAL.md`;
- `PAPER1_DECLARATIONS_FINAL.md`;
- `PAPER1_HUMAN_METADATA_FINALIZATION_RECEIPT_V1.json`.

The receipt records the SHA-256 of the verified human metadata file and the rendered human-facing outputs, while pinning the already-frozen identities:

- scientific source SHA-256: `66ad208f2a922800cb7f1d14f96b28295de13af4cdbdbec2f8b698b8fa320cc5`;
- Ecology Letters submission derivative SHA-256: `a2f45e2b91953b47f24682e95667533a923680ec65a9b0fef2c88a423b75cf84`;
- archive bundle SHA-256: `ebf1d848ac2eaa99f7e15b5f8a95e33262f1f76a768b1f4f8944331b177ff680`.

## What this gate cannot authorize

Passing human metadata does not alter the ecological evidence state. It cannot:

- open Level B;
- open any focal Level-C hard/soft/process-knockout outcome;
- reinterpret unavailable/non-detected observations as biological negatives;
- change Level-A thresholds or results;
- change the independent replication unit from 12 held-out taxa;
- increment empirical ledger beyond 1.

After the human gate passes, the remaining publication action is to create the approved final public release/archive DOI and record that external identifier. A DOI/public release must reference the approved final submission state rather than silently changing the scientific package.
