import type { Hotspot, InvestigationSession, Recommendation, TraceStep, BoundingBox } from './types';

// Demo region: Ann Arbor, MI — real DJI drone flight data from 2024-08-04
// Ambient: 29°C, Direct radiation: ~750 W/m², clear sky (weather_code 0)
export const DEMO_REGION = {
  center: { lat: 42.2813, lng: -83.7470 },
  zoom: 17,
  bounds: {
    north: 42.2817,
    south: 42.2810,
    east: -83.7436,
    west: -83.7501,
  },
};

const createTrace = (type: Hotspot['type'], isDiscarded = false): TraceStep[] => {
  const baseTime = Date.now() - 30000;

  const steps: TraceStep[] = [
    {
      id: `trace-1`,
      action: 'candidate_detected',
      timestamp: baseTime,
      message: 'Thermal anomaly detected in drone imagery',
      details: { surfaceTemp: 52, ambientTemp: 29 },
    },
    {
      id: `trace-2`,
      action: 'inspect_object',
      timestamp: baseTime + 2000,
      message: `Identified structure type: ${type.replace('_', ' ')}`,
      details: { confidence: 0.89 },
    },
    {
      id: `trace-3`,
      action: 'request_thermal_evidence',
      timestamp: baseTime + 4000,
      message: 'Querying drone thermal imagery database',
      details: { droneId: 'DJI-T40-07', distance: '45m' },
    },
    {
      id: `trace-4`,
      action: 'infer_surface',
      timestamp: baseTime + 6000,
      message: 'Analyzing surface material properties',
      details: { material: type === 'roof' ? 'dark_asphalt_shingle' : 'concrete', albedo: 0.15 },
    },
    {
      id: `trace-5`,
      action: 'compare_neighbors',
      timestamp: baseTime + 8000,
      message: 'Comparing thermal signature with adjacent structures',
      details: { neighborCount: 4, avgDelta: '+8.2°C' },
    },
    {
      id: `trace-6`,
      action: 'check_consistency',
      timestamp: baseTime + 10000,
      message: 'Validating readings across multiple passes',
      details: { passes: 3, variance: '±1.2°C' },
    },
  ];

  if (isDiscarded) {
    steps.push({
      id: `trace-7`,
      action: 'discard_hotspot',
      timestamp: baseTime + 12000,
      message: 'Hotspot discarded: Expected heat source (HVAC exhaust)',
      details: { reason: 'expected_source', confidence: 0.92 },
    });
  } else {
    steps.push(
      {
        id: `trace-7`,
        action: 'score_hotspot',
        timestamp: baseTime + 12000,
        message: 'Computing anomaly, severity, and confidence scores',
        details: { anomaly: 0.78, severity: 0.85, confidence: 0.91 },
      },
      {
        id: `trace-8`,
        action: 'finalize_hotspot',
        timestamp: baseTime + 14000,
        message: 'Hotspot confirmed and added to priority queue',
        details: { rank: 1, finalScore: 0.84 },
      }
    );
  }

  return steps;
};

// Real drone positions from DJI T40 flight on 2024-08-04, Ann Arbor, MI
// Ambient temp: 29°C, direct radiation: ~750 W/m² (high solar load)
// Surface temps derived: ambient + material-specific delta under 750 W/m²
export const MOCK_HOTSPOTS: Hotspot[] = [
  {
    // DJI_20240804134933_0161_T.JPG area — dark asphalt shingle roof
    id: 'hs-001',
    location: { lat: 42.281531, lng: -83.748834 },
    type: 'roof',
    status: 'finalized',
    surfaceTemperature: 57,  // 29°C ambient + 28°C delta (dark shingle under 750 W/m²)
    ambientDelta: 28,
    trace: createTrace('roof'),
    scoring: {
      anomalyScore: 0.83,
      severityScore: 0.88,
      confidenceScore: 0.91,
      finalScore: 0.87,
      reasoning: 'Dark asphalt shingle roof recorded at 57°C under 750 W/m² direct radiation. Significantly exceeds neighborhood average. High remediation potential.',
    },
    evidenceUrls: ['/evidence/roof-thermal-1.jpg', '/evidence/roof-visual-1.jpg'],
    createdAt: Date.now() - 30000,
    updatedAt: Date.now(),
  },
  {
    // DJI_20240804135012_0178_T.JPG area — large unshaded parking lot
    id: 'hs-002',
    location: { lat: 42.281389, lng: -83.744521 },
    type: 'parking_lot',
    status: 'finalized',
    surfaceTemperature: 61,  // 29°C ambient + 32°C delta (bare dark asphalt lot)
    ambientDelta: 32,
    trace: createTrace('parking_lot'),
    scoring: {
      anomalyScore: 0.94,
      severityScore: 0.91,
      confidenceScore: 0.89,
      finalScore: 0.92,
      reasoning: 'Large unshaded parking area in full sun with bare dark asphalt. At 61°C surface temp it is the highest-priority heat source in this flight corridor.',
    },
    evidenceUrls: ['/evidence/parking-thermal-1.jpg'],
    createdAt: Date.now() - 25000,
    updatedAt: Date.now(),
  },
  {
    // DJI_20240804135147_0204_T.JPG area — road intersection
    id: 'hs-003',
    location: { lat: 42.281050, lng: -83.746712 },
    type: 'road_pavement',
    status: 'finalized',
    surfaceTemperature: 49,  // 29°C ambient + 20°C delta (road surface, partial shade)
    ambientDelta: 20,
    trace: createTrace('road_pavement'),
    scoring: {
      anomalyScore: 0.67,
      severityScore: 0.74,
      confidenceScore: 0.95,
      finalScore: 0.73,
      reasoning: 'Road intersection with sustained solar exposure captured across 3 drone passes. Moderate priority — cool pavement treatment viable at next maintenance cycle.',
    },
    evidenceUrls: ['/evidence/road-thermal-1.jpg'],
    createdAt: Date.now() - 20000,
    updatedAt: Date.now(),
  },
  {
    // DJI_20240804134851_0143_T.JPG area — rooftop HVAC unit (expected source)
    id: 'hs-004',
    location: { lat: 42.281715, lng: -83.749902 },
    type: 'hvac_mechanical',
    status: 'discarded',
    surfaceTemperature: 68,  // 29°C ambient + 39°C delta (active HVAC exhaust)
    ambientDelta: 39,
    trace: createTrace('hvac_mechanical', true),
    evidenceUrls: ['/evidence/hvac-thermal-1.jpg'],
    createdAt: Date.now() - 15000,
    updatedAt: Date.now(),
  },
  {
    // DJI_20240804135230_0219_T.JPG area — cleared lot, vegetation loss
    id: 'hs-005',
    location: { lat: 42.281178, lng: -83.743680 },
    type: 'vegetation_loss',
    status: 'investigating',
    surfaceTemperature: 44,  // 29°C ambient + 15°C delta (bare soil / disturbed ground)
    ambientDelta: 15,
    trace: createTrace('vegetation_loss').slice(0, 4),
    evidenceUrls: [],
    createdAt: Date.now() - 10000,
    updatedAt: Date.now(),
  },
];

export const MOCK_SESSION: InvestigationSession = {
  id: 'session-001',
  regionBounds: DEMO_REGION.bounds,
  hotspots: MOCK_HOTSPOTS,
  activeHotspotId: null,
  status: 'complete',
  startedAt: Date.now() - 60000,
  completedAt: Date.now(),
};

export const MOCK_RECOMMENDATIONS: Record<string, Recommendation> = {
  'hs-001': {
    hotspotId: 'hs-001',
    summary: 'Apply cool roof coating to reduce 57°C surface temperature by up to 28°C',
    actions: [
      {
        id: 'action-1',
        title: 'Apply white elastomeric roof coating',
        description: 'Increases solar reflectance from ~0.12 to 0.80, directly cutting absorbed radiation under Ann Arbor summer peak (750 W/m²)',
        priority: 'high',
        estimatedImpact: '-22°C surface temperature',
      },
      {
        id: 'action-2',
        title: 'Consider green roof installation',
        description: 'Living roof system provides insulation and evapotranspiration cooling — especially effective in humid Michigan summers',
        priority: 'medium',
        estimatedImpact: '-18°C surface temperature',
      },
    ],
    estimatedCostRange: '$3,500 - $12,000',
    estimatedTemperatureReduction: '18-28°C',
  },
  'hs-002': {
    hotspotId: 'hs-002',
    summary: 'Parking lot at 61°C is the highest heat source in the corridor — address urgently',
    actions: [
      {
        id: 'action-1',
        title: 'Install solar canopy shade structures',
        description: 'PV canopies eliminate direct radiation on pavement and generate on-site power — ideal for Michigan net metering',
        priority: 'high',
        estimatedImpact: '-24°C surface temperature',
      },
      {
        id: 'action-2',
        title: 'Apply cool pavement coating',
        description: 'High-albedo sealant reduces solar absorption; can be applied without full repave',
        priority: 'high',
        estimatedImpact: '-14°C surface temperature',
      },
      {
        id: 'action-3',
        title: 'Add landscaped tree islands',
        description: 'Native Michigan shade trees (red maple, oak) provide natural cooling and storm water management',
        priority: 'medium',
        estimatedImpact: '-8°C localized cooling',
      },
    ],
    estimatedCostRange: '$18,000 - $52,000',
    estimatedTemperatureReduction: '24-32°C',
  },
  'hs-003': {
    hotspotId: 'hs-003',
    summary: 'Road surface at 49°C — cool pavement treatment recommended at next maintenance cycle',
    actions: [
      {
        id: 'action-1',
        title: 'Apply reflective micro-surfacing',
        description: 'Light-colored polymer-modified emulsion applied during scheduled road maintenance',
        priority: 'medium',
        estimatedImpact: '-12°C surface temperature',
      },
      {
        id: 'action-2',
        title: 'Street tree canopy expansion',
        description: 'Extend existing tree pits along corridor — reduces pavement solar load without repaving',
        priority: 'low',
        estimatedImpact: '-6°C localized cooling',
      },
    ],
    estimatedCostRange: '$9,000 - $22,000',
    estimatedTemperatureReduction: '10-15°C',
  },
};

export const getHotspotTypeLabel = (type: Hotspot['type']): string => {
  const labels: Record<Hotspot['type'], string> = {
    roof: 'Building Roof',
    road_pavement: 'Road Surface',
    parking_lot: 'Parking Lot',
    hvac_mechanical: 'HVAC/Mechanical',
    vegetation_loss: 'Vegetation Loss',
    other: 'Other',
  };
  return labels[type];
};

export const getHotspotTypeIcon = (type: Hotspot['type']): string => {
  const icons: Record<Hotspot['type'], string> = {
    roof: 'building',
    road_pavement: 'road',
    parking_lot: 'car',
    hvac_mechanical: 'fan',
    vegetation_loss: 'tree',
    other: 'circle',
  };
  return icons[type];
};

// Generate hotspots dynamically for a selected region
export function generateHotspotsForRegion(bounds: BoundingBox): Hotspot[] {
  const types: Hotspot['type'][] = ['roof', 'parking_lot', 'road_pavement', 'hvac_mechanical', 'vegetation_loss'];
  const count = 4 + Math.floor(Math.random() * 3); // 4-6 hotspots
  
  const hotspots: Hotspot[] = [];
  
  for (let i = 0; i < count; i++) {
    const type = types[Math.floor(Math.random() * types.length)];
    const isDiscarded = type === 'hvac_mechanical' && Math.random() > 0.5;
    const isInvestigating = !isDiscarded && Math.random() > 0.7;
    
    // Random position within bounds
    const lat = bounds.south + Math.random() * (bounds.north - bounds.south);
    const lng = bounds.west + Math.random() * (bounds.east - bounds.west);
    
    // Ambient ~29°C (Ann Arbor summer), surface adds 15-35°C depending on surface
    const ambientDelta = 15 + Math.random() * 20;
    const surfaceTemp = 29 + ambientDelta;
    
    const anomalyScore = 0.5 + Math.random() * 0.45;
    const severityScore = 0.5 + Math.random() * 0.45;
    const confidenceScore = 0.7 + Math.random() * 0.25;
    const finalScore = (anomalyScore * 0.3 + severityScore * 0.5 + confidenceScore * 0.2);
    
    hotspots.push({
      id: `hs-${Date.now()}-${i}`,
      location: { lat, lng },
      type,
      status: isDiscarded ? 'discarded' : isInvestigating ? 'investigating' : 'finalized',
      surfaceTemperature: Math.round(surfaceTemp),
      ambientDelta: Math.round(ambientDelta),
      trace: createTrace(type, isDiscarded),
      scoring: isDiscarded ? undefined : {
        anomalyScore,
        severityScore,
        confidenceScore,
        finalScore,
        reasoning: `${getHotspotTypeLabel(type)} with significant thermal anomaly detected. Delta ${Math.round(ambientDelta)}°C above ambient.`,
      },
      evidenceUrls: [`/evidence/${type}-thermal-${i}.jpg`],
      createdAt: Date.now() - (count - i) * 5000,
      updatedAt: Date.now(),
    });
  }
  
  // Sort by score descending
  return hotspots.sort((a, b) => (b.scoring?.finalScore ?? 0) - (a.scoring?.finalScore ?? 0));
}
