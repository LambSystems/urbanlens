// ThermalGen V2 - Core Types

export type HotspotType = 
  | 'roof' 
  | 'road_pavement' 
  | 'parking_lot' 
  | 'hvac_mechanical' 
  | 'vegetation_loss' 
  | 'other';

export type TraceAction =
  | 'candidate_detected'
  | 'inspect_object'
  | 'request_thermal_evidence'
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

export interface TraceStep {
  id: string;
  action: TraceAction;
  timestamp: number;
  message: string;
  details?: Record<string, unknown>;
  evidenceUrl?: string;
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
