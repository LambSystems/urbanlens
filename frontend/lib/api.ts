/**
 * Backend API client for ThermalGen / UrbanLens.
 *
 * Typed against backend/app/schemas.py - all field names match the Python schema.
 * Use `mapHotspot()` to convert a BackendHotspot into the frontend Hotspot type.
 */
import type { ChainOfThoughtStep, Hotspot, HotspotType, Recommendation, TraceAction, TraceStep } from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

// Capture payload types (used by thermal-map and thermal-context)

export interface CaptureMapStatePayload {
  zoom: number;
  mapTypeId: string | null;
  tilt: number | null;
  heading: number | null;
}

export interface CaptureRegionPayload {
  bounds: { north: number; south: number; east: number; west: number };
  center: BackendLatLng;
  areaKm2: number;
}

// Backend schema types

export interface BackendLatLng {
  lat: number;
  lng: number;
}

export interface BackendTraceEvidence {
  object_confidence?: number;
  object_label?: string;
  material_type?: string;
  material_confidence?: number;
  source_count?: number;
  coverage_score?: number;
  neighbor_count?: number;
  relative_percentile?: number;
  consistency_score?: number;
  anomaly_score?: number;
  severity_score?: number;
  confidence_score?: number;
}

export interface BackendTraceStep {
  step_id: string;
  hotspot_id: string;
  kind: string;
  status: 'pending' | 'running' | 'completed';
  timestamp_ms?: number;
  started_at?: string | null;
  completed_at?: string | null;
  summary: string;
  details: Record<string, unknown>;
  evidence: BackendTraceEvidence;
}

export interface BackendHotspot {
  hotspot_id: string;
  region_id: string;
  bbox: { x: number; y: number; w: number; h: number };
  centroid: BackendLatLng;
  hotspot_type: string;
  display_name?: string | null;
  status_label?: string | null;
  sidebar_summary?: string | null;
  evidence_highlights?: string[];
  tool_signals?: string[];
  status: string;
  surface_temperature_c?: number | null;
  ambient_delta_c?: number | null;
  source_count: number;
  coverage_score?: number | null;
  anomaly_score?: number | null;
  severity_score?: number | null;
  confidence_score?: number | null;
  final_rank_score?: number | null;
  discard_reason?: string | null;
  recommended_action?: string | null;
  evidence_urls: string[];
  priority_rank?: number | null;
  is_top_ranked: boolean;
  created_at?: string | null;
  updated_at?: string | null;
  why: string[];
  trace: BackendTraceStep[];
}

export interface BackendRankedHotspot {
  hotspot_id: string;
  priority_rank: number;
  hotspot_type: string;
  recommended_action: string;
  anomaly_score: number;
  severity_score: number;
  confidence_score: number;
  final_rank_score: number;
  why: string[];
}

export interface BackendAnalysisSummary {
  candidate_count: number;
  discarded_count: number;
  finalized_count: number;
}

export interface BackendAnalysisRegion {
  region_id: string;
  display_name?: string | null;
  center: BackendLatLng;
  radius_m: number;
  status: string;
  available_source_count: number;
  coverage_score?: number | null;
  thermal_image_path?: string | null;
  thermal_image_url?: string | null;
  thermal_image_width?: number | null;
  thermal_image_height?: number | null;
  thermal_preview_path?: string | null;
  thermal_preview_url?: string | null;
  thermal_preview_width?: number | null;
  thermal_preview_height?: number | null;
  thermal_source?: string | null;
  source_image_path?: string | null;
  source_image_url?: string | null;
  source_image_width?: number | null;
  source_image_height?: number | null;
  source_image_file_size_bytes?: number | null;
  aligned_rgb_path?: string | null;
  aligned_rgb_width?: number | null;
  aligned_rgb_height?: number | null;
  summary: BackendAnalysisSummary;
}

export interface BackendAnalysisResult {
  region_id: string;
  status: string;
  hotspots: BackendHotspot[];
  top_hotspots: BackendRankedHotspot[];
  top_hotspot_id?: string | null;
  discarded_hotspot_ids: string[];
}

export interface BackendAnalysisResponse {
  region: BackendAnalysisRegion;
  result: BackendAnalysisResult;
}

export interface BackendPlannerResponse {
  region_id: string;
  question: string;
  answer: string;
  answer_title?: string | null;
  answer_sections?: string[];
  referenced_hotspot_ids: string[];
  planner_mode: string;
}

export interface BackendVoiceBriefingResponse {
  region_id: string;
  audio_url?: string | null;
  summary_text: string;
  provider: string;
}

export interface BackendEvent {
  region_id: string;
  hotspot_id: string;
  step_id: string;
  kind: string;
  status: 'pending' | 'running' | 'completed';
  timestamp_ms: number;
  summary: string;
  details: Record<string, unknown>;
  scheduled_offset_ms: number;
}

export interface ThermalInferenceResponse {
  source: string;
  source_image_path?: string | null;
  source_image_width?: number | null;
  source_image_height?: number | null;
  source_image_file_size_bytes?: number | null;
  aligned_rgb_path?: string | null;
  aligned_rgb_width?: number | null;
  aligned_rgb_height?: number | null;
  thermal_image_path?: string | null;
  thermal_image_url?: string | null;
  thermal_image_width?: number | null;
  thermal_image_height?: number | null;
  thermal_preview_path?: string | null;
  thermal_preview_url?: string | null;
  thermal_preview_width?: number | null;
  thermal_preview_height?: number | null;
  checkpoint_path?: string | null;
  metadata: Record<string, unknown>;
  model_input: Record<string, unknown>;
  thermal_data: {
    min_temp_c?: number;
    max_temp_c?: number;
    mean_temp_c?: number;
    hotspot_regions?: Array<{
      centroid?: { lat: number; lng: number };
      centroid_px?: { x: number; y: number };
      bbox_px?: { x: number; y: number; w: number; h: number };
      intensity: number;
      area_px: number;
    }>;
    fallback_reason?: string;
  };
}

// Session / investigate API (mirrors session_routes.py + schemas.py)

export interface SessionResponse {
  session_id: string;
  center: BackendLatLng;
  radius_m: number;
  status: string;
}

export interface InvestigationResponse {
  session_id: string;
  prompt: string;
  chain_of_thought: ChainOfThoughtStep[];
  answer: string;
}

// API functions

export async function createAnalysis(
  center: BackendLatLng,
  radius_m: number,
): Promise<BackendAnalysisResponse> {
  const res = await fetch(`${API_BASE}/analysis`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ center, radius_m }),
  });
  if (!res.ok) throw new Error(`POST /analysis failed: ${res.status}`);
  return res.json();
}

export async function getAnalysis(regionId: string): Promise<BackendAnalysisResponse> {
  const res = await fetch(`${API_BASE}/analysis/${regionId}`);
  if (!res.ok) throw new Error(`GET /analysis/${regionId} failed: ${res.status}`);
  return res.json();
}

/** POST /analysis/from-capture-upload - multipart: metadata JSON string + image file */
export async function createAnalysisFromCaptureUpload(
  region: CaptureRegionPayload,
  mapState: CaptureMapStatePayload,
  viewport: { north: number; south: number; east: number; west: number } | null,
  imageBounds: { north: number; south: number; east: number; west: number } | null,
  imageBase64: string,
): Promise<BackendAnalysisResponse> {
  const metadataObj = {
    region: { bounds: region.bounds, center: region.center, areaKm2: region.areaKm2 },
    map: { zoom: mapState.zoom, mapTypeId: mapState.mapTypeId, tilt: mapState.tilt, heading: mapState.heading },
    viewport: viewport ?? { north: 0, south: 0, east: 0, west: 0 },
    imageBounds,
  };

  // base64 -> Blob
  const byteChars = atob(imageBase64);
  const byteArr = new Uint8Array(byteChars.length);
  for (let i = 0; i < byteChars.length; i++) byteArr[i] = byteChars.charCodeAt(i);
  const blob = new Blob([byteArr], { type: 'image/png' });

  const formData = new FormData();
  formData.append('metadata', JSON.stringify(metadataObj));
  formData.append('image', blob, 'capture.png');

  const res = await fetch(`${API_BASE}/analysis/from-capture-upload`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) throw new Error(`POST /analysis/from-capture-upload failed: ${res.status}`);
  return res.json();
}

/** POST /analysis/{region_id}/voice-briefing */
export async function requestVoiceBriefing(
  regionId: string,
  question?: string,
): Promise<BackendVoiceBriefingResponse> {
  const res = await fetch(`${API_BASE}/analysis/${regionId}/voice-briefing`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question: question ?? null }),
  });
  if (!res.ok) throw new Error(`POST /analysis/${regionId}/voice-briefing failed: ${res.status}`);
  return res.json();
}

export async function getAnalysisEvents(regionId: string): Promise<BackendEvent[]> {
  const res = await fetch(`${API_BASE}/analysis/${regionId}/events`);
  if (!res.ok) throw new Error(`GET /analysis/${regionId}/events failed: ${res.status}`);
  return res.json();
}

export async function getHotspotDetail(regionId: string, hotspotId: string): Promise<BackendHotspot> {
  const res = await fetch(`${API_BASE}/analysis/${regionId}/hotspots/${hotspotId}`);
  if (!res.ok) throw new Error(`GET /analysis/${regionId}/hotspots/${hotspotId} failed: ${res.status}`);
  return res.json();
}

export async function askQuestion(
  regionId: string,
  question: string,
): Promise<BackendPlannerResponse> {
  const res = await fetch(`${API_BASE}/analysis/${regionId}/questions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
  });
  if (!res.ok) throw new Error(`POST /analysis/${regionId}/questions failed: ${res.status}`);
  return res.json();
}

/** POST /thermal/infer/upload — send raw image blob, get thermal overlay back */
export async function inferThermalFromMapBlob(
  blob: Blob,
  params: { lat?: number; lng?: number; radius_m?: number; filename?: string } = {},
): Promise<ThermalInferenceResponse> {
  const query = new URLSearchParams();
  if (params.lat !== undefined) query.set('lat', String(params.lat));
  if (params.lng !== undefined) query.set('lng', String(params.lng));
  if (params.radius_m !== undefined) query.set('radius_m', String(params.radius_m));
  if (params.filename) query.set('filename', params.filename);
  query.set('allow_fallback', 'true');

  const qs = query.toString();
  const res = await fetch(`${API_BASE}/thermal/infer/upload${qs ? `?${qs}` : ''}`, {
    method: 'POST',
    headers: { 'Content-Type': blob.type || 'image/png' },
    body: blob,
  });
  if (!res.ok) throw new Error(`POST /thermal/infer/upload failed: ${res.status}`);
  return res.json();
}

/** POST /session — create a new investigation session for a lat/lng region */
export async function createSession(
  center: BackendLatLng,
  radius_m: number,
): Promise<SessionResponse> {
  const res = await fetch(`${API_BASE}/session`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ center, radius_m }),
  });
  if (!res.ok) throw new Error(`POST /session failed: ${res.status}`);
  return res.json();
}

/** POST /session/{id}/prompt — send a prompt and get back answer + visible investigation trace */
export async function sendSessionPrompt(
  sessionId: string,
  prompt: string,
): Promise<InvestigationResponse> {
  const res = await fetch(`${API_BASE}/session/${sessionId}/prompt`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt }),
  });
  if (!res.ok) throw new Error(`POST /session/${sessionId}/prompt failed: ${res.status}`);
  return res.json();
}

/**
 * POST /session/{id}/prompt/stream — SSE streaming.
 * Calls onStep for each investigation trace step as it arrives,
 * then returns the final answer when done.
 */
export async function sendSessionPromptStream(
  sessionId: string,
  prompt: string,
  onStep: (step: ChainOfThoughtStep) => void,
): Promise<{ answer: string; chain_of_thought: ChainOfThoughtStep[] }> {
  const res = await fetch(`${API_BASE}/session/${sessionId}/prompt/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt }),
  });
  if (!res.ok) throw new Error(`POST /session/${sessionId}/prompt/stream failed: ${res.status}`);

  const allSteps: ChainOfThoughtStep[] = [];
  let finalAnswer = '';

  const reader = res.body!.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() || '';

    let eventType = '';
    for (const line of lines) {
      if (line.startsWith('event:')) {
        eventType = line.slice(6).trim();
      } else if (line.startsWith('data:') && eventType) {
        const data = line.slice(5).trim();
        if (eventType === 'step' && data) {
          try {
            const step: ChainOfThoughtStep = JSON.parse(data);
            allSteps.push(step);
            onStep(step);
          } catch { /* skip malformed */ }
        } else if (eventType === 'done' && data) {
          try {
            const result = JSON.parse(data);
            finalAnswer = result.answer || '';
          } catch { /* skip */ }
        }
        eventType = '';
      }
    }
  }

  // If no explicit done event, extract answer from last answer step
  if (!finalAnswer) {
    const answerStep = [...allSteps].reverse().find(s => s.step_type === 'answer');
    finalAnswer = answerStep?.summary || 'Agent completed investigation.';
  }

  return { answer: finalAnswer, chain_of_thought: allSteps };
}

export async function createVoiceBriefing(
  regionId: string,
  question?: string,
): Promise<BackendVoiceBriefingResponse> {
  const res = await fetch(`${API_BASE}/analysis/${regionId}/voice-briefing`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
  });
  if (!res.ok) throw new Error(`POST /analysis/${regionId}/voice-briefing failed: ${res.status}`);
  return res.json();
}

// Mappers

function mapBackendStatus(s: string): Hotspot['status'] {
  if (s === 'discarded') return 'discarded';
  if (s === 'finalized') return 'finalized';
  if (s === 'candidate') return 'candidate';
  return 'investigating';
}

function flattenEvidence(ev: BackendTraceEvidence): Record<string, unknown> {
  const out: Record<string, unknown> = {};
  for (const [k, v] of Object.entries(ev)) {
    if (v !== null && v !== undefined) out[k] = v;
  }
  return out;
}

function normalizeEvidenceUrl(url: string): string {
  // Any root-relative path is backend-served — prefix with the backend origin.
  if (url.startsWith('/')) return `${API_BASE}${url}`;
  return url;
}

export function mapHotspot(b: BackendHotspot): Hotspot {
  const evidenceUrls = b.evidence_urls.map(normalizeEvidenceUrl);
  const thermalPreviewUrl = evidenceUrls.find((url) => url.includes('/thermal-assets/'));

  const trace: TraceStep[] = b.trace.map((step) => ({
    id: step.step_id,
    action: step.kind as TraceAction,
    timestamp: step.timestamp_ms ?? 0,
    message: step.summary,
    details: { ...step.details, ...flattenEvidence(step.evidence) },
    evidenceUrl: step.kind === 'request_thermal_evidence' ? thermalPreviewUrl : undefined,
    status: step.status,
  }));

  const hasScoring =
    b.anomaly_score !== null &&
    b.anomaly_score !== undefined &&
    b.severity_score !== null &&
    b.severity_score !== undefined &&
    b.confidence_score !== null &&
    b.confidence_score !== undefined;

  return {
    id: b.hotspot_id,
    location: { lat: b.centroid.lat, lng: b.centroid.lng },
    type: b.hotspot_type as HotspotType,
    status: mapBackendStatus(b.status),
    surfaceTemperature: b.surface_temperature_c ?? 0,
    ambientDelta: b.ambient_delta_c ?? 0,
    trace,
    scoring: hasScoring
      ? {
        anomalyScore: b.anomaly_score!,
        severityScore: b.severity_score!,
        confidenceScore: b.confidence_score!,
        finalScore: b.final_rank_score ?? b.severity_score! * b.confidence_score!,
        reasoning: b.why.join('. '),
      }
      : undefined,
    evidenceUrls,
    createdAt: b.created_at ? new Date(b.created_at).getTime() : Date.now(),
    updatedAt: b.updated_at ? new Date(b.updated_at).getTime() : Date.now(),
    displayName: b.display_name ?? undefined,
    statusLabel: b.status_label ?? undefined,
    sidebarSummary: b.sidebar_summary ?? undefined,
    evidenceHighlights: b.evidence_highlights,
    toolSignals: b.tool_signals,
    discardReason: b.discard_reason ?? undefined,
    recommendedAction: b.recommended_action ?? undefined,
    priorityRank: b.priority_rank ?? undefined,
    isTopRanked: b.is_top_ranked,
  };
}

// Derive a Recommendation from a finalized backend hotspot.
// The backend doesn't have full recommendation objects yet, so we synthesize
// from recommended_action + why bullets.
const COST_ESTIMATES: Record<string, string> = {
  roof: '$3,500 - $12,000',
  parking_lot: '$18,000 - $52,000',
  road_pavement: '$9,000 - $22,000',
  hvac_mechanical: '$2,000 - $8,000',
  vegetation_loss: '$5,000 - $20,000',
  other: '$5,000 - $25,000',
};

const TEMP_REDUCTIONS: Record<string, string> = {
  roof: '18 - 28 C',
  parking_lot: '24 - 32 C',
  road_pavement: '10 - 15 C',
  hvac_mechanical: '5 - 12 C',
  vegetation_loss: '8 - 18 C',
  other: '5 - 15 C',
};

export function mapRecommendation(b: BackendHotspot): Recommendation | null {
  if (!b.recommended_action || b.status === 'discarded') return null;

  const action = b.recommended_action;
  const type = b.hotspot_type;

  return {
    hotspotId: b.hotspot_id,
    summary: `${b.display_name ?? type} - ${action} recommended based on agent investigation.`,
    actions: [
      {
        id: 'action-1',
        title: action.charAt(0).toUpperCase() + action.slice(1),
        description: b.why.join('. ') || 'Agent identified this as the highest-priority intervention.',
        priority: (b.final_rank_score ?? 0) >= 0.6 ? 'high' : 'medium',
        estimatedImpact: `Addresses thermal anomaly - reduce surface temp by ${TEMP_REDUCTIONS[type] ?? '5 - 20 C'}`,
      },
    ],
    estimatedCostRange: COST_ESTIMATES[type] ?? '$5,000 - $25,000',
    estimatedTemperatureReduction: TEMP_REDUCTIONS[type] ?? '5 - 20 C',
  };
}
