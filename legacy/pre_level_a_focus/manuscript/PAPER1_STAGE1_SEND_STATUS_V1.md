# Paper 1 Ecology Letters Stage-1 send status v1

**Target:** Ecology Letters — unsolicited Method proposal  
**Canonical Stage-1 routing surface:** `ECOLOGY_LETTERS_SUBMISSION_MANIFEST_V0_6.md`  
**Frozen Stage-1 package identity:** `2787b4462850458dbbb01f975ef71d7171f553e2f4f7898c851a43a1548fea87`  
**Scientific state:** unchanged; Level A is the sole completed empirical endpoint, Level B is unopened, focal Level-C outcomes are sealed, empirical ledger = 1.

## Current gate

The Stage-1 scientific package is already byte-addressed as a 20-file release candidate. The current send-readiness audit must pass all package-integrity checks without modifying those frozen files. With no external human metadata supplied, the only admissible terminal state is:

`blocked_human_metadata`

The five required Stage-1 human fields are:

1. `authors_order` — final proposal author list in confirmed order;
2. `affiliations` — current final affiliation line(s) for that author list;
3. `corresponding_author_name`;
4. `corresponding_email`;
5. `author_qualifications` — concise qualification wording for the frozen author group.

The canonical blank handoff is:

`config/ecology_letters_stage1_human_metadata_template.json`

Do not infer or back-fill these fields from repository author names, historical affiliations, account metadata or old drafts.

## Scientific/package checks that must remain green

`python scripts/audit_ecology_letters_stage1_send_readiness.py`

must report all package checks true, including:

- exact 295-word canonical pitch;
- synchronized promoted title;
- v0.8 pitch / v0.9 rationale / v0.6 email and compliance routing;
- fingerprintable relation-endpoint contract with `opening_rule_reference`;
- valid Stage-1 release-candidate receipt;
- byte identity of all 20 canonical files;
- human placeholders still present in the frozen email wrapper rather than silently inferred;
- focal Level-C values sealed;
- empirical ledger = 1.

The expected frozen package identity is:

`2787b4462850458dbbb01f975ef71d7171f553e2f4f7898c851a43a1548fea87`

## Human handoff

Create a working copy of the canonical metadata template outside the frozen package, fill only verified information, then audit it with:

```bash
python scripts/audit_ecology_letters_stage1_send_readiness.py --human-metadata path/to/stage1_human_metadata.json
```

Only the status

`metadata_complete_package_scientifically_ready`

authorizes rendering the final Stage-1 email. It does **not** itself send anything.

Render with:

```bash
python scripts/render_ecology_letters_stage1_email.py \
  --human-metadata path/to/stage1_human_metadata.json \
  --out path/to/ecology_letters_stage1_email.md
```

The renderer must retain:

- recipients: `ecolets@cefe.cnrs.fr; ecolets2@cefe.cnrs.fr`;
- subject: `Unsolicited Method proposal — Relation endpoints for ecological inference`;
- the exact canonical 295-word proposal body;
- one compact attachment: `manuscript/figures/ecology_letters_method_proposal_figure_v0_5.svg`.

## What Stage 1 does not require

No new ecological analysis, new Level-C field data, candidate replacement, threshold change, or full-manuscript release is required before the unsolicited Method proposal can be rendered. Stage 1 asks whether the editors wish to invite/approve a full Method submission; full-submission release/DOI publication remains downstream of that editorial gate.

## Sending boundary

Rendering is not sending. Do not transmit the Stage-1 proposal until the human metadata are explicitly verified and the sender explicitly authorizes the external email action. The Stage-1 administrative gate cannot open Level B or Level C and increments the empirical ledger by 0.
