'use client';

import { useEffect, useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Eye, 
  Camera, 
  Layers, 
  GitCompare, 
  CheckCircle2, 
  XCircle, 
  BarChart3, 
  Radar, 
  Play, 
  Pause, 
  RotateCcw,
  ChevronRight
} from 'lucide-react';
import { useThermal } from '@/lib/thermal-context';
import type { TraceAction, TraceStep } from '@/lib/types';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { cn } from '@/lib/utils';

const ACTION_CONFIG: Record<TraceAction, { icon: typeof Eye; label: string; color: string }> = {
  candidate_detected: { icon: Radar, label: 'Candidate Detected', color: 'text-blue-400' },
  inspect_object: { icon: Eye, label: 'Inspecting Object', color: 'text-cyan-400' },
  request_thermal_evidence: { icon: Camera, label: 'Requesting Evidence', color: 'text-purple-400' },
  infer_surface: { icon: Layers, label: 'Analyzing Surface', color: 'text-amber-400' },
  compare_neighbors: { icon: GitCompare, label: 'Comparing Neighbors', color: 'text-teal-400' },
  check_consistency: { icon: CheckCircle2, label: 'Checking Consistency', color: 'text-green-400' },
  score_hotspot: { icon: BarChart3, label: 'Computing Score', color: 'text-orange-400' },
  discard_hotspot: { icon: XCircle, label: 'Discarded', color: 'text-red-400' },
  finalize_hotspot: { icon: CheckCircle2, label: 'Finalized', color: 'text-emerald-400' },
};

function TypewriterText({ text, isVisible }: { text: string; isVisible: boolean }) {
  const [displayText, setDisplayText] = useState('');
  const [isComplete, setIsComplete] = useState(false);
  
  useEffect(() => {
    if (!isVisible) {
      setDisplayText('');
      setIsComplete(false);
      return;
    }
    
    let index = 0;
    setDisplayText('');
    setIsComplete(false);
    
    const interval = setInterval(() => {
      if (index < text.length) {
        setDisplayText(text.slice(0, index + 1));
        index++;
      } else {
        setIsComplete(true);
        clearInterval(interval);
      }
    }, 25);
    
    return () => clearInterval(interval);
  }, [text, isVisible]);
  
  return (
    <span>
      {displayText}
      {!isComplete && isVisible && (
        <span className="inline-block w-0.5 h-4 bg-primary animate-pulse ml-0.5" />
      )}
    </span>
  );
}

function TraceStepItem({ 
  step, 
  index, 
  isVisible, 
  isActive,
  isLast 
}: { 
  step: TraceStep; 
  index: number; 
  isVisible: boolean;
  isActive: boolean;
  isLast: boolean;
}) {
  const config = ACTION_CONFIG[step.action];
  const Icon = config.icon;
  
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: isVisible ? 1 : 0, x: isVisible ? 0 : -20 }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
      className="relative"
    >
      {/* Timeline connector line */}
      {!isLast && (
        <div 
          className={cn(
            "absolute left-4 top-10 w-0.5 h-full -translate-x-1/2",
            isVisible ? "bg-border" : "bg-transparent"
          )} 
        />
      )}
      
      <div className={cn(
        "flex gap-3 pb-4 group",
        isActive && "relative"
      )}>
        {/* Icon bubble */}
        <div className={cn(
          "relative z-10 flex h-8 w-8 shrink-0 items-center justify-center rounded-full border-2 transition-all duration-300",
          isActive 
            ? "bg-primary/20 border-primary shadow-lg shadow-primary/25" 
            : "bg-muted border-border",
          config.color
        )}>
          <Icon className="h-4 w-4" />
          
          {/* Active pulse effect */}
          {isActive && (
            <span className="absolute inset-0 rounded-full animate-ping bg-primary/30" />
          )}
        </div>
        
        {/* Content */}
        <div className="flex-1 min-w-0 pt-0.5">
          <div className="flex items-center gap-2 mb-1">
            <span className={cn(
              "text-xs font-medium uppercase tracking-wide",
              config.color
            )}>
              {config.label}
            </span>
            <span className="text-[10px] text-muted-foreground tabular-nums">
              +{((step.timestamp - (step.timestamp - index * 2000)) / 1000).toFixed(1)}s
            </span>
          </div>
          
          <p className="text-sm text-foreground leading-relaxed">
            {isActive ? (
              <TypewriterText text={step.message} isVisible={isVisible} />
            ) : (
              step.message
            )}
          </p>
          
          {/* Details badge */}
          {step.details && isVisible && (
            <motion.div
              initial={{ opacity: 0, y: 5 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="mt-2 flex flex-wrap gap-1.5"
            >
              {Object.entries(step.details).map(([key, value]) => (
                <span 
                  key={key}
                  className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-muted/50 text-[10px] font-mono text-muted-foreground"
                >
                  <span className="text-muted-foreground/70">{key}:</span>
                  <span className="text-foreground/80">{String(value)}</span>
                </span>
              ))}
            </motion.div>
          )}

          {step.evidenceUrl && isVisible && (
            <motion.div
              initial={{ opacity: 0, y: 5 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.35 }}
              className="mt-3 overflow-hidden rounded-md border border-border bg-muted/30"
            >
              <img
                src={step.evidenceUrl}
                alt="Thermal evidence preview"
                className="h-32 w-full object-cover"
              />
            </motion.div>
          )}
        </div>
      </div>
    </motion.div>
  );
}

export function TraceTimeline() {
  const { 
    activeHotspot, 
    playback, 
    startPlayback, 
    pausePlayback, 
    resetPlayback,
    advanceStep 
  } = useThermal();
  
  const scrollRef = useRef<HTMLDivElement>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  // Auto-advance effect
  useEffect(() => {
    if (playback.isPlaying && activeHotspot) {
      intervalRef.current = setInterval(() => {
        advanceStep();
      }, playback.speed);
    }
    
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [playback.isPlaying, playback.speed, advanceStep, activeHotspot]);

  // Auto-scroll to latest step
  useEffect(() => {
    if (scrollRef.current && playback.currentStepIndex >= 0) {
      const container = scrollRef.current;
      const steps = container.querySelectorAll('[data-trace-step]');
      const currentStep = steps[playback.currentStepIndex];
      
      if (currentStep) {
        currentStep.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }
  }, [playback.currentStepIndex]);

  if (!activeHotspot) {
    return (
      <div className="flex flex-col items-center justify-center h-full p-6 text-center">
        <div className="w-12 h-12 rounded-full bg-muted/50 flex items-center justify-center mb-4">
          <Radar className="w-6 h-6 text-muted-foreground" />
        </div>
        <p className="text-sm text-muted-foreground">
          Select a hotspot on the map to view its investigation trace
        </p>
      </div>
    );
  }

  const { trace } = activeHotspot;
  const allVisible = playback.currentStepIndex >= trace.length - 1;

  return (
    <div className="flex flex-col h-full min-h-0">
      {/* Header with controls */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-border bg-muted/30 shrink-0">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium">Agent Trace</span>
          <span className="text-xs text-muted-foreground">
            {playback.currentStepIndex + 1} / {trace.length} steps
          </span>
        </div>
        
        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="icon"
            className="h-7 w-7"
            onClick={resetPlayback}
            disabled={playback.currentStepIndex < 0}
          >
            <RotateCcw className="h-3.5 w-3.5" />
          </Button>
          
          {playback.isPlaying ? (
            <Button
              variant="ghost"
              size="icon"
              className="h-7 w-7"
              onClick={pausePlayback}
            >
              <Pause className="h-3.5 w-3.5" />
            </Button>
          ) : (
            <Button
              variant="ghost"
              size="icon"
              className="h-7 w-7"
              onClick={startPlayback}
              disabled={allVisible}
            >
              <Play className="h-3.5 w-3.5" />
            </Button>
          )}
          
          <Button
            variant="ghost"
            size="icon"
            className="h-7 w-7"
            onClick={advanceStep}
            disabled={playback.isPlaying || allVisible}
          >
            <ChevronRight className="h-3.5 w-3.5" />
          </Button>
        </div>
      </div>
      
      {/* Timeline content */}
      <ScrollArea className="flex-1 min-h-0">
        <div ref={scrollRef} className="p-4">
          <AnimatePresence mode="sync">
            {trace.map((step, index) => {
              const isVisible = index <= playback.currentStepIndex;
              const isActive = index === playback.currentStepIndex;
              
              return (
                <div key={step.id} data-trace-step>
                  <TraceStepItem
                    step={step}
                    index={index}
                    isVisible={isVisible}
                    isActive={isActive}
                    isLast={index === trace.length - 1}
                  />
                </div>
              );
            })}
          </AnimatePresence>
        </div>
      </ScrollArea>
    </div>
  );
}
