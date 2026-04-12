from __future__ import annotations

<<<<<<< HEAD
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
=======
from ..schemas import BoundingBox, HotspotType, LatLng


def propose_candidates(thermal_data: dict, region_center: LatLng, radius_m: int) -> list[dict]:
    del thermal_data, radius_m
    return [
        {
            "centroid": LatLng(lat=region_center.lat + 0.0007, lng=region_center.lng + 0.0005),
            "bbox": BoundingBox(x=112, y=78, w=64, h=48),
            "hotspot_type": HotspotType.roof,
            "intensity": 0.87,
        },
        {
            "centroid": LatLng(lat=region_center.lat - 0.0003, lng=region_center.lng + 0.0008),
            "bbox": BoundingBox(x=214, y=166, w=86, h=30),
            "hotspot_type": HotspotType.road_pavement,
            "intensity": 0.52,
        },
        {
            "centroid": LatLng(lat=region_center.lat + 0.0004, lng=region_center.lng - 0.0004),
            "bbox": BoundingBox(x=298, y=104, w=38, h=40),
            "hotspot_type": HotspotType.hvac_mechanical,
            "intensity": 0.74,
        },
        {
            "centroid": LatLng(lat=region_center.lat - 0.0006, lng=region_center.lng - 0.0007),
            "bbox": BoundingBox(x=354, y=208, w=92, h=58),
            "hotspot_type": HotspotType.parking_lot,
            "intensity": 0.61,
        },
    ]
>>>>>>> cfcc364afa7f678c2839ff0dfbdd6b652c34845b
