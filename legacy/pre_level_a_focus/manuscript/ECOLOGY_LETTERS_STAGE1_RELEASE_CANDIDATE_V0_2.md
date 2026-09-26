# Ecology Letters Stage-1 release candidate v0.2

## Status

Stage-1 scientific/editor-facing content is frozen at byte level while human metadata remains external.

Source tree commit:

`8a1dbfb2bc4d03e3ade39e9b6b20173ab71aac4e`

Byte-addressed package identity:

`2787b4462850458dbbb01f975ef71d7171f553e2f4f7898c851a43a1548fea87`

Canonical receipt:

`results/ecology_letters_stage1_release_candidate_v0_2.json`

Audit utility:

`scripts/audit_ecology_letters_stage1_release_candidate.py`

## What changed from v0.1

v0.1 froze a source-tree commit plus the canonical path set. v0.2 additionally freezes the exact Git blob SHA-1 of each of the 20 canonical files. The audit recomputes Git blob hashes directly from current file bytes.

Therefore:

- one-byte content drift is detected;
- a missing canonical file is detected;
- JSON/Markdown/SVG/script content cannot change silently while retaining RC status;
- no network call is required for CI verification.

The Stage-1 send-readiness gate now requires both receipt integrity and byte identity to pass before human metadata can clear the final gate.

## Frozen layers

The 20-file map covers the canonical Stage-1 proposal/routing surfaces, novelty/separation support, figure, endpoint-contract demonstration and operational readiness/rendering surfaces that existed at the source tree.

The receipt itself and the byte-audit implementation are intentionally outside the 20-file map to avoid self-reference.

## Human layer

Human metadata is not embedded in the release candidate. It remains separately supplied and explicitly confirmed through:

- `config/ecology_letters_stage1_human_metadata_template.json`;
- `scripts/audit_ecology_letters_stage1_send_readiness.py`;
- `scripts/render_ecology_letters_stage1_email.py`.

The correct state without confirmed metadata remains `blocked_human_metadata` **only if** the RC byte audit passes. Any scientific/package drift instead returns `blocked_package_integrity`.

## Scientific boundary

- Level A remains the sole completed empirical endpoint.
- Level B remains unopened.
- Focal Level-C hard/soft/knockout values remain sealed.
- The RC audit reads no focal Level-C values.
- RC v0.2 empirical-ledger increment = 0.
- Global 284b empirical ledger remains 1.

This release-candidate hardening is provenance/integrity infrastructure, not a new empirical conclusion.
