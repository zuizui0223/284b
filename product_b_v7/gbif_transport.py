"""Authorized GBIF search transport for Product-B v7 admin-code occurrence preflight."""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Mapping
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from product_b_v5.gbif_transport import GBIFPartnerTransportAudit, GBIFSearchCeilingExceeded
from product_b_v5.occurrence_source import LogicalOccurrenceQuery
from .gbif_search import (
    GBIF_SEARCH_HARD_LIMIT,
    GBIFSearchEnvelope,
    next_v7_search_request,
    parse_search_envelope,
    serialize_v7_gbif_search_request,
)


class AuthorizedV7GBIFSearchTransport:
    def __init__(self, *, timeout_seconds: float = 60.0) -> None:
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        self.timeout_seconds = float(timeout_seconds)
        self._audits: list[GBIFPartnerTransportAudit] = []

    @property
    def audits(self) -> tuple[GBIFPartnerTransportAudit, ...]:
        return tuple(self._audits)

    def _fetch_payload(self, endpoint: str, params: Mapping[str, str]) -> Mapping[str, object]:
        request = Request(
            endpoint + "?" + urlencode(params),
            headers={
                "Accept": "application/json",
                "User-Agent": "zuizui0223-284b-product-b-v7/0.1",
            },
            method="GET",
        )
        with urlopen(request, timeout=self.timeout_seconds) as response:
            payload = json.loads(response.read().decode("utf-8"))
        if not isinstance(payload, Mapping):
            raise ValueError("GBIF search response must be a JSON object")
        return payload

    def __call__(self, query: LogicalOccurrenceQuery) -> tuple[Mapping[str, object], ...]:
        request = serialize_v7_gbif_search_request(query)
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
                        f"{query.pair_id}:{query.partner} declared count {declared_count} exceeds frozen search ceiling {GBIF_SEARCH_HARD_LIMIT}"
                    )
            elif envelope.count != declared_count:
                raise ValueError("GBIF declared count changed during frozen pagination")

            page_rows = payload["results"]
            if not isinstance(page_rows, list):
                page_rows = list(page_rows)
            for row in page_rows:
                if not isinstance(row, Mapping):
                    raise ValueError("GBIF result row must be a JSON object")
                rows.append(row)
            pages += 1
            request = next_v7_search_request(query, envelope)

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
