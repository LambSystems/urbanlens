'use client';

import { ThermalProvider } from '@/lib/thermal-context';
import { ThermalMap } from '@/components/thermal-map';
import { ThermalSidebar } from '@/components/thermal-sidebar';

export default function Home() {
  return (
    <ThermalProvider>
      <main className="h-screen w-screen flex overflow-hidden">
        {/* Map takes remaining space */}
        <div className="flex-1 relative">
          <ThermalMap />
          
          {/* Map overlay: region info */}
          <div className="absolute top-4 left-4 z-10">
            <div className="bg-card/90 backdrop-blur-sm border border-border rounded-lg px-4 py-3 shadow-lg">
              <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">
                Demo Region
              </p>
              <p className="text-sm font-medium">Downtown Phoenix, AZ</p>
              <p className="text-xs text-muted-foreground mt-0.5">
                33.4484°N, 112.0740°W
              </p>
            </div>
          </div>
          
          {/* Map legend */}
          <div className="absolute bottom-4 left-4 z-10">
            <div className="bg-card/90 backdrop-blur-sm border border-border rounded-lg px-3 py-2 shadow-lg">
              <p className="text-[10px] text-muted-foreground uppercase tracking-wider mb-2">
                Heat Severity
              </p>
              <div className="flex items-center gap-3">
                <LegendItem color="bg-red-500" label="Critical" />
                <LegendItem color="bg-orange-500" label="High" />
                <LegendItem color="bg-amber-500" label="Medium" />
                <LegendItem color="bg-green-500" label="Low" />
                <LegendItem color="bg-gray-500" label="Discarded" />
              </div>
            </div>
          </div>
        </div>
        
        {/* Sidebar */}
        <ThermalSidebar />
      </main>
    </ThermalProvider>
  );
}

function LegendItem({ color, label }: { color: string; label: string }) {
  return (
    <div className="flex items-center gap-1.5">
      <span className={`h-2.5 w-2.5 rounded-full ${color}`} />
      <span className="text-[10px] text-muted-foreground">{label}</span>
    </div>
  );
}
