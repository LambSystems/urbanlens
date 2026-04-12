'use client';

import { useState, useRef, useCallback, useEffect } from 'react';
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
  Volume2,
  Loader2,
  MessageSquare,
  Send,
  Bot,
} from 'lucide-react';
import { useThermal } from '@/lib/thermal-context';
import { RankingPanel } from './ranking-panel';
import { TraceTimeline } from './trace-timeline';
import { RecommendationCard } from './recommendation-card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { Textarea } from '@/components/ui/textarea';
import { ScrollArea } from '@/components/ui/scroll-area';
import { cn } from '@/lib/utils';

const SIDEBAR_MIN_WIDTH = 280;
const SIDEBAR_MAX_WIDTH = 640;
const SIDEBAR_DEFAULT_WIDTH = 380;

function ThermalOverlayCard() {
  const { thermalInference, isThermalInferenceLoading } = useThermal();
  const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

  if (isThermalInferenceLoading) {
    return (
      <div className="rounded-xl border border-orange-500/20 bg-orange-500/5 p-3 flex items-center gap-3">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-orange-500/10 shrink-0">
          <Loader2 className="h-4 w-4 text-orange-400 animate-spin" />
        </div>
        <div>
          <p className="text-xs font-medium text-orange-400">Running thermal model…</p>
          <p className="text-[10px] text-muted-foreground">HybridThermal checkpoint processing capture</p>
        </div>
      </div>
    );
  }

  if (!thermalInference) return null;

  const previewUrl = thermalInference.thermal_preview_url
    ? thermalInference.thermal_preview_url.startsWith('/')
      ? `${API_BASE}${thermalInference.thermal_preview_url}`
      : thermalInference.thermal_preview_url
    : null;

  const td = thermalInference.thermal_data;
  const isReal = thermalInference.source === 'hybrid_thermal';
  const regionCount = td.hotspot_regions?.length ?? 0;

  return (
    <div className="rounded-xl border border-orange-500/25 bg-gradient-to-b from-orange-500/8 to-transparent overflow-hidden">
      {/* Header */}
      <div className="flex items-center gap-2 px-3 pt-3 pb-2">
        <div className="flex h-6 w-6 items-center justify-center rounded-md bg-orange-500/15 shrink-0">
          <Thermometer className="h-3.5 w-3.5 text-orange-400" />
        </div>
        <span className="text-xs font-semibold text-orange-400">Thermal Overlay</span>
        <span className={cn(
          "ml-auto text-[9px] px-1.5 py-0.5 rounded-full font-medium",
          isReal
            ? "bg-green-500/15 text-green-400"
            : "bg-muted text-muted-foreground"
        )}>
          {isReal ? 'Model' : 'Synthetic'}
        </span>
      </div>

      {/* Preview image */}
      {previewUrl && (
        <div className="relative mx-3 mb-2 rounded-lg overflow-hidden bg-black/20">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={previewUrl}
            alt="Thermal heatmap"
            className="w-full object-cover"
            style={{ maxHeight: '120px' }}
          />
          {/* Temperature legend overlay */}
          <div className="absolute bottom-1.5 right-1.5 flex items-center gap-1 rounded px-1.5 py-0.5 bg-black/60 text-[9px] text-white/80">
            <span className="inline-block h-1.5 w-8 rounded-sm bg-gradient-to-r from-[#130704] via-[#d85a00] to-[#fff1a8]" />
            cool → hot
          </div>
        </div>
      )}

      {/* Stats row */}
      {td.min_temp_c !== undefined && (
        <div className="grid grid-cols-3 gap-1.5 px-3 pb-3">
          <div className="rounded-lg bg-muted/40 p-2 text-center">
            <p className="text-[9px] text-muted-foreground uppercase tracking-wider mb-0.5">Min</p>
            <p className="text-xs font-mono font-semibold">{td.min_temp_c.toFixed(1)}°</p>
          </div>
          <div className="rounded-lg bg-orange-500/12 border border-orange-500/20 p-2 text-center">
            <p className="text-[9px] text-orange-400 uppercase tracking-wider mb-0.5">Mean</p>
            <p className="text-xs font-mono font-semibold text-orange-300">{td.mean_temp_c?.toFixed(1)}°</p>
          </div>
          <div className="rounded-lg bg-red-500/10 border border-red-500/15 p-2 text-center">
            <p className="text-[9px] text-red-400 uppercase tracking-wider mb-0.5">Peak</p>
            <p className="text-xs font-mono font-semibold text-red-300">{td.max_temp_c?.toFixed(1)}°</p>
          </div>
        </div>
      )}

      {regionCount > 0 && (
        <div className="border-t border-orange-500/10 px-3 py-2">
          <p className="text-[10px] text-muted-foreground">
            <span className="font-medium text-orange-400">{regionCount}</span> heat region{regionCount !== 1 ? 's' : ''} detected
          </p>
        </div>
      )}
    </div>
  );
}

function RegionSelector() {
  const {
    selectionMode,
    startDrawing,
    cancelSelection,
    selectedRegion,
    analysisProgress,
    startAnalysis,
    hotspots,
    voiceBriefing,
    isVoiceBriefingLoading,
    playVoiceBriefing,
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
      <div className="p-4 space-y-3">
        <div className="rounded-xl border border-green-500/30 bg-green-500/5 p-4">
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

        {/* Thermal model overlay */}
        <ThermalOverlayCard />

        {/* Voice Briefing */}
        <div className="rounded-xl border border-border bg-card p-3">
          <div className="flex items-center gap-2 mb-2">
            <Volume2 className="h-4 w-4 text-muted-foreground" />
            <span className="text-xs font-medium">Voice Briefing</span>
          </div>
          <Button
            variant="outline"
            size="sm"
            className="w-full gap-2 text-xs"
            onClick={playVoiceBriefing}
            disabled={isVoiceBriefingLoading}
          >
            {isVoiceBriefingLoading ? (
              <Loader2 className="h-3.5 w-3.5 animate-spin" />
            ) : (
              <Volume2 className="h-3.5 w-3.5" />
            )}
            {isVoiceBriefingLoading ? 'Generating briefing…' : 'Play Briefing'}
          </Button>
          {voiceBriefing?.text && (
            <p className="mt-2 text-xs text-muted-foreground leading-relaxed">
              {voiceBriefing.text}
            </p>
          )}
        </div>
      </div>
    );
  }

  return null;
}

const REASONING_STEPS = [
  { label: 'Reading hotspot findings…', icon: '🔍' },
  { label: 'Applying Thermal Evidence…', icon: '🌡️' },
  { label: 'Consulting Heat Risk Profile…', icon: '📊' },
  { label: 'Cross-referencing ranked candidates…', icon: '⚖️' },
  { label: 'Formulating response…', icon: '💡' },
];

function AgentReasoningTrace() {
  const [stepIndex, setStepIndex] = useState(0);

  // Cycle through reasoning steps while loading
  useEffect(() => {
    const id = setInterval(() => {
      setStepIndex(prev => (prev + 1) % REASONING_STEPS.length);
    }, 900);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="rounded-xl border border-primary/20 bg-primary/5 p-4 space-y-3">
      <div className="flex items-center gap-2 mb-1">
        <Bot className="h-4 w-4 text-primary shrink-0 animate-pulse" />
        <span className="text-xs font-semibold text-primary">Agent Reasoning</span>
      </div>
      <div className="space-y-2">
        {REASONING_STEPS.map((step, i) => {
          const isDone = i < stepIndex;
          const isActive = i === stepIndex;
          return (
            <motion.div
              key={step.label}
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: isDone || isActive ? 1 : 0.25, x: 0 }}
              transition={{ duration: 0.3, delay: i * 0.05 }}
              className="flex items-center gap-2"
            >
              <div className={cn(
                "h-5 w-5 rounded-full flex items-center justify-center text-[10px] shrink-0 transition-colors",
                isDone ? "bg-primary/20 text-primary" : isActive ? "bg-primary/10 text-primary" : "bg-muted text-muted-foreground"
              )}>
                {isDone ? '✓' : step.icon}
              </div>
              <span className={cn(
                "text-xs transition-colors",
                isActive ? "text-foreground font-medium" : isDone ? "text-muted-foreground line-through" : "text-muted-foreground/40"
              )}>
                {step.label}
              </span>
              {isActive && (
                <span className="ml-auto flex gap-0.5">
                  {[0, 1, 2].map(d => (
                    <span
                      key={d}
                      className="h-1 w-1 rounded-full bg-primary animate-bounce"
                      style={{ animationDelay: `${d * 150}ms` }}
                    />
                  ))}
                </span>
              )}
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}

function mdToHtml(text: string): string {
  return text
    // Bold **text**
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    // Italic *text*
    .replace(/(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)/g, '<em>$1</em>')
    // Headers ## and # → bold line
    .replace(/^#{1,3}\s+(.+)$/gm, '<strong class="block mb-0.5">$1</strong>')
    // Trim surrounding whitespace
    .trim();
}

function MdSpan({ text }: { text: string }) {
  return (
    <span
      dangerouslySetInnerHTML={{ __html: mdToHtml(text) }}
      className="[&_strong]:font-semibold [&_em]:italic"
    />
  );
}

function ChainOfThoughtExpander({ steps }: { steps: NonNullable<import('@/lib/types').ChatMessage['chainOfThought']> }) {
  const [open, setOpen] = useState(false);
  const toolCalls = steps.filter(s => s.step_type === 'tool_call');
  const label = toolCalls.length
    ? `${steps.length} steps · tools: ${toolCalls.map(s => s.tool_name).filter(Boolean).join(', ')}`
    : `${steps.length} steps`;

  return (
    <div className="mt-2">
      <button
        onClick={() => setOpen(o => !o)}
        className="flex items-center gap-1.5 text-[10px] text-muted-foreground hover:text-foreground transition-colors"
      >
        <span className={cn('transition-transform', open && 'rotate-90')}>▶</span>
        Chain of thought · {label}
      </button>
      {open && (
        <div className="mt-2 space-y-1.5 border-l-2 border-border pl-3">
          {steps.map((step) => (
            <div key={step.step_id} className="space-y-1">
              {step.step_type === 'tool_call' && (
                <div className="flex items-start gap-1.5">
                  <span className="text-[10px] font-mono bg-muted px-1.5 py-0.5 rounded text-muted-foreground shrink-0">
                    🔧 {step.tool_name ?? 'tool'}
                  </span>
                  <span className="text-[10px] text-muted-foreground leading-relaxed">{step.summary}</span>
                </div>
              )}
              {step.step_type === 'reasoning' && (
                <p className="text-[10px] text-muted-foreground/70 leading-relaxed italic">
                  💭 {step.summary.slice(0, 200)}{step.summary.length > 200 ? '…' : ''}
                </p>
              )}
              {step.step_type === 'answer' && (
                <p className="text-[10px] text-green-500/80">✓ Final answer generated</p>
              )}
              {step.evidence && Object.keys(step.evidence).length > 0 && (
                <pre className="text-[9px] bg-muted/50 rounded p-1.5 overflow-x-auto text-muted-foreground">
                  {JSON.stringify(step.evidence, null, 2).slice(0, 400)}
                </pre>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function PlannerPanel() {
  const { chatMessages, isAgentLoading, askAgent, selectedRegion } = useThermal();
  const [question, setQuestion] = useState('');
  const bottomRef = useRef<HTMLDivElement>(null);

  const SUGGESTED = [
    'What should we inspect first here?',
    'Where would it be smart to plant trees to counter heat?',
    'Why did the top hotspot rank first?',
    'Where would cooling interventions matter most?',
  ];

  // Scroll to bottom when messages arrive
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages, isAgentLoading]);

  const submit = useCallback(async () => {
    const q = question.trim();
    if (!q || !selectedRegion || isAgentLoading) return;
    setQuestion('');
    await askAgent(q);
  }, [question, selectedRegion, isAgentLoading, askAgent]);

  const handleSubmit = (e: React.SyntheticEvent) => {
    e.preventDefault();
    submit();
  };

  return (
    <div className="flex flex-col h-full min-h-0">
      <ScrollArea className="flex-1 min-h-0">
        <div className="p-4 space-y-4">

          {/* Suggested questions — only when no history yet */}
          {chatMessages.length === 0 && !isAgentLoading && (
            <div className="space-y-3">
              <p className="text-xs text-muted-foreground leading-relaxed">
                Ask anything about this region. The agent investigates using tools and remembers the conversation.
              </p>
              <div className="space-y-2">
                <p className="text-[10px] uppercase tracking-wider text-muted-foreground font-medium">Try asking</p>
                {SUGGESTED.map((s) => (
                  <button
                    key={s}
                    onClick={() => setQuestion(s)}
                    className="w-full text-left text-xs text-muted-foreground px-3 py-2 rounded-lg border border-border/60 bg-muted/30 hover:bg-muted/60 hover:text-foreground transition-colors"
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Conversation history */}
          {chatMessages.map((msg, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              className={cn('flex gap-2', msg.role === 'user' ? 'justify-end' : 'justify-start')}
            >
              {msg.role === 'assistant' && (
                <div className="shrink-0 h-6 w-6 rounded-full bg-primary/10 flex items-center justify-center mt-0.5">
                  <Bot className="h-3.5 w-3.5 text-primary" />
                </div>
              )}

              <div className={cn(
                'max-w-[85%] space-y-1',
                msg.role === 'user' ? 'items-end' : 'items-start',
              )}>
                <div className={cn(
                  'rounded-xl px-3 py-2 text-xs leading-relaxed',
                  msg.role === 'user'
                    ? 'bg-primary text-primary-foreground rounded-br-sm'
                    : 'bg-muted/60 text-foreground rounded-bl-sm',
                )}>
                  <MdSpan text={msg.content} />
                </div>

                {/* Real chain of thought for assistant messages */}
                {msg.role === 'assistant' && msg.chainOfThought && msg.chainOfThought.length > 0 && (
                  <ChainOfThoughtExpander steps={msg.chainOfThought} />
                )}
              </div>

              {msg.role === 'user' && (
                <div className="shrink-0 h-6 w-6 rounded-full bg-muted flex items-center justify-center mt-0.5">
                  <MessageSquare className="h-3 w-3 text-muted-foreground" />
                </div>
              )}
            </motion.div>
          ))}

          {/* Agent reasoning trace while waiting */}
          {isAgentLoading && <AgentReasoningTrace />}

          <div ref={bottomRef} />
        </div>
      </ScrollArea>

      {/* Input */}
      <div className="shrink-0 border-t border-sidebar-border p-3 bg-sidebar">
        <form onSubmit={handleSubmit} className="flex flex-col gap-2">
          <Textarea
            placeholder="Ask anything about this locality…"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                submit();
              }
            }}
            rows={2}
            className="resize-none text-xs min-h-14"
            disabled={isAgentLoading || !selectedRegion}
          />
          <Button
            type="submit"
            size="sm"
            className="w-full gap-2 text-xs"
            disabled={!question.trim() || isAgentLoading || !selectedRegion}
          >
            {isAgentLoading ? (
              <Loader2 className="h-3.5 w-3.5 animate-spin" />
            ) : (
              <Send className="h-3.5 w-3.5" />
            )}
            {isAgentLoading ? 'Agent reasoning…' : 'Ask Agent'}
          </Button>
        </form>
      </div>
    </div>
  );
}

export function ThermalSidebar() {
  const { sidebarOpen, setSidebarOpen, activeHotspot, selectionMode, regionDisplayName, chatMessages } = useThermal();
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
              <p className="text-[10px] text-muted-foreground truncate max-w-45">
                {regionDisplayName ?? 'Urban Heat Triage'}
              </p>
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
                <TabsTrigger
                  value="planner"
                  className="gap-1.5 data-[state=active]:bg-sidebar-accent"
                >
                  <MessageSquare className="h-3.5 w-3.5" />
                  <span className="text-xs">Planner</span>
                  {chatMessages.length > 0 && (
                    <span className="ml-1 h-1.5 w-1.5 rounded-full bg-green-500" />
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

              {/* Planner tab — Q&A over existing analysis */}
              <TabsContent
                value="planner"
                className="flex-1 min-h-0 m-0 flex flex-col data-[state=inactive]:hidden"
              >
                <PlannerPanel />
              </TabsContent>
            </Tabs>
          </div>
        )}
      </motion.aside>
    </>
  );
}
