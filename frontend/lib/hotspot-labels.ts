import type { Hotspot } from './types';

export const getHotspotTypeLabel = (type: Hotspot['type']): string => {
  const labels: Record<Hotspot['type'], string> = {
    roof: 'Building Roof',
    parking_lot: 'Parking Lot',
    road_pavement: 'Road Surface',
    hvac_mechanical: 'HVAC / Mechanical',
    vegetation_loss: 'Vegetation Loss',
    other: 'Other Surface',
  };
  return labels[type] ?? 'Unknown Surface';
};
