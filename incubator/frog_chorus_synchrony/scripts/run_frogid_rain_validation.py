#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

FROGID_URL = "https://dwca-exports.ala.org.au/dr14760.zip"
FROGID_SHA = "f5dd70ed07956e3e37de4fb04692b83a9d726eae2312767c9eda2dcbf61f759d"
WEATHER_URL = "https://archive-api.open-meteo.com/v1/archive"
NS = {"dwc": "http://rs.tdwg.org/dwc/text/"}
START_DATE = "2017-10-01"
END_DATE = "2024-11-09"
WET_MM = 1.0
DRY_CAP = 30
BATCH_SIZE = 20


def fetch_bytes(url: str, timeout: int = 180) -> bytes:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "frogid-chorus-synchrony-validation/0.1",
            "Accept": "application/json,*/*",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read()


def local_term(term: str) -> str:
    return term.rsplit("/", 1)[-1].rsplit("#", 1)[-1] if term else ""


def decode_sep(value: str | None, default: str) -> str:
    if value is None:
        return default
    return bytes(value, "utf-8").decode("unicode_escape")


def core_rows(zf: zipfile.ZipFile):
    meta = ET.fromstring(zf.read("meta.xml"))
    core = meta.find("dwc:core", NS)
    if core is None:
        raise RuntimeError("DwC-A missing core")
    files = core.find("dwc:files", NS)
    location = files.find("dwc:location", NS) if files is not None else None
    if location is None or not location.text:
        raise RuntimeError("DwC-A core missing location")
    filename = location.text.strip()
    fields = {
        local_term(field.attrib.get("term", "")): int(field.attrib["index"])
        for field in core.findall("dwc:field", NS)
    }
    delim = decode_sep(core.attrib.get("fieldsTerminatedBy"), "\t")
    quote = decode_sep(core.attrib.get("fieldsEnclosedBy"), '"')
    ignore = int(core.attrib.get("ignoreHeaderLines", "0"))
    encoding = core.attrib.get("encoding", "UTF-8").replace("-", "")
    reader = csv.reader(
        io.StringIO(zf.read(filename).decode(encoding, errors="replace")),
        delimiter=delim,
        quotechar=quote or '"',
    )
    for _ in range(ignore):
        next(reader, None)
    return fields, reader


def get(row, fields, name):
    idx = fields.get(name)
    return row[idx].strip() if idx is not None and idx < len(row) else ""


def selected(event_id: str) -> bool:
    return hashlib.sha256(event_id.encode("utf-8")).digest()[0] < 16


def grid_cell(value: float) -> float:
    return round(value * 4.0) / 4.0


def parse_date(raw: str) -> date:
    value = str(raw or "").strip()
    # FrogID v7 uses ISO event dates, but accept an ISO datetime defensively.
    try:
        return date.fromisoformat(value[:10])
    except Exception as exc:
        raise ValueError(f"unparseable eventDate {raw!r}") from exc


def parse_hour(raw: str) -> float:
    value = str(raw or "").strip()
    m = re.search(r"(\d{1,2}):(\d{2})(?::(\d{2}(?:\.\d+)?))?", value)
    if not m:
        raise ValueError(f"unparseable eventTime {raw!r}")
    hour = int(m.group(1)) + int(m.group(2)) / 60.0
    if m.group(3):
        hour += float(m.group(3)) / 3600.0
    if not (0 <= hour < 24):
        raise ValueError(f"invalid hour {hour}")
    return hour


def load_frogid_sample():
    data = fetch_bytes(FROGID_URL)
    if hashlib.sha256(data).hexdigest() != FROGID_SHA:
        raise RuntimeError("FrogID archive hash drift")

    zf = zipfile.ZipFile(io.BytesIO(data))
    fields, reader = core_rows(zf)
    required = {
        "eventID", "scientificName", "eventDate", "eventTime",
        "decimalLatitude", "decimalLongitude", "coordinateUncertaintyInMeters",
        "stateProvince", "recordedBy",
    }
    missing = required - set(fields)
    if missing:
        raise RuntimeError(f"FrogID missing fields {sorted(missing)}")

    events = {}
    event_species = defaultdict(set)

    for row in reader:
        event_id = get(row, fields, "eventID")
        if not event_id or not selected(event_id):
            continue

        species = get(row, fields, "scientificName")
        if species:
            event_species[event_id].add(species)

        if event_id in events:
            continue

        try:
            lat = float(get(row, fields, "decimalLatitude"))
            lon = float(get(row, fields, "decimalLongitude"))
            uncertainty = float(get(row, fields, "coordinateUncertaintyInMeters"))
        except Exception:
            continue
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            continue
        if not math.isfinite(uncertainty) or uncertainty > 25000:
            continue

        raw_date = get(row, fields, "eventDate")
        raw_time = get(row, fields, "eventTime")
        state = get(row, fields, "stateProvince")
        recorder = get(row, fields, "recordedBy")
        if not raw_date or not raw_time or not state or not recorder:
            continue

        try:
            event_date = parse_date(raw_date)
            event_hour = parse_hour(raw_time)
        except ValueError:
            continue

        events[event_id] = {
            "eventID": event_id,
            "event_date": event_date,
            "event_hour": event_hour,
            "state": state,
            "recorder": recorder,
            "uncertainty_m": uncertainty,
            "lat": lat,
            "lon": lon,
            "cell_lat": grid_cell(lat),
            "cell_lon": grid_cell(lon),
        }

    rows = []
    for event_id, meta in events.items():
        richness = len(event_species.get(event_id, set()))
        if richness < 1:
            continue
        rows.append(
            {
                **meta,
                "richness": richness,
                "multi": int(richness >= 2),
                "year": meta["event_date"].year,
                "month": meta["event_date"].month,
                "cell_id": f"{meta['cell_lat']:.2f},{meta['cell_lon']:.2f}",
            }
        )

    frame = pd.DataFrame(rows)
    if len(frame) != 40754:
        raise RuntimeError(f"frozen sample size drift: {len(frame)} != 40754")
    if int(frame["multi"].sum()) != 18174:
        raise RuntimeError(
            f"frozen multi-species count drift: {int(frame['multi'].sum())} != 18174"
        )
    if int(frame["cell_id"].nunique()) != 1623:
        raise RuntimeError(
            f"frozen cell count drift: {int(frame['cell_id'].nunique())} != 1623"
        )
    return frame


def weather_request(cells):
    latitudes = ",".join(f"{lat:.2f}" for lat, _ in cells)
    longitudes = ",".join(f"{lon:.2f}" for _, lon in cells)
    params = {
        "latitude": latitudes,
        "longitude": longitudes,
        "start_date": START_DATE,
        "end_date": END_DATE,
        "daily": "precipitation_sum",
        "timezone": "auto",
        "models": "era5",
        "cell_selection": "nearest",
        "elevation": "nan",
    }
    url = WEATHER_URL + "?" + urllib.parse.urlencode(params)
    last_error = None
    for attempt in range(6):
        try:
            payload = json.loads(fetch_bytes(url, timeout=180).decode("utf-8"))
            if isinstance(payload, dict) and payload.get("error"):
                raise RuntimeError(payload.get("reason", "Open-Meteo error"))
            return payload
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, RuntimeError) as exc:
            last_error = exc
            if attempt == 5:
                break
            time.sleep(min(30, 2 ** attempt))
    raise RuntimeError(f"Open-Meteo request failed after retries: {last_error}")


def retrieve_weather(cells):
    weather = {}
    source_hash = hashlib.sha256()
    ordered = sorted(cells)

    for start in range(0, len(ordered), BATCH_SIZE):
        batch = ordered[start:start + BATCH_SIZE]
        payload = weather_request(batch)
        outputs = payload if isinstance(payload, list) else [payload]
        if len(outputs) != len(batch):
            raise RuntimeError(
                f"Open-Meteo batch cardinality mismatch: {len(outputs)} != {len(batch)}"
            )

        for input_cell, record in zip(batch, outputs):
            daily = record.get("daily") or {}
            dates = daily.get("time") or []
            precip = daily.get("precipitation_sum") or []
            if len(dates) != len(precip) or not dates:
                raise RuntimeError(f"incomplete daily precipitation for cell {input_cell}")
            series = {}
            for day_string, value in zip(dates, precip):
                if value is None:
                    raise RuntimeError(
                        f"missing ERA5 precipitation {input_cell} {day_string}"
                    )
                p = float(value)
                if not math.isfinite(p) or p < 0:
                    raise RuntimeError(
                        f"invalid ERA5 precipitation {input_cell} {day_string}: {value}"
                    )
                d = date.fromisoformat(day_string)
                series[d] = p
                source_hash.update(
                    f"{input_cell[0]:.2f},{input_cell[1]:.2f},{day_string},{p:.6f}\n".encode()
                )

            # Contract asks for auto local calendar days; keep timezone metadata as audit.
            weather[input_cell] = {
                "series": series,
                "timezone": record.get("timezone"),
                "latitude": record.get("latitude"),
                "longitude": record.get("longitude"),
                "elevation": record.get("elevation"),
            }
        # Be gentle with the public API.
        time.sleep(0.15)

    return weather, source_hash.hexdigest()


def antecedent_dry_days(series, event_date):
    dry = 0
    for offset in range(1, DRY_CAP + 1):
        d = event_date - timedelta(days=offset)
        if d not in series:
            raise RuntimeError(f"weather date missing: {d}")
        if series[d] >= WET_MM:
            break
        dry += 1
    return dry


def zscore(series):
    x = np.asarray(series, dtype=float)
    mean = float(np.mean(x))
    sd = float(np.std(x, ddof=0))
    if not math.isfinite(sd) or sd == 0:
        raise RuntimeError("invalid z-score SD")
    return (x - mean) / sd, mean, sd


def fit_model(df, cluster_col):
    formula = "multi ~ dry_z + C(state) * C(month) + year_z + sin_hour + cos_hour"
    model = smf.glm(formula, data=df, family=sm.families.Binomial())
    fitted = model.fit(
        cov_type="cluster",
        cov_kwds={"groups": df[cluster_col]},
        maxiter=100,
    )
    term = "dry_z"
    beta = float(fitted.params[term])
    se = float(fitted.bse[term])
    p = float(fitted.pvalues[term])
    q = 1.959963984540054
    lo = beta - q * se
    hi = beta + q * se
    return {
        "n_recordings": int(len(df)),
        "multi_species_recordings": int(df["multi"].sum()),
        "n_clusters": int(df[cluster_col].nunique()),
        "formula": formula,
        "cluster": cluster_col,
        "beta": beta,
        "se_cluster": se,
        "ci95_beta": [lo, hi],
        "odds_ratio_per_sd_log1p_dry_days": math.exp(beta),
        "ci95_or": [math.exp(lo), math.exp(hi)],
        "p_value": p,
        "support_rule_pass": bool(beta < 0 and p < 0.05 and hi < 0),
    }


def main():
    df = load_frogid_sample()
    cells = sorted(set(zip(df["cell_lat"], df["cell_lon"])))
    if len(cells) != 1623:
        raise RuntimeError("cell drift before weather")

    weather, weather_sha = retrieve_weather(cells)

    dry_values = []
    timezone_missing = 0
    for row in df.itertuples(index=False):
        cell_key = (row.cell_lat, row.cell_lon)
        record = weather.get(cell_key)
        if record is None:
            raise RuntimeError(f"missing weather cell {cell_key}")
        if not record["timezone"]:
            timezone_missing += 1
        dry_values.append(antecedent_dry_days(record["series"], row.event_date))

    if timezone_missing:
        raise RuntimeError(f"timezone metadata missing for {timezone_missing} events")

    df = df.copy()
    df["dry_days"] = dry_values
    df["log1p_dry"] = np.log1p(df["dry_days"].astype(float))
    df["dry_z"], dry_mean, dry_sd = zscore(df["log1p_dry"])
    df["year_z"], year_mean, year_sd = zscore(df["year"].astype(float))
    radians = 2.0 * math.pi * df["event_hour"].astype(float) / 24.0
    df["sin_hour"] = np.sin(radians)
    df["cos_hour"] = np.cos(radians)

    # Fail closed on any modeling covariate missingness.
    required = [
        "multi", "dry_z", "state", "month", "year_z", "sin_hour", "cos_hour",
        "cell_id", "recorder", "uncertainty_m",
    ]
    if df[required].isna().any().any():
        raise RuntimeError("missing modeled value after frozen sample construction")

    primary = fit_model(df, "cell_id")

    high_precision = df[df["uncertainty_m"] <= 10000].copy()
    if len(high_precision) < 10000:
        raise RuntimeError("high-coordinate-precision sensitivity became underpowered structurally")
    sensitivity_precision = fit_model(high_precision, "cell_id")
    sensitivity_recorder = fit_model(df, "recorder")

    dry_hist = Counter(int(v) for v in df["dry_days"])
    cell_timezones = Counter(
        weather[(lat, lon)]["timezone"] for lat, lon in cells
    )

    result = {
        "analysis": "frogid_rain_synchrony_external_validation_v0_1",
        "contract": "FROGID_VALIDATION_MODEL_CONTRACT_V0_1.json",
        "frogid_source_sha256": FROGID_SHA,
        "weather_source": {
            "provider": "Open-Meteo Historical Weather API",
            "model": "ERA5",
            "normalized_daily_weather_sha256": weather_sha,
            "cells": len(cells),
            "retrieval_window": [START_DATE, END_DATE],
            "wet_day_threshold_mm": WET_MM,
            "event_day_excluded": True,
            "dry_day_cap": DRY_CAP,
            "timezone_counts": dict(sorted(cell_timezones.items())),
        },
        "frozen_sample": {
            "recordings": int(len(df)),
            "multi_species_recordings": int(df["multi"].sum()),
            "weather_cells": int(df["cell_id"].nunique()),
            "recorders": int(df["recorder"].nunique()),
            "high_precision_recordings_le10km": int(len(high_precision)),
        },
        "exposure": {
            "dry_days_histogram": {
                str(k): int(v) for k, v in sorted(dry_hist.items())
            },
            "log1p_dry_mean": dry_mean,
            "log1p_dry_sd": dry_sd,
            "calendar_year_mean": year_mean,
            "calendar_year_sd": year_sd,
        },
        "primary": primary,
        "sensitivities": {
            "coordinate_uncertainty_le10km": sensitivity_precision,
            "recorder_cluster": sensitivity_recorder,
        },
        "naamp_primary_replaced": False,
        "causal_claim_authorized": False,
        "post_opening_retuning_performed": False,
    }

    out = Path("frog_frogid_rain_validation_v0_1.json")
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
