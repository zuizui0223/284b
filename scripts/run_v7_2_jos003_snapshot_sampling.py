#!/usr/bin/env python3
"""Execute the frozen JOS003 v7.2 snapshot sampling preflight exactly once.

The script is inert unless the pair-specific manifest is both frozen and explicitly
authorized. Before any Parquet row scan it re-lists the entire frozen 2026-08-01
snapshot prefix and requires the exact predeclared object-manifest digest. It then
scans the focal host only. The eight frozen controls are scanned in one second
query only when the focal host passes the unchanged 50/30/10 sampling floor.

Raw GBIF rows are never written to the repository or workflow artifact.
"""
from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path
import sys
from typing import Mapping, Sequence
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

import pyarrow.dataset as ds
import pyarrow.fs as pafs

from product_b_v7_2.jos003_execution import execute_jos003_snapshot_sampling_preflight
from product_b_v7_2.snapshot_occurrence import SnapshotTaxonQuery, validate_snapshot_taxon_query
from product_b_v7_2.snapshot_transport import (
    EXPECTED_BUCKET,
    EXPECTED_OBJECT_COUNT,
    EXPECTED_OBJECT_MANIFEST_SHA256,
    EXPECTED_OCCURRENCE_PREFIX,
    EXPECTED_PARQUET_OBJECT_COUNT,
    EXPECTED_REGION,
    EXPECTED_SNAPSHOT_DATE,
    SnapshotObject,
    evaluate_snapshot_contract,
    object_manifest_sha256,
)

ROOT = Path(__file__).resolve().parents[1]
GLOBAL_CONTRACT = ROOT / "config/product_b_v7_2_snapshot_transport_contract_v0_1.json"
MANIFEST = ROOT / "config/product_b_v7_2_jos003_execution_manifest_v0_1.json"
OUTPUT = ROOT / "artifacts/product_b_v7_2_jos003_snapshot_sampling.json"
S3_ENDPOINT = f"https://{EXPECTED_BUCKET}.s3.amazonaws.com/"
DATE_PREFIX = f"occurrence/{EXPECTED_SNAPSHOT_DATE}/"
DATASET_PATH = f"{EXPECTED_BUCKET}/{EXPECTED_OCCURRENCE_PREFIX.rstrip('/')}"
SELECTED_COLUMNS = (
    "gbifid",
    "datasetkey",
    "occurrenceid",
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
)


def _read_bytes(url: str, *, timeout: float = 60.0) -> bytes:
    request = Request(
        url,
        headers={"User-Agent": "zuizui0223-284b-product-b-v7-2-jos003-snapshot/0.1"},
        method="GET",
    )
    with urlopen(request, timeout=timeout) as response:
        return response.read()


def _tag(element: ET.Element, local_name: str) -> str:
    if element.tag.startswith("{"):
        return element.tag.split("}", 1)[0] + "}" + local_name
    return local_name


def _text(parent: ET.Element, local_name: str) -> str:
    child = parent.find(_tag(parent, local_name))
    return "" if child is None or child.text is None else child.text.strip()


def _list_snapshot_objects() -> tuple[SnapshotObject, ...]:
    objects: list[SnapshotObject] = []
    continuation: str | None = None
    page = 0
    while True:
        params = {"list-type": "2", "prefix": DATE_PREFIX, "max-keys": "1000"}
        if continuation:
            params["continuation-token"] = continuation
        root = ET.fromstring(_read_bytes(S3_ENDPOINT + "?" + urlencode(params)))
        page += 1
        for content in root.findall(_tag(root, "Contents")):
            objects.append(
                SnapshotObject(
                    key=_text(content, "Key"),
                    size=int(_text(content, "Size")),
                    etag=_text(content, "ETag"),
                    last_modified=_text(content, "LastModified"),
                )
            )
        if _text(root, "IsTruncated").lower() != "true":
            break
        continuation = _text(root, "NextContinuationToken")
        if not continuation:
            raise ValueError("snapshot listing truncated without continuation token")
        if page > 1000:
            raise ValueError("snapshot listing exceeded 1000 pages")
    return tuple(objects)


def _verify_frozen_snapshot_objects() -> dict[str, object]:
    objects = _list_snapshot_objects()
    digest = object_manifest_sha256(objects)
    parquet_count = sum(item.key.startswith(EXPECTED_OCCURRENCE_PREFIX) for item in objects)
    if len(objects) != EXPECTED_OBJECT_COUNT:
        raise ValueError("snapshot object count changed before row access")
    if parquet_count != EXPECTED_PARQUET_OBJECT_COUNT:
        raise ValueError("snapshot Parquet object count changed before row access")
    if digest != EXPECTED_OBJECT_MANIFEST_SHA256:
        raise ValueError("snapshot object manifest changed before row access")
    return {
        "object_count": len(objects),
        "parquet_object_count": parquet_count,
        "object_manifest_sha256": digest,
    }


class FrozenSnapshotTransport:
    def __init__(self) -> None:
        self._filesystem = None
        self._dataset = None
        self.object_manifest_recheck: dict[str, object] | None = None
        self.object_manifest_recheck_passed = False
        self.row_access_started = False
        self.scan_group_ids: list[str] = []
        self.matched_rows_by_group: dict[str, dict[str, int]] = {}

    def _ensure_dataset(self):
        if self._dataset is not None:
            return self._dataset
        self.object_manifest_recheck = _verify_frozen_snapshot_objects()
        self.object_manifest_recheck_passed = True
        self._filesystem = pafs.S3FileSystem(anonymous=True, region=EXPECTED_REGION)
        self._dataset = ds.dataset(
            DATASET_PATH,
            filesystem=self._filesystem,
            format="parquet",
        )
        return self._dataset

    def __call__(
        self, query: SnapshotTaxonQuery
    ) -> Mapping[str, Sequence[Mapping[str, object]]]:
        reasons = validate_snapshot_taxon_query(query)
        if reasons:
            raise ValueError("invalid frozen snapshot query: " + ",".join(reasons))
        dataset = self._ensure_dataset()
        expression = (
            ds.field("specieskey").isin(list(query.species_keys))
            & (ds.field("countrycode") == query.country_code)
            & (ds.field("occurrencestatus") == query.occurrence_status)
        )
        scanner = dataset.scanner(
            columns=list(SELECTED_COLUMNS),
            filter=expression,
            batch_size=65536,
            use_threads=True,
        )
        grouped: dict[str, list[Mapping[str, object]]] = {
            key: [] for key in query.species_keys
        }
        self.scan_group_ids.append(query.group_id)
        self.row_access_started = True
        for batch in scanner.to_batches():
            for row in batch.to_pylist():
                species_key = str(row.get("specieskey", ""))
                if species_key not in grouped:
                    raise ValueError("snapshot scanner returned undeclared specieskey")
                grouped[species_key].append(row)
                if len(grouped[species_key]) > query.max_rows_per_taxon:
                    raise ValueError(
                        "snapshot matched-row ceiling exceeded for species key " + species_key
                    )
        self.matched_rows_by_group[query.group_id] = {
            key: len(rows) for key, rows in grouped.items()
        }
        return grouped


def _preconditions() -> tuple[dict[str, object], dict[str, object]]:
    global_contract = json.loads(GLOBAL_CONTRACT.read_text(encoding="utf-8"))
    global_decision = evaluate_snapshot_contract(global_contract)
    if not global_decision.passed:
        raise RuntimeError(
            "v7.2 global snapshot contract invalid: " + ",".join(global_decision.reasons)
        )
    if global_contract.get("occurrence_row_reads_allowed") is not False:
        raise RuntimeError("generic snapshot occurrence access must remain closed")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    return global_contract, manifest


def main() -> int:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    transport = FrozenSnapshotTransport()
    try:
        _, manifest = _preconditions()
        result = execute_jos003_snapshot_sampling_preflight(
            manifest=manifest,
            transport=transport,
        )
        outcome = {
            "result_version": "product_b_v7_2_jos003_snapshot_sampling_v0.1",
            "pair_id": "JOS003",
            "status": result.terminal_state,
            "execution": asdict(result),
            "snapshot_date": EXPECTED_SNAPSHOT_DATE,
            "snapshot_object_manifest_sha256": EXPECTED_OBJECT_MANIFEST_SHA256,
            "object_manifest_recheck_passed": transport.object_manifest_recheck_passed,
            "object_manifest_recheck": transport.object_manifest_recheck,
            "snapshot_row_access_started": transport.row_access_started,
            "scan_group_ids": transport.scan_group_ids,
            "matched_rows_by_group": transport.matched_rows_by_group,
            "raw_snapshot_rows_persisted": False,
            "literature_witness_rows_reopened": False,
            "live_occurrence_search_used": False,
            "model_fit_reads_opened": False,
            "invariant_reads_opened": False,
            "process_knockout_reads_opened": False,
        }
        exit_code = 0
    except Exception as exc:
        terminal = (
            "engineering_execution_unresolved"
            if transport.row_access_started
            else "pre_row_execution_failure"
        )
        outcome = {
            "result_version": "product_b_v7_2_jos003_snapshot_sampling_v0.1",
            "pair_id": "JOS003",
            "status": terminal,
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "snapshot_date": EXPECTED_SNAPSHOT_DATE,
            "snapshot_object_manifest_sha256": EXPECTED_OBJECT_MANIFEST_SHA256,
            "object_manifest_recheck_passed": transport.object_manifest_recheck_passed,
            "object_manifest_recheck": transport.object_manifest_recheck,
            "snapshot_row_access_started": transport.row_access_started,
            "scan_group_ids": transport.scan_group_ids,
            "matched_rows_by_group": transport.matched_rows_by_group,
            "raw_snapshot_rows_persisted": False,
            "literature_witness_rows_reopened": False,
            "live_occurrence_search_used": False,
            "model_fit_reads_opened": False,
            "invariant_reads_opened": False,
            "process_knockout_reads_opened": False,
        }
        exit_code = 1

    OUTPUT.write_text(json.dumps(outcome, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(outcome, indent=2, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
