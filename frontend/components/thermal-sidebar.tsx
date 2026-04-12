'use client';

import { useState, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ChevronLeft,
  ChevronRight,
  Flame,
  BarChart2,
  Activity,
  MousePointer2,
  Scan,
  X,
  MapPin,
  Thermometer,
  GripVertical
} from 'lucide-react';
import { useThermal } from '@/lib/thermal-context';
import { RankingPanel } from './ranking-panel';
import { TraceTimeline } from './trace-timeline';
import { RecommendationCard } from './recommendation-card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { cn } from '@/lib/utils';

const SIDEBAR_MIN_WIDTH = 280;
const SIDEBAR_MAX_WIDTH = 640;
const SIDEBAR_DEFAULT_WIDTH = 380;

function RegionSelector() {
  const { 
    selectionMode, 
    startDrawing, 
    cancelSelection, 
    selectedRegion,
    analysisProgress,
    startAnalysis,
    hotspots 
  } = useThermal();

  if (selectionMode === 'idle') {
    return (
      <div className="p-4">
        <div className="rounded-xl border border-dashed border-border bg-muted/30 p-6 text-center">
          <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-primary/10">
            <MousePointer2 className="h-7 w-7 text-primary" />
          </div>
          <h3 className="mb-2 text-base font-semibold">Select Analysis Region</h3>
          <p className="mb-5 text-sm text-muted-foreground leading-relaxed">
            Draw a rectangle on the map to define the area for thermal analysis
          </p>
          <Button onClick={startDrawing} className="w-full gap-2">
            <Scan className="h-4 w-4" />
            Start Selection
          </Button>
        </div>
      </div>
    );
  }

  if (selectionMode === 'drawing') {
    return (
      <div className="p-4">
        <div className="rounded-xl border border-primary/50 bg-primary/5 p-6 text-center">
          <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-primary/20 animate-pulse">
            <MousePointer2 className="h-7 w-7 text-primary" />
          </div>
          <h3 className="mb-2 text-base font-semibold text-primary">Drawing Mode Active</h3>
          <p className="mb-5 text-sm text-muted-foreground leading-relaxed">
            Click and drag on the map to draw a rectangle around your target area
          </p>
          <Button variant="outline" onClick={cancelSelection} className="w-full gap-2">
            <X className="h-4 w-4" />
            Cancel
          </Button>
        </div>
      </div>
    );
  }

  if (selectionMode === 'selected' && selectedRegion) {
    return (
      <div className="p-4 space-y-4">
        <div className="rounded-xl border border-border bg-card p-4">
          <div className="flex items-start gap-3 mb-4">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-green-500/10">
              <MapPin className="h-5 w-5 text-green-500" />
            </div>
            <div className="flex-1 min-w-0">
              <h3 className="font-semibold text-sm">Region Selected</h3>
              <p className="text-xs text-muted-foreground mt-0.5">
                {selectedRegion.areaKm2.toFixed(3)} km² area
              </p>
            </div>
          </div>
          
          <div className="grid grid-cols-2 gap-3 text-xs mb-4">
            <div className="rounded-lg bg-muted/50 p-2.5">
              <p className="text-muted-foreground mb-0.5">North</p>
              <p className="font-mono font-medium">{selectedRegion.bounds.north.toFixed(4)}°</p>
            </div>
            <div className="rounded-lg bg-muted/50 p-2.5">
              <p className="text-muted-foreground mb-0.5">South</p>
              <p className="font-mono font-medium">{selectedRegion.bounds.south.toFixed(4)}°</p>
            </div>
            <div className="rounded-lg bg-muted/50 p-2.5">
              <p className="text-muted-foreground mb-0.5">East</p>
              <p className="font-mono font-medium">{selectedRegion.bounds.east.toFixed(4)}°</p>
            </div>
            <div className="rounded-lg bg-muted/50 p-2.5">
              <p className="text-muted-foreground mb-0.5">West</p>
              <p className="font-mono font-medium">{selectedRegion.bounds.west.toFixed(4)}°</p>
            </div>
          </div>

          <div className="flex gap-2">
            <Button variant="outline" onClick={cancelSelection} className="flex-1">
              Redraw
            </Button>
            <Button onClick={startAnalysis} className="flex-1 gap-2">
              <Thermometer className="h-4 w-4" />
              Analyze
            </Button>
          </div>
        </div>
      </div>
    );
  }

  if (selectionMode === 'analyzing' && analysisProgress) {
    return (
      <div className="p-4">
        <div className="rounded-xl border border-primary/30 bg-card p-5">
          <div className="flex items-center gap-3 mb-5">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
              <Scan className="h-5 w-5 text-primary animate-pulse" />
            </div>
            <div className="flex-1 min-w-0">
              <h3 className="font-semibold text-sm">Analyzing Region</h3>
              <p className="text-xs text-muted-foreground mt-0.5">
                {analysisProgress.message}
              </p>
            </div>
          </div>
          
          <div className="space-y-3">
            <div className="flex items-center justify-between text-xs">
              <span className="text-muted-foreground capitalize">{analysisProgress.phase}</span>
              <span className="font-mono text-primary">{analysisProgress.progress}%</span>
            </div>
            <Progress value={analysisProgress.progress} className="h-2" />
          </div>

          <div className="mt-5 grid grid-cols-4 gap-1.5">
            {['satellite', 'thermal', 'classification', 'scoring'].map((phase, i) => {
              const phases = ['satellite', 'thermal', 'classification', 'scoring'];
              const currentIndex = phases.indexOf(analysisProgress.phase);
              const isComplete = i < currentIndex;
              const isCurrent = i === currentIndex;
              
              return (
                <div 
                  key={phase}
                  className={cn(
                    "h-1.5 rounded-full transition-colors",
                    isComplete && "bg-primary",
                    isCurrent && "bg-primary/50",
                    !isComplete && !isCurrent && "bg-muted"
                  )}
                />
              );
            })}
          </div>
        </div>
      </div>
    );
  }

  if (selectionMode === 'complete') {
    return (
      <div className="p-4">
        <div className="rounded-xl border border-green-500/30 bg-green-500/5 p-4 mb-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-green-500/10">
              <Thermometer className="h-5 w-5 text-green-500" />
            </div>
            <div className="flex-1 min-w-0">
              <h3 className="font-semibold text-sm text-green-500">Analysis Complete</h3>
              <p className="text-xs text-muted-foreground mt-0.5">
                {hotspots.length} heat zones detected
              </p>
            </div>
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={cancelSelection}
              className="text-xs h-8"
            >
              New Region
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return null;
}

export function ThermalSidebar() {
  const { sidebarOpen, setSidebarOpen, activeHotspot, selectionMode } = useThermal();
  const [activeTab, setActiveTab] = useState('ranking');
  const [sidebarWidth, setSidebarWidth] = useState(SIDEBAR_DEFAULT_WIDTH);

  const isResizing = useRef(false);
  const resizeStartX = useRef(0);
  const resizeStartWidth = useRef(0);

  const handleResizeStart = useCallback((e: React.MouseEvent) => {
    isResizing.current = true;
    resizeStartX.current = e.clientX;
    resizeStartWidth.current = sidebarWidth;
    e.preventDefault();

    const handleMouseMove = (ev: MouseEvent) => {
      if (!isResizing.current) return;
      // Sidebar is on the right, dragging left increases width
      const delta = resizeStartX.current - ev.clientX;
      const next = Math.max(SIDEBAR_MIN_WIDTH, Math.min(SIDEBAR_MAX_WIDTH, resizeStartWidth.current + delta));
      setSidebarWidth(next);
    };

    const handleMouseUp = () => {
      isResizing.current = false;
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    };

    document.body.style.cursor = 'col-resize';
    document.body.style.userSelect = 'none';
    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseup', handleMouseUp);
  }, [sidebarWidth]);

  const showTabs = selectionMode === 'complete';

  return (
    <>
      {/* Toggle button when closed */}
      <AnimatePresence>
        {!sidebarOpen && (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            className="absolute top-4 right-4 z-20"
          >
            <Button
              variant="secondary"
              size="icon"
              onClick={() => setSidebarOpen(true)}
              className="shadow-lg"
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Sidebar panel */}
      <motion.aside
        initial={false}
        animate={{
          width: sidebarOpen ? sidebarWidth : 0,
          opacity: sidebarOpen ? 1 : 0,
        }}
        transition={{ type: 'spring', stiffness: 300, damping: 30 }}
        className={cn(
          "relative h-full border-l border-border bg-sidebar overflow-hidden",
          "flex flex-col"
        )}
      >
        {/* Resize handle — left edge drag strip */}
        {sidebarOpen && (
          <div
            className="absolute left-0 top-0 bottom-0 w-3 z-30 flex items-center justify-center cursor-col-resize group"
            onMouseDown={handleResizeStart}
          >
            <div className="w-0.5 h-12 rounded-full bg-border group-hover:bg-primary/60 transition-colors duration-150" />
          </div>
        )}

        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-sidebar-border bg-sidebar shrink-0">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-md bg-primary/10">
              <Flame className="h-4 w-4 text-primary" />
            </div>
            <div>
              <h1 className="text-sm font-semibold text-sidebar-foreground">UrbanLens</h1>
              <p className="text-[10px] text-muted-foreground">Urban Heat Triage</p>
            </div>
          </div>

          <Button
            variant="ghost"
            size="icon"
            className="h-7 w-7"
            onClick={() => setSidebarOpen(false)}
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>

        {/* Region Selector (shown when not complete) */}
        {!showTabs && (
          <div className="shrink-0 overflow-y-auto">
            <RegionSelector />
          </div>
        )}

        {/* Tabs (shown after analysis complete) */}
        {showTabs && (
          <div className="flex-1 flex flex-col min-h-0">
            {/* "Analysis Complete" banner — fixed height */}
            <div className="shrink-0">
              <RegionSelector />
            </div>

            <Tabs
              value={activeTab}
              onValueChange={setActiveTab}
              className="flex-1 flex flex-col min-h-0"
            >
              <TabsList className="w-full justify-start rounded-none border-b border-sidebar-border bg-transparent px-4 h-10 shrink-0">
                <TabsTrigger
                  value="ranking"
                  className="gap-1.5 data-[state=active]:bg-sidebar-accent"
                >
                  <BarChart2 className="h-3.5 w-3.5" />
                  <span className="text-xs">Ranking</span>
                </TabsTrigger>
                <TabsTrigger
                  value="trace"
                  className="gap-1.5 data-[state=active]:bg-sidebar-accent"
                >
                  <Activity className="h-3.5 w-3.5" />
                  <span className="text-xs">Trace</span>
                  {activeHotspot && (
                    <span className="ml-1 h-1.5 w-1.5 rounded-full bg-primary animate-pulse" />
                  )}
                </TabsTrigger>
              </TabsList>

              {/* Ranking tab — full height scroll */}
              <TabsContent
                value="ranking"
                className="flex-1 min-h-0 m-0 data-[state=inactive]:hidden"
              >
                <RankingPanel />
              </TabsContent>

              {/* Trace tab — timeline scrolls, recommendation pinned below */}
              <TabsContent
                value="trace"
                className="flex-1 min-h-0 m-0 flex flex-col data-[state=inactive]:hidden"
              >
                <div className="flex-1 min-h-0 overflow-hidden">
                  <TraceTimeline />
                </div>

                {activeHotspot && (
                  <div className="shrink-0 border-t border-sidebar-border overflow-y-auto max-h-64 p-3">
                    <RecommendationCard />
                  </div>
                )}
              </TabsContent>
            </Tabs>
          </div>
        )}
      </motion.aside>
    </>
  );
}
