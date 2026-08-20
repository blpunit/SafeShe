"use client";

import { useState, useEffect, useRef } from "react";
import Map, { Marker, NavigationControl, Source, Layer, MapRef } from "react-map-gl/maplibre";
import "maplibre-gl/dist/maplibre-gl.css";
import { MapPin, Navigation, AlertTriangle } from "lucide-react";
import { CommunityReportResponse } from "@/api/services/communityService";

// Bangalore fallback coordinates
const FALLBACK_LAT = 12.9716;
const FALLBACK_LNG = 77.5946;

interface Location {
  coordinates: [number, number];
}

interface SafeMapProps {
  source?: Location | null;
  destination?: Location | null;
  routeGeometry?: any | null; // GeoJSON
  reports?: CommunityReportResponse[] | null;
  onLocationDetected?: (lat: number, lng: number) => void;
}

export default function SafeMap({ source, destination, routeGeometry, reports, onLocationDetected }: SafeMapProps) {
  const [viewState, setViewState] = useState({
    longitude: FALLBACK_LNG,
    latitude: FALLBACK_LAT,
    zoom: 12
  });
  
  const [userLocation, setUserLocation] = useState<{lat: number, lng: number} | null>(null);
  const mapRef = useRef<MapRef>(null);

  const fallbackGeoJSON = (source && destination && !routeGeometry) ? {
    type: "Feature",
    properties: {},
    geometry: {
      type: "LineString",
      coordinates: [source.coordinates, destination.coordinates]
    }
  } : null;

  const rawGeoJson = routeGeometry || fallbackGeoJSON;
  
  const geoJsonData = rawGeoJson ? (
    rawGeoJson.type === "FeatureCollection" ? rawGeoJson : {
      type: "FeatureCollection",
      features: [rawGeoJson]
    }
  ) : null;

  useEffect(() => {
    // If it's a FeatureCollection with multiple features, compute bounding box for all coordinates
    if (geoJsonData?.features && mapRef.current) {
      let minLng = 180, minLat = 90, maxLng = -180, maxLat = -90;
      let hasCoords = false;
      
      geoJsonData.features.forEach((feature: any) => {
        if (feature?.geometry?.coordinates) {
          const coords = feature.geometry.coordinates;
          if (coords.length > 0) {
            hasCoords = true;
            for (const coord of coords) {
              if (coord[0] < minLng) minLng = coord[0];
              if (coord[1] < minLat) minLat = coord[1];
              if (coord[0] > maxLng) maxLng = coord[0];
              if (coord[1] > maxLat) maxLat = coord[1];
            }
          }
        }
      });

      if (hasCoords) {
        mapRef.current.fitBounds(
          [[minLng, minLat], [maxLng, maxLat]],
          { padding: 50, duration: 1000 }
        );
      }
    }
  }, [geoJsonData]);

  const isFirstLoad = useRef(true);

  useEffect(() => {
    let intervalId: NodeJS.Timeout;
    
    const fetchLocation = () => {
      if ("geolocation" in navigator) {
        navigator.geolocation.getCurrentPosition(
          (position) => {
            setUserLocation({
              lat: position.coords.latitude,
              lng: position.coords.longitude
            });
            onLocationDetected?.(position.coords.latitude, position.coords.longitude);
            // Snap to location only on first load
            if (!source && isFirstLoad.current) {
              setViewState((prev) => ({
                ...prev,
                longitude: position.coords.longitude,
                latitude: position.coords.latitude,
                zoom: 14
              }));
              isFirstLoad.current = false;
            }
          },
          (error) => console.warn("Geolocation error", error),
          { enableHighAccuracy: true, timeout: 2500, maximumAge: 0 }
        );
      } else {
        setUserLocation({ lat: FALLBACK_LAT, lng: FALLBACK_LNG });
      }
    };

    fetchLocation(); // Initial fetch
    intervalId = setInterval(fetchLocation, 3000); // Every 3 seconds

    return () => clearInterval(intervalId);
  }, []);

  // Use the active source for the marker, otherwise fallback to browser location
  const displaySource = source ? { lat: source.coordinates[1], lng: source.coordinates[0] } : userLocation;

  return (
    <div className="h-full w-full relative">
      <Map
        ref={mapRef}
        {...viewState}
        onMove={evt => setViewState(evt.viewState)}
        mapStyle={{
          version: 8,
          sources: {
            "osm-raster": {
              type: "raster",
              tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
              tileSize: 256,
              attribution: "&copy; OpenStreetMap contributors"
            }
          },
          layers: [
            {
              id: "osm-tiles",
              type: "raster",
              source: "osm-raster",
              minzoom: 0,
              maxzoom: 19
            }
          ]
        }}
        style={{ width: "100%", height: "100%" }}
      >
        <NavigationControl position="bottom-right" />
        
        {displaySource && (
          <Marker 
            longitude={displaySource.lng} 
            latitude={displaySource.lat} 
            anchor="center"
          >
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-white shadow-[0_2px_8px_rgba(0,0,0,0.25)] border-[3px] border-white ring-1 ring-black/5">
              <Navigation size={14} className="text-blue-600 fill-blue-600" />
            </div>
          </Marker>
        )}

        {destination && (
          <Marker 
            longitude={destination.coordinates[0]} 
            latitude={destination.coordinates[1]} 
            anchor="bottom"
          >
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-white shadow-lg animate-pulse-soft">
              <MapPin size={16} />
            </div>
          </Marker>
        )}

        {geoJsonData && (
          <Source id="route-source" type="geojson" data={geoJsonData}>
            <Layer 
              id="route-layer-recommended" 
              type="line" 
              source="route-source"
              filter={["==", "is_recommended", true]} 
              layout={{
                "line-join": "round",
                "line-cap": "round"
              }}
              paint={{
                "line-color": ["coalesce", ["get", "color"], "#16A34A"],
                "line-width": 6
              }} 
            />
            <Layer 
              id="route-layer-alternative" 
              type="line" 
              source="route-source"
              filter={["!=", "is_recommended", true]} 
              layout={{
                "line-join": "round",
                "line-cap": "round"
              }}
              paint={{
                "line-color": ["coalesce", ["get", "color"], "#4F46E5"],
                "line-width": 6,
                "line-dasharray": [2, 2]
              }} 
            />
          </Source>
        )}

        {reports?.map(report => (
          <Marker 
            key={report._id || report.id}
            longitude={report.location.coordinates[0]} 
            latitude={report.location.coordinates[1]} 
            anchor="bottom"
          >
            <div className={`flex flex-col items-center group cursor-pointer`}>
              <div className="bg-card px-2 py-1 rounded-md text-[10px] font-bold shadow-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap mb-1 border border-border flex flex-col items-center">
                <span>{report.report_type}</span>
                <span className={`text-[8px] uppercase tracking-wider ${
                  report.verification_status === 'Verified' ? 'text-success' :
                  report.verification_status === 'Pending' ? 'text-warning' : 'text-danger'
                }`}>{report.verification_status}</span>
              </div>
              <div className={`flex h-8 w-8 items-center justify-center rounded-full text-white shadow-lg border-2 border-background transition-transform group-hover:scale-110 ${
                report.verification_status === 'Verified' ? 'bg-success' : 
                report.verification_status === 'Pending' ? 'bg-warning' : 
                'bg-danger animate-pulse'
              }`}>
                <AlertTriangle size={16} />
              </div>
            </div>
          </Marker>
        ))}
      </Map>
    </div>
  );
}
