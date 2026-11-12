import { useEffect, useMemo, useState } from 'react';
import { StyleSheet, View } from 'react-native';
import { Camera, GeoJSONSource, Layer, Map, Marker, UserLocation } from '@maplibre/maplibre-react-native';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';

import { DsLoading, DsText } from '../../../components/design-system';
import { colors, radius, spacing } from '../../../theme';
import { mapService } from '../services/mapService';

type Coordinate = { latitude: number; longitude: number };
type Props = { pickup?: Coordinate | null; destination?: Coordinate | null; driver?: Coordinate | null; route?: GeoJSON.Geometry | null; showUserLocation?: boolean; height?: number; onMapPress?: (coordinate: Coordinate) => void };

export function VirgoMap({ pickup, destination, driver, route, showUserLocation = false, height = 240, onMapPress }: Props) {
  const [styleUrl, setStyleUrl] = useState<string | null>(null);
  const [error, setError] = useState(false);
  useEffect(() => { void mapService.configuration().then(value => setStyleUrl(value.style_url)).catch(() => setError(true)); }, []);
  const points = [pickup, destination, driver].filter(Boolean) as Coordinate[];
  const initialViewState = useMemo(() => points.length > 1 ? { bounds: bounds(points), padding: { top: 48, right: 48, bottom: 48, left: 48 } } : { center: points[0] ? [points[0].longitude, points[0].latitude] as [number, number] : [93.9368, 24.8170] as [number, number], zoom: points[0] ? 14 : 10 }, [destination?.latitude, destination?.longitude, driver?.latitude, driver?.longitude, pickup?.latitude, pickup?.longitude]);
  if (error) return <View style={[styles.fallback, { height }]}><MaterialCommunityIcons color={colors.textTertiary} name="map-off-outline" size={32} /><DsText color={colors.textSecondary}>Map is unavailable</DsText></View>;
  if (!styleUrl) return <View style={[styles.fallback, { height }]}><DsLoading label="Loading map…" /></View>;
  return <View style={[styles.container, { height }]}><Map mapStyle={styleUrl} onDidFailLoadingMap={() => setError(true)} onPress={event => { const [longitude, latitude] = event.nativeEvent.lngLat; onMapPress?.({ latitude, longitude }); }} style={styles.map}><Camera initialViewState={initialViewState} />{showUserLocation ? <UserLocation accuracy animated heading /> : null}{route ? <GeoJSONSource data={{ type: 'Feature', properties: {}, geometry: route }} id="ride-route"><Layer id="ride-route-line" paint={{ 'line-color': colors.primary, 'line-width': 5, 'line-opacity': 0.88 }} type="line" /></GeoJSONSource> : null}{pickup ? <MapMarker coordinate={pickup} icon="map-marker" id="pickup" tone={colors.primary} /> : null}{destination ? <MapMarker coordinate={destination} icon="map-marker-check" id="destination" tone={colors.success} /> : null}{driver ? <MapMarker coordinate={driver} icon="car" id="driver" tone={colors.textPrimary} /> : null}</Map>{onMapPress ? <View pointerEvents="none" style={styles.mapHint}><MaterialCommunityIcons color={colors.primary} name="gesture-tap" size={16} /><DsText color={colors.primary} style={styles.hintText}>Tap map to place pin</DsText></View> : null}<View pointerEvents="none" style={styles.attribution}><DsText color={colors.textSecondary} style={styles.attributionText}>© OpenStreetMap · Geoapify</DsText></View></View>;
}

function MapMarker({ coordinate, icon, id, tone }: { coordinate: Coordinate; icon: string; id: string; tone: string }) { return <Marker anchor="bottom" id={id} lngLat={[coordinate.longitude, coordinate.latitude]}><View style={[styles.marker, { backgroundColor: tone }]}><MaterialCommunityIcons color={colors.white} name={icon} size={18} /></View></Marker>; }
function bounds(points: Coordinate[]): [number, number, number, number] { const longitudes = points.map(point => point.longitude); const latitudes = points.map(point => point.latitude); return [Math.min(...longitudes), Math.min(...latitudes), Math.max(...longitudes), Math.max(...latitudes)]; }
const styles = StyleSheet.create({ container: { borderColor: colors.border, borderRadius: radius.lg, borderWidth: 1, overflow: 'hidden' }, map: { flex: 1 }, fallback: { alignItems: 'center', backgroundColor: colors.surfaceMuted, borderColor: colors.border, borderRadius: radius.lg, borderWidth: 1, gap: spacing.sm, justifyContent: 'center' }, marker: { alignItems: 'center', borderColor: colors.white, borderRadius: radius.pill, borderWidth: 2, height: 34, justifyContent: 'center', width: 34 }, mapHint: { alignItems: 'center', backgroundColor: 'rgba(255,255,255,0.94)', borderRadius: radius.pill, flexDirection: 'row', gap: spacing.xs, left: spacing.sm, paddingHorizontal: spacing.sm, paddingVertical: spacing.xs, position: 'absolute', top: spacing.sm }, hintText: { fontSize: 11, lineHeight: 14 }, attribution: { backgroundColor: 'rgba(255,255,255,0.88)', bottom: 3, paddingHorizontal: 4, position: 'absolute', right: 3 }, attributionText: { fontSize: 9, lineHeight: 12 } });

export const CabSureMap = VirgoMap;

