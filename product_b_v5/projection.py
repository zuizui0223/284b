"""Deterministic WGS84 -> EPSG:6933 projection for Product-B v5.

EPSG:6933 is WGS 84 / NSIDC EASE-Grid 2.0 Global using ellipsoidal
Lambert Cylindrical Equal Area, standard parallel 30 degrees, central meridian
0 degrees, false easting/northing 0 metres.  This pure implementation removes a
runtime CRS-library choice from the frozen sampling-cell audit.
"""

from __future__ import annotations

from math import cos, isfinite, log, pi, radians, sin, sqrt


WGS84_SEMI_MAJOR_M = 6_378_137.0
WGS84_INVERSE_FLATTENING = 298.257223563
EPSG6933_STANDARD_PARALLEL_DEG = 30.0
EPSG6933_MIN_LATITUDE_DEG = -86.0
EPSG6933_MAX_LATITUDE_DEG = 86.0

_FLATTENING = 1.0 / WGS84_INVERSE_FLATTENING
_E2 = _FLATTENING * (2.0 - _FLATTENING)
_E = sqrt(_E2)
_STANDARD_PARALLEL_RAD = radians(EPSG6933_STANDARD_PARALLEL_DEG)
_K0 = cos(_STANDARD_PARALLEL_RAD) / sqrt(
    1.0 - _E2 * sin(_STANDARD_PARALLEL_RAD) ** 2
)


def _authalic_q(latitude_rad: float) -> float:
    sin_lat = sin(latitude_rad)
    denominator = 1.0 - _E2 * sin_lat * sin_lat
    logarithmic = log((1.0 - _E * sin_lat) / (1.0 + _E * sin_lat))
    return (1.0 - _E2) * (
        sin_lat / denominator - logarithmic / (2.0 * _E)
    )


def wgs84_to_epsg6933(longitude: float, latitude: float) -> tuple[float, float]:
    """Project one WGS84 lon/lat coordinate into EPSG:6933 metres.

    EPSG:6933's declared area of use is 86 S to 86 N. Coordinates outside that
    latitude range fail closed rather than being extrapolated into sampling cells.
    """

    lon = float(longitude)
    lat = float(latitude)
    if not isfinite(lon) or not isfinite(lat):
        raise ValueError("longitude and latitude must be finite")
    if not (-180.0 <= lon <= 180.0):
        raise ValueError("longitude must be in [-180, 180]")
    if not (EPSG6933_MIN_LATITUDE_DEG <= lat <= EPSG6933_MAX_LATITUDE_DEG):
        raise ValueError("latitude lies outside EPSG:6933 area of use")

    longitude_rad = lon * pi / 180.0
    latitude_rad = lat * pi / 180.0
    easting = WGS84_SEMI_MAJOR_M * _K0 * longitude_rad
    northing = WGS84_SEMI_MAJOR_M * _authalic_q(latitude_rad) / (2.0 * _K0)
    return easting, northing
