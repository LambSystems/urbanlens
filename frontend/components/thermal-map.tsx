'use client';

import { useCallback, useMemo, useState, useRef, useEffect } from 'react';
import { GoogleMap, useJsApiLoader, Marker, Circle, Rectangle, DrawingManager } from '@react-google-maps/api';
import { useThermal } from '@/lib/thermal-context';
import { DEMO_REGION } from '@/lib/mock-data';
import type { Hotspot, BoundingBox, SelectedRegion } from '@/lib/types';

const libraries: ('drawing' | 'geometry')[] = ['drawing', 'geometry'];

const mapContainerStyle = {
  width: '100%',
  height: '100%',
};

const darkMapStyles = [
  { elementType: 'geometry', stylers: [{ color: '#0f172a' }] },
  { elementType: 'labels.text.stroke', stylers: [{ color: '#0f172a' }] },
  { elementType: 'labels.text.fill', stylers: [{ color: '#64748b' }] },
  {
    featureType: 'administrative',
    elementType: 'geometry.stroke',
    stylers: [{ color: '#1e293b' }],
  },
  {
    featureType: 'administrative.land_parcel',
    elementType: 'labels.text.fill',
    stylers: [{ color: '#475569' }],
  },
  {
    featureType: 'poi',
    elementType: 'geometry',
    stylers: [{ color: '#1e293b' }],
  },
  {
    featureType: 'poi',
    elementType: 'labels.text.fill',
    stylers: [{ color: '#475569' }],
  },
  {
    featureType: 'poi.park',
    elementType: 'geometry',
    stylers: [{ color: '#134e4a' }],
  },
  {
    featureType: 'road',
    elementType: 'geometry',
    stylers: [{ color: '#1e293b' }],
  },
  {
    featureType: 'road',
    elementType: 'geometry.stroke',
    stylers: [{ color: '#0f172a' }],
  },
  {
    featureType: 'road',
    elementType: 'labels.text.fill',
    stylers: [{ color: '#64748b' }],
  },
  {
    featureType: 'road.highway',
    elementType: 'geometry',
    stylers: [{ color: '#334155' }],
  },
  {
    featureType: 'transit',
    elementType: 'geometry',
    stylers: [{ color: '#1e293b' }],
  },
  {
    featureType: 'water',
    elementType: 'geometry',
    stylers: [{ color: '#0c4a6e' }],
  },
  {
    featureType: 'water',
    elementType: 'labels.text.fill',
    stylers: [{ color: '#38bdf8' }],
  },
];

function getMarkerColor(hotspot: Hotspot): string {
  if (hotspot.status === 'discarded') return '#6b7280';
  if (hotspot.status === 'investigating') return '#f59e0b';
  
  const score = hotspot.scoring?.finalScore ?? 0;
  if (score >= 0.8) return '#ef4444';
  if (score >= 0.6) return '#f97316';
  if (score >= 0.4) return '#eab308';
  return '#22c55e';
}

function getCircleRadius(hotspot: Hotspot): number {
  const baseRadius = 20;
  const score = hotspot.scoring?.finalScore ?? 0.5;
  return baseRadius + (score * 30);
}

function calculateArea(bounds: BoundingBox): number {
  const latDiff = bounds.north - bounds.south;
  const lngDiff = bounds.east - bounds.west;
  const latKm = latDiff * 111;
  const lngKm = lngDiff * 111 * Math.cos((bounds.north + bounds.south) / 2 * Math.PI / 180);
  return latKm * lngKm;
}

export function ThermalMap() {
  const { 
    hotspots, 
    activeHotspot, 
    setActiveHotspot,
    selectionMode,
    setSelectionMode,
    selectedRegion,
    setSelectedRegion,
  } = useThermal();
  
  const [drawingManager, setDrawingManager] = useState<google.maps.drawing.DrawingManager | null>(null);
  const rectangleRef = useRef<google.maps.Rectangle | null>(null);
  const mapRef = useRef<google.maps.Map | null>(null);

  const { isLoaded, loadError } = useJsApiLoader({
    googleMapsApiKey: process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY ?? '',
    libraries,
  });

  const center = useMemo(() => DEMO_REGION.center, []);

  const mapOptions: google.maps.MapOptions = useMemo(() => ({
    styles: darkMapStyles,
    disableDefaultUI: true,
    zoomControl: true,
    mapTypeControl: false,
    streetViewControl: false,
    fullscreenControl: false,
    clickableIcons: false,
    draggableCursor: selectionMode === 'drawing' ? 'crosshair' : undefined,
  }), [selectionMode]);

  const handleMarkerClick = useCallback(
    (hotspot: Hotspot) => {
      setActiveHotspot(hotspot);
    },
    [setActiveHotspot]
  );

  const handleMapClick = useCallback(() => {
    if (selectionMode !== 'drawing') {
      setActiveHotspot(null);
    }
  }, [selectionMode, setActiveHotspot]);

  const onMapLoad = useCallback((map: google.maps.Map) => {
    mapRef.current = map;
  }, []);

  const onDrawingManagerLoad = useCallback((dm: google.maps.drawing.DrawingManager) => {
    setDrawingManager(dm);
  }, []);

  const onRectangleComplete = useCallback((rect: google.maps.Rectangle) => {
    // Remove old rectangle if exists
    if (rectangleRef.current) {
      rectangleRef.current.setMap(null);
    }
    rectangleRef.current = rect;

    const bounds = rect.getBounds();
    if (bounds) {
      const ne = bounds.getNorthEast();
      const sw = bounds.getSouthWest();
      
      const selectedBounds: BoundingBox = {
        north: ne.lat(),
        south: sw.lat(),
        east: ne.lng(),
        west: sw.lng(),
      };
      
      const region: SelectedRegion = {
        bounds: selectedBounds,
        center: {
          lat: (ne.lat() + sw.lat()) / 2,
          lng: (ne.lng() + sw.lng()) / 2,
        },
        areaKm2: calculateArea(selectedBounds),
      };
      
      setSelectedRegion(region);
      setSelectionMode('selected');
      
      // Style the rectangle
      rect.setOptions({
        fillColor: '#f97316',
        fillOpacity: 0.15,
        strokeColor: '#f97316',
        strokeWeight: 2,
        editable: false,
        draggable: false,
      });
    }
    
    // Turn off drawing mode
    if (drawingManager) {
      drawingManager.setDrawingMode(null);
    }
  }, [drawingManager, setSelectedRegion, setSelectionMode]);

  // Enable drawing mode when selectionMode changes to 'drawing'
  useEffect(() => {
    if (drawingManager) {
      if (selectionMode === 'drawing') {
        drawingManager.setDrawingMode(google.maps.drawing.OverlayType.RECTANGLE);
      } else {
        drawingManager.setDrawingMode(null);
      }
    }
  }, [selectionMode, drawingManager]);

  // Clean up rectangle when canceling
  useEffect(() => {
    if (selectionMode === 'idle' && rectangleRef.current) {
      rectangleRef.current.setMap(null);
      rectangleRef.current = null;
    }
  }, [selectionMode]);

  // Fit map to selected region
  useEffect(() => {
    if (selectedRegion && mapRef.current && selectionMode === 'complete') {
      const bounds = new google.maps.LatLngBounds(
        { lat: selectedRegion.bounds.south, lng: selectedRegion.bounds.west },
        { lat: selectedRegion.bounds.north, lng: selectedRegion.bounds.east }
      );
      mapRef.current.fitBounds(bounds, 60);
    }
  }, [selectedRegion, selectionMode]);

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
      onLoad={onMapLoad}
    >
      {/* Drawing Manager */}
      <DrawingManager
        onLoad={onDrawingManagerLoad}
        onRectangleComplete={onRectangleComplete}
        options={{
          drawingControl: false,
          rectangleOptions: {
            fillColor: '#f97316',
            fillOpacity: 0.2,
            strokeColor: '#f97316',
            strokeWeight: 2,
            editable: false,
            draggable: false,
          },
        }}
      />

      {/* Selected region rectangle overlay (when complete) */}
      {selectedRegion && selectionMode === 'complete' && (
        <Rectangle
          bounds={{
            north: selectedRegion.bounds.north,
            south: selectedRegion.bounds.south,
            east: selectedRegion.bounds.east,
            west: selectedRegion.bounds.west,
          }}
          options={{
            fillColor: '#22c55e',
            fillOpacity: 0.08,
            strokeColor: '#22c55e',
            strokeWeight: 2,
          }}
        />
      )}

      {/* Hotspot markers and circles */}
      {hotspots.map((hotspot) => {
        const isActive = activeHotspot?.id === hotspot.id;
        const color = getMarkerColor(hotspot);
        
        return (
          <div key={hotspot.id}>
            <Circle
              center={hotspot.location}
              radius={getCircleRadius(hotspot)}
              options={{
                fillColor: color,
                fillOpacity: isActive ? 0.5 : 0.25,
                strokeColor: color,
                strokeOpacity: isActive ? 1 : 0.6,
                strokeWeight: isActive ? 3 : 1.5,
              }}
            />
            
            <Marker
              position={hotspot.location}
              onClick={() => handleMarkerClick(hotspot)}
              icon={{
                path: google.maps.SymbolPath.CIRCLE,
                scale: isActive ? 14 : 10,
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
