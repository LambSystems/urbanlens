from __future__ import annotations

from pathlib import Path

from .schemas import AnalysisResponse, VoiceBriefingResponse


CAPTURES_DIR = Path(__file__).resolve().parents[1] / "data" / "captures"


def build_voice_briefing_summary(analysis: AnalysisResponse, question: str | None = None) -> str:
    if analysis.result.top_hotspots:
        top = analysis.result.top_hotspots[0]
        opener = (
            f"For the question '{question}', " if question else ""
        )
        return (
            f"{opener}the top finding is {top.hotspot_id}, a {top.hotspot_type.value.replace('_', ' ')}. "
            f"It ranked first with anomaly {top.anomaly_score:.2f}, severity {top.severity_score:.2f}, "
            f"and confidence {top.confidence_score:.2f}. The recommended next step is {top.recommended_action}."
        )

    if analysis.result.hotspots:
        return "The analysis completed, but there are no finalized recommendations yet."

    return "No analysis findings are available yet."


def create_voice_briefing(analysis: AnalysisResponse, question: str | None = None) -> VoiceBriefingResponse:
    region_id = analysis.region.region_id
    summary_text = build_voice_briefing_summary(analysis, question=question)

    capture_dir = CAPTURES_DIR / region_id
    capture_dir.mkdir(parents=True, exist_ok=True)
    summary_path = capture_dir / "briefing.txt"
    summary_path.write_text(summary_text, encoding="utf-8")

    audio_path = capture_dir / "briefing.mp3"
    audio_url = f"/data/captures/{region_id}/briefing.mp3" if audio_path.exists() else None

    return VoiceBriefingResponse(
        region_id=region_id,
        audio_url=audio_url,
        summary_text=summary_text,
        provider="elevenlabs_stub",
    )
