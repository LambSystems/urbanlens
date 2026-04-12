from __future__ import annotations

ANOMALY_THRESHOLD = 0.35


def compute_anomaly_score(
    thermal_intensity: float,
    relative_percentile: float,
    consistency_score: float,
) -> float:
    """Weighted anomaly score — gates whether a hotspot is worth escalating."""
    raw = (
        thermal_intensity * 0.45
        + relative_percentile * 0.35
        + consistency_score * 0.20
    )
    return round(min(max(raw, 0.0), 1.0), 4)


def passes_anomaly_gate(anomaly_score: float) -> bool:
    return anomaly_score >= ANOMALY_THRESHOLD
