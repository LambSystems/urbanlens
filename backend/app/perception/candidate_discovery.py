from __future__ import annotations

from ..schemas import HotspotType, LatLng


def propose_candidates(
    thermal_data: dict,
    center: LatLng,
    radius_m: int,
) -> list[dict]:
    """
    Propose hotspot candidates from thermal overlay data.

    In live mode, thermal_data would contain intensity maps from ThermalGen.
    In demo/mock mode (thermal_data is empty), returns a lightweight placeholder
    list so the analysis pipeline still runs.
    """
    if not thermal_data:
        return [
            {
                "hotspot_type": HotspotType.roof,
                "centroid_offset": (0.0, 0.0),
                "source": "capture_fallback",
            }
        ]

    hotspots: list[dict] = []
    hotspot_regions = thermal_data.get("hotspot_regions", [])

    for i, region in enumerate(hotspot_regions):
        lat_offset = region.get("lat_offset", 0.0)
        lng_offset = region.get("lng_offset", 0.0)
        raw_type = region.get("type", "other")
        try:
            htype = HotspotType(raw_type)
        except ValueError:
            htype = HotspotType.other

        hotspots.append(
            {
                "hotspot_type": htype,
                "centroid_offset": (lat_offset, lng_offset),
                "intensity": region.get("intensity", 0.5),
                "source": "thermalgen",
            }
        )

    return hotspots
