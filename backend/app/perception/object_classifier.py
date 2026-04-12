from __future__ import annotations

from colorsys import rgb_to_hsv
from pathlib import Path

from PIL import Image, ImageStat

from ..schemas import BoundingBox, HotspotType, SurfaceFamily
from .vision_classifier import classify_hotspot_crop_with_llm

_MODEL_W = 640
_MODEL_H = 512
_PROMOTE_CONFIDENCE = 0.82


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

    green_count = 0
    dark_count = 0
    light_count = 0
    low_sat_count = 0

    for r, g, b in pixels:
        brightness = (r + g + b) / 3
        _, saturation, _ = rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
        if g > r * 1.08 and g > b * 1.05 and g > 60:
            green_count += 1
        if brightness < 92:
            dark_count += 1
        if brightness > 185:
            light_count += 1
        if saturation < 0.18:
            low_sat_count += 1

    return {
        "mean_r": mean_r,
        "mean_g": mean_g,
        "mean_b": mean_b,
        "std_mean": (std_r + std_g + std_b) / 3,
        "green_ratio": green_count / total,
        "dark_ratio": dark_count / total,
        "light_ratio": light_count / total,
        "low_sat_ratio": low_sat_count / total,
        "aspect_ratio": crop.width / max(crop.height, 1),
        "area_ratio": (crop.width * crop.height) / max(_MODEL_W * _MODEL_H, 1),
    }


def _family_from_features(features: dict[str, float]) -> SurfaceFamily:
    aspect_ratio = features["aspect_ratio"]
    elongated = aspect_ratio > 2.4 or aspect_ratio < 0.42

    if features["green_ratio"] > 0.34 and features["mean_g"] > features["mean_r"] + 8:
        return SurfaceFamily.vegetated_area
    if elongated or features["low_sat_ratio"] > 0.58:
        return SurfaceFamily.paved_surface
    if features["light_ratio"] > 0.15 and features["area_ratio"] < 0.018:
        return SurfaceFamily.mechanical_feature
    if features["low_sat_ratio"] > 0.42:
        return SurfaceFamily.built_surface
    return SurfaceFamily.ambiguous


def classify_object(
    image_path: str | None,
    bbox: BoundingBox,
    intensity: float,
    fallback_type: HotspotType = HotspotType.other,
) -> dict:
    """Classify only when a vision tool is confident; otherwise keep ThermalGen output semantic-neutral."""
    crop = _crop_from_bbox(image_path, bbox, expand=1.65)
    if crop is None:
        return {
            "hotspot_type": HotspotType.other,
            "surface_family": SurfaceFamily.ambiguous,
            "type_confidence": 0.30,
            "object_label": "thermal_peak",
            "object_confidence": 0.30,
            "llm_reasoning": "",
            "classification_method": "thermal_only",
            "visual_features": {},
        }

    features = _visual_features(crop)
    fallback_family = _family_from_features(features)
    llm_result = classify_hotspot_crop_with_llm(
        crop=crop,
        intensity=intensity,
        fallback_type=fallback_type,
        fallback_family=fallback_family,
    )

    if llm_result:
        llm_confidence = float(llm_result["type_confidence"])
        llm_type = llm_result["hotspot_type"]
        if llm_type != HotspotType.other and llm_confidence >= _PROMOTE_CONFIDENCE:
            return {
                "hotspot_type": llm_type,
                "surface_family": llm_result["surface_family"],
                "type_confidence": round(llm_confidence, 2),
                "object_label": llm_result["object_label"],
                "object_confidence": round(llm_confidence, 2),
                "llm_reasoning": llm_result.get("reasoning", ""),
                "classification_method": "vision_llm",
                "visual_features": {k: round(v, 4) for k, v in features.items()},
            }

    return {
        "hotspot_type": HotspotType.other,
        "surface_family": fallback_family,
        "type_confidence": 0.35,
        "object_label": "thermal_peak",
        "object_confidence": 0.35,
        "llm_reasoning": "",
        "classification_method": "thermal_only",
        "visual_features": {k: round(v, 4) for k, v in features.items()},
    }
