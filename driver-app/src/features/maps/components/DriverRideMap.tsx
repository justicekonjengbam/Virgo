import { useEffect, useMemo, useRef, useState } from 'react';
import { Pressable, StyleSheet, View } from 'react-native';
import { Camera, CameraRef, GeoJSONSource, Layer, Map, Marker, UserLocation } from '@maplibre/maplibre-react-native';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';

import { DriverText } from '../../../components/DriverText';
import { colors, radius, spacing } from '../../../theme';
import { getMapConfiguration } from '../services/driverMapService';

type Coordinate = { latitude: number; longitude: number };
type Props = {
  pickup: Coordinate;
  destination: Coordinate;
  driver?: Coordinate | null;
  route?: GeoJSON.Geometry | null;
  height?: number;
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

export function DriverRideMap({ pickup, destination, driver, route, height = 400 }: Props) {
  const cameraRef = useRef<CameraRef>(null);
  const [styleUrl, setStyleUrl] = useState<string>(DEFAULT_MAP_STYLE);
  const [failed, setFailed] = useState(false);
  const [is3D, setIs3D] = useState(false);
  const [zoomLevel, setZoomLevel] = useState<number>(15.5);

  useEffect(() => {
    void getMapConfiguration()
      .then(config => {
        if (config?.style_url) {
          setStyleUrl(config.style_url);
        }
      })
      .catch(() => {
        // Fall back gracefully to built-in Carto Voyager raster tiles
      });
  }, []);

  const isVector = useMemo(() => styleUrl.includes('geoapify.com') || styleUrl.includes('vector'), [styleUrl]);
  const points = useMemo(() => [pickup, destination, ...(driver ? [driver] : [])], [destination, driver, pickup]);
  const mapBounds = useMemo(() => bounds(points), [points]);

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
    const target = driver || pickup;
    if (target && cameraRef.current) {
      cameraRef.current.easeTo({
        center: [target.longitude, target.latitude],
        zoom: 16,
        duration: 400,
      });
      setZoomLevel(16);
    }
  };

  if (failed) {
    return (
      <View style={[styles.fallback, { height }]}>
        <MaterialCommunityIcons color={colors.textTertiary} name="map-off-outline" size={34} />
        <DriverText color={colors.textSecondary}>Map is unavailable</DriverText>
      </View>
    );
  }

  return (
    <View style={[styles.container, { height }]}>
      <Map
        mapStyle={styleUrl}
        onDidFailLoadingMap={() => {
          if (styleUrl !== DEFAULT_MAP_STYLE) {
            setStyleUrl(DEFAULT_MAP_STYLE);
          } else {
            setFailed(true);
          }
        }}
        style={styles.map}
        touchPitch
        touchRotate
      >
        <Camera
          initialViewState={{
            bounds: mapBounds,
            padding: { top: 50, right: 50, bottom: 50, left: 50 },
            pitch: is3D ? 40 : 0,
          }}
          ref={cameraRef}
        />
        <UserLocation accuracy animated heading />

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
          <GeoJSONSource data={{ type: 'Feature', properties: {}, geometry: route }} id="driver-route">
            <Layer
              id="driver-route-casing"
              paint={{ 'line-color': '#1a4f8b', 'line-width': 7, 'line-opacity': 0.7 }}
              type="line"
            />
            <Layer
              id="driver-route-line"
              paint={{ 'line-color': colors.primary, 'line-width': 5, 'line-opacity': 0.95 }}
              type="line"
            />
          </GeoJSONSource>
        ) : null}

        <RideMarker coordinate={pickup} icon="map-marker" id="pickup" tone={colors.primary} />
        <RideMarker coordinate={destination} icon="map-marker-check" id="destination" tone={colors.success} />
        {driver ? <RideMarker coordinate={driver} icon="car" id="driver" tone={colors.textPrimary} /> : null}
      </Map>

      <View style={styles.controlsGroup}>
        <Pressable
          accessibilityLabel="Toggle 3D Buildings view"
          onPress={toggle3D}
          style={[styles.controlBtn, is3D && styles.controlBtnActive]}
        >
          <DriverText color={is3D ? colors.white : colors.textPrimary} size={11} weight="700">
            3D
          </DriverText>
        </Pressable>

        <Pressable accessibilityLabel="Zoom in" onPress={zoomIn} style={styles.controlBtn}>
          <MaterialCommunityIcons color={colors.textPrimary} name="plus" size={20} />
        </Pressable>

        <Pressable accessibilityLabel="Zoom out" onPress={zoomOut} style={styles.controlBtn}>
          <MaterialCommunityIcons color={colors.textPrimary} name="minus" size={20} />
        </Pressable>

        <Pressable accessibilityLabel="Recenter" onPress={recenter} style={styles.controlBtn}>
          <MaterialCommunityIcons color={colors.primary} name="crosshairs-gps" size={18} />
        </Pressable>
      </View>

      <View style={styles.attribution}>
        <DriverText color={colors.textSecondary} size={9}>
          © OpenStreetMap · Geoapify
        </DriverText>
      </View>
    </View>
  );
}

function RideMarker({ coordinate, icon, id, tone }: { coordinate: Coordinate; icon: string; id: string; tone: string }) {
  return (
    <Marker anchor="bottom" id={id} lngLat={[coordinate.longitude, coordinate.latitude]}>
      <View style={[styles.marker, { backgroundColor: tone }]}>
        <MaterialCommunityIcons color={colors.white} name={icon} size={18} />
      </View>
    </Marker>
  );
}

function bounds(points: Coordinate[]): [number, number, number, number] {
  const xs = points.map(point => point.longitude);
  const ys = points.map(point => point.latitude);
  return [Math.min(...xs), Math.min(...ys), Math.max(...xs), Math.max(...ys)];
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
  attribution: {
    backgroundColor: 'rgba(255,255,255,0.88)',
    bottom: 3,
    paddingHorizontal: 4,
    position: 'absolute',
    right: 3,
  },
});
