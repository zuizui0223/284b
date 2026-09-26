# Ecology Letters Stage-1 release candidate v0.1

## Status

The scientific/methodological Stage-1 package is frozen as a release candidate while human metadata remains external and unresolved.

Source tree commit:

`36d3d3c414b1ae18ccd27f57c4f109997bdab64e`

Package identity:

`c39f94e81f27183ce3d298dee2206242934baee3b7b036741fe6c80c6a08dbad`

Canonical receipt:

`results/ecology_letters_stage1_release_candidate_v0_1.json`

Freeze utility:

`scripts/freeze_ecology_letters_stage1_release_candidate.py`

## Identity semantics

The package identity is SHA-256 over deterministic JSON containing:

1. the Git commit that content-addresses the source tree; and
2. the exact sorted set of canonical Stage-1 files.

This deliberately separates **scientific/package identity** from **human metadata**. A later rendered email may add only explicitly confirmed author metadata; it does not redefine the scientific release candidate.

A different source commit or canonical file set yields a different package identity.

## Frozen scientific boundary

- Level A remains the sole completed empirical endpoint.
- Level B remains unopened.
- Focal Level-C hard/soft/knockout values remain sealed.
- The release-candidate freeze reads no focal Level-C outcomes.
- Empirical-ledger increment from this freeze is 0.
- Global 284b empirical ledger remains 1.

## Human layer

The release candidate intentionally contains no inferred author metadata. The separate human-metadata template and readiness gate remain authoritative:

- `config/ecology_letters_stage1_human_metadata_template.json`;
- `scripts/audit_ecology_letters_stage1_send_readiness.py`;
- `scripts/render_ecology_letters_stage1_email.py`.

Until those fields are explicitly confirmed, the correct submission state remains `blocked_human_metadata`.

## What this freeze does not claim

This receipt does not prove outcome blindness, send email, create an invitation, open Level C, or add an empirical result. It fixes the pre-send scientific/tooling package so any subsequent scientific change requires a new source-tree commit and therefore a new release-candidate identity.
