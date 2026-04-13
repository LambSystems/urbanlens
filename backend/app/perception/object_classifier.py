from __future__ import annotations

from colorsys import rgb_to_hsv
from pathlib import Path

from PIL import Image, ImageStat

from ..schemas import BoundingBox, HotspotType, SurfaceFamily
from .vision_classifier import classify_hotspot_crop_with_llm

_MODEL_W = 640
_MODEL_H = 512


def _crop_from_bbox(image_path: str | None, bbox: BoundingBox, expand: float = 1.0) -> Image.Image | None:
    if not image_path:
        return None
    path = Path(image_path)
    if not path.exists():
        return None

    image = Image.open(path).convert("RGB")
    scale_x = image.width / _MODEL_W
    scale_y = image.height / _MODEL_H
    cx = bbox.x + bbox.w / 2
    cy = bbox.y + bbox.h / 2
    half_w = (bbox.w * expand) / 2
    half_h = (bbox.h * expand) / 2

    left = max(0, int((cx - half_w) * scale_x))
    top = max(0, int((cy - half_h) * scale_y))
    right = min(image.width, int((cx + half_w) * scale_x))
    bottom = min(image.height, int((cy + half_h) * scale_y))

    if right <= left or bottom <= top:
        return None
    return image.crop((left, top, right, bottom))


def _visual_features(crop: Image.Image) -> dict[str, float]:
    stat = ImageStat.Stat(crop)
    mean_r, mean_g, mean_b = stat.mean[:3]
    std_r, std_g, std_b = stat.stddev[:3]
    sample = crop.resize((48, 48))
    pixels = list(sample.getdata())
    total = max(len(pixels), 1)

    green_ratio = 0
    dark_ratio = 0
    light_ratio = 0
    low_sat_ratio = 0

    for r, g, b in pixels:
        brightness = (r + g + b) / 3
        _, saturation, _ = rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
        if g > r * 1.08 and g > b * 1.05 and g > 60:
            green_ratio += 1
        if brightness < 92:
            dark_ratio += 1
        if brightness > 185:
            light_ratio += 1
        if saturation < 0.18:
            low_sat_ratio += 1

    return {
        "mean_r": mean_r,
        "mean_g": mean_g,
        "mean_b": mean_b,
        "std_mean": (std_r + std_g + std_b) / 3,
        "green_ratio": green_ratio / total,
        "dark_ratio": dark_ratio / total,
        "light_ratio": light_ratio / total,
        "low_sat_ratio": low_sat_ratio / total,
        "aspect_ratio": crop.width / max(crop.height, 1),
        "area_ratio": (crop.width * crop.height) / max(_MODEL_W * _MODEL_H, 1),
    }


def classify_object(
    image_path: str | None,
    bbox: BoundingBox,
    intensity: float,
    fallback_type: HotspotType = HotspotType.other,
) -> dict:
    crop = _crop_from_bbox(image_path, bbox, expand=1.65)
    if crop is None:
        return {
            "hotspot_type": fallback_type,
            "surface_family": SurfaceFamily.ambiguous,
            "type_confidence": 0.45,
            "object_label": fallback_type.value,
            "object_confidence": 0.45,
        }

    features = _visual_features(crop)
    aspect_ratio = features["aspect_ratio"]
    area_ratio = features["area_ratio"]
    elongated = aspect_ratio > 2.4 or aspect_ratio < 0.42
    compact = 0.65 <= aspect_ratio <= 1.7

    hotspot_type = fallback_type
    surface_family = SurfaceFamily.ambiguous
    confidence = 0.52
    label = fallback_type.value

    if features["green_ratio"] > 0.34 and features["mean_g"] > features["mean_r"] + 8:
        hotspot_type = HotspotType.vegetation_loss
        surface_family = SurfaceFamily.vegetated_area
        label = "vegetation"
        confidence = 0.82
    elif area_ratio < 0.018 and intensity >= 0.78 and features["light_ratio"] > 0.15:
        hotspot_type = HotspotType.hvac_mechanical
        surface_family = SurfaceFamily.mechanical_feature
        label = "rooftop_hvac"
        confidence = 0.79
    elif elongated and features["low_sat_ratio"] > 0.58:
        hotspot_type = HotspotType.road_pavement
        surface_family = SurfaceFamily.paved_surface
        label = "road"
        confidence = 0.73
    elif compact and area_ratio > 0.035 and features["low_sat_ratio"] > 0.68 and features["std_mean"] < 42:
        hotspot_type = HotspotType.parking_lot
        surface_family = SurfaceFamily.paved_surface
        label = "parking_lot"
        confidence = 0.76
    elif compact and features["low_sat_ratio"] > 0.45:
        hotspot_type = HotspotType.roof
        surface_family = SurfaceFamily.built_surface
        label = "roof"
        confidence = 0.74
    elif features["dark_ratio"] > 0.28 and area_ratio > 0.03:
        hotspot_type = HotspotType.parking_lot
        surface_family = SurfaceFamily.paved_surface
        label = "parking_lot"
        confidence = 0.65
    elif fallback_type != HotspotType.other:
        hotspot_type = fallback_type
        surface_family = (
            SurfaceFamily.built_surface
            if fallback_type == HotspotType.roof
            else SurfaceFamily.paved_surface
            if fallback_type in {HotspotType.parking_lot, HotspotType.road_pavement}
            else SurfaceFamily.mechanical_feature
            if fallback_type == HotspotType.hvac_mechanical
            else SurfaceFamily.vegetated_area
            if fallback_type == HotspotType.vegetation_loss
            else SurfaceFamily.ambiguous
        )
        label = fallback_type.value
        confidence = 0.58

    if surface_family == SurfaceFamily.ambiguous:
        if features["green_ratio"] > 0.2:
            surface_family = SurfaceFamily.vegetated_area
        elif elongated or features["low_sat_ratio"] > 0.5:
            surface_family = SurfaceFamily.paved_surface
        else:
            surface_family = SurfaceFamily.built_surface

    type_confidence = round(confidence, 2)
    llm_result = classify_hotspot_crop_with_llm(
        crop=crop,
        intensity=intensity,
        fallback_type=hotspot_type,
        fallback_family=surface_family,
    )
    reasoning = ""
    object_label = label
    if llm_result:
        surface_family = llm_result["surface_family"]
        object_label = llm_result["object_label"]
        reasoning = llm_result.get("reasoning", "")
        llm_confidence = float(llm_result["type_confidence"])
        if llm_result["hotspot_type"] != HotspotType.other and llm_confidence >= 0.72:
            hotspot_type = llm_result["hotspot_type"]
            type_confidence = llm_confidence
            confidence = max(confidence, llm_confidence)
        else:
            hotspot_type = HotspotType.other
            type_confidence = max(type_confidence, llm_confidence)
            object_label = surface_family.value

    if type_confidence < 0.68:
        hotspot_type = HotspotType.other
        object_label = surface_family.value

    return {
        "hotspot_type": hotspot_type,
        "surface_family": surface_family,
        "type_confidence": type_confidence,
        "object_label": object_label,
        "object_confidence": round(confidence, 2),
        "llm_reasoning": reasoning,
        "visual_features": {k: round(v, 4) for k, v in features.items()},
    }
