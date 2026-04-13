'use client';

import { ThermalProvider, useThermal } from '@/lib/thermal-context';
import { ThermalMap } from '@/components/thermal-map';
import { ThermalSidebar } from '@/components/thermal-sidebar';
import { cn } from '@/lib/utils';

function MapOverlays() {
  const { selectionMode, selectedRegion, hotspots, analysisProgress } = useThermal();
  
  return (
    <>
      {/* Instruction overlay when drawing */}
      {selectionMode === 'drawing' && (
        <div className="absolute inset-0 pointer-events-none z-5">
          <div className="absolute top-4 left-1/2 -translate-x-1/2">
            <div className="bg-primary text-primary-foreground px-4 py-2 rounded-full text-sm font-medium shadow-lg animate-pulse">
              Click and drag to select region
            </div>
          </div>
        </div>
      )}
      
      {/* Region info overlay */}
      {selectionMode === 'complete' && selectedRegion && (
        <div className="absolute top-4 left-4 z-10">
          <div className="bg-card/95 backdrop-blur-sm border border-border rounded-xl px-4 py-3 shadow-xl">
            <p className="text-[10px] text-muted-foreground uppercase tracking-wider mb-1">
              Selected Region
            </p>
            <p className="text-sm font-semibold">
              {selectedRegion.areaKm2.toFixed(3)} km²
            </p>
            <p className="text-xs text-muted-foreground mt-0.5">
              {hotspots.filter(h => h.status !== 'discarded').length} active heat zones
            </p>
          </div>
        </div>
      )}
      
      {/* Analysis overlay */}
      {selectionMode === 'analyzing' && analysisProgress && (
        <div className="absolute inset-0 bg-background/30 backdrop-blur-[2px] z-10 flex items-center justify-center">
          <div className="bg-card border border-border rounded-2xl p-6 shadow-2xl max-w-xs text-center">
            <div className="mx-auto mb-4 h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center">
              <div className="h-6 w-6 border-2 border-primary border-t-transparent rounded-full animate-spin" />
            </div>
            <p className="font-semibold mb-1">Analyzing Region</p>
            <p className="text-sm text-muted-foreground">{analysisProgress.message}</p>
          </div>
        </div>
      )}
      
      {/* Map legend - only show when we have hotspots */}
      {selectionMode === 'complete' && hotspots.length > 0 && (
        <div className="absolute bottom-4 left-4 z-10">
          <div className="bg-card/95 backdrop-blur-sm border border-border rounded-xl px-4 py-3 shadow-xl">
            <p className="text-[10px] text-muted-foreground uppercase tracking-wider mb-2">
              Heat Severity
            </p>
            <div className="flex items-center gap-4">
              <LegendItem color="bg-red-500" label="Critical" />
              <LegendItem color="bg-orange-500" label="High" />
              <LegendItem color="bg-amber-500" label="Medium" />
              <LegendItem color="bg-green-500" label="Low" />
            </div>
          </div>
        </div>
      )}
      
      {/* Idle state hint */}
      {selectionMode === 'idle' && (
        <div className="absolute bottom-4 left-4 z-10">
          <div className="bg-card/95 backdrop-blur-sm border border-border rounded-xl px-4 py-3 shadow-xl">
            <p className="text-xs text-muted-foreground">
              Use the sidebar to select a region for analysis
            </p>
          </div>
        </div>
      )}
    </>
  );
}

function LegendItem({ color, label }: { color: string; label: string }) {
  return (
    <div className="flex items-center gap-1.5">
      <span className={cn("h-2.5 w-2.5 rounded-full", color)} />
      <span className="text-[11px] text-muted-foreground">{label}</span>
    </div>
  );
}

function DashboardContent() {
  return (
    <main className="h-screen w-screen flex overflow-hidden">
      {/* Map takes remaining space */}
      <div className="flex-1 relative">
        <ThermalMap />
        <MapOverlays />
      </div>
      
      {/* Sidebar */}
      <ThermalSidebar />
    </main>
  );
}

export default function Home() {
  return (
    <ThermalProvider>
      <DashboardContent />
    </ThermalProvider>
  );
}
