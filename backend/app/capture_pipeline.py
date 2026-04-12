from __future__ import annotations

from datetime import UTC, datetime
from math import cos, pi
from pathlib import Path

from PIL import Image

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
        image_url=f"/captures/{region_id}/{Path(image_path).name}",
        lat=center.lat,
        lng=center.lng,
        bounds=bounds,
        timestamp=datetime.now(UTC),
        altitude=None,
        heading=map_state.heading,
        resolution=None,
    )


def generate_thermal_overlay_from_capture(
    satellite_image_path: str,
    center: LatLng,
    bounds: SourceBounds,
    zoom: int = 17,
) -> dict:
    # Store all outputs alongside the source image so every snippet's files
    # live together under data/captures/<region_id>/
    capture_dir = Path(satellite_image_path).parent
    return generate_thermal(
        image_path=satellite_image_path,
        metadata={
            "center": {"lat": center.lat, "lng": center.lng},
            "zoom": zoom,
            "north": bounds.north,
            "south": bounds.south,
            "east": bounds.east,
            "west": bounds.west,
        },
        output_dir=capture_dir,
        allow_fallback=True,
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


def inspect_image_file(image_path: str | Path) -> dict:
    path = Path(image_path)
    with Image.open(path) as image:
        width, height = image.size
    return {
        "path": str(path),
        "url": f"/captures/{path.parent.name}/{path.name}",
        "width": width,
        "height": height,
        "file_size_bytes": path.stat().st_size,
    }
