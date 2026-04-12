from __future__ import annotations

import base64
import json
from collections import defaultdict
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from threading import Lock
from uuid import uuid4

from .capture_pipeline import (
    build_satellite_capture_source_record,
    ensure_capture_dir,
    inspect_image_file,
    save_capture_image,
    generate_thermal_overlay_from_capture,
    propose_hotspots_from_capture,
    radius_m_from_bounds,
)
from .orchestrator import STEP_INTERVAL_MS, build_analysis_from_candidates
from .schemas import (
    AnalysisEvent,
    AnalysisResponse,
    AnalysisStatus,
    CreateAnalysisFromCaptureMetadataRequest,
    CreateAnalysisFromCaptureRequest,
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
        analysis, events = build_analysis_from_candidates([], {}, payload.center, payload.radius_m, region_id)

        with self._lock:
            self._analyses[region_id] = analysis
            self._events[region_id] = events
            self._created_at[region_id] = datetime.now(UTC)

        return self.get_analysis(region_id)

    def create_analysis_from_capture(self, payload: CreateAnalysisFromCaptureRequest) -> AnalysisResponse:
        region_id = f"region_{uuid4().hex[:8]}"
        image_bytes = base64.b64decode(payload.capture.image_base64)
        image_path = save_capture_image(region_id, image_bytes, suffix=".png")
        image_info = inspect_image_file(image_path)
        metadata_path = self._write_capture_metadata(
            region_id,
            payload.region.model_dump(by_alias=True),
            payload.map.model_dump(by_alias=True),
            payload.viewport.model_dump(),
            payload.image_bounds.model_dump() if payload.image_bounds else None,
            image_info,
        )
        del metadata_path
        return self._create_analysis_from_capture_core(
            region_id=region_id,
            metadata=CreateAnalysisFromCaptureMetadataRequest(
                region=payload.region,
                map=payload.map,
                viewport=payload.viewport,
                image_bounds=payload.image_bounds,
            ),
            image_path=image_path,
        )

    def create_analysis_from_capture_upload(
        self,
        metadata: CreateAnalysisFromCaptureMetadataRequest,
        image_bytes: bytes,
        image_suffix: str = ".png",
    ) -> AnalysisResponse:
        region_id = f"region_{uuid4().hex[:8]}"
        image_path = save_capture_image(region_id, image_bytes, suffix=image_suffix)
        image_info = inspect_image_file(image_path)
        metadata_path = self._write_capture_metadata(
            region_id,
            metadata.region.model_dump(by_alias=True),
            metadata.map.model_dump(by_alias=True),
            metadata.viewport.model_dump(),
            metadata.image_bounds.model_dump() if metadata.image_bounds else None,
            image_info,
        )
        del metadata_path
        return self._create_analysis_from_capture_core(
            region_id=region_id,
            metadata=metadata,
            image_path=image_path,
        )

    def _create_analysis_from_capture_core(
        self,
        region_id: str,
        metadata: CreateAnalysisFromCaptureMetadataRequest,
        image_path: str,
    ) -> AnalysisResponse:
        radius_m = radius_m_from_bounds(metadata.region.bounds)
        image_bounds = metadata.image_bounds or metadata.region.bounds
        thermal_result = generate_thermal_overlay_from_capture(
            satellite_image_path=image_path,
            center=metadata.region.center,
            bounds=image_bounds,
            zoom=int(metadata.map.zoom),
        )
        proposed = propose_hotspots_from_capture(metadata.region.center, radius_m, thermal_result)
        thermal_data = thermal_result.get("thermal_data", {})

        analysis, events = build_analysis_from_candidates(
            proposed, thermal_data, metadata.region.center, radius_m, region_id
        )

        analysis.region.bounds = metadata.region.bounds
        analysis.region.area_km2 = metadata.region.area_km2
        # Store thermal overlay URLs on the region so frontend can render GroundOverlay
        analysis.region.thermal_image_url = thermal_result.get("thermal_image_url")
        analysis.region.thermal_image_path = thermal_result.get("thermal_image_path")
        analysis.region.thermal_image_width = thermal_result.get("thermal_image_width")
        analysis.region.thermal_image_height = thermal_result.get("thermal_image_height")
        analysis.region.thermal_preview_url = thermal_result.get("thermal_preview_url")
        analysis.region.thermal_preview_path = thermal_result.get("thermal_preview_path")
        analysis.region.thermal_preview_width = thermal_result.get("thermal_preview_width")
        analysis.region.thermal_preview_height = thermal_result.get("thermal_preview_height")
        analysis.region.thermal_source = thermal_result.get("source", "unknown")
        analysis.region.source_image_path = thermal_result.get("source_image_path")
        analysis.region.source_image_url = f"/captures/{region_id}/{Path(image_path).name}"
        analysis.region.source_image_width = thermal_result.get("source_image_width")
        analysis.region.source_image_height = thermal_result.get("source_image_height")
        analysis.region.source_image_file_size_bytes = thermal_result.get("source_image_file_size_bytes")
        analysis.region.aligned_rgb_path = thermal_result.get("aligned_rgb_path")
        analysis.region.aligned_rgb_width = thermal_result.get("aligned_rgb_width")
        analysis.region.aligned_rgb_height = thermal_result.get("aligned_rgb_height")
        analysis.region.source_records.insert(
            0,
            build_satellite_capture_source_record(
                region_id=region_id,
                center=metadata.region.center,
                bounds=image_bounds,
                map_state=metadata.map,
                image_path=image_path,
            )
        )
        analysis.region.available_source_count = len(analysis.region.source_records)
        analysis.region.summary.candidate_count = len(analysis.result.hotspots)

        with self._lock:
            self._analyses[region_id] = analysis
            self._events[region_id] = events
            self._created_at[region_id] = datetime.now(UTC)

        return self.get_analysis(region_id)

    @staticmethod
    def _write_capture_metadata(
        region_id: str,
        region: dict,
        map_state: dict,
        viewport: dict,
        image_bounds: dict | None,
        image: dict,
    ) -> str:
        capture_dir = ensure_capture_dir(region_id)
        metadata_path = capture_dir / "metadata.json"
        metadata_path.write_text(
            json.dumps(
                {
                    "region": region,
                    "map": map_state,
                    "viewport": viewport,
                    "image_bounds": image_bounds,
                    "source_image": image,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        return str(metadata_path)

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
            hotspot.updated_at = datetime.now(UTC)

        analysis.region.status = AnalysisStatus.completed if all_terminal else AnalysisStatus.running
        analysis.result.status = analysis.region.status
        return analysis


store = InMemoryAnalysisStore()
