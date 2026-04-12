from __future__ import annotations

ANOMALY_THRESHOLD = 0.25


def compute_anomaly_score(
    thermal_intensity: float,
    relative_percentile: float | None = None,
    consistency_score: float | None = None,
) -> float:
    base = thermal_intensity * 0.6
    if relative_percentile is not None:
        base += relative_percentile * 0.3
    if consistency_score is not None:
        base += consistency_score * 0.1
    return round(min(max(base, 0.0), 1.0), 4)


def passes_anomaly_gate(anomaly_score: float) -> bool:
    return anomaly_score >= ANOMALY_THRESHOLD
