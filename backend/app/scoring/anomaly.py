"""
Urban Legend — Anomaly Scoring

Anomaly is the structural gate. Hotspots below the threshold get discarded.

    if anomaly_score < ANOMALY_THRESHOLD:
        discard

Inputs: hotspot features, context comparison, local baseline
Output: anomaly_score (0-1)
"""
from __future__ import annotations

ANOMALY_THRESHOLD = 0.25


def compute_anomaly_score(
    thermal_intensity: float,
    relative_percentile: float | None = None,
    consistency_score: float | None = None,
) -> float:
    """Compute anomaly score for a hotspot.

    STUB: weighted combination of thermal intensity and context signals.
    """
    base = thermal_intensity * 0.6
    if relative_percentile is not None:
        base += relative_percentile * 0.3
    if consistency_score is not None:
        base += consistency_score * 0.1
    return round(min(max(base, 0.0), 1.0), 4)


def passes_anomaly_gate(anomaly_score: float) -> bool:
    """Check whether a hotspot passes the anomaly threshold."""
    return anomaly_score >= ANOMALY_THRESHOLD
