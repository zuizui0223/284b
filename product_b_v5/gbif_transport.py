"""Authorized standard-library GBIF occurrence transport for Product-B v5.

This module is inert until called through the already-frozen one-shot pipeline.
It uses only the request serializer in :mod:`product_b_v5.gbif_search`, preserves
its page/ceiling semantics, and keeps raw occurrence rows in memory only.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Mapping
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .gbif_search import (
    GBIF_SEARCH_HARD_LIMIT,
    GBIFSearchEnvelope,
    next_search_request,
    parse_search_envelope,
    serialize_gbif_search_request,
)
from .occurrence_source import LogicalOccurrenceQuery


class GBIFSearchCeilingExceeded(RuntimeError):
    """Raised when an opened count cannot be retrieved under frozen search rules."""


@dataclass(frozen=True)
class GBIFPartnerTransportAudit:
    pair_id: str
    partner: str
    declared_count: int
    pages_fetched: int
    rows_fetched: int


class AuthorizedGBIFSearchTransport:
    """Callable GBIF search transport with auditable per-partner paging metadata."""

    def __init__(self, *, timeout_seconds: float = 60.0) -> None:
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        self.timeout_seconds = float(timeout_seconds)
        self._audits: list[GBIFPartnerTransportAudit] = []

    @property
    def audits(self) -> tuple[GBIFPartnerTransportAudit, ...]:
        return tuple(self._audits)

    def _fetch_payload(self, endpoint: str, params: Mapping[str, str]) -> Mapping[str, object]:
        url = endpoint + "?" + urlencode(params)
        request = Request(
            url,
            headers={
                "Accept": "application/json",
                "User-Agent": "zuizui0223-284b-product-b-v5/0.2",
            },
            method="GET",
        )
        with urlopen(request, timeout=self.timeout_seconds) as response:
            payload = json.loads(response.read().decode("utf-8"))
        if not isinstance(payload, Mapping):
            raise ValueError("GBIF search response must be a JSON object")
        return payload

    def __call__(self, query: LogicalOccurrenceQuery) -> tuple[Mapping[str, object], ...]:
        request = serialize_gbif_search_request(query)
        rows: list[Mapping[str, object]] = []
        pages = 0
        declared_count: int | None = None

        while request is not None:
            payload = self._fetch_payload(request.endpoint, request.as_mapping())
            envelope: GBIFSearchEnvelope = parse_search_envelope(payload)
            if pages == 0:
                declared_count = envelope.count
                if declared_count > GBIF_SEARCH_HARD_LIMIT:
                    raise GBIFSearchCeilingExceeded(
                        f"{query.pair_id}:{query.partner} declared count {declared_count} "
                        f"exceeds frozen search ceiling {GBIF_SEARCH_HARD_LIMIT}"
                    )
            elif envelope.count != declared_count:
                raise ValueError("GBIF declared count changed during frozen pagination")

            page_rows = payload["results"]
            if not isinstance(page_rows, list):
                page_rows = list(page_rows)  # validated as a non-string sequence upstream
            for row in page_rows:
                if not isinstance(row, Mapping):
                    raise ValueError("GBIF result row must be a JSON object")
                rows.append(row)
            pages += 1
            request = next_search_request(query, envelope)

        if declared_count is None:
            raise ValueError("GBIF transport completed without opening a first page")
        if len(rows) != declared_count:
            raise ValueError(
                f"GBIF pagination row count mismatch: declared={declared_count}, fetched={len(rows)}"
            )
        self._audits.append(
            GBIFPartnerTransportAudit(
                pair_id=query.pair_id,
                partner=query.partner,
                declared_count=declared_count,
                pages_fetched=pages,
                rows_fetched=len(rows),
            )
        )
        return tuple(rows)
