"""Fail-closed JOS003 snapshot sampling execution for Product-B v7.2.

The focal host is read from the frozen monthly snapshot first. The eight frozen
replacement hosts may be opened as one batched snapshot query only if the focal
host passes the unchanged 50/30/10 host sampling floor. Literature witnesses,
model fitting, invariant evaluation, and process knockouts are outside this module.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Mapping, Protocol, Sequence

from product_b_v6.preflight import build_directed_witness_sampling_preflight_from_records
from product_b_v6.witness import (
    HOST_MIN_EFFECTIVE_CELLS,
    HOST_MIN_RECORDS,
    HOST_MIN_UNIQUE_CELLS,
    HostSamplingSummary,
)
from product_b_v7_2.snapshot_occurrence import (
    MAX_MATCHED_ROWS_PER_TAXON,
    SnapshotTaxonQuery,
    adapt_snapshot_host_rows,
    validate_snapshot_taxon_query,
)
from product_b_v7_2.snapshot_transport import (
    EXPECTED_OBJECT_MANIFEST_SHA256,
    EXPECTED_SCHEMA_SHA256,
    EXPECTED_SNAPSHOT_DATE,
)

EXPECTED_MANIFEST_VERSION = "product_b_v7_2_jos003_snapshot_sampling_v0.1"
EXPECTED_PAIR_ID = "JOS003"
EXPECTED_FRAME_ID = "USA-ADM0-2327393"
EXPECTED_COUNTRY = "US"
EXPECTED_X_NAME = "Yucca filamentosa"
EXPECTED_X_SPECIES_KEY = "2775561"
EXPECTED_Y_NAME = "Tegeticula cassandra"
EXPECTED_CONTROLS = (
    ("JOS3_C01", "Yucca baccata", "2775788"),
    ("JOS3_C02", "Yucca schidigera", "2775710"),
    ("JOS3_C03", "Yucca elata", "2775775"),
    ("JOS3_C04", "Yucca glauca", "2775497"),
    ("JOS3_C05", "Yucca rostrata", "2775576"),
    ("JOS3_C06", "Yucca harrimaniae", "2775580"),
    ("JOS3_C07", "Yucca treculeana", "2775506"),
    ("JOS3_C08", "Yucca faxoniana", "2775736"),
)
_SHA_RE = re.compile(r"^[0-9a-f]{40}$")


class JOS003ExecutionNotAuthorized(RuntimeError):
    pass


class SnapshotOccurrenceTransport(Protocol):
    def __call__(
        self, query: SnapshotTaxonQuery
    ) -> Mapping[str, Sequence[Mapping[str, object]]]: ...


@dataclass(frozen=True)
class JOS003AuthorizationDecision:
    authorized: bool
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class SnapshotHostSamplingAuditResult:
    taxon_id: str
    scientific_name: str
    species_key: str
    raw_records: int
    retained_records: int
    unique_cells: int
    effective_cells: float
    quality_excluded: int
    missing_uncertainty: int
    missing_occurrence_id_rows: int
    missing_catalog_number_rows: int
    missing_recorder_rows: int
    identity_fields_unavailable: tuple[str, ...]
    sampling_adequate: bool
    failure_reasons: tuple[str, ...]


@dataclass(frozen=True)
class JOS003SamplingExecutionResult:
    authorization: JOS003AuthorizationDecision
    focal: SnapshotHostSamplingAuditResult
    controls_opened: bool
    control_results: tuple[SnapshotHostSamplingAuditResult, ...]
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
                str(item.get("species_key", "")),
            )
        )
    return tuple(output)


def evaluate_jos003_execution_manifest(manifest: Mapping[str, object]) -> JOS003AuthorizationDecision:
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

    if manifest.get("snapshot_date") != EXPECTED_SNAPSHOT_DATE:
        reasons.append("snapshot_date_mismatch")
    if manifest.get("snapshot_object_manifest_sha256") != EXPECTED_OBJECT_MANIFEST_SHA256:
        reasons.append("snapshot_object_manifest_mismatch")
    if manifest.get("snapshot_schema_sha256") != EXPECTED_SCHEMA_SHA256:
        reasons.append("snapshot_schema_mismatch")
    if manifest.get("live_occurrence_search_forbidden") is not True:
        reasons.append("live_search_not_forbidden")
    if manifest.get("frame_id") != EXPECTED_FRAME_ID:
        reasons.append("frame_id_mismatch")
    if manifest.get("operational_country_filter") != EXPECTED_COUNTRY:
        reasons.append("country_filter_mismatch")
    if str(manifest.get("x_species_key", "")) != EXPECTED_X_SPECIES_KEY:
        reasons.append("x_species_key_mismatch")
    if manifest.get("x_biological_name") != EXPECTED_X_NAME:
        reasons.append("x_name_mismatch")
    if manifest.get("y_literature_witness_taxon") != EXPECTED_Y_NAME:
        reasons.append("y_name_mismatch")
    if manifest.get("y_snapshot_occurrence_reads_planned") is not False:
        reasons.append("dependent_snapshot_occurrence_must_remain_unread")

    if manifest.get("prospective_host_feasibility_prescreen_passed") is not True:
        reasons.append("host_feasibility_prescreen_not_passed")
    if manifest.get("literature_witness_preflight_passed") is not True:
        reasons.append("literature_witness_preflight_not_passed")
    if manifest.get("literature_witness_count") != 12:
        reasons.append("literature_witness_count_mismatch")
    if manifest.get("independent_frame_preflight_passed") is not True:
        reasons.append("independent_frame_preflight_not_passed")
    if manifest.get("focal_taxonomy_resolved") is not True:
        reasons.append("focal_taxonomy_not_resolved")
    if manifest.get("control_taxonomy_preflight_passed") is not True:
        reasons.append("control_taxonomy_preflight_not_passed")
    if _normalized_controls(manifest) != EXPECTED_CONTROLS:
        reasons.append("control_host_pool_mismatch")

    floor = manifest.get("host_sampling_floor")
    if not isinstance(floor, Mapping) or (
        floor.get("minimum_independent_records"),
        floor.get("minimum_unique_10km_cells"),
        floor.get("minimum_effective_10km_cells"),
    ) != (HOST_MIN_RECORDS, HOST_MIN_UNIQUE_CELLS, HOST_MIN_EFFECTIVE_CELLS):
        reasons.append("host_sampling_floor_changed")
    if manifest.get("minimum_sampling_adequate_control_hosts") != 5:
        reasons.append("minimum_control_host_count_mismatch")
    if manifest.get("max_matched_rows_per_taxon") != MAX_MATCHED_ROWS_PER_TAXON:
        reasons.append("matched_row_ceiling_changed")

    if manifest.get("execution_consumed") is True:
        reasons.append("execution_already_consumed")
    if manifest.get("execution_authorized") is not True:
        reasons.append("execution_not_authorized")
    if manifest.get("snapshot_occurrence_rows_allowed") is not True:
        reasons.append("snapshot_occurrence_rows_not_allowed")
    if manifest.get("model_fit_reads_allowed") is not False:
        reasons.append("model_fit_reads_must_remain_closed")
    if manifest.get("invariant_reads_allowed") is not False:
        reasons.append("invariant_reads_must_remain_closed")
    if manifest.get("process_knockout_reads_allowed") is not False:
        reasons.append("process_knockout_reads_must_remain_closed")
    return JOS003AuthorizationDecision(authorized=not reasons, reasons=tuple(reasons))


def require_jos003_execution_authorization(manifest: Mapping[str, object]) -> JOS003AuthorizationDecision:
    decision = evaluate_jos003_execution_manifest(manifest)
    if not decision.authorized:
        raise JOS003ExecutionNotAuthorized(
            "Product-B v7.2 JOS003 snapshot execution is fail-closed: "
            + ",".join(decision.reasons)
        )
    return decision


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
    species_key: str,
    rows: Sequence[Mapping[str, object]],
) -> SnapshotHostSamplingAuditResult:
    adapted = adapt_snapshot_host_rows(rows, expected_species_key=species_key)
    preflight = build_directed_witness_sampling_preflight_from_records(adapted.batch.records)
    summary = preflight.host_summary
    reasons = _host_sampling_reasons(summary)
    return SnapshotHostSamplingAuditResult(
        taxon_id=taxon_id,
        scientific_name=scientific_name,
        species_key=species_key,
        raw_records=preflight.audit.raw_records_x,
        retained_records=preflight.audit.retained_records_x,
        unique_cells=summary.unique_cells,
        effective_cells=summary.effective_cells,
        quality_excluded=preflight.audit.quality_excluded_x,
        missing_uncertainty=preflight.audit.missing_uncertainty_x,
        missing_occurrence_id_rows=adapted.audit.missing_occurrence_id_rows,
        missing_catalog_number_rows=adapted.audit.missing_catalog_number_rows,
        missing_recorder_rows=adapted.audit.missing_recorder_rows,
        identity_fields_unavailable=adapted.audit.unavailable_identity_fields,
        sampling_adequate=not reasons,
        failure_reasons=reasons,
    )


def _validate_transport_result(
    query: SnapshotTaxonQuery,
    result: Mapping[str, Sequence[Mapping[str, object]]],
) -> None:
    reasons = validate_snapshot_taxon_query(query)
    if reasons:
        raise ValueError("invalid frozen snapshot query: " + ",".join(reasons))
    returned = set(str(key) for key in result)
    expected = set(query.species_keys)
    extra = returned - expected
    if extra:
        raise ValueError("snapshot transport returned undeclared species keys: " + ",".join(sorted(extra)))
    for key, rows in result.items():
        if len(rows) > query.max_rows_per_taxon:
            raise ValueError("snapshot matched-row ceiling exceeded for species key " + str(key))


def execute_jos003_snapshot_sampling_preflight(
    *,
    manifest: Mapping[str, object],
    transport: SnapshotOccurrenceTransport,
) -> JOS003SamplingExecutionResult:
    authorization = require_jos003_execution_authorization(manifest)
    minimum = int(manifest["minimum_sampling_adequate_control_hosts"])

    focal_query = SnapshotTaxonQuery(
        group_id="JOS003_focal",
        species_keys=(EXPECTED_X_SPECIES_KEY,),
    )
    focal_batch = transport(focal_query)
    _validate_transport_result(focal_query, focal_batch)
    focal_rows = tuple(focal_batch.get(EXPECTED_X_SPECIES_KEY, ()))
    focal = _host_result(
        taxon_id="JOS003_X",
        scientific_name=EXPECTED_X_NAME,
        species_key=EXPECTED_X_SPECIES_KEY,
        rows=focal_rows,
    )
    if not focal.sampling_adequate:
        return JOS003SamplingExecutionResult(
            authorization=authorization,
            focal=focal,
            controls_opened=False,
            control_results=(),
            adequate_control_host_count=0,
            minimum_required_control_hosts=minimum,
            terminal_state="unresolved_host_sampling",
            terminal_reasons=focal.failure_reasons,
        )

    control_keys = tuple(item[2] for item in EXPECTED_CONTROLS)
    control_query = SnapshotTaxonQuery(
        group_id="JOS003_controls",
        species_keys=control_keys,
    )
    control_batch = transport(control_query)
    _validate_transport_result(control_query, control_batch)
    control_results: list[SnapshotHostSamplingAuditResult] = []
    for control_id, scientific_name, species_key in EXPECTED_CONTROLS:
        control_results.append(
            _host_result(
                taxon_id=control_id,
                scientific_name=scientific_name,
                species_key=species_key,
                rows=tuple(control_batch.get(species_key, ())),
            )
        )

    adequate_count = sum(item.sampling_adequate for item in control_results)
    if adequate_count < minimum:
        state = "unresolved_controls_sampling"
        reasons = ("insufficient_sampling_adequate_control_hosts",)
    else:
        state = "engineering_snapshot_sampling_preflight_passed"
        reasons = ()
    return JOS003SamplingExecutionResult(
        authorization=authorization,
        focal=focal,
        controls_opened=True,
        control_results=tuple(control_results),
        adequate_control_host_count=adequate_count,
        minimum_required_control_hosts=minimum,
        terminal_state=state,
        terminal_reasons=reasons,
    )


__all__ = [
    "EXPECTED_MANIFEST_VERSION",
    "EXPECTED_PAIR_ID",
    "EXPECTED_X_SPECIES_KEY",
    "EXPECTED_CONTROLS",
    "JOS003ExecutionNotAuthorized",
    "JOS003AuthorizationDecision",
    "SnapshotHostSamplingAuditResult",
    "JOS003SamplingExecutionResult",
    "evaluate_jos003_execution_manifest",
    "require_jos003_execution_authorization",
    "execute_jos003_snapshot_sampling_preflight",
]
