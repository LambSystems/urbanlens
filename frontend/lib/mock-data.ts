import type { Hotspot, InvestigationSession, Recommendation, TraceStep, BoundingBox } from './types';

// Demo region: Downtown Phoenix, AZ (known for urban heat)
export const DEMO_REGION = {
  center: { lat: 33.4484, lng: -112.0740 },
  zoom: 16,
  bounds: {
    north: 33.4520,
    south: 33.4450,
    east: -112.0680,
    west: -112.0800,
  },
};

const createTrace = (type: Hotspot['type'], isDiscarded = false): TraceStep[] => {
  const baseTime = Date.now() - 30000;
  
  const steps: TraceStep[] = [
    {
      id: `trace-1`,
      action: 'candidate_detected',
      timestamp: baseTime,
      message: 'Thermal anomaly detected in satellite imagery',
      details: { surfaceTemp: 52, ambientTemp: 38 },
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

export const MOCK_HOTSPOTS: Hotspot[] = [
  {
    id: 'hs-001',
    location: { lat: 33.4492, lng: -112.0755 },
    type: 'roof',
    status: 'finalized',
    surfaceTemperature: 54,
    ambientDelta: 16,
    trace: createTrace('roof'),
    scoring: {
      anomalyScore: 0.78,
      severityScore: 0.85,
      confidenceScore: 0.91,
      finalScore: 0.84,
      reasoning: 'Dark asphalt roof significantly exceeds neighborhood average. High remediation potential.',
    },
    evidenceUrls: ['/evidence/roof-thermal-1.jpg', '/evidence/roof-visual-1.jpg'],
    createdAt: Date.now() - 30000,
    updatedAt: Date.now(),
  },
  {
    id: 'hs-002',
    location: { lat: 33.4478, lng: -112.0720 },
    type: 'parking_lot',
    status: 'finalized',
    surfaceTemperature: 58,
    ambientDelta: 20,
    trace: createTrace('parking_lot'),
    scoring: {
      anomalyScore: 0.92,
      severityScore: 0.88,
      confidenceScore: 0.87,
      finalScore: 0.89,
      reasoning: 'Large unshaded parking area with dark asphalt. Major heat contributor to local microclimate.',
    },
    evidenceUrls: ['/evidence/parking-thermal-1.jpg'],
    createdAt: Date.now() - 25000,
    updatedAt: Date.now(),
  },
  {
    id: 'hs-003',
    location: { lat: 33.4465, lng: -112.0765 },
    type: 'road_pavement',
    status: 'finalized',
    surfaceTemperature: 51,
    ambientDelta: 13,
    trace: createTrace('road_pavement'),
    scoring: {
      anomalyScore: 0.65,
      severityScore: 0.72,
      confidenceScore: 0.94,
      finalScore: 0.71,
      reasoning: 'Road intersection with high solar exposure. Moderate priority due to infrastructure constraints.',
    },
    evidenceUrls: ['/evidence/road-thermal-1.jpg'],
    createdAt: Date.now() - 20000,
    updatedAt: Date.now(),
  },
  {
    id: 'hs-004',
    location: { lat: 33.4488, lng: -112.0730 },
    type: 'hvac_mechanical',
    status: 'discarded',
    surfaceTemperature: 62,
    ambientDelta: 24,
    trace: createTrace('hvac_mechanical', true),
    evidenceUrls: ['/evidence/hvac-thermal-1.jpg'],
    createdAt: Date.now() - 15000,
    updatedAt: Date.now(),
  },
  {
    id: 'hs-005',
    location: { lat: 33.4472, lng: -112.0748 },
    type: 'vegetation_loss',
    status: 'investigating',
    surfaceTemperature: 48,
    ambientDelta: 10,
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
    summary: 'Install cool roof coating to reduce surface temperature by up to 25°C',
    actions: [
      {
        id: 'action-1',
        title: 'Apply reflective roof coating',
        description: 'White elastomeric coating can increase solar reflectance from 0.15 to 0.80',
        priority: 'high',
        estimatedImpact: '-20°C surface temperature',
      },
      {
        id: 'action-2',
        title: 'Consider green roof installation',
        description: 'Living roof system provides insulation and evapotranspiration cooling',
        priority: 'medium',
        estimatedImpact: '-15°C surface temperature',
      },
    ],
    estimatedCostRange: '$3,500 - $12,000',
    estimatedTemperatureReduction: '15-25°C',
  },
  'hs-002': {
    hotspotId: 'hs-002',
    summary: 'Implement parking lot cooling strategies to address major heat island source',
    actions: [
      {
        id: 'action-1',
        title: 'Install shade structures',
        description: 'Solar panel canopies provide shade while generating clean energy',
        priority: 'high',
        estimatedImpact: '-18°C surface temperature',
      },
      {
        id: 'action-2',
        title: 'Apply cool pavement coating',
        description: 'Reflective sealant reduces heat absorption significantly',
        priority: 'high',
        estimatedImpact: '-12°C surface temperature',
      },
      {
        id: 'action-3',
        title: 'Add tree islands',
        description: 'Strategic tree placement provides natural cooling',
        priority: 'medium',
        estimatedImpact: '-8°C localized cooling',
      },
    ],
    estimatedCostRange: '$15,000 - $45,000',
    estimatedTemperatureReduction: '20-30°C',
  },
  'hs-003': {
    hotspotId: 'hs-003',
    summary: 'Explore cool pavement options for road surface treatment',
    actions: [
      {
        id: 'action-1',
        title: 'Apply reflective surface treatment',
        description: 'Light-colored micro-surfacing during next maintenance cycle',
        priority: 'medium',
        estimatedImpact: '-10°C surface temperature',
      },
    ],
    estimatedCostRange: '$8,000 - $20,000',
    estimatedTemperatureReduction: '8-12°C',
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
    
    const surfaceTemp = 45 + Math.random() * 20;
    const ambientDelta = 8 + Math.random() * 18;
    
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
