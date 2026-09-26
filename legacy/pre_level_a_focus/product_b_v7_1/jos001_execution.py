"""Fail-closed JOS001 engineering-only host/control sampling execution.

JOS001 is permanently excluded from confirmatory evidence. The dependent moth is
represented by frozen literature witnesses and is never queried here. The focal
host is opened first. Replacement Yucca controls are opened in fixed order only
if the focal host passes the unchanged 50/30/10 sampling floor. No model fitting,
invariant evaluation, or process-knockout API exists in this module.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Mapping, Protocol, Sequence

from product_b_v5.occurrence_adapter import adapt_gbif_pair_rows
from product_b_v5.occurrence_source import LogicalOccurrenceQuery
from product_b_v6.preflight import build_directed_witness_sampling_preflight_from_records
from product_b_v6.witness import (
    HOST_MIN_EFFECTIVE_CELLS,
    HOST_MIN_RECORDS,
    HOST_MIN_UNIQUE_CELLS,
    HostSamplingSummary,
)

EXPECTED_MANIFEST_VERSION = "product_b_v7_1_jos001_engineering_sampling_v0.1"
EXPECTED_PAIR_ID = "JOS001"
EXPECTED_CHECKLIST_KEY = "d7dddbf4-2cf0-4f39-9b2a-bb099caae36c"
EXPECTED_COUNTRY = "US"
EXPECTED_X_TAXON_KEY = "2775592"
EXPECTED_CONTROLS = (
    ("JOS_C01", "Yucca baccata", "2775788"),
    ("JOS_C02", "Yucca schidigera", "2775710"),
    ("JOS_C03", "Yucca elata", "2775775"),
    ("JOS_C04", "Yucca glauca", "2775497"),
    ("JOS_C05", "Yucca filamentosa", "2775561"),
    ("JOS_C07", "Yucca rostrata", "2775576"),
    ("JOS_C08", "Yucca harrimaniae", "2775580"),
)
_SHA_RE = re.compile(r"^[0-9a-f]{40}$")


class JOS001ExecutionNotAuthorized(RuntimeError):
    pass


class OccurrenceTransport(Protocol):
    def __call__(self, query: LogicalOccurrenceQuery) -> Sequence[Mapping[str, object]]: ...


@dataclass(frozen=True)
class JOS001AuthorizationDecision:
    authorized: bool
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class HostSamplingAuditResult:
    taxon_id: str
    scientific_name: str
    taxon_key: str
    raw_records: int
    retained_records: int
    unique_cells: int
    effective_cells: float
    quality_excluded: int
    sampling_adequate: bool
    failure_reasons: tuple[str, ...]


@dataclass(frozen=True)
class JOS001SamplingExecutionResult:
    authorization: JOS001AuthorizationDecision
    focal: HostSamplingAuditResult
    controls_opened: bool
    control_results: tuple[HostSamplingAuditResult, ...]
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
        output.append((
            str(item.get("control_taxon_id", "")),
            str(item.get("scientific_name", "")),
            str(item.get("taxon_key", "")),
        ))
    return tuple(output)


def evaluate_jos001_execution_manifest(manifest: Mapping[str, object]) -> JOS001AuthorizationDecision:
    reasons: list[str] = []
    if manifest.get("manifest_version") != EXPECTED_MANIFEST_VERSION:
        reasons.append("manifest_version_mismatch")
    if manifest.get("pair_id") != EXPECTED_PAIR_ID:
        reasons.append("pair_id_mismatch")
    if manifest.get("engineering_only") is not True:
        reasons.append("engineering_only_boundary_changed")
    if manifest.get("confirmatory_promotion_allowed") is not False:
        reasons.append("confirmatory_promotion_must_remain_forbidden")
    if manifest.get("contract_frozen") is not True:
        reasons.append("contract_not_frozen")
    freeze = str(manifest.get("pre_execution_package_commit", ""))
    if _SHA_RE.fullmatch(freeze) is None:
        reasons.append("pre_execution_package_commit_not_frozen_sha")
    if manifest.get("checklist_key") != EXPECTED_CHECKLIST_KEY:
        reasons.append("checklist_key_mismatch")
    if str(manifest.get("x_transport_taxon_key", "")) != EXPECTED_X_TAXON_KEY:
        reasons.append("x_taxon_key_mismatch")
    if manifest.get("frame_id") != "USA-ADM0-2327393":
        reasons.append("frame_id_mismatch")
    if manifest.get("operational_country_filter") != EXPECTED_COUNTRY:
        reasons.append("country_filter_mismatch")
    if manifest.get("prospective_host_feasibility_prescreen_passed") is not True:
        reasons.append("host_feasibility_prescreen_not_passed")
    if manifest.get("literature_witness_preflight_passed") is not True:
        reasons.append("literature_witness_preflight_not_passed")
    if manifest.get("independent_frame_preflight_passed") is not True:
        reasons.append("independent_frame_preflight_not_passed")
    if manifest.get("focal_taxonomy_resolved") is not True:
        reasons.append("focal_taxonomy_not_resolved")
    if manifest.get("control_taxonomy_preflight_passed") is not True:
        reasons.append("control_taxonomy_preflight_not_passed")
    if _normalized_controls(manifest) != EXPECTED_CONTROLS:
        reasons.append("control_host_pool_mismatch")
    if manifest.get("minimum_sampling_adequate_control_hosts") != 5:
        reasons.append("minimum_control_host_count_mismatch")
    if manifest.get("execution_consumed") is True:
        reasons.append("execution_already_consumed")
    if manifest.get("execution_authorized") is not True:
        reasons.append("execution_not_authorized")
    if manifest.get("occurrence_reads_allowed") is not True:
        reasons.append("occurrence_reads_not_allowed")
    if manifest.get("model_fit_reads_allowed") is not False:
        reasons.append("model_fit_reads_must_remain_closed")
    if manifest.get("invariant_reads_allowed") is not False:
        reasons.append("invariant_reads_must_remain_closed")
    if manifest.get("process_knockout_reads_allowed") is not False:
        reasons.append("process_knockout_reads_must_remain_closed")
    return JOS001AuthorizationDecision(authorized=not reasons, reasons=tuple(reasons))


def require_jos001_execution_authorization(manifest: Mapping[str, object]) -> JOS001AuthorizationDecision:
    decision = evaluate_jos001_execution_manifest(manifest)
    if not decision.authorized:
        raise JOS001ExecutionNotAuthorized(
            "Product-B v7.1 JOS001 engineering occurrence execution is fail-closed: "
            + ",".join(decision.reasons)
        )
    return decision


def _query(*, pair_id: str, taxon_key: str, manifest: Mapping[str, object]) -> LogicalOccurrenceQuery:
    return LogicalOccurrenceQuery(
        pair_id=pair_id,
        partner="x",
        taxon_key=taxon_key,
        checklist_key=str(manifest["checklist_key"]),
        geographic_filter_type="country_code_iso2",
        geographic_filter_value=EXPECTED_COUNTRY,
    )


def validate_returned_rows_against_country_query(
    query: LogicalOccurrenceQuery,
    rows: Sequence[Mapping[str, object]],
) -> None:
    if query.geographic_filter_type != "country_code_iso2" or query.geographic_filter_value != EXPECTED_COUNTRY:
        raise ValueError("JOS001 returned-row validator requires frozen country=US query")
    for row in rows:
        row_id = str(row.get("key", "<missing-key>"))
        status = row.get("occurrenceStatus")
        if status is not None and str(status) != "PRESENT":
            raise ValueError("returned occurrence violates PRESENT filter: " + row_id)
        country = row.get("countryCode")
        if country is not None and str(country).strip().upper() != EXPECTED_COUNTRY:
            raise ValueError("returned occurrence violates frozen country filter: " + row_id)


def _host_sampling_reasons(summary: HostSamplingSummary) -> tuple[str, ...]:
    reasons: list[str] = []
    if summary.independent_records < HOST_MIN_RECORDS:
        reasons.append("host_independent_record_floor_failed")
    if summary.unique_cells < HOST_MIN_UNIQUE_CELLS:
        reasons.append("host_unique_cell_floor_failed")
    if summary.effective_cells < HOST_MIN_EFFECTIVE_CELLS:
        reasons.append("host_effective_cell_floor_failed")
    return tuple(reasons)


def _host_result(
    *,
    taxon_id: str,
    scientific_name: str,
    taxon_key: str,
    rows: Sequence[Mapping[str, object]],
) -> HostSamplingAuditResult:
    adapted = adapt_gbif_pair_rows(x_rows=tuple(rows), y_rows=())
    preflight = build_directed_witness_sampling_preflight_from_records(adapted.records)
    summary = preflight.host_summary
    reasons = _host_sampling_reasons(summary)
    return HostSamplingAuditResult(
        taxon_id=taxon_id,
        scientific_name=scientific_name,
        taxon_key=taxon_key,
        raw_records=preflight.audit.raw_records_x,
        retained_records=preflight.audit.retained_records_x,
        unique_cells=summary.unique_cells,
        effective_cells=summary.effective_cells,
        quality_excluded=preflight.audit.quality_excluded_x,
        sampling_adequate=not reasons,
        failure_reasons=reasons,
    )


def execute_jos001_sampling_preflight(
    *,
    manifest: Mapping[str, object],
    transport: OccurrenceTransport,
) -> JOS001SamplingExecutionResult:
    authorization = require_jos001_execution_authorization(manifest)
    minimum = int(manifest["minimum_sampling_adequate_control_hosts"])

    focal_query = _query(pair_id=EXPECTED_PAIR_ID, taxon_key=EXPECTED_X_TAXON_KEY, manifest=manifest)
    focal_rows = tuple(transport(focal_query))
    validate_returned_rows_against_country_query(focal_query, focal_rows)
    focal = _host_result(
        taxon_id="JOS_X",
        scientific_name="Yucca brevifolia",
        taxon_key=EXPECTED_X_TAXON_KEY,
        rows=focal_rows,
    )
    if not focal.sampling_adequate:
        return JOS001SamplingExecutionResult(
            authorization=authorization,
            focal=focal,
            controls_opened=False,
            control_results=(),
            adequate_control_host_count=0,
            minimum_required_control_hosts=minimum,
            terminal_state="unresolved_host_sampling",
            terminal_reasons=focal.failure_reasons,
        )

    control_results: list[HostSamplingAuditResult] = []
    for control_id, scientific_name, taxon_key in EXPECTED_CONTROLS:
        query = _query(pair_id=f"{EXPECTED_PAIR_ID}_{control_id}", taxon_key=taxon_key, manifest=manifest)
        rows = tuple(transport(query))
        validate_returned_rows_against_country_query(query, rows)
        control_results.append(
            _host_result(
                taxon_id=control_id,
                scientific_name=scientific_name,
                taxon_key=taxon_key,
                rows=rows,
            )
        )

    adequate_count = sum(item.sampling_adequate for item in control_results)
    if adequate_count < minimum:
        state = "unresolved_controls_sampling"
        reasons = ("insufficient_sampling_adequate_control_hosts",)
    else:
        state = "engineering_sampling_preflight_passed"
        reasons = ()
    return JOS001SamplingExecutionResult(
        authorization=authorization,
        focal=focal,
        controls_opened=True,
        control_results=tuple(control_results),
        adequate_control_host_count=adequate_count,
        minimum_required_control_hosts=minimum,
        terminal_state=state,
        terminal_reasons=reasons,
    )
