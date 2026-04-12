from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from datetime import UTC, datetime
from threading import Lock
from uuid import uuid4

from .orchestrator import STEP_INTERVAL_MS, build_analysis
from .schemas import (
    AnalysisEvent,
    AnalysisResponse,
    AnalysisStatus,
    CreateAnalysisRequest,
    DebugAnalysisView,
    HotspotCandidate,
    HotspotStatus,
    TraceStepStatus,
)


class InMemoryAnalysisStore:
    def __init__(self) -> None:
        self._lock = Lock()
        self._analyses: dict[str, AnalysisResponse] = {}
        self._events: dict[str, list[AnalysisEvent]] = defaultdict(list)
        self._created_at: dict[str, datetime] = {}

    def create_analysis(self, payload: CreateAnalysisRequest) -> AnalysisResponse:
        region_id = f"region_{uuid4().hex[:8]}"
        analysis, events = build_analysis(payload.center, payload.radius_m, region_id)

        with self._lock:
            self._analyses[region_id] = analysis
            self._events[region_id] = events
            self._created_at[region_id] = datetime.now(UTC)

        return self.get_analysis(region_id)

    def get_analysis(self, region_id: str) -> AnalysisResponse:
        with self._lock:
            analysis = deepcopy(self._analyses[region_id])
            events = list(self._events[region_id])
            created_at = self._created_at[region_id]

        elapsed_ms = max(int((datetime.now(UTC) - created_at).total_seconds() * 1000), 0)
        progressed = self._apply_progress(analysis, events, elapsed_ms)
        return progressed

    def get_hotspot(self, region_id: str, hotspot_id: str) -> HotspotCandidate:
        analysis = self.get_analysis(region_id)
        for hotspot in analysis.result.hotspots:
            if hotspot.hotspot_id == hotspot_id:
                return hotspot
        raise KeyError(hotspot_id)

    def get_events(self, region_id: str) -> list[AnalysisEvent]:
        with self._lock:
            events = deepcopy(self._events[region_id])
            created_at = self._created_at[region_id]

        elapsed_ms = max(int((datetime.now(UTC) - created_at).total_seconds() * 1000), 0)
        for event in events:
            event.status = self._status_for_offset(elapsed_ms, event.scheduled_offset_ms)
        return events

    def get_debug_view(self, region_id: str) -> DebugAnalysisView:
        from .orchestrator import build_debug_view

        analysis = self.get_analysis(region_id)
        return build_debug_view(analysis)

    @staticmethod
    def _status_for_offset(elapsed_ms: int, scheduled_offset_ms: int) -> TraceStepStatus:
        if elapsed_ms >= scheduled_offset_ms + STEP_INTERVAL_MS:
            return TraceStepStatus.completed
        if elapsed_ms >= scheduled_offset_ms:
            return TraceStepStatus.running
        return TraceStepStatus.pending

    def _apply_progress(
        self,
        analysis: AnalysisResponse,
        events: list[AnalysisEvent],
        elapsed_ms: int,
    ) -> AnalysisResponse:
        events_by_step = {event.step_id: event for event in events}
        all_terminal = True

        for hotspot in analysis.result.hotspots:
            completed_steps = 0
            for step in hotspot.trace:
                event = events_by_step[step.step_id]
                step.status = self._status_for_offset(elapsed_ms, event.scheduled_offset_ms)
                if step.status == TraceStepStatus.completed:
                    if step.started_at is None:
                        step.started_at = datetime.now(UTC)
                    if step.completed_at is None:
                        step.completed_at = datetime.now(UTC)
                    completed_steps += 1
                elif step.status == TraceStepStatus.running:
                    if step.started_at is None:
                        step.started_at = datetime.now(UTC)
                    all_terminal = False
                else:
                    all_terminal = False

            if hotspot.trace[-1].status != TraceStepStatus.completed:
                hotspot.status = HotspotStatus.investigating
                all_terminal = False
            elif hotspot.trace[-1].kind.value == "discard_hotspot":
                hotspot.status = HotspotStatus.discarded
            else:
                hotspot.status = HotspotStatus.finalized

            if completed_steps and hotspot.status == HotspotStatus.investigating:
                hotspot.status = HotspotStatus.evidence_gathered

        analysis.region.status = AnalysisStatus.completed if all_terminal else AnalysisStatus.running
        analysis.result.status = analysis.region.status
        return analysis


store = InMemoryAnalysisStore()
