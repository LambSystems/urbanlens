from __future__ import annotations

from datetime import UTC, datetime
from math import cos, pi
from pathlib import Path

from .perception.candidate_discovery import propose_candidates
from .schemas import CaptureMapState, HotspotType, LatLng, SourceBounds, SourceRecord, SourceType
from .thermal.generator import generate_thermal


CAPTURES_DIR = Path(__file__).resolve().parents[1] / "data" / "captures"


def radius_m_from_bounds(bounds: SourceBounds) -> int:
    lat_m = ((bounds.north - bounds.south) * 111_000) / 2
    lng_scale = max(cos(((bounds.north + bounds.south) / 2) * pi / 180), 0.1)
    lng_m = ((bounds.east - bounds.west) * 111_000 * lng_scale) / 2
    return max(int(max(lat_m, lng_m)), 1)


def build_satellite_capture_source_record(
    region_id: str,
    center: LatLng,
    bounds: SourceBounds,
    map_state: CaptureMapState,
    image_path: str,
) -> SourceRecord:
    return SourceRecord(
        source_id=f"satellite_capture_{region_id}",
        source_type=SourceType.satellite,
        image_path=image_path,
        lat=center.lat,
        lng=center.lng,
        bounds=bounds,
        timestamp=datetime.now(UTC),
        altitude=None,
        heading=map_state.heading,
        resolution=None,
        metadata_quality_score=0.92,
        geolocation_confidence=0.95,
    )


def generate_thermal_overlay_from_capture(
    satellite_image_path: str,
    center: LatLng,
    bounds: SourceBounds,
) -> dict:
    return generate_thermal(
        satellite_image_path=satellite_image_path,
        region_bounds={
            "lat": center.lat,
            "lng": center.lng,
            "north": bounds.north,
            "south": bounds.south,
            "east": bounds.east,
            "west": bounds.west,
        },
    )


def propose_hotspots_from_capture(
    center: LatLng,
    radius_m: int,
    thermal_result: dict,
) -> list[dict]:
    thermal_data = thermal_result.get("thermal_data", {})
    return propose_candidates(thermal_data, center, radius_m)


def infer_capture_hotspot_types(candidates: list[dict]) -> list[HotspotType]:
    return [candidate.get("hotspot_type", HotspotType.other) for candidate in candidates]


def ensure_capture_dir(region_id: str) -> Path:
    path = CAPTURES_DIR / region_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_capture_image(region_id: str, image_bytes: bytes, suffix: str = ".png") -> str:
    capture_dir = ensure_capture_dir(region_id)
    image_path = capture_dir / f"source{suffix}"
    image_path.write_bytes(image_bytes)
    return str(image_path)
