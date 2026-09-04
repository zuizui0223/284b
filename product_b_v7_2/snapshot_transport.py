"""Pure validation helpers for Product-B v7.2 GBIF monthly snapshots.

No function in this module downloads or inspects occurrence rows.  It validates
metadata declarations and canonicalizes anonymous S3 object-listing metadata so a
snapshot can be frozen before any future pair is selected.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import hashlib
import json
import re
from typing import Iterable, Mapping, Sequence

EXPECTED_CONTRACT_VERSION = "product_b_v7_2_snapshot_transport_v0.1"
EXPECTED_PROVIDER = "aws_open_data"
EXPECTED_REGION = "us-east-1"
EXPECTED_BUCKET = "gbif-open-data-us-east-1"
EXPECTED_SNAPSHOT_DATE = "2026-08-01"
EXPECTED_OCCURRENCE_PREFIX = "occurrence/2026-08-01/occurrence.parquet/"
EXPECTED_CITATION_KEY = "occurrence/2026-08-01/citation.txt"
DOI_RE = re.compile(r"10\.15468/dl\.[A-Za-z0-9]+", re.IGNORECASE)
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

REQUIRED_SNAPSHOT_FIELDS = (
    "gbifid",
    "datasetkey",
    "occurrenceid",
    "institutioncode",
    "collectioncode",
    "catalognumber",
    "recordedby",
    "eventdate",
    "countrycode",
    "occurrencestatus",
    "decimallatitude",
    "decimallongitude",
    "coordinateuncertaintyinmeters",
    "taxonkey",
    "specieskey",
    "scientificname",
    "issue",
    "license",
    "lastinterpreted",
)


@dataclass(frozen=True)
class SnapshotObject:
    key: str
    size: int
    etag: str
    last_modified: str


@dataclass(frozen=True)
class SnapshotMetadataAudit:
    snapshot_date: str
    object_manifest_sha256: str
    object_count: int
    total_object_bytes: int
    citation_sha256: str
    citation_doi: str
    parquet_object_count: int


@dataclass(frozen=True)
class SnapshotContractDecision:
    passed: bool
    reasons: tuple[str, ...]


def _valid_date(text: str) -> bool:
    try:
        date.fromisoformat(text)
    except ValueError:
        return False
    return True


def canonicalize_object_manifest(objects: Iterable[SnapshotObject]) -> bytes:
    rows = sorted(
        (
            {
                "key": item.key,
                "size": item.size,
                "etag": item.etag,
                "last_modified": item.last_modified,
            }
            for item in objects
        ),
        key=lambda row: row["key"],
    )
    if not rows:
        raise ValueError("snapshot object manifest must not be empty")
    keys = [row["key"] for row in rows]
    if len(keys) != len(set(keys)):
        raise ValueError("snapshot object manifest contains duplicate keys")
    for row in rows:
        if not row["key"].startswith(f"occurrence/{EXPECTED_SNAPSHOT_DATE}/"):
            raise ValueError("snapshot object lies outside frozen date prefix")
        if not isinstance(row["size"], int) or row["size"] < 0:
            raise ValueError("snapshot object size must be a non-negative integer")
        if not str(row["etag"]).strip():
            raise ValueError("snapshot object ETag must not be blank")
        if not str(row["last_modified"]).strip():
            raise ValueError("snapshot object last_modified must not be blank")
    return (json.dumps(rows, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def object_manifest_sha256(objects: Iterable[SnapshotObject]) -> str:
    return hashlib.sha256(canonicalize_object_manifest(objects)).hexdigest()


def citation_sha256(citation_bytes: bytes) -> str:
    if not citation_bytes:
        raise ValueError("citation.txt must not be empty")
    return hashlib.sha256(citation_bytes).hexdigest()


def extract_citation_doi(citation_text: str) -> str:
    match = DOI_RE.search(citation_text)
    if match is None:
        raise ValueError("citation.txt does not contain a GBIF download DOI")
    return match.group(0).lower()


def build_metadata_audit(
    *,
    objects: Sequence[SnapshotObject],
    citation_bytes: bytes,
) -> SnapshotMetadataAudit:
    parquet_count = sum(item.key.startswith(EXPECTED_OCCURRENCE_PREFIX) for item in objects)
    if parquet_count < 1:
        raise ValueError("frozen snapshot listing contains no occurrence.parquet objects")
    if not any(item.key == EXPECTED_CITATION_KEY for item in objects):
        raise ValueError("frozen snapshot listing does not contain citation.txt")
    citation_text = citation_bytes.decode("utf-8")
    return SnapshotMetadataAudit(
        snapshot_date=EXPECTED_SNAPSHOT_DATE,
        object_manifest_sha256=object_manifest_sha256(objects),
        object_count=len(objects),
        total_object_bytes=sum(item.size for item in objects),
        citation_sha256=citation_sha256(citation_bytes),
        citation_doi=extract_citation_doi(citation_text),
        parquet_object_count=parquet_count,
    )


def evaluate_snapshot_contract(contract: Mapping[str, object]) -> SnapshotContractDecision:
    reasons: list[str] = []
    if contract.get("contract_version") != EXPECTED_CONTRACT_VERSION:
        reasons.append("contract_version_mismatch")
    if contract.get("engineering_only") is not True:
        reasons.append("engineering_only_boundary_changed")
    if contract.get("confirmatory_claims_allowed") is not False:
        reasons.append("confirmatory_claim_boundary_changed")
    if contract.get("live_occurrence_search_forbidden") is not True:
        reasons.append("live_search_not_forbidden")
    if contract.get("primary_transport") != "gbif_monthly_public_cloud_snapshot":
        reasons.append("primary_transport_mismatch")

    snapshot = contract.get("snapshot")
    if not isinstance(snapshot, Mapping):
        reasons.append("snapshot_declaration_missing")
    else:
        if snapshot.get("provider") != EXPECTED_PROVIDER:
            reasons.append("snapshot_provider_mismatch")
        if snapshot.get("region") != EXPECTED_REGION:
            reasons.append("snapshot_region_mismatch")
        if snapshot.get("bucket") != EXPECTED_BUCKET:
            reasons.append("snapshot_bucket_mismatch")
        snapshot_date = str(snapshot.get("snapshot_date", ""))
        if not _valid_date(snapshot_date) or snapshot_date != EXPECTED_SNAPSHOT_DATE:
            reasons.append("snapshot_date_mismatch")
        if snapshot.get("occurrence_prefix") != EXPECTED_OCCURRENCE_PREFIX:
            reasons.append("occurrence_prefix_mismatch")
        if snapshot.get("citation_key") != EXPECTED_CITATION_KEY:
            reasons.append("citation_key_mismatch")

    if contract.get("metadata_reads_allowed") is not True:
        reasons.append("metadata_reads_not_allowed")
    if contract.get("occurrence_row_reads_allowed") is not False:
        reasons.append("occurrence_rows_must_remain_closed")
    if contract.get("new_pair_selection_allowed") is not False:
        reasons.append("pair_selection_must_remain_closed_before_metadata_audit")
    if contract.get("snapshot_native_taxonomy_bridge_required") is not True:
        reasons.append("snapshot_taxonomy_bridge_not_required")
    if contract.get("authenticated_download_creation_in_ci_forbidden") is not True:
        reasons.append("authenticated_download_ci_boundary_changed")

    fields = contract.get("required_snapshot_fields_before_occurrence_execution")
    if not isinstance(fields, list) or tuple(fields) != REQUIRED_SNAPSHOT_FIELDS:
        reasons.append("required_snapshot_schema_changed")

    floor = contract.get("future_pair_sampling_floor")
    if not isinstance(floor, Mapping) or (
        floor.get("minimum_independent_records"),
        floor.get("minimum_unique_10km_cells"),
        floor.get("minimum_effective_10km_cells"),
    ) != (50, 30, 10.0):
        reasons.append("host_sampling_floor_changed")

    witnesses = contract.get("future_literature_witness_floor")
    if not isinstance(witnesses, Mapping) or (
        witnesses.get("minimum_independent_witnesses"),
        witnesses.get("minimum_unique_10km_cells"),
    ) != (5, 3):
        reasons.append("literature_witness_floor_changed")
    if contract.get("minimum_sampling_adequate_control_hosts") != 5:
        reasons.append("minimum_control_count_changed")

    firewalled = contract.get("firewalled_consumed_pairs")
    required_firewall = {"OPM_FIG_001", "OPM_YUC_001", "OPM_YUC_002", "SEN001", "EPV001", "HTR001", "KIM001", "JOS001"}
    if not isinstance(firewalled, list) or set(firewalled) != required_firewall:
        reasons.append("consumed_pair_firewall_changed")
    return SnapshotContractDecision(passed=not reasons, reasons=tuple(reasons))


def validate_completed_metadata_audit(audit: Mapping[str, object]) -> tuple[str, ...]:
    reasons: list[str] = []
    if audit.get("snapshot_date") != EXPECTED_SNAPSHOT_DATE:
        reasons.append("audit_snapshot_date_mismatch")
    for field in ("object_manifest_sha256", "citation_sha256"):
        value = str(audit.get(field, ""))
        if SHA256_RE.fullmatch(value) is None:
            reasons.append(field + "_invalid")
    try:
        object_count = int(audit.get("object_count", 0))
        parquet_count = int(audit.get("parquet_object_count", 0))
        total_bytes = int(audit.get("total_object_bytes", -1))
    except (TypeError, ValueError):
        reasons.append("audit_counts_invalid")
    else:
        if object_count < 2:
            reasons.append("audit_object_count_too_small")
        if parquet_count < 1:
            reasons.append("audit_has_no_parquet_objects")
        if total_bytes <= 0:
            reasons.append("audit_total_bytes_invalid")
    doi = str(audit.get("citation_doi", ""))
    if DOI_RE.fullmatch(doi) is None:
        reasons.append("citation_doi_invalid")
    return tuple(reasons)


__all__ = [
    "SnapshotObject",
    "SnapshotMetadataAudit",
    "SnapshotContractDecision",
    "REQUIRED_SNAPSHOT_FIELDS",
    "canonicalize_object_manifest",
    "object_manifest_sha256",
    "citation_sha256",
    "extract_citation_doi",
    "build_metadata_audit",
    "evaluate_snapshot_contract",
    "validate_completed_metadata_audit",
]
