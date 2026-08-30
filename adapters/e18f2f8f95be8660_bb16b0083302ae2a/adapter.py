from __future__ import annotations

from datetime import datetime
from typing import Any


def translate(data: dict[str, Any]) -> dict[str, Any]:
    """Map the approved weather fixture into the internal observation shape."""
    if not isinstance(data, dict):
        raise TypeError("source payload must be an object")

    cloud_density = data.get("cloud_density")
    coords = data.get("coords")
    timestamp = data.get("timestamp")

    if not isinstance(cloud_density, (int, float)) or isinstance(cloud_density, bool):
        raise TypeError("cloud_density must be numeric")
    if not 0 <= cloud_density <= 100:
        raise ValueError("cloud_density must be between 0 and 100")
    if not isinstance(coords, list) or len(coords) != 2:
        raise ValueError("coords must contain latitude and longitude")
    if not all(isinstance(value, (int, float)) and not isinstance(value, bool) for value in coords):
        raise TypeError("coordinates must be numeric")
    if not isinstance(timestamp, str):
        raise TypeError("timestamp must be an ISO 8601 string")

    recorded_at = datetime.fromisoformat(timestamp)
    return {
        "sunlight_intensity": round(float(1 - cloud_density / 100), 12),
        "lat": float(coords[0]),
        "lng": float(coords[1]),
        "recorded_at": recorded_at.isoformat(),
    }
