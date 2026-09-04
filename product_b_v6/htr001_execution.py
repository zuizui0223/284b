"""Fail-closed Product-B v6 HTR001 sampling/control execution.

Occurrence data are opened only after the separately frozen HTR001 manifest passes
every authorization check. The focal Euphorbia dregeana / Hydnora triceps
asymmetric sampling gate is evaluated first. Frozen replacement Euphorbia hosts
are opened only if the focal gate passes. No invariant/model/knockout outcome is
accessible from this module.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Mapping, Protocol, Sequence

from product_b_v5.occurrence_source import LogicalOccurrenceQuery
from product_b_v5.pipeline import validate_returned_rows_against_query
from product_b_v6.preflight import (
    DirectedWitnessSamplingPreflight,
    adapt_and_build_directed_witness_sampling_preflight,
)
from product_b_v6.witness import (
    HOST_MIN_EFFECTIVE_CELLS,
    HOST_MIN_RECORDS,
    HOST_MIN_UNIQUE_CELLS,
    HostSamplingSummary,
)

EXPECTED_MANIFEST_VERSION = "product_b_v6_directed_witness_preflight_v0.1"
EXPECTED_PAIR_ID = "HTR001"
EXPECTED_CHECKLIST_KEY = "d7dddbf4-2cf0-4f39-9b2a-bb099caae36c"
EXPECTED_X_TAXON_KEY = "3069738"
EXPECTED_Y_TAXON_KEY = "3646101"
EXPECTED_CONTROL_HOSTS = (
    ("HTR_C01", "Euphorbia mauritanica", "7926635"),
    ("HTR_C02", "Euphorbia gummifera", "3068472"),
    ("HTR_C03", "Euphorbia gregaria", "3069722"),
    ("HTR_C04", "Euphorbia damarana", "3069701"),
    ("HTR_C05", "Euphorbia gariepina", "3069506"),
    ("HTR_C06", "Euphorbia virosa", "3066685"),
)
_SHA_RE = re.compile(r"^[0-9a-f]{40}$")


class HTR001ExecutionNotAuthorized(RuntimeError):
    """Raised before any HTR001 occurrence transport call when the manifest is closed."""


class OccurrenceTransport(Protocol):
    def __call__(self, query: LogicalOccurrenceQuery) -> Sequence[Mapping[str, object]]: ...


@dataclass(frozen=True)
class HTR001AuthorizationDecision:
    authorized: bool
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class ControlHostSamplingResult:
    control_taxon_id: str
    scientific_name: str
    taxon_key: str
    raw_records: int
    retained_records: int
    unique_cells: int
    effective_cells: float
    sampling_adequate: bool
    quality_excluded: int


@dataclass(frozen=True)
class HTR001SamplingExecutionResult:
    authorization: HTR001AuthorizationDecision
    focal: DirectedWitnessSamplingPreflight
    controls_opened: bool
    control_results: tuple[ControlHostSamplingResult, ...]
    adequate_control_host_count: int
    minimum_required_control_hosts: int
    terminal_state: str
    terminal_reasons: tuple[str, ...]


def _normalized_controls(manifest: Mapping[str, object]) -> tuple[tuple[str, str, str], ...]:
    raw = manifest.get("control_hosts")
    if not isinstance(raw, list):
        return ()
    output: list[tuple[str, str, str]] = []
    for item in raw:
        if not isinstance(item, Mapping):
            return ()
        output.append(
            (
                str(item.get("control_taxon_id", "")),
                str(item.get("scientific_name", "")),
                str(item.get("taxon_key", "")),
            )
        )
    return tuple(output)


def evaluate_htr001_execution_manifest(manifest: Mapping[str, object]) -> HTR001AuthorizationDecision:
    reasons: list[str] = []
    if manifest.get("manifest_version") != EXPECTED_MANIFEST_VERSION:
        reasons.append("manifest_version_mismatch")
    if manifest.get("pair_id") != EXPECTED_PAIR_ID:
        reasons.append("pair_id_mismatch")
    if manifest.get("contract_frozen") is not True:
        reasons.append("contract_not_frozen")

    freeze = str(manifest.get("pre_execution_package_commit", ""))
    if _SHA_RE.fullmatch(freeze) is None:
        reasons.append("pre_execution_package_commit_not_frozen_sha")

    if manifest.get("checklist_key") != EXPECTED_CHECKLIST_KEY:
        reasons.append("checklist_key_mismatch")
    if str(manifest.get("x_transport_taxon_key", "")) != EXPECTED_X_TAXON_KEY:
        reasons.append("x_taxon_key_mismatch")
    if str(manifest.get("y_taxon_key", "")) != EXPECTED_Y_TAXON_KEY:
        reasons.append("y_taxon_key_mismatch")
    if _normalized_controls(manifest) != EXPECTED_CONTROL_HOSTS:
        reasons.append("control_host_pool_mismatch")
    if manifest.get("minimum_sampling_adequate_control_hosts") != 5:
        reasons.append("minimum_control_host_count_mismatch")

    if manifest.get("execution_consumed") is True:
        reasons.append("execution_already_consumed")
    if manifest.get("execution_authorized") is not True:
        reasons.append("execution_not_authorized")
    if manifest.get("occurrence_reads_allowed") is not True:
        reasons.append("occurrence_reads_not_allowed")
    if manifest.get("invariant_reads_allowed") is not False:
        reasons.append("invariant_reads_must_remain_closed")

    return HTR001AuthorizationDecision(authorized=not reasons, reasons=tuple(reasons))


def require_htr001_execution_authorization(manifest: Mapping[str, object]) -> HTR001AuthorizationDecision:
    decision = evaluate_htr001_execution_manifest(manifest)
    if not decision.authorized:
        raise HTR001ExecutionNotAuthorized(
            "Product-B v6 HTR001 occurrence execution is fail-closed: "
            + ",".join(decision.reasons)
        )
    return decision


def _query(
    *,
    query_pair_id: str,
    partner: str,
    taxon_key: str,
    manifest: Mapping[str, object],
    scope: Mapping[str, object],
) -> LogicalOccurrenceQuery:
    if scope.get("pair_id") != EXPECTED_PAIR_ID:
        raise ValueError("scope pair_id mismatch")
    if scope.get("operational_scope_state") != "operational_scope_resolved":
        raise ValueError("HTR001 operational scope is not resolved")
    if scope.get("filter_type") != "polygon_wkt":
        raise ValueError("HTR001 execution requires frozen polygon_wkt scope")
    if scope.get("buffer_degrees") != 0:
        raise ValueError("HTR001 scope buffer must remain zero")
    if scope.get("occurrence_information_used_in_derivation") is not False:
        raise ValueError("HTR001 scope must remain occurrence-blind")
    review = scope.get("host_specificity_review")
    if not isinstance(review, Mapping) or review.get("state") != "resolved_under_2024_revision":
        raise ValueError("HTR001 host-specificity review is not frozen as resolved")
    filter_value = str(scope.get("filter_value", "")).strip()
    if not filter_value:
        raise ValueError("HTR001 scope filter_value is blank")
    return LogicalOccurrenceQuery(
        pair_id=query_pair_id,
        partner=partner,
        taxon_key=taxon_key,
        checklist_key=str(manifest["checklist_key"]),
        geographic_filter_type="polygon_wkt",
        geographic_filter_value=filter_value,
    )


def host_sampling_adequate(summary: HostSamplingSummary) -> bool:
    return (
        summary.independent_records >= HOST_MIN_RECORDS
        and summary.unique_cells >= HOST_MIN_UNIQUE_CELLS
        and summary.effective_cells >= HOST_MIN_EFFECTIVE_CELLS
    )


def execute_htr001_sampling_preflight(
    *,
    manifest: Mapping[str, object],
    scope: Mapping[str, object],
    transport: OccurrenceTransport,
) -> HTR001SamplingExecutionResult:
    """Execute the authorized focal gate, then controls only if focal passes."""

    authorization = require_htr001_execution_authorization(manifest)

    x_query = _query(
        query_pair_id=EXPECTED_PAIR_ID,
        partner="x",
        taxon_key=EXPECTED_X_TAXON_KEY,
        manifest=manifest,
        scope=scope,
    )
    y_query = _query(
        query_pair_id=EXPECTED_PAIR_ID,
        partner="y",
        taxon_key=EXPECTED_Y_TAXON_KEY,
        manifest=manifest,
        scope=scope,
    )

    x_rows = tuple(transport(x_query))
    validate_returned_rows_against_query(x_query, x_rows)
    y_rows = tuple(transport(y_query))
    validate_returned_rows_against_query(y_query, y_rows)
    _, focal = adapt_and_build_directed_witness_sampling_preflight(x_rows=x_rows, y_rows=y_rows)

    if not focal.preflight.passed:
        return HTR001SamplingExecutionResult(
            authorization=authorization,
            focal=focal,
            controls_opened=False,
            control_results=(),
            adequate_control_host_count=0,
            minimum_required_control_hosts=int(manifest["minimum_sampling_adequate_control_hosts"]),
            terminal_state="unresolved_witness_sampling",
            terminal_reasons=focal.preflight.reasons,
        )

    control_results: list[ControlHostSamplingResult] = []
    for control_id, scientific_name, taxon_key in EXPECTED_CONTROL_HOSTS:
        query = _query(
            query_pair_id=f"{EXPECTED_PAIR_ID}_{control_id}",
            partner="x",
            taxon_key=taxon_key,
            manifest=manifest,
            scope=scope,
        )
        rows = tuple(transport(query))
        validate_returned_rows_against_query(query, rows)
        _, preflight = adapt_and_build_directed_witness_sampling_preflight(x_rows=rows, y_rows=())
        audit = preflight.audit
        summary = preflight.host_summary
        control_results.append(
            ControlHostSamplingResult(
                control_taxon_id=control_id,
                scientific_name=scientific_name,
                taxon_key=taxon_key,
                raw_records=audit.raw_records_x,
                retained_records=audit.retained_records_x,
                unique_cells=summary.unique_cells,
                effective_cells=summary.effective_cells,
                sampling_adequate=host_sampling_adequate(summary),
                quality_excluded=audit.quality_excluded_x,
            )
        )

    adequate_count = sum(result.sampling_adequate for result in control_results)
    minimum = int(manifest["minimum_sampling_adequate_control_hosts"])
    if adequate_count < minimum:
        terminal_state = "unresolved_controls_sampling"
        terminal_reasons = ("insufficient_sampling_adequate_control_hosts",)
    else:
        terminal_state = "sampling_preflight_passed"
        terminal_reasons = ()

    return HTR001SamplingExecutionResult(
        authorization=authorization,
        focal=focal,
        controls_opened=True,
        control_results=tuple(control_results),
        adequate_control_host_count=adequate_count,
        minimum_required_control_hosts=minimum,
        terminal_state=terminal_state,
        terminal_reasons=terminal_reasons,
    )
