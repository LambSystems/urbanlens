'use client';

import { useMemo } from 'react';
import { motion } from 'framer-motion';
import {
  Building2, 
  Car, 
  Trees, 
  Fan, 
  Route,
  Circle,
  Thermometer,
  TrendingUp,
  ShieldCheck
} from 'lucide-react';
import { useThermal } from '@/lib/thermal-context';
import { getHotspotTypeLabel } from '@/lib/hotspot-labels';
import type { Hotspot, HotspotType } from '@/lib/types';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Progress } from '@/components/ui/progress';
import { cn } from '@/lib/utils';

const TYPE_ICONS: Record<HotspotType, typeof Building2> = {
  roof: Building2,
  parking_lot: Car,
  road_pavement: Route,
  hvac_mechanical: Fan,
  vegetation_loss: Trees,
  other: Circle,
};

function getSeverityColor(score: number): string {
  if (score >= 0.8) return 'text-red-500';
  if (score >= 0.6) return 'text-orange-500';
  if (score >= 0.4) return 'text-amber-500';
  return 'text-green-500';
}

function getSeverityBg(score: number): string {
  if (score >= 0.8) return 'bg-red-500/10';
  if (score >= 0.6) return 'bg-orange-500/10';
  if (score >= 0.4) return 'bg-amber-500/10';
  return 'bg-green-500/10';
}

function getProgressColor(score: number): string {
  if (score >= 0.8) return 'bg-red-500';
  if (score >= 0.6) return 'bg-orange-500';
  if (score >= 0.4) return 'bg-amber-500';
  return 'bg-green-500';
}

function HotspotCard({
  hotspot,
  rank,
  isActive,
  onClick
}: {
  hotspot: Hotspot;
  rank: number;
  isActive: boolean;
  onClick: () => void;
}) {
  const Icon = TYPE_ICONS[hotspot.type] ?? Circle;
  const score = hotspot.scoring?.finalScore ?? 0;
  const isDiscarded = hotspot.status === 'discarded';
  const label = hotspot.displayName ?? getHotspotTypeLabel(hotspot.type);

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: rank * 0.05 }}
      className={cn(
        "rounded-lg border transition-all duration-200",
        isActive
          ? "border-primary bg-primary/5 shadow-sm"
          : "border-border bg-card",
        isDiscarded && "opacity-60"
      )}
    >
      <button
        onClick={onClick}
        className="w-full text-left p-3 hover:bg-muted/30 rounded-lg transition-colors"
      >
        <div className="flex items-start gap-3">
          {/* Rank badge */}
          <div className={cn(
            "flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-xs font-bold",
            isDiscarded
              ? "bg-muted text-muted-foreground"
              : getSeverityBg(score),
            !isDiscarded && getSeverityColor(score)
          )}>
            {isDiscarded ? '×' : `#${rank}`}
          </div>

          {/* Content */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <Icon className="h-4 w-4 text-muted-foreground shrink-0" />
              <span className="text-sm font-medium truncate">{label}</span>
              {/* status_label badge */}
              {hotspot.statusLabel && (
                <span className={cn(
                  "ml-auto shrink-0 text-[9px] font-semibold uppercase tracking-wide px-1.5 py-0.5 rounded",
                  hotspot.status === 'finalized' && hotspot.isTopRanked
                    ? "bg-primary/15 text-primary"
                    : hotspot.status === 'discarded'
                    ? "bg-muted text-muted-foreground"
                    : "bg-amber-500/15 text-amber-500"
                )}>
                  {hotspot.statusLabel}
                </span>
              )}
              {hotspot.status === 'investigating' && !hotspot.statusLabel && (
                <span className="ml-auto flex h-2 w-2 shrink-0">
                  <span className="animate-ping absolute h-2 w-2 rounded-full bg-amber-400 opacity-75" />
                  <span className="relative rounded-full h-2 w-2 bg-amber-500" />
                </span>
              )}
            </div>

            {/* Temperature info */}
            {(hotspot.surfaceTemperature > 0 || hotspot.ambientDelta > 0) && (
              <div className="flex items-center gap-3 text-xs text-muted-foreground mb-2">
                <span className="flex items-center gap-1">
                  <Thermometer className="h-3 w-3" />
                  {hotspot.surfaceTemperature}°C
                </span>
                <span className={cn(
                  "flex items-center gap-1",
                  hotspot.ambientDelta > 15 ? "text-red-400" : "text-amber-400"
                )}>
                  +{hotspot.ambientDelta}° above ambient
                </span>
              </div>
            )}

            {/* Score bars */}
            {hotspot.scoring && !isDiscarded && (
              <div className="space-y-1.5">
                <ScoreBar label="Anomaly" value={hotspot.scoring.anomalyScore} icon={TrendingUp} />
                <ScoreBar label="Severity" value={hotspot.scoring.severityScore} icon={Thermometer} />
                <ScoreBar label="Confidence" value={hotspot.scoring.confidenceScore} icon={ShieldCheck} />
              </div>
            )}

            {isDiscarded && (
              <p className="text-xs text-muted-foreground italic">
                {hotspot.discardReason ?? 'Discarded: Expected heat source'}
              </p>
            )}
          </div>
        </div>
      </button>

      {/* Expanded detail when active */}
      {isActive && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
          transition={{ duration: 0.2 }}
          className="border-t border-border/60 px-3 pb-3 pt-2 space-y-2"
        >
          {/* tool_signals */}
          {hotspot.toolSignals && hotspot.toolSignals.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {hotspot.toolSignals.map((sig) => (
                <span
                  key={sig}
                  className="inline-flex items-center px-2 py-0.5 rounded-full bg-primary/10 text-primary text-[10px] font-medium"
                >
                  {sig}
                </span>
              ))}
            </div>
          )}

          {/* sidebar_summary */}
          {hotspot.sidebarSummary && (
            <p className="text-xs text-muted-foreground leading-relaxed">
              {hotspot.sidebarSummary}
            </p>
          )}

          {/* evidence_highlights */}
          {hotspot.evidenceHighlights && hotspot.evidenceHighlights.length > 0 && (
            <ul className="space-y-1">
              {hotspot.evidenceHighlights.map((h, i) => (
                <li key={i} className="flex items-start gap-1.5 text-xs text-muted-foreground">
                  <span className="mt-1 h-1.5 w-1.5 rounded-full bg-primary/60 shrink-0" />
                  {h}
                </li>
              ))}
            </ul>
          )}

          {/* recommended_action */}
          {hotspot.recommendedAction && !isDiscarded && (
            <div className="rounded-md bg-primary/8 border border-primary/20 px-2.5 py-2">
              <p className="text-[10px] uppercase tracking-wider text-primary/70 font-medium mb-0.5">
                Recommended Next Step
              </p>
              <p className="text-xs font-medium text-foreground">
                {hotspot.recommendedAction}
              </p>
            </div>
          )}
        </motion.div>
      )}
    </motion.div>
  );
}

function ScoreBar({ 
  label, 
  value, 
  icon: Icon 
}: { 
  label: string; 
  value: number; 
  icon: typeof TrendingUp;
}) {
  const percentage = Math.round(value * 100);
  
  return (
    <div className="flex items-center gap-2">
      <Icon className="h-3 w-3 text-muted-foreground shrink-0" />
      <span className="text-[10px] text-muted-foreground w-14 shrink-0">{label}</span>
      <div className="flex-1 h-1.5 bg-muted rounded-full overflow-hidden">
        <div 
          className={cn("h-full rounded-full transition-all duration-500", getProgressColor(value))}
          style={{ width: `${percentage}%` }}
        />
      </div>
      <span className="text-[10px] font-mono text-muted-foreground w-8 text-right">
        {percentage}%
      </span>
    </div>
  );
}

export function RankingPanel() {
  const { hotspots, activeHotspot, setActiveHotspot } = useThermal();
  
  const rankedHotspots = useMemo(() => {
    const finalized = hotspots
      .filter(h => h.status === 'finalized' && h.scoring)
      .sort((a, b) => (b.scoring?.finalScore ?? 0) - (a.scoring?.finalScore ?? 0));
    
    const investigating = hotspots.filter(h => h.status === 'investigating');
    const discarded = hotspots.filter(h => h.status === 'discarded');
    
    return { finalized, investigating, discarded };
  }, [hotspots]);
  
  const totalFinalized = rankedHotspots.finalized.length;
  const totalInvestigating = rankedHotspots.investigating.length;
  const totalDiscarded = rankedHotspots.discarded.length;

  return (
    <div className="flex flex-col h-full min-h-0">
      {/* Header */}
      <div className="px-4 py-3 border-b border-border bg-muted/30 shrink-0">
        <h2 className="text-sm font-medium mb-1">Priority Ranking</h2>
        <div className="flex items-center gap-3 text-xs text-muted-foreground">
          <span>{totalFinalized} confirmed</span>
          <span className="w-1 h-1 rounded-full bg-muted-foreground/50" />
          <span>{totalInvestigating} investigating</span>
          <span className="w-1 h-1 rounded-full bg-muted-foreground/50" />
          <span>{totalDiscarded} discarded</span>
        </div>
      </div>

      {/* List */}
      <ScrollArea className="flex-1 min-h-0">
        <div className="p-3 space-y-2">
          {/* Finalized hotspots */}
          {rankedHotspots.finalized.map((hotspot, index) => (
            <HotspotCard
              key={hotspot.id}
              hotspot={hotspot}
              rank={index + 1}
              isActive={activeHotspot?.id === hotspot.id}
              onClick={() => setActiveHotspot(hotspot)}
            />
          ))}
          
          {/* Investigating hotspots */}
          {rankedHotspots.investigating.length > 0 && (
            <>
              <div className="pt-3 pb-1">
                <span className="text-[10px] uppercase tracking-wider text-muted-foreground font-medium">
                  Investigating
                </span>
              </div>
              {rankedHotspots.investigating.map((hotspot) => (
                <HotspotCard
                  key={hotspot.id}
                  hotspot={hotspot}
                  rank={0}
                  isActive={activeHotspot?.id === hotspot.id}
                  onClick={() => setActiveHotspot(hotspot)}
                />
              ))}
            </>
          )}
          
          {/* Discarded hotspots */}
          {rankedHotspots.discarded.length > 0 && (
            <>
              <div className="pt-3 pb-1">
                <span className="text-[10px] uppercase tracking-wider text-muted-foreground font-medium">
                  Discarded
                </span>
              </div>
              {rankedHotspots.discarded.map((hotspot) => (
                <HotspotCard
                  key={hotspot.id}
                  hotspot={hotspot}
                  rank={0}
                  isActive={activeHotspot?.id === hotspot.id}
                  onClick={() => setActiveHotspot(hotspot)}
                />
              ))}
            </>
          )}
        </div>
      </ScrollArea>
    </div>
  );
}
