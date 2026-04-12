'use client';

import { useCallback, useMemo } from 'react';
import { GoogleMap, useJsApiLoader, Marker, Circle } from '@react-google-maps/api';
import { useThermal } from '@/lib/thermal-context';
import { DEMO_REGION } from '@/lib/mock-data';
import type { Hotspot } from '@/lib/types';

const mapContainerStyle = {
  width: '100%',
  height: '100%',
};

const darkMapStyles = [
  { elementType: 'geometry', stylers: [{ color: '#1a1a2e' }] },
  { elementType: 'labels.text.stroke', stylers: [{ color: '#1a1a2e' }] },
  { elementType: 'labels.text.fill', stylers: [{ color: '#8b8b8b' }] },
  {
    featureType: 'administrative',
    elementType: 'geometry.stroke',
    stylers: [{ color: '#2a2a4a' }],
  },
  {
    featureType: 'administrative.land_parcel',
    elementType: 'labels.text.fill',
    stylers: [{ color: '#64748b' }],
  },
  {
    featureType: 'poi',
    elementType: 'geometry',
    stylers: [{ color: '#1e1e3f' }],
  },
  {
    featureType: 'poi',
    elementType: 'labels.text.fill',
    stylers: [{ color: '#64748b' }],
  },
  {
    featureType: 'poi.park',
    elementType: 'geometry',
    stylers: [{ color: '#1a3a2a' }],
  },
  {
    featureType: 'road',
    elementType: 'geometry',
    stylers: [{ color: '#2a2a4a' }],
  },
  {
    featureType: 'road',
    elementType: 'geometry.stroke',
    stylers: [{ color: '#1a1a2e' }],
  },
  {
    featureType: 'road',
    elementType: 'labels.text.fill',
    stylers: [{ color: '#8b8b8b' }],
  },
  {
    featureType: 'road.highway',
    elementType: 'geometry',
    stylers: [{ color: '#3a3a5a' }],
  },
  {
    featureType: 'transit',
    elementType: 'geometry',
    stylers: [{ color: '#1e1e3f' }],
  },
  {
    featureType: 'water',
    elementType: 'geometry',
    stylers: [{ color: '#0e1a2b' }],
  },
  {
    featureType: 'water',
    elementType: 'labels.text.fill',
    stylers: [{ color: '#4a6a8a' }],
  },
];

const mapOptions: google.maps.MapOptions = {
  styles: darkMapStyles,
  disableDefaultUI: true,
  zoomControl: true,
  mapTypeControl: false,
  streetViewControl: false,
  fullscreenControl: false,
  clickableIcons: false,
};

function getMarkerColor(hotspot: Hotspot): string {
  if (hotspot.status === 'discarded') return '#6b7280'; // gray
  if (hotspot.status === 'investigating') return '#f59e0b'; // amber
  
  const score = hotspot.scoring?.finalScore ?? 0;
  if (score >= 0.8) return '#ef4444'; // red - critical
  if (score >= 0.6) return '#f97316'; // orange - high
  if (score >= 0.4) return '#eab308'; // yellow - medium
  return '#22c55e'; // green - low
}

function getCircleRadius(hotspot: Hotspot): number {
  const baseRadius = 25;
  const score = hotspot.scoring?.finalScore ?? 0.5;
  return baseRadius + (score * 25);
}

export function ThermalMap() {
  const { hotspots, activeHotspot, setActiveHotspot } = useThermal();

  const { isLoaded, loadError } = useJsApiLoader({
    googleMapsApiKey: process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY ?? '',
  });

  const center = useMemo(() => DEMO_REGION.center, []);

  const handleMarkerClick = useCallback(
    (hotspot: Hotspot) => {
      setActiveHotspot(hotspot);
    },
    [setActiveHotspot]
  );

  const handleMapClick = useCallback(() => {
    setActiveHotspot(null);
  }, [setActiveHotspot]);

  if (loadError) {
    return (
      <div className="flex h-full w-full items-center justify-center bg-background">
        <div className="text-center">
          <p className="text-destructive font-medium">Failed to load Google Maps</p>
          <p className="text-muted-foreground text-sm mt-1">Please check your API key configuration</p>
        </div>
      </div>
    );
  }

  if (!isLoaded) {
    return (
      <div className="flex h-full w-full items-center justify-center bg-background">
        <div className="flex items-center gap-3">
          <div className="h-5 w-5 animate-spin rounded-full border-2 border-primary border-t-transparent" />
          <span className="text-muted-foreground">Loading map...</span>
        </div>
      </div>
    );
  }

  return (
    <GoogleMap
      mapContainerStyle={mapContainerStyle}
      center={center}
      zoom={DEMO_REGION.zoom}
      options={mapOptions}
      onClick={handleMapClick}
    >
      {hotspots.map((hotspot) => {
        const isActive = activeHotspot?.id === hotspot.id;
        const color = getMarkerColor(hotspot);
        
        return (
          <div key={hotspot.id}>
            {/* Heat radius circle */}
            <Circle
              center={hotspot.location}
              radius={getCircleRadius(hotspot)}
              options={{
                fillColor: color,
                fillOpacity: isActive ? 0.4 : 0.2,
                strokeColor: color,
                strokeOpacity: isActive ? 0.9 : 0.5,
                strokeWeight: isActive ? 3 : 1,
              }}
            />
            
            {/* Marker */}
            <Marker
              position={hotspot.location}
              onClick={() => handleMarkerClick(hotspot)}
              icon={{
                path: google.maps.SymbolPath.CIRCLE,
                scale: isActive ? 12 : 8,
                fillColor: color,
                fillOpacity: 1,
                strokeColor: '#ffffff',
                strokeWeight: isActive ? 3 : 2,
              }}
            />
          </div>
        );
      })}
    </GoogleMap>
  );
}
