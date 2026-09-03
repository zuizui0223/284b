"""Fail-closed authorization guard for Product-B v5 occurrence preflight.

Network/occurrence code must call this guard before constructing any request.
The committed manifest is intentionally unauthorized even though the current
geographic scope and transport contracts are frozen.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence


EXPECTED_MANIFEST_VERSION = "product_b_v5_sampling_preflight_v0.2"
EXPECTED_CHECKLIST_KEY = "d7dddbf4-2cf0-4f39-9b2a-bb099caae36c"


class ExecutionNotAuthorized(RuntimeError):
    """Raised before any occurrence read when the frozen manifest is not authorized."""


@dataclass(frozen=True)
class AuthorizationDecision:
    authorized: bool
    eligible_pair_ids: tuple[str, ...]
    taxonomy_eligible_pair_ids: tuple[str, ...]
    reasons: tuple[str, ...]


def _pair_list(
    manifest: Mapping[str, object],
    field: str,
    *,
    require_nonempty: bool,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    raw = manifest.get(field)
    reasons: list[str] = []
    if not isinstance(raw, list):
        return (), (f"{field}_missing",)

    values = tuple(str(value) for value in raw)
    if require_nonempty and not values:
        reasons.append(f"{field}_empty")
    if any(not value.strip() for value in values):
        reasons.append(f"{field}_contains_blank")
    if len(set(values)) != len(values):
        reasons.append(f"{field}_not_unique")
    return values, tuple(reasons)


def evaluate_execution_manifest(manifest: Mapping[str, object]) -> AuthorizationDecision:
    """Validate every pre-execution gate without touching an occurrence source."""

    reasons: list[str] = []

    if manifest.get("manifest_version") != EXPECTED_MANIFEST_VERSION:
        reasons.append("manifest_version_mismatch")
    if manifest.get("contract_frozen") is not True:
        reasons.append("contract_not_frozen")
    if manifest.get("scope_gate_frozen") is not True:
        reasons.append("scope_gate_not_frozen")
    if manifest.get("preprocessing_contract_frozen") is not True:
        reasons.append("preprocessing_contract_not_frozen")
    if manifest.get("transport_contract_frozen") is not True:
        reasons.append("transport_contract_not_frozen")
    if manifest.get("checklist_key") != EXPECTED_CHECKLIST_KEY:
        reasons.append("checklist_key_mismatch")

    taxonomy_pairs, taxonomy_errors = _pair_list(
        manifest,
        "taxonomy_eligible_pair_ids",
        require_nonempty=True,
    )
    reasons.extend(taxonomy_errors)

    scope_pairs, scope_errors = _pair_list(
        manifest,
        "scope_eligible_pair_ids",
        require_nonempty=False,
    )
    reasons.extend(scope_errors)

    scope_outside_taxonomy = sorted(set(scope_pairs) - set(taxonomy_pairs))
    if scope_outside_taxonomy:
        reasons.append("scope_pair_not_taxonomy_eligible")
    if not scope_pairs:
        reasons.append("no_scope_eligible_pairs")

    if manifest.get("execution_authorized") is not True:
        reasons.append("execution_not_authorized")
    if manifest.get("occurrence_reads_allowed") is not True:
        reasons.append("occurrence_reads_not_allowed")

    return AuthorizationDecision(
        authorized=not reasons,
        eligible_pair_ids=scope_pairs,
        taxonomy_eligible_pair_ids=taxonomy_pairs,
        reasons=tuple(reasons),
    )


def require_execution_authorization(
    manifest: Mapping[str, object], *, requested_pair_ids: Sequence[str]
) -> AuthorizationDecision:
    """Raise before any occurrence access unless all frozen gates authorize it."""

    decision = evaluate_execution_manifest(manifest)
    if not decision.authorized:
        raise ExecutionNotAuthorized(
            "Product-B v5 occurrence execution is fail-closed: "
            + ",".join(decision.reasons)
        )

    requested = tuple(str(value) for value in requested_pair_ids)
    if any(not value.strip() for value in requested):
        raise ExecutionNotAuthorized("requested pair id must not be blank")
    if len(set(requested)) != len(requested):
        raise ExecutionNotAuthorized("requested pair ids must be unique")

    unknown = sorted(set(requested) - set(decision.eligible_pair_ids))
    if unknown:
        raise ExecutionNotAuthorized(
            "requested pair is outside frozen scope-eligible set: "
            + ",".join(unknown)
        )

    return decision
