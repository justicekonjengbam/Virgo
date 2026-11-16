import { useEffect, useMemo, useRef, useState } from 'react';
import { Pressable, StyleSheet, View } from 'react-native';
import { Camera, CameraRef, GeoJSONSource, Layer, LocationManager, Map, Marker, UserLocation } from '@maplibre/maplibre-react-native';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';

import { DsText } from '../../../components/design-system';
import { colors, radius, spacing } from '../../../theme';
import { mapService } from '../services/mapService';

type Coordinate = { latitude: number; longitude: number };
type Props = {
  pickup?: Coordinate | null;
  destination?: Coordinate | null;
  driver?: Coordinate | null;
  route?: GeoJSON.Geometry | null;
  showUserLocation?: boolean;
  height?: number;
  expandable?: boolean;
  onMapPress?: (coordinate: Coordinate) => void;
};

const DEFAULT_MAP_STYLE = JSON.stringify({
  version: 8,
  name: 'Carto Voyager Raster',
  sources: {
    'carto-voyager': {
      type: 'raster',
      tiles: [
        'https://a.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png',
        'https://b.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png',
        'https://c.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png',
        'https://d.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png',
      ],
      tileSize: 256,
      attribution: '© OpenStreetMap contributors, © CARTO',
      maxzoom: 20,
    },
  },
  layers: [
    {
      id: 'carto-voyager-layer',
      type: 'raster',
      source: 'carto-voyager',
      minzoom: 0,
      maxzoom: 20,
    },
  ],
});

export function VirgoMap({
  pickup,
  destination,
  driver,
  route,
  showUserLocation = false,
  height = 360,
  expandable = false,
  onMapPress,
}: Props) {
  const cameraRef = useRef<CameraRef>(null);
  const [styleUrl, setStyleUrl] = useState<string>(DEFAULT_MAP_STYLE);
  const [error, setError] = useState(false);
  const [is3D, setIs3D] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [zoomLevel, setZoomLevel] = useState<number>(pickup ? 16 : 14.5);
  const [isMounted, setIsMounted] = useState(true);

  useEffect(() => {
    return () => {
      setIsMounted(false);
      try {
        LocationManager.stop();
      } catch {}
    };
  }, []);

  useEffect(() => {
    void mapService
      .configuration()
      .then(value => {
        if (value?.style_url) {
          setStyleUrl(value.style_url);
        }
      })
      .catch(() => {
        // Fall back gracefully to built-in Carto Voyager raster tiles
      });
  }, []);

  const isVector = useMemo(() => styleUrl.includes('geoapify.com') || styleUrl.includes('vector'), [styleUrl]);
  const points = [pickup, destination, driver].filter(Boolean) as Coordinate[];

  const initialViewState = useMemo(() => {
    if (points.length > 1) {
      return {
        bounds: bounds(points),
        padding: { top: 50, right: 50, bottom: 50, left: 50 },
        pitch: is3D ? 40 : 0,
      };
    }
    const center = points[0]
      ? ([points[0].longitude, points[0].latitude] as [number, number])
      : ([93.9368, 24.8170] as [number, number]);
    return {
      center,
      zoom: points[0] ? 16 : 14.5,
      pitch: is3D ? 40 : 0,
    };
  }, [destination?.latitude, destination?.longitude, driver?.latitude, driver?.longitude, is3D, pickup?.latitude, pickup?.longitude]);

  useEffect(() => {
    if (pickup && cameraRef.current) {
      cameraRef.current.easeTo({
        center: [pickup.longitude, pickup.latitude],
        zoom: 16,
        duration: 400,
      });
      setZoomLevel(16);
    }
  }, [pickup?.latitude, pickup?.longitude]);

  const toggle3D = () => {
    const next = !is3D;
    setIs3D(next);
    const center = points[0]
      ? ([points[0].longitude, points[0].latitude] as [number, number])
      : ([93.9368, 24.8170] as [number, number]);
    cameraRef.current?.easeTo({
      center,
      pitch: next ? 45 : 0,
      duration: 350,
    });
  };

  const zoomIn = () => {
    const next = Math.min(20, zoomLevel + 1);
    setZoomLevel(next);
    cameraRef.current?.zoomTo(next, { duration: 250 });
  };

  const zoomOut = () => {
    const next = Math.max(10, zoomLevel - 1);
    setZoomLevel(next);
    cameraRef.current?.zoomTo(next, { duration: 250 });
  };

  const recenter = () => {
    const target = pickup || driver || destination;
    if (target && cameraRef.current) {
      cameraRef.current.easeTo({
        center: [target.longitude, target.latitude],
        zoom: 16,
        duration: 400,
      });
      setZoomLevel(16);
    }
  };

  const actualHeight = isExpanded ? 520 : height;

  if (error) {
    return (
      <View style={[styles.fallback, { height: actualHeight }]}>
        <MaterialCommunityIcons color={colors.textTertiary} name="map-off-outline" size={32} />
        <DsText color={colors.textSecondary}>Map is unavailable</DsText>
      </View>
    );
  }

  return (
    <View style={[styles.container, { height: actualHeight }]}>
      <Map
        mapStyle={styleUrl}
        onDidFailLoadingMap={() => {
          if (styleUrl !== DEFAULT_MAP_STYLE) {
            setStyleUrl(DEFAULT_MAP_STYLE);
          } else {
            setError(true);
          }
        }}
        onPress={event => {
          const [longitude, latitude] = event.nativeEvent.lngLat;
          onMapPress?.({ latitude, longitude });
        }}
        style={styles.map}
        touchPitch
        touchRotate
      >
        <Camera initialViewState={initialViewState} ref={cameraRef} />
        {showUserLocation && isMounted ? <UserLocation animated={false} /> : null}

        {isVector ? (
          <Layer
            id="3d-buildings"
            minzoom={14}
            paint={{
              'fill-extrusion-color': '#dcd6cd',
              'fill-extrusion-height': ['coalesce', ['get', 'render_height'], 10],
              'fill-extrusion-base': ['coalesce', ['get', 'render_min_height'], 0],
              'fill-extrusion-opacity': 0.82,
            }}
            source="default"
            source-layer="building"
            type="fill-extrusion"
          />
        ) : null}

        {route ? (
          <GeoJSONSource data={{ type: 'Feature', properties: {}, geometry: route }} id="ride-route">
            <Layer
              id="ride-route-casing"
              paint={{ 'line-color': '#1a4f8b', 'line-width': 7, 'line-opacity': 0.7 }}
              type="line"
            />
            <Layer
              id="ride-route-line"
              paint={{ 'line-color': colors.primary, 'line-width': 5, 'line-opacity': 0.95 }}
              type="line"
            />
          </GeoJSONSource>
        ) : null}

        {pickup ? <MapMarker coordinate={pickup} icon="map-marker" id="pickup" tone={colors.primary} /> : null}
        {destination ? <MapMarker coordinate={destination} icon="map-marker-check" id="destination" tone={colors.success} /> : null}
        {driver ? <MapMarker coordinate={driver} icon="car" id="driver" tone={colors.textPrimary} /> : null}
      </Map>

      {onMapPress ? (
        <View pointerEvents="none" style={styles.mapHint}>
          <MaterialCommunityIcons color={colors.primary} name="gesture-tap" size={16} />
          <DsText color={colors.primary} style={styles.hintText}>
            Tap map to place pin
          </DsText>
        </View>
      ) : null}

      <View style={styles.controlsGroup}>
        {expandable ? (
          <Pressable
            accessibilityLabel={isExpanded ? 'Shrink map' : 'Expand map'}
            onPress={() => setIsExpanded(!isExpanded)}
            style={styles.controlBtn}
          >
            <MaterialCommunityIcons
              color={colors.textPrimary}
              name={isExpanded ? 'arrow-collapse' : 'arrow-expand'}
              size={18}
            />
          </Pressable>
        ) : null}

        <Pressable
          accessibilityLabel="Toggle 3D Buildings view"
          onPress={toggle3D}
          style={[styles.controlBtn, is3D && styles.controlBtnActive]}
        >
          <DsText color={is3D ? colors.white : colors.textPrimary} style={styles.controlText}>
            3D
          </DsText>
        </Pressable>

        <Pressable accessibilityLabel="Zoom in" onPress={zoomIn} style={styles.controlBtn}>
          <MaterialCommunityIcons color={colors.textPrimary} name="plus" size={20} />
        </Pressable>

        <Pressable accessibilityLabel="Zoom out" onPress={zoomOut} style={styles.controlBtn}>
          <MaterialCommunityIcons color={colors.textPrimary} name="minus" size={20} />
        </Pressable>

        {pickup || driver || destination ? (
          <Pressable accessibilityLabel="Recenter" onPress={recenter} style={styles.controlBtn}>
            <MaterialCommunityIcons color={colors.primary} name="crosshairs-gps" size={18} />
          </Pressable>
        ) : null}
      </View>

      <View pointerEvents="none" style={styles.attribution}>
        <DsText color={colors.textSecondary} style={styles.attributionText}>
          © OpenStreetMap · Geoapify
        </DsText>
      </View>
    </View>
  );
}

function MapMarker({ coordinate, icon, id, tone }: { coordinate: Coordinate; icon: string; id: string; tone: string }) {
  return (
    <Marker anchor="bottom" id={id} lngLat={[coordinate.longitude, coordinate.latitude]}>
      <View style={[styles.marker, { backgroundColor: tone }]}>
        <MaterialCommunityIcons color={colors.white} name={icon} size={18} />
      </View>
    </Marker>
  );
}

function bounds(points: Coordinate[]): [number, number, number, number] {
  const longitudes = points.map(point => point.longitude);
  const latitudes = points.map(point => point.latitude);
  return [Math.min(...longitudes), Math.min(...latitudes), Math.max(...longitudes), Math.max(...latitudes)];
}

const styles = StyleSheet.create({
  container: {
    borderColor: colors.border,
    borderRadius: radius.lg,
    borderWidth: 1,
    overflow: 'hidden',
    position: 'relative',
  },
  map: { flex: 1 },
  fallback: {
    alignItems: 'center',
    backgroundColor: colors.surfaceMuted,
    borderColor: colors.border,
    borderRadius: radius.lg,
    borderWidth: 1,
    gap: spacing.sm,
    justifyContent: 'center',
  },
  marker: {
    alignItems: 'center',
    borderColor: colors.white,
    borderRadius: radius.pill,
    borderWidth: 2,
    height: 34,
    justifyContent: 'center',
    width: 34,
  },
  mapHint: {
    alignItems: 'center',
    backgroundColor: 'rgba(255,255,255,0.94)',
    borderRadius: radius.pill,
    flexDirection: 'row',
    gap: spacing.xs,
    left: spacing.sm,
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    position: 'absolute',
    top: spacing.sm,
  },
  hintText: { fontSize: 11, lineHeight: 14 },
  controlsGroup: {
    alignItems: 'center',
    gap: spacing.xs,
    position: 'absolute',
    right: spacing.sm,
    top: spacing.sm,
  },
  controlBtn: {
    alignItems: 'center',
    backgroundColor: 'rgba(255,255,255,0.96)',
    borderColor: colors.border,
    borderRadius: radius.pill,
    borderWidth: 1,
    elevation: 3,
    height: 34,
    justifyContent: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1.5 },
    shadowOpacity: 0.15,
    shadowRadius: 3,
    width: 34,
  },
  controlBtnActive: {
    backgroundColor: colors.primary,
    borderColor: colors.primary,
  },
  controlText: {
    fontSize: 11,
    fontWeight: '700',
  },
  attribution: {
    backgroundColor: 'rgba(255,255,255,0.88)',
    bottom: 3,
    paddingHorizontal: 4,
    position: 'absolute',
    right: 3,
  },
  attributionText: { fontSize: 9, lineHeight: 12 },
});

export const CabSureMap = VirgoMap;
