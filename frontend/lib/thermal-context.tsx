'use client';

import { createContext, useContext, useState, useCallback, type ReactNode } from 'react';
import type { Hotspot, InvestigationSession, TracePlaybackState } from './types';
import { MOCK_SESSION, MOCK_HOTSPOTS } from './mock-data';

interface ThermalContextValue {
  session: InvestigationSession;
  hotspots: Hotspot[];
  activeHotspot: Hotspot | null;
  setActiveHotspot: (hotspot: Hotspot | null) => void;
  playback: TracePlaybackState;
  setPlayback: (state: TracePlaybackState) => void;
  startPlayback: () => void;
  pausePlayback: () => void;
  resetPlayback: () => void;
  advanceStep: () => void;
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
}

const ThermalContext = createContext<ThermalContextValue | null>(null);

export function ThermalProvider({ children }: { children: ReactNode }) {
  const [session] = useState<InvestigationSession>(MOCK_SESSION);
  const [hotspots] = useState<Hotspot[]>(MOCK_HOTSPOTS);
  const [activeHotspot, setActiveHotspotState] = useState<Hotspot | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [playback, setPlayback] = useState<TracePlaybackState>({
    isPlaying: false,
    currentStepIndex: -1,
    speed: 800,
  });

  const setActiveHotspot = useCallback((hotspot: Hotspot | null) => {
    setActiveHotspotState(hotspot);
    // Reset playback when switching hotspots
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
