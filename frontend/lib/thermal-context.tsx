'use client';

import { createContext, useContext, useState, useCallback, useRef, type ReactNode } from 'react';
import type {
  Hotspot,
  InvestigationSession,
  TracePlaybackState,
  SelectionMode,
  SelectedRegion,
  AnalysisProgress,
  Recommendation,
} from './types';
import { MOCK_SESSION } from './mock-data';
import {
  createAnalysis,
  createAnalysisFromCaptureUpload,
  getAnalysis,
  askQuestion,
  requestVoiceBriefing,
  mapHotspot,
  mapRecommendation,
} from './api';
import type { BackendPlannerResponse, CaptureMapStatePayload } from './api';

const POLL_INTERVAL_MS = 1200; // matches backend STEP_INTERVAL_MS

interface ThermalContextValue {
  // Session state
  session: InvestigationSession;
  hotspots: Hotspot[];
  recommendations: Record<string, Recommendation>;

  // Region selection
  selectionMode: SelectionMode;
  setSelectionMode: (mode: SelectionMode) => void;
  selectedRegion: SelectedRegion | null;
  setSelectedRegion: (region: SelectedRegion | null) => void;
  startDrawing: () => void;
  cancelSelection: () => void;

  // Analysis state
  analysisProgress: AnalysisProgress | null;
  regionId: string | null;
  startAnalysis: () => void;

  // Hotspot inspection
  activeHotspot: Hotspot | null;
  setActiveHotspot: (hotspot: Hotspot | null) => void;

  // Trace playback
  playback: TracePlaybackState;
  setPlayback: (state: TracePlaybackState) => void;
  startPlayback: () => void;
  pausePlayback: () => void;
  resetPlayback: () => void;
  advanceStep: () => void;

  // Planner Q&A
  plannerAnswer: BackendPlannerResponse | null;
  askPlannerQuestion: (question: string) => Promise<void>;
  isPlannerLoading: boolean;

  // Voice briefing
  voiceBriefing: { url: string | null; text: string } | null;
  isVoiceBriefingLoading: boolean;
  playVoiceBriefing: () => Promise<void>;

  // Capture
  setCapture: (payload: {
    imageBase64: string;
    mapState: CaptureMapStatePayload;
    viewport: { north: number; south: number; east: number; west: number } | null;
  } | null) => void;

  // UI state
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
}

const ThermalContext = createContext<ThermalContextValue | null>(null);

// Derive radius_m from a selected region's bounds (half-diagonal in metres)
function boundsToRadius(region: SelectedRegion): number {
  const latHalfDeg = (region.bounds.north - region.bounds.south) / 2;
  const lngHalfDeg = (region.bounds.east - region.bounds.west) / 2;
  const latM = latHalfDeg * 111_000;
  const lngM = lngHalfDeg * 111_000 * Math.cos((region.center.lat * Math.PI) / 180);
  return Math.max(Math.round(Math.sqrt(latM ** 2 + lngM ** 2)), 80);
}

// Given a list of hotspots, derive the current playback index from step statuses.
// Used to auto-sync the trace timeline when the backend progresses steps.
function derivedStepIndex(hotspot: Hotspot): number {
  let last = -1;
  hotspot.trace.forEach((step, idx) => {
    if (step.status === 'completed' || step.status === 'running') last = idx;
  });
  return last;
}

export function ThermalProvider({ children }: { children: ReactNode }) {
  const [session] = useState<InvestigationSession>(MOCK_SESSION);
  const [hotspots, setHotspots] = useState<Hotspot[]>([]);
  const [recommendations, setRecommendations] = useState<Record<string, Recommendation>>({});
  const [activeHotspot, setActiveHotspotState] = useState<Hotspot | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const [selectionMode, setSelectionMode] = useState<SelectionMode>('idle');
  const [selectedRegion, setSelectedRegion] = useState<SelectedRegion | null>(null);
  const [analysisProgress, setAnalysisProgress] = useState<AnalysisProgress | null>(null);
  const [regionId, setRegionId] = useState<string | null>(null);

  const [playback, setPlayback] = useState<TracePlaybackState>({
    isPlaying: false,
    currentStepIndex: -1,
    speed: 800,
  });

  const [plannerAnswer, setPlannerAnswer] = useState<BackendPlannerResponse | null>(null);
  const [isPlannerLoading, setIsPlannerLoading] = useState(false);

  const pollRef = useRef<NodeJS.Timeout | null>(null);
  const activeHotspotIdRef = useRef<string | null>(null);

  // Capture payload stored when user draws rectangle
  const captureRef = useRef<{
    imageBase64: string;
    mapState: CaptureMapStatePayload;
    viewport: { north: number; south: number; east: number; west: number } | null;
  } | null>(null);

  const setCapture = useCallback((payload: typeof captureRef.current) => {
    captureRef.current = payload;
  }, []);

  // Voice briefing state
  const [voiceBriefing, setVoiceBriefing] = useState<{ url: string | null; text: string } | null>(null);
  const [isVoiceBriefingLoading, setIsVoiceBriefingLoading] = useState(false);

  // ── Helpers ──────────────────────────────────────────────────────────────

  const stopPolling = useCallback(() => {
    if (pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
  }, []);

  const applyBackendResponse = useCallback(
    (data: Awaited<ReturnType<typeof getAnalysis>>) => {
      const mapped = data.result.hotspots.map(mapHotspot);
      setHotspots(mapped);

      // Build recommendations for finalized hotspots
      const recs: Record<string, Recommendation> = {};
      for (const bh of data.result.hotspots) {
        const rec = mapRecommendation(bh);
        if (rec) recs[bh.hotspot_id] = rec;
      }
      setRecommendations(recs);

      // Keep activeHotspot in sync so trace timeline updates live
      if (activeHotspotIdRef.current) {
        const updated = mapped.find(h => h.id === activeHotspotIdRef.current);
        if (updated) {
          setActiveHotspotState(updated);
          // Auto-advance playback index to latest completed/running step
          const stepIdx = derivedStepIndex(updated);
          setPlayback(prev => ({ ...prev, currentStepIndex: stepIdx }));
        }
      }

      // Derive progress from backend summary
      const { candidate_count, discarded_count, finalized_count } = data.region.summary;
      const done = discarded_count + finalized_count;
      const progress = candidate_count > 0 ? Math.round((done / candidate_count) * 100) : 0;
      setAnalysisProgress({
        phase: 'scoring',
        progress,
        message: `Investigating ${candidate_count} candidates — ${done} resolved`,
      });

      if (data.result.status === 'completed') {
        stopPolling();
        setSelectionMode('complete');
        setAnalysisProgress(null);
      }
    },
    [stopPolling],
  );

  // ── Region selection ──────────────────────────────────────────────────────

  const startDrawing = useCallback(() => {
    stopPolling();
    setSelectionMode('drawing');
    setSelectedRegion(null);
    setHotspots([]);
    setRecommendations({});
    setActiveHotspotState(null);
    setAnalysisProgress(null);
    setRegionId(null);
    setPlannerAnswer(null);
    setVoiceBriefing(null);
    captureRef.current = null;
    activeHotspotIdRef.current = null;
  }, [stopPolling]);

  const cancelSelection = useCallback(() => {
    stopPolling();
    setSelectionMode('idle');
    setSelectedRegion(null);
    setHotspots([]);
    setRecommendations({});
    setActiveHotspotState(null);
    setAnalysisProgress(null);
    setRegionId(null);
    setPlannerAnswer(null);
    setVoiceBriefing(null);
    captureRef.current = null;
    activeHotspotIdRef.current = null;
  }, [stopPolling]);

  // ── Analysis ──────────────────────────────────────────────────────────────

  const startAnalysis = useCallback(() => {
    if (!selectedRegion) return;
    stopPolling();
    setSelectionMode('analyzing');
    setHotspots([]);
    setRecommendations({});
    setVoiceBriefing(null);
    setAnalysisProgress({ phase: 'satellite', progress: 0, message: 'Capturing satellite image…' });

    const center = { lat: selectedRegion.center.lat, lng: selectedRegion.center.lng };
    const radius_m = boundsToRadius(selectedRegion);
    const cap = captureRef.current;

    const doRequest = cap
      ? createAnalysisFromCaptureUpload(
          { bounds: selectedRegion.bounds, center, areaKm2: selectedRegion.areaKm2 },
          cap.mapState,
          cap.viewport,
          cap.imageBase64,
        )
      : createAnalysis(center, radius_m);

    doRequest
      .then((data) => {
        const rid = data.region.region_id;
        setRegionId(rid);
        applyBackendResponse(data);

        // Start polling until completed
        pollRef.current = setInterval(async () => {
          try {
            const updated = await getAnalysis(rid);
            applyBackendResponse(updated);
          } catch {
            // network hiccup — keep polling
          }
        }, POLL_INTERVAL_MS);
      })
      .catch(() => {
        setSelectionMode('idle');
        setAnalysisProgress(null);
      });
  }, [selectedRegion, stopPolling, applyBackendResponse]);

  // ── Active hotspot ────────────────────────────────────────────────────────

  const setActiveHotspot = useCallback((hotspot: Hotspot | null) => {
    setActiveHotspotState(hotspot);
    activeHotspotIdRef.current = hotspot?.id ?? null;
    if (hotspot) {
      const stepIdx = derivedStepIndex(hotspot);
      setPlayback({ isPlaying: false, currentStepIndex: stepIdx, speed: 800 });
    } else {
      setPlayback({ isPlaying: false, currentStepIndex: -1, speed: 800 });
    }
  }, []);

  // ── Trace playback ────────────────────────────────────────────────────────

  const startPlayback = useCallback(() => {
    setPlayback(prev => ({
      ...prev,
      isPlaying: true,
      currentStepIndex: prev.currentStepIndex < 0 ? 0 : prev.currentStepIndex,
    }));
  }, []);

  const pausePlayback = useCallback(() => {
    setPlayback(prev => ({ ...prev, isPlaying: false }));
  }, []);

  const resetPlayback = useCallback(() => {
    setPlayback({ isPlaying: false, currentStepIndex: -1, speed: 800 });
  }, []);

  const advanceStep = useCallback(() => {
    if (!activeHotspot) return;
    setPlayback(prev => {
      const nextIndex = prev.currentStepIndex + 1;
      const maxIndex = activeHotspot.trace.length - 1;
      if (nextIndex > maxIndex) return { ...prev, isPlaying: false };
      return { ...prev, currentStepIndex: nextIndex };
    });
  }, [activeHotspot]);

  // ── Voice briefing ────────────────────────────────────────────────────────

  const playVoiceBriefing = useCallback(async () => {
    if (!regionId || isVoiceBriefingLoading) return;
    setIsVoiceBriefingLoading(true);
    try {
      const res = await requestVoiceBriefing(regionId);
      setVoiceBriefing({ url: res.audio_url, text: res.summary_text });
      if (res.audio_url) {
        const audio = new Audio(res.audio_url);
        audio.play().catch(() => {/* autoplay blocked — UI shows text fallback */});
      }
    } finally {
      setIsVoiceBriefingLoading(false);
    }
  }, [regionId, isVoiceBriefingLoading]);

  // ── Planner Q&A ───────────────────────────────────────────────────────────

  const askPlannerQuestion = useCallback(
    async (question: string) => {
      if (!regionId) return;
      setIsPlannerLoading(true);
      try {
        const answer = await askQuestion(regionId, question);
        setPlannerAnswer(answer);
      } finally {
        setIsPlannerLoading(false);
      }
    },
    [regionId],
  );

  return (
    <ThermalContext.Provider
      value={{
        session,
        hotspots,
        recommendations,
        selectionMode,
        setSelectionMode,
        selectedRegion,
        setSelectedRegion,
        startDrawing,
        cancelSelection,
        analysisProgress,
        regionId,
        startAnalysis,
        activeHotspot,
        setActiveHotspot,
        playback,
        setPlayback,
        startPlayback,
        pausePlayback,
        resetPlayback,
        advanceStep,
        plannerAnswer,
        askPlannerQuestion,
        isPlannerLoading,
        voiceBriefing,
        isVoiceBriefingLoading,
        playVoiceBriefing,
        setCapture,
        sidebarOpen,
        setSidebarOpen,
      }}
    >
      {children}
    </ThermalContext.Provider>
  );
}

export function useThermal() {
  const context = useContext(ThermalContext);
  if (!context) {
    throw new Error('useThermal must be used within a ThermalProvider');
  }
  return context;
}
