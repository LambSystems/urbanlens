'use client';

import { createContext, useContext, useState, useCallback, type ReactNode } from 'react';
import type { 
  Hotspot, 
  InvestigationSession, 
  TracePlaybackState, 
  SelectionMode, 
  SelectedRegion,
  AnalysisProgress,
  BoundingBox 
} from './types';
import { MOCK_SESSION, MOCK_HOTSPOTS, generateHotspotsForRegion } from './mock-data';

interface ThermalContextValue {
  // Session state
  session: InvestigationSession;
  hotspots: Hotspot[];
  
  // Region selection (TeraWatt-style)
  selectionMode: SelectionMode;
  setSelectionMode: (mode: SelectionMode) => void;
  selectedRegion: SelectedRegion | null;
  setSelectedRegion: (region: SelectedRegion | null) => void;
  startDrawing: () => void;
  cancelSelection: () => void;
  
  // Analysis state
  analysisProgress: AnalysisProgress | null;
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
  
  // UI state
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
}

const ThermalContext = createContext<ThermalContextValue | null>(null);

export function ThermalProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<InvestigationSession>(MOCK_SESSION);
  const [hotspots, setHotspots] = useState<Hotspot[]>([]);
  const [activeHotspot, setActiveHotspotState] = useState<Hotspot | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  
  // Region selection state
  const [selectionMode, setSelectionMode] = useState<SelectionMode>('idle');
  const [selectedRegion, setSelectedRegion] = useState<SelectedRegion | null>(null);
  const [analysisProgress, setAnalysisProgress] = useState<AnalysisProgress | null>(null);
  
  const [playback, setPlayback] = useState<TracePlaybackState>({
    isPlaying: false,
    currentStepIndex: -1,
    speed: 800,
  });

  const startDrawing = useCallback(() => {
    setSelectionMode('drawing');
    setSelectedRegion(null);
    setHotspots([]);
    setActiveHotspotState(null);
    setAnalysisProgress(null);
  }, []);

  const cancelSelection = useCallback(() => {
    setSelectionMode('idle');
    setSelectedRegion(null);
    setHotspots([]);
    setActiveHotspotState(null);
    setAnalysisProgress(null);
  }, []);

  const startAnalysis = useCallback(() => {
    if (!selectedRegion) return;
    
    setSelectionMode('analyzing');
    
    // Simulate analysis phases
    const phases: Array<{ phase: AnalysisProgress['phase']; message: string; duration: number }> = [
      { phase: 'satellite', message: 'Acquiring satellite imagery...', duration: 800 },
      { phase: 'thermal', message: 'Processing thermal bands...', duration: 1200 },
      { phase: 'classification', message: 'Classifying heat sources...', duration: 1000 },
      { phase: 'scoring', message: 'Computing anomaly scores...', duration: 800 },
    ];

    let currentPhase = 0;
    
    const runPhase = () => {
      if (currentPhase >= phases.length) {
        // Analysis complete - generate hotspots
        const newHotspots = generateHotspotsForRegion(selectedRegion.bounds);
        setHotspots(newHotspots);
        setSelectionMode('complete');
        setAnalysisProgress(null);
        return;
      }

      const phase = phases[currentPhase];
      let progress = 0;
      
      setAnalysisProgress({
        phase: phase.phase,
        progress: 0,
        message: phase.message,
      });

      const progressInterval = setInterval(() => {
        progress += 10;
        if (progress >= 100) {
          clearInterval(progressInterval);
          currentPhase++;
          setTimeout(runPhase, 100);
        } else {
          setAnalysisProgress({
            phase: phase.phase,
            progress,
            message: phase.message,
          });
        }
      }, phase.duration / 10);
    };

    runPhase();
  }, [selectedRegion]);

  const setActiveHotspot = useCallback((hotspot: Hotspot | null) => {
    setActiveHotspotState(hotspot);
    setPlayback({
      isPlaying: false,
      currentStepIndex: -1,
      speed: 800,
    });
  }, []);

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
    setPlayback({
      isPlaying: false,
      currentStepIndex: -1,
      speed: 800,
    });
  }, []);

  const advanceStep = useCallback(() => {
    if (!activeHotspot) return;
    
    setPlayback(prev => {
      const nextIndex = prev.currentStepIndex + 1;
      const maxIndex = activeHotspot.trace.length - 1;
      
      if (nextIndex > maxIndex) {
        return { ...prev, isPlaying: false };
      }
      
      return { ...prev, currentStepIndex: nextIndex };
    });
  }, [activeHotspot]);

  return (
    <ThermalContext.Provider
      value={{
        session,
        hotspots,
        selectionMode,
        setSelectionMode,
        selectedRegion,
        setSelectedRegion,
        startDrawing,
        cancelSelection,
        analysisProgress,
        startAnalysis,
        activeHotspot,
        setActiveHotspot,
        playback,
        setPlayback,
        startPlayback,
        pausePlayback,
        resetPlayback,
        advanceStep,
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
