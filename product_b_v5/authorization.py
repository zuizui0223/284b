"""Fail-closed authorization guard for Product-B v5 occurrence preflight.

Network/occurrence code must call this guard before constructing any request.
The committed manifest is intentionally unauthorized.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence


EXPECTED_MANIFEST_VERSION = "product_b_v5_sampling_preflight_v0.1"
EXPECTED_CHECKLIST_KEY = "d7dddbf4-2cf0-4f39-9b2a-bb099caae36c"


class ExecutionNotAuthorized(RuntimeError):
    """Raised before any occurrence read when the frozen manifest is not authorized."""


@dataclass(frozen=True)
class AuthorizationDecision:
    authorized: bool
    eligible_pair_ids: tuple[str, ...]
    reasons: tuple[str, ...]


def evaluate_execution_manifest(manifest: Mapping[str, object]) -> AuthorizationDecision:
    """Validate the frozen manifest without touching a network or occurrence source."""

    reasons: list[str] = []

    if manifest.get("manifest_version") != EXPECTED_MANIFEST_VERSION:
        reasons.append("manifest_version_mismatch")
    if manifest.get("contract_frozen") is not True:
        reasons.append("contract_not_frozen")
    if manifest.get("checklist_key") != EXPECTED_CHECKLIST_KEY:
        reasons.append("checklist_key_mismatch")

    raw_pairs = manifest.get("eligible_pair_ids")
    if not isinstance(raw_pairs, list) or not raw_pairs:
        reasons.append("eligible_pair_ids_missing")
        eligible_pairs: tuple[str, ...] = ()
    else:
        eligible_pairs = tuple(str(value) for value in raw_pairs)
        if any(not value.strip() for value in eligible_pairs):
            reasons.append("eligible_pair_id_blank")
        if len(set(eligible_pairs)) != len(eligible_pairs):
            reasons.append("eligible_pair_ids_not_unique")

    if manifest.get("execution_authorized") is not True:
        reasons.append("execution_not_authorized")
    if manifest.get("occurrence_reads_allowed") is not True:
        reasons.append("occurrence_reads_not_allowed")

    return AuthorizationDecision(
        authorized=not reasons,
        eligible_pair_ids=eligible_pairs,
        reasons=tuple(reasons),
    )


def require_execution_authorization(
    manifest: Mapping[str, object], *, requested_pair_ids: Sequence[str]
) -> AuthorizationDecision:
    """Raise before any occurrence access unless manifest and requested pairs are authorized."""

    decision = evaluate_execution_manifest(manifest)
    if not decision.authorized:
        raise ExecutionNotAuthorized(
            "Product-B v5 occurrence execution is fail-closed: "
            + ",".join(decision.reasons)
        )

    requested = tuple(str(value) for value in requested_pair_ids)
    unknown = sorted(set(requested) - set(decision.eligible_pair_ids))
    if unknown:
        raise ExecutionNotAuthorized(
            "requested pair is outside frozen eligible set: " + ",".join(unknown)
        )

    return decision
