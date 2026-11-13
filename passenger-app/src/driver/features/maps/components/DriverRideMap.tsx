import { useEffect, useMemo, useState } from 'react';
import { StyleSheet, View } from 'react-native';
import { Camera, GeoJSONSource, Layer, Map, Marker, UserLocation } from '@maplibre/maplibre-react-native';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';

import { DriverText } from '../../../components/DriverText';
import { colors, radius, spacing } from '../../../theme';
import { getMapConfiguration } from '../services/driverMapService';

type Coordinate = { latitude: number; longitude: number };
type Props = { pickup: Coordinate; destination: Coordinate; driver?: Coordinate | null; route?: GeoJSON.Geometry | null; height?: number };

export function DriverRideMap({ pickup, destination, driver, route, height = 300 }: Props) {
  const [styleUrl, setStyleUrl] = useState<string | null>(null);
  const [failed, setFailed] = useState(false);
  useEffect(() => { void getMapConfiguration().then(config => setStyleUrl(config.style_url)).catch(() => setFailed(true)); }, []);
  const points = useMemo(() => [pickup, destination, ...(driver ? [driver] : [])], [destination, driver, pickup]);
  const mapBounds = useMemo(() => bounds(points), [points]);
  if (failed || !styleUrl) return <View style={[styles.fallback, { height }]}>{failed ? <><MaterialCommunityIcons color={colors.textTertiary} name="map-off-outline" size={34}/><DriverText color={colors.textSecondary}>Map is unavailable</DriverText></> : <DriverText color={colors.textSecondary}>Loading map…</DriverText>}</View>;
  return <View style={[styles.container, { height }]}><Map mapStyle={styleUrl} onDidFailLoadingMap={() => setFailed(true)} style={styles.map}><Camera initialViewState={{ bounds: mapBounds, padding: { top: 48, right: 48, bottom: 48, left: 48 } }}/><UserLocation accuracy animated heading/>{route ? <GeoJSONSource data={{ type: 'Feature', properties: {}, geometry: route }} id="driver-route"><Layer id="driver-route-line" paint={{ 'line-color': colors.primary, 'line-width': 5, 'line-opacity': 0.88 }} type="line"/></GeoJSONSource> : null}<RideMarker coordinate={pickup} icon="map-marker" id="pickup" tone={colors.primary}/><RideMarker coordinate={destination} icon="map-marker-check" id="destination" tone={colors.success}/></Map><View style={styles.attribution}><DriverText color={colors.textSecondary} size={9}>© OpenStreetMap · Geoapify</DriverText></View></View>;
}

function RideMarker({ coordinate, icon, id, tone }: { coordinate: Coordinate; icon: string; id: string; tone: string }) { return <Marker anchor="bottom" id={id} lngLat={[coordinate.longitude, coordinate.latitude]}><View style={[styles.marker, { backgroundColor: tone }]}><MaterialCommunityIcons color={colors.white} name={icon} size={18}/></View></Marker>; }
function bounds(points: Coordinate[]): [number, number, number, number] { const xs = points.map(point => point.longitude); const ys = points.map(point => point.latitude); return [Math.min(...xs), Math.min(...ys), Math.max(...xs), Math.max(...ys)]; }
const styles = StyleSheet.create({ container: { borderColor: colors.border, borderRadius: radius.lg, borderWidth: 1, overflow: 'hidden' }, map: { flex: 1 }, fallback: { alignItems: 'center', backgroundColor: colors.surfaceMuted, borderColor: colors.border, borderRadius: radius.lg, borderWidth: 1, gap: spacing.sm, justifyContent: 'center' }, marker: { alignItems: 'center', borderColor: colors.white, borderRadius: radius.pill, borderWidth: 2, height: 34, justifyContent: 'center', width: 34 }, attribution: { backgroundColor: 'rgba(255,255,255,0.88)', bottom: 3, paddingHorizontal: 4, position: 'absolute', right: 3 } });
