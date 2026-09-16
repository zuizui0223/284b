# Paper 1 Stage-1 administrative policy v2

**Scope:** administrative preparation for the frozen Ecology Letters unsolicited Method proposal only. This document does not modify the 20-file frozen Stage-1 scientific package, its 295-word pitch, proposal figure, relation-endpoint contract, empirical results or claim boundary.

## Current publisher requirement

Current Ecology Letters guidance requires an unsolicited Method proposal of no more than 300 words describing the nature and novelty of the work and its contribution to the discipline. The journal's Method editorial additionally asks for the qualifications of the author(s) who will write the manuscript. Neither source states that the **final full-manuscript author order** must already be frozen at proposal stage.

Therefore the Stage-1 administrative gate should distinguish:

- **proposal-stage authorship:** a provisional author set that the sender is willing to present to the editors now;
- **full-submission authorship:** the final author list/order, contribution statement and all-author approval required before an invited manuscript is sent.

The proposal must never misrepresent authorship. “Provisional” means administratively not yet frozen for a later full submission, not permission to list people who have not agreed to be associated with the proposal.

## Minimal Stage-1 metadata

To render the existing frozen proposal email, the sender needs only:

1. a provisional author list for the proposal;
2. current affiliation line(s) for the sender/authors as they wish them presented;
3. a sender/corresponding email for the proposal;
4. author-qualification wording.

For a **single-author proposal**, item 4 can reuse the qualification statement already frozen in the canonical 295-word pitch:

> The lead author works across empirical pollination ecology, species-distribution modelling and reproducible computational inference.

For a multi-author proposal, qualification wording should be supplied explicitly so that the proposal describes the qualifications of the author group rather than silently extrapolating the lead-author sentence.

The sender name defaults to the first provisional author unless explicitly supplied.

## Implementation

Use `scripts/prepare_ecology_letters_stage1_metadata_v2.py` to transform proposal-stage metadata into the exact legacy metadata schema consumed by the already-frozen:

- `scripts/audit_ecology_letters_stage1_send_readiness.py`;
- `scripts/render_ecology_letters_stage1_email.py`.

The helper does **not** send email and does not alter any frozen Stage-1 asset. It exists only to remove an unnecessary administrative assumption that the final full-submission author order must be known before the unsolicited proposal is rendered.

## Scientific boundary

- Level A: sole completed empirical endpoint; independent replication = 12 taxa.
- Level B: unopened.
- Level C: focal biological outcomes sealed.
- Empirical ledger: 1.

No Stage-1 metadata choice may alter these statements.
