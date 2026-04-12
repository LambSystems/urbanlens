from __future__ import annotations

import json
import re
from io import BytesIO

from PIL import Image

from ..llm import get_llm_provider
from ..schemas import HotspotType, SurfaceFamily


def _extract_json(text: str) -> dict | None:
    if not text:
        return None
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            return None
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return None


def _sanitize_enum(value: str | None, enum_cls, default):
    if not value:
        return default
    try:
        return enum_cls(value)
    except Exception:
        return default


def classify_hotspot_crop_with_llm(
    crop: Image.Image,
    intensity: float,
    fallback_type: HotspotType,
    fallback_family: SurfaceFamily,
) -> dict | None:
    provider = get_llm_provider()
    classify_fn = getattr(provider, "classify_hotspot_image", None)
    if not callable(classify_fn):
        return None

    buffer = BytesIO()
    crop.save(buffer, format="PNG")
    image_bytes = buffer.getvalue()

    prompt = (
        "Classify this satellite hotspot crop with surrounding context. "
        "You are looking at a heated area found by a thermal model, but you must identify the visible surface "
        "from RGB imagery, not just heat. "
        "Pay close attention to urban context clues such as parking lane striping, road continuity, roof edges, rooftop equipment, and vegetation patterns. "
        "Choose one surface_family from: built_surface, paved_surface, vegetated_area, mechanical_feature, ambiguous. "
        "Choose one hotspot_type from: roof, road_pavement, parking_lot, hvac_mechanical, vegetation_loss, other. "
        "If uncertain between fine-grained classes, prefer hotspot_type=other and keep the broader surface_family. "
        "Return JSON only with keys: surface_family, hotspot_type, type_confidence, object_label, reasoning. "
        f"Fallback type from heuristics: {fallback_type.value}. "
        f"Fallback family from heuristics: {fallback_family.value}. "
        f"Relative thermal intensity: {intensity:.2f}."
    )

    result = classify_fn(image_bytes=image_bytes, mime_type="image/png", prompt=prompt)
    if not result:
        return None

    payload = _extract_json(result.get("text", ""))
    if not payload:
        return None

    surface_family = _sanitize_enum(payload.get("surface_family"), SurfaceFamily, fallback_family)
    hotspot_type = _sanitize_enum(payload.get("hotspot_type"), HotspotType, HotspotType.other)

    try:
        type_confidence = float(payload.get("type_confidence", 0.0))
    except Exception:
        type_confidence = 0.0

    object_label = str(payload.get("object_label") or hotspot_type.value).strip() or hotspot_type.value
    reasoning = str(payload.get("reasoning") or "").strip()

    return {
        "surface_family": surface_family,
        "hotspot_type": hotspot_type,
        "type_confidence": max(0.0, min(type_confidence, 1.0)),
        "object_label": object_label,
        "reasoning": reasoning,
        "provider": result.get("provider"),
    }
