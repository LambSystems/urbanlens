'use client';

import { useCallback, useMemo, useState, useRef, useEffect } from 'react';
import { GoogleMap, useJsApiLoader, Marker, Rectangle, DrawingManager } from '@react-google-maps/api';
import { useThermal } from '@/lib/thermal-context';
import type { Hotspot, BoundingBox, SelectedRegion } from '@/lib/types';

const libraries: ('drawing' | 'geometry')[] = ['drawing', 'geometry'];

const mapContainerStyle = {
  width: '100%',
  height: '100%',
};

const MODEL_IMAGE_WIDTH = 640;
const MODEL_IMAGE_HEIGHT = 512;
const MODEL_ASPECT_RATIO = MODEL_IMAGE_WIDTH / MODEL_IMAGE_HEIGHT;
const DEFAULT_MAP_CENTER = { lat: 42.2813, lng: -83.7470 };
const DEFAULT_MAP_ZOOM = 17;

function getMarkerColor(hotspot: Hotspot): string {
  if (hotspot.status === 'discarded') return '#6b7280';
  if (hotspot.status === 'investigating') return '#f59e0b';

  const score = hotspot.scoring?.finalScore ?? 0;
  if (score >= 0.8) return '#ef4444';
  if (score >= 0.6) return '#f97316';
  if (score >= 0.4) return '#eab308';
  return '#22c55e';
}

function normalizeBoundsToModelAspect(bounds: BoundingBox): BoundingBox {
  const centerLat = (bounds.north + bounds.south) / 2;
  const centerLng = (bounds.east + bounds.west) / 2;
  const cosLat = Math.cos((centerLat * Math.PI) / 180);

  const halfHeightM = ((bounds.north - bounds.south) * 111_000) / 2;
  const halfWidthM = ((bounds.east - bounds.west) * 111_000 * Math.max(cosLat, 1e-6)) / 2;
  const currentAspectRatio = halfWidthM / Math.max(halfHeightM, 1e-6);

  let nextHalfWidthM = halfWidthM;
  let nextHalfHeightM = halfHeightM;

  if (currentAspectRatio > MODEL_ASPECT_RATIO) {
    nextHalfHeightM = halfWidthM / MODEL_ASPECT_RATIO;
  } else {
    nextHalfWidthM = halfHeightM * MODEL_ASPECT_RATIO;
  }

  const halfLatDeg = nextHalfHeightM / 111_000;
  const halfLngDeg = nextHalfWidthM / (111_000 * Math.max(cosLat, 1e-6));

  return {
    north: centerLat + halfLatDeg,
    south: centerLat - halfLatDeg,
    east: centerLng + halfLngDeg,
    west: centerLng - halfLngDeg,
  };
}

function fitStaticMapZoom(bounds: BoundingBox, center: { lat: number; lng: number }): number {
  const cosLat = Math.cos((center.lat * Math.PI) / 180);
  const widthM = (bounds.east - bounds.west) * 111_000 * Math.max(cosLat, 1e-6);
  const heightM = (bounds.north - bounds.south) * 111_000;
  const targetMetersPerPixel = Math.max(widthM / MODEL_IMAGE_WIDTH, heightM / MODEL_IMAGE_HEIGHT, 0.01);
  const zoom = Math.log2((156_543.03392 * Math.max(cosLat, 1e-6)) / targetMetersPerPixel);
  return Math.max(15, Math.min(21, Math.floor(zoom)));
}

function staticMapImageBounds(
  center: { lat: number; lng: number },
  zoom: number,
  imageWidth = MODEL_IMAGE_WIDTH,
  imageHeight = MODEL_IMAGE_HEIGHT,
): { north: number; south: number; east: number; west: number } {
  const cosLat = Math.cos((center.lat * Math.PI) / 180);
  const mPerPx = (156_543.03392 * cosLat) / Math.pow(2, zoom);
  const halfHM = (imageHeight / 2) * mPerPx;
  const halfWM = (imageWidth / 2) * mPerPx;
  const halfLatDeg = halfHM / 111_000;
  const halfLngDeg = halfWM / (111_000 * Math.max(cosLat, 1e-6));
  return {
    north: center.lat + halfLatDeg,
    south: center.lat - halfLatDeg,
    east: center.lng + halfLngDeg,
    west: center.lng - halfLngDeg,
  };
}

function calculateArea(bounds: BoundingBox): number {
  const latDiff = bounds.north - bounds.south;
  const lngDiff = bounds.east - bounds.west;
  const latKm = latDiff * 111;
  const lngKm = lngDiff * 111 * Math.cos((bounds.north + bounds.south) / 2 * Math.PI / 180);
  return latKm * lngKm;
}

function ThermalGroundOverlay({
  mapRef,
  imageUrl,
  bounds,
}: {
  mapRef: React.RefObject<google.maps.Map | null>;
  imageUrl: string;
  bounds: { north: number; south: number; east: number; west: number };
}) {
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !imageUrl) return;
    const overlay = new google.maps.GroundOverlay(imageUrl, bounds, {
      opacity: 0.82,
      clickable: false,
    });
    overlay.setMap(map);
    return () => overlay.setMap(null);
  // Re-render when URL or bounds change
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [imageUrl, bounds.north, bounds.south, bounds.east, bounds.west]);

  return null;
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
    setCapture,
    thermalOverlayUrl,
    thermalOverlayBounds,
  } = useThermal();

  const [showThermal, setShowThermal] = useState(true);

  const [drawingManager, setDrawingManager] = useState<google.maps.drawing.DrawingManager | null>(null);
  const rectangleRef = useRef<google.maps.Rectangle | null>(null);
  const mapRef = useRef<google.maps.Map | null>(null);

  const { isLoaded, loadError } = useJsApiLoader({
    googleMapsApiKey: process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY ?? '',
    libraries,
  });

  const center = useMemo(() => DEFAULT_MAP_CENTER, []);
  const thermalAvailable = Boolean(thermalOverlayUrl && thermalOverlayBounds);
  const showViewToggle = Boolean(selectedRegion) && selectionMode !== 'idle' && selectionMode !== 'drawing';

  const mapOptions: google.maps.MapOptions = useMemo(() => ({
    mapTypeId: 'hybrid',
    disableDefaultUI: true,
    zoomControl: true,
    mapTypeControl: false,
    streetViewControl: false,
    fullscreenControl: false,
    clickableIcons: false,
    tilt: 0,
    heading: 0,
    draggableCursor: selectionMode === 'drawing' ? 'crosshair' : undefined,
    styles: [
      { featureType: 'poi', elementType: 'labels', stylers: [{ visibility: 'off' }] },
      { featureType: 'transit', elementType: 'labels', stylers: [{ visibility: 'off' }] },
    ],
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
    map.setTilt(0);
    map.setHeading(0);
    mapRef.current = map;
  }, []);

  const onDrawingManagerLoad = useCallback((dm: google.maps.drawing.DrawingManager) => {
    setDrawingManager(dm);
  }, []);

  const onRectangleComplete = useCallback((rect: google.maps.Rectangle) => {
    if (rectangleRef.current) {
      rectangleRef.current.setMap(null);
    }
    rectangleRef.current = rect;

    const bounds = rect.getBounds();
    if (bounds) {
      const ne = bounds.getNorthEast();
      const sw = bounds.getSouthWest();

      const drawnBounds: BoundingBox = {
        north: ne.lat(),
        south: sw.lat(),
        east: ne.lng(),
        west: sw.lng(),
      };
      const normalizedBounds = normalizeBoundsToModelAspect(drawnBounds);
      const regionCenter = {
        lat: (normalizedBounds.north + normalizedBounds.south) / 2,
        lng: (normalizedBounds.east + normalizedBounds.west) / 2,
      };

      const map = mapRef.current;
      const viewport = map?.getBounds();
      const vne = viewport?.getNorthEast();
      const vsw = viewport?.getSouthWest();
      const analysisZoom = fitStaticMapZoom(normalizedBounds, regionCenter);
      const captureBounds = staticMapImageBounds(
        regionCenter,
        analysisZoom,
        MODEL_IMAGE_WIDTH,
        MODEL_IMAGE_HEIGHT,
      );

      const region: SelectedRegion = {
        bounds: captureBounds,
        center: regionCenter,
        areaKm2: calculateArea(captureBounds),
      };

      setSelectedRegion(region);
      setSelectionMode('selected');

      const mapState = {
        zoom: analysisZoom,
        mapTypeId: 'satellite',
        tilt: 0,
        heading: 0,
      };
      const viewportBounds = vne && vsw ? {
        north: vne.lat(),
        south: vsw.lat(),
        east: vne.lng(),
        west: vsw.lng(),
      } : null;

      const staticUrl =
        `https://maps.googleapis.com/maps/api/staticmap` +
        `?center=${regionCenter.lat},${regionCenter.lng}` +
        `&zoom=${analysisZoom}` +
        `&size=${MODEL_IMAGE_WIDTH}x${MODEL_IMAGE_HEIGHT}` +
        `&maptype=satellite` +
        `&key=${process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY ?? ''}`;

      fetch(staticUrl)
        .then(r => r.blob())
        .then(blob => new Promise<string>((resolve, reject) => {
          const reader = new FileReader();
          reader.onload = () => resolve(reader.result as string);
          reader.onerror = reject;
          reader.readAsDataURL(blob);
        }))
        .then(dataUrl => {
          const imageBase64 = dataUrl.split(',')[1];
          setCapture({ imageBase64, mapState, viewport: viewportBounds, imageBounds: captureBounds });
        })
        .catch(err => {
          console.warn('Static Maps image fetch failed, analysis will use coordinate fallback:', err);
          setCapture(null);
        });

      rect.setOptions({
        fillColor: '#f97316',
        fillOpacity: 0.15,
        strokeColor: '#f97316',
        strokeWeight: 2,
        editable: false,
        draggable: false,
        bounds: captureBounds,
      });
      rect.setBounds(captureBounds);
    }

    if (drawingManager) {
      drawingManager.setDrawingMode(null);
    }
  }, [drawingManager, setCapture, setSelectedRegion, setSelectionMode]);

  useEffect(() => {
    if (drawingManager) {
      if (selectionMode === 'drawing') {
        drawingManager.setDrawingMode(google.maps.drawing.OverlayType.RECTANGLE);
      } else {
        drawingManager.setDrawingMode(null);
      }
    }
  }, [selectionMode, drawingManager]);

  useEffect(() => {
    if (selectionMode === 'idle' && rectangleRef.current) {
      rectangleRef.current.setMap(null);
      rectangleRef.current = null;
    }
  }, [selectionMode]);

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
    <div className="relative h-full w-full">
      <GoogleMap
        mapContainerStyle={mapContainerStyle}
        center={center}
        zoom={DEFAULT_MAP_ZOOM}
        options={mapOptions}
        onClick={handleMapClick}
        onLoad={onMapLoad}
      >
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

        {showThermal && thermalAvailable && selectionMode === 'complete' && (
          <ThermalGroundOverlay
            mapRef={mapRef}
            imageUrl={thermalOverlayUrl as string}
            bounds={thermalOverlayBounds as { north: number; south: number; east: number; west: number }}
          />
        )}

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

        {hotspots.map((hotspot) => {
          const isActive = activeHotspot?.id === hotspot.id;
          const color = getMarkerColor(hotspot);

          return (
            <Marker
              key={hotspot.id}
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
          );
        })}
      </GoogleMap>

      {showViewToggle && (
        <div className="absolute bottom-6 left-1/2 -translate-x-1/2 z-10">
          <div className="flex items-center rounded-full bg-black/70 backdrop-blur-sm border border-white/10 p-1 gap-1 shadow-xl">
            <button
              onClick={() => setShowThermal(true)}
              disabled={!thermalAvailable}
              className={`px-4 py-1.5 rounded-full text-xs font-medium transition-all ${
                showThermal && thermalAvailable
                  ? 'bg-orange-500 text-white shadow-md'
                  : thermalAvailable
                    ? 'text-white/60 hover:text-white/90'
                    : 'text-white/35 cursor-not-allowed'
              }`}
            >
              Thermal
            </button>
            <button
              onClick={() => setShowThermal(false)}
              className={`px-4 py-1.5 rounded-full text-xs font-medium transition-all ${
                !showThermal || !thermalAvailable
                  ? 'bg-white/20 text-white shadow-md'
                  : 'text-white/60 hover:text-white/90'
              }`}
            >
              Satellite
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
