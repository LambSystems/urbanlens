// ThermalGen V2 - Core Types

export type SelectionMode = 'idle' | 'drawing' | 'selected' | 'analyzing' | 'complete';

export interface SelectedRegion {
  bounds: BoundingBox;
  center: LatLng;
  areaKm2: number;
}

export type HotspotType = 
  | 'roof' 
  | 'road_pavement' 
  | 'parking_lot' 
  | 'hvac_mechanical' 
  | 'vegetation_loss' 
  | 'other';

export type TraceAction =
  | 'candidate_detected'
  | 'generate_thermal_overlay'
  | 'inspect_object'
  | 'request_thermal_evidence'
  | 'analyze_heat_risk'
  | 'infer_surface'
  | 'compare_neighbors'
  | 'check_consistency'
  | 'score_hotspot'
  | 'discard_hotspot'
  | 'finalize_hotspot';

export type HotspotStatus = 'candidate' | 'investigating' | 'finalized' | 'discarded';

export interface LatLng {
  lat: number;
  lng: number;
}

export interface BoundingBox {
  north: number;
  south: number;
  east: number;
  west: number;
}

export type TraceStepStatus = 'pending' | 'running' | 'completed';

export interface TraceStep {
  id: string;
  action: TraceAction;
  timestamp: number;
  message: string;
  details?: Record<string, unknown>;
  evidenceUrl?: string;
  status?: TraceStepStatus;
}

export interface ScoringResult {
  anomalyScore: number;      // 0-1, gates (must exceed threshold)
  severityScore: number;     // 0-1, orders (priority ranking)
  confidenceScore: number;   // 0-1, modulates (trust level)
  finalScore: number;        // Combined weighted score
  reasoning: string;
}

export interface Hotspot {
  id: string;
  location: LatLng;
  type: HotspotType;
  status: HotspotStatus;
  surfaceTemperature: number;  // Celsius
  ambientDelta: number;        // Degrees above ambient
  trace: TraceStep[];
  scoring?: ScoringResult;
  evidenceUrls: string[];
  createdAt: number;
  updatedAt: number;
  // Backend display fields
  displayName?: string;
  statusLabel?: string;
  sidebarSummary?: string;
  evidenceHighlights?: string[];
  toolSignals?: string[];
  discardReason?: string;
  recommendedAction?: string;
  priorityRank?: number;
  isTopRanked?: boolean;
}

export interface RecommendationAction {
  id: string;
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
  estimatedImpact: string;
}

export interface Recommendation {
  hotspotId: string;
  summary: string;
  actions: RecommendationAction[];
  estimatedCostRange: string;
  estimatedTemperatureReduction: string;
}

export interface InvestigationSession {
  id: string;
  regionBounds: BoundingBox;
  hotspots: Hotspot[];
  activeHotspotId: string | null;
  status: 'idle' | 'detecting' | 'investigating' | 'complete';
  startedAt: number;
  completedAt?: number;
}

// UI State types
export interface TracePlaybackState {
  isPlaying: boolean;
  currentStepIndex: number;
  speed: number; // ms per step
}

export interface AnalysisProgress {
  phase: 'satellite' | 'thermal' | 'classification' | 'scoring';
  progress: number; // 0-100
  message: string;
}

export interface ChainOfThoughtStep {
  step_id: string;
  step_type: 'tool_call' | 'reasoning' | 'answer';
  tool_name?: string | null;
  status: string;
  summary: string;
  evidence?: Record<string, unknown> | null;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  chainOfThought?: ChainOfThoughtStep[];
}
