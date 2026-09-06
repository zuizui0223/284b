"""Schema-only gate for the frozen Product-B v7.2 monthly snapshot."""
from __future__ import annotations

import hashlib
import json
from typing import Mapping

from .snapshot_transport import REQUIRED_SNAPSHOT_FIELDS


def canonical_schema_bytes(fields: Mapping[str, str]) -> bytes:
    normalized = {str(name): str(dtype) for name, dtype in fields.items()}
    if not normalized:
        raise ValueError("snapshot schema must not be empty")
    if len(normalized) != len(fields):
        raise ValueError("snapshot schema contains duplicate normalized field names")
    return (json.dumps(normalized, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def schema_sha256(fields: Mapping[str, str]) -> str:
    return hashlib.sha256(canonical_schema_bytes(fields)).hexdigest()


def validate_snapshot_schema(fields: Mapping[str, str]) -> tuple[str, ...]:
    reasons: list[str] = []
    names = set(fields)
    missing = [name for name in REQUIRED_SNAPSHOT_FIELDS if name not in names]
    if missing:
        reasons.append("missing_required_fields:" + ",".join(missing))

    for key_field in ("taxonkey", "specieskey", "gbifid"):
        dtype = str(fields.get(key_field, "")).lower()
        if dtype and "string" not in dtype:
            reasons.append(key_field + "_must_be_string_in_2026_08_snapshot")
    for coordinate in ("decimallatitude", "decimallongitude", "coordinateuncertaintyinmeters"):
        dtype = str(fields.get(coordinate, "")).lower()
        if dtype and not any(token in dtype for token in ("double", "float")):
            reasons.append(coordinate + "_must_be_floating")
    recordedby_type = str(fields.get("recordedby", "")).lower()
    if recordedby_type and "list" not in recordedby_type:
        reasons.append("recordedby_must_be_list")
    eventdate_type = str(fields.get("eventdate", "")).lower()
    if eventdate_type and "timestamp" not in eventdate_type:
        reasons.append("eventdate_must_be_timestamp")
    return tuple(reasons)


__all__ = ["canonical_schema_bytes", "schema_sha256", "validate_snapshot_schema"]
