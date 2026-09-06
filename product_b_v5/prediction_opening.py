"""Filter sealed prediction artifacts without materializing unauthorized cells."""
from __future__ import annotations

from pathlib import Path
from collections.abc import Iterable

import pandas as pd
import pyarrow.dataset as ds

PREDICTION_COLUMNS = (
    "taxon",
    "source",
    "M_km",
    "procedure",
    "comparison_row_id",
    "ecological_score",
)


def read_authorized_prediction_cells(
    parquet_path: str | Path,
    authorized_cells: Iterable[tuple[int, str]],
) -> pd.DataFrame:
    """Return only prospectively authorized procedure×M rows from a sealed file.

    The filter is applied by the Arrow scanner before conversion to pandas.
    Unauthorized procedure×M rows are therefore never materialized in the
    caller's process. An empty authorization set returns an empty frame without
    opening the parquet artifact.
    """
    allowed = {(int(m), str(p)) for m, p in authorized_cells}
    if not allowed:
        return pd.DataFrame(columns=list(PREDICTION_COLUMNS))

    dataset = ds.dataset(str(parquet_path), format="parquet")
    expression = None
    for m_km, procedure in sorted(allowed):
        term = (ds.field("M_km") == int(m_km)) & (ds.field("procedure") == str(procedure))
        expression = term if expression is None else (expression | term)
    table = dataset.to_table(columns=list(PREDICTION_COLUMNS), filter=expression)
    frame = table.to_pandas()
    observed = {
        (int(row.M_km), str(row.procedure))
        for row in frame[["M_km", "procedure"]].itertuples(index=False)
    }
    if not observed.issubset(allowed):
        raise RuntimeError("filtered prediction reader materialized an unauthorized procedure/M cell")
    return frame


__all__ = ["PREDICTION_COLUMNS", "read_authorized_prediction_cells"]
