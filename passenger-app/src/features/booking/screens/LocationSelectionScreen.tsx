import { useEffect, useRef, useState } from 'react';
import { ActivityIndicator, Pressable, SafeAreaView, ScrollView, StyleSheet, TextInput, View } from 'react-native';
import { LocationManager } from '@maplibre/maplibre-react-native';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';

import { DsButton, DsCard, DsText } from '../../../components/design-system';
import { AppPageHeader } from '../../../components/navigation/AppPageHeader';
import { colors, radius, spacing, typography } from '../../../theme';
import { VirgoMap } from '../../maps/components/VirgoMap';
import { mapService } from '../../maps/services/mapService';
import { bookingApi, type LocationOption } from '../data/bookingApi';

type Props = { title: string; onBack: () => void; onMenuPress: () => void; onSelected: (location: LocationOption) => void | Promise<void>; scope?: 'local' | 'outstation' };

export function LocationSelectionScreen({ title, onBack, onMenuPress, onSelected, scope = 'local' }: Props) {
  const [query, setQuery] = useState('');
  const [catalogLocations, setCatalogLocations] = useState<LocationOption[]>([]);
  const [locations, setLocations] = useState<LocationOption[]>([]);
  const [selected, setSelected] = useState<LocationOption | null>(null);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState(scope === 'outstation' ? 'Search landmarks, cities, districts, or place a pin anywhere in India.' : 'Search or pin any location within 150 km of Imphal.');
  const skipNextSearch = useRef(false);

  useEffect(() => {
    if (scope === 'local') {
      bookingApi.locations()
        .then(catalog => {
          setCatalogLocations(catalog);
          setLocations(catalog);
        })
        .catch(() => {
          // If network fetch fails, fallback search is handled gracefully
        });
    }
  }, [scope]);

  const selectCoordinates = async (latitude: number, longitude: number, progressMessage: string) => {
    setLoading(true); setMessage(progressMessage);
    try {
      const place = await mapService.reverse(latitude, longitude, scope);
      skipNextSearch.current = true;
      setSelected(place); setQuery(place.name); setLocations([place]);
      setMessage('Pin selected. Confirm this location below.');
    } catch { setMessage(scope === 'outstation' ? 'That point could not be resolved. Choose another location within India.' : 'That point could not be resolved. Choose another point within Imphal.'); }
    finally { setLoading(false); }
  };

  useEffect(() => {
    if (skipNextSearch.current) { skipNextSearch.current = false; return; }
    const normalized = query.trim();
    if (normalized.length < 2) {
      setLocations(scope === 'local' ? catalogLocations : []);
      setLoading(false);
      setMessage(scope === 'outstation' ? 'Search landmarks, cities, districts, or place a pin anywhere in India.' : 'Search or pin any location within 150 km of Imphal.');
      return;
    }
    setLoading(true);
    const timer = setTimeout(() => {
      void mapService.search(normalized, scope)
        .then(results => {
          if (results.length > 0) {
            setLocations(results);
            setMessage('');
          } else if (scope === 'local' && catalogLocations.length > 0) {
            const localMatches = catalogLocations.filter(loc =>
              loc.name.toLowerCase().includes(normalized.toLowerCase()) ||
              loc.formatted_address.toLowerCase().includes(normalized.toLowerCase())
            );
            setLocations(localMatches);
            setMessage(localMatches.length ? '' : 'No matching place found.');
          } else {
            setLocations([]);
            setMessage('No matching place found.');
          }
        })
        .catch(() => {
          if (scope === 'local' && catalogLocations.length > 0) {
            const localMatches = catalogLocations.filter(loc =>
              loc.name.toLowerCase().includes(normalized.toLowerCase()) ||
              loc.formatted_address.toLowerCase().includes(normalized.toLowerCase())
            );
            setLocations(localMatches);
            setMessage(localMatches.length ? '' : 'No matching place found.');
          } else {
            setMessage('Place search is temporarily unavailable.');
          }
        })
        .finally(() => setLoading(false));
    }, 350);
    return () => clearTimeout(timer);
  }, [query, scope, catalogLocations]);

  const useCurrentLocation = async () => {
    setLoading(true); setMessage('Finding your current location…');
    try {
      if (!await LocationManager.requestPermissions()) { setMessage('Allow precise location to use your current position.'); return; }
      let position = await LocationManager.getCurrentPosition();
      if (!position) {
        position = await new Promise(resolve => {
          const listener = (next: NonNullable<typeof position>) => { clearTimeout(timeout); LocationManager.removeListener(listener); resolve(next); };
          const timeout = setTimeout(() => { LocationManager.removeListener(listener); resolve(undefined); }, 10_000);
          LocationManager.addListener(listener);
        });
      }
      if (!position) { setMessage('A GPS position is not available yet.'); return; }
      await selectCoordinates(position.coords.latitude, position.coords.longitude, 'Resolving your current address…');
    } catch { setMessage(scope === 'outstation' ? 'Current location could not be resolved.' : 'Current location is outside Imphal or could not be resolved.'); }
    finally { setLoading(false); }
  };
  const confirm = async () => { if (!selected) return; setSubmitting(true); try { await onSelected(selected); } catch { setMessage('Unable to save this location. Please try again.'); } finally { setSubmitting(false); } };

  return <SafeAreaView style={styles.safe}><View style={styles.screen}><ScrollView contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled"><AppPageHeader onBack={onBack} onMenuPress={onMenuPress} title={title}/><View style={styles.search}><MaterialCommunityIcons color={colors.primary} name="magnify" size={24}/><TextInput accessibilityLabel="Search locations" onChangeText={value => { setQuery(value); setSelected(null); }} placeholder="Search any pickup or destination" placeholderTextColor={colors.textTertiary} style={styles.input} value={query}/>{loading ? <ActivityIndicator color={colors.primary}/> : query ? <Pressable accessibilityLabel="Clear search" onPress={() => { setQuery(''); setSelected(null); setLocations(scope === 'local' ? catalogLocations : []); }}><MaterialCommunityIcons color={colors.textSecondary} name="close-circle" size={22}/></Pressable> : null}</View><Pressable accessibilityRole="button" onPress={() => void useCurrentLocation()} style={styles.current}><MaterialCommunityIcons color={colors.primary} name="crosshairs-gps" size={22}/><DsText color={colors.primary} variant="bodyMedium">Use my current location</DsText></Pressable><VirgoMap height={220} onMapPress={coordinate => void selectCoordinates(coordinate.latitude, coordinate.longitude, 'Finding the address at this pin…')} pickup={selected} showUserLocation/>{message ? <DsText color={colors.textSecondary}>{message}</DsText> : null}<View style={styles.results}>{locations.map((location, index) => { const identity = location.place_id ?? location.id ?? `${location.latitude}:${location.longitude}`; const active = (selected?.place_id ?? selected?.id) === (location.place_id ?? location.id); return <Pressable accessibilityRole="button" key={`${identity}:${index}`} onPress={() => { setSelected(location); setMessage('Location selected. Confirm it below.'); }}><DsCard elevated={active} style={[styles.item, active && styles.selectedItem]}><View style={styles.pin}><MaterialCommunityIcons color={colors.primary} name="map-marker" size={22}/></View><View style={styles.copy}><DsText variant="h3">{location.name}</DsText><DsText color={colors.textSecondary} variant="caption">{location.formatted_address}</DsText></View><MaterialCommunityIcons color={active ? colors.primary : colors.textTertiary} name={active ? 'check-circle' : 'circle-outline'} size={24}/></DsCard></Pressable>; })}</View></ScrollView><View style={styles.footer}><DsButton disabled={!selected} label="Use this location" loading={submitting} onPress={confirm}/></View></View></SafeAreaView>;
}

const styles = StyleSheet.create({ safe: { backgroundColor: colors.background, flex: 1 }, screen: { flex: 1 }, content: { gap: spacing.lg, padding: spacing.xl, paddingBottom: spacing.xxl }, search: { alignItems: 'center', backgroundColor: colors.surface, borderColor: colors.borderStrong, borderRadius: radius.md, borderWidth: 1, flexDirection: 'row', gap: spacing.sm, minHeight: 54, paddingHorizontal: spacing.md }, input: { ...typography.body, color: colors.textPrimary, flex: 1, paddingVertical: spacing.md }, current: { alignItems: 'center', alignSelf: 'flex-start', flexDirection: 'row', gap: spacing.sm, paddingVertical: spacing.xs }, results: { gap: spacing.md }, item: { alignItems: 'center', flexDirection: 'row', gap: spacing.md, padding: spacing.md }, selectedItem: { borderColor: colors.primary, borderWidth: 1.5, shadowColor: colors.primaryShadow, shadowOpacity: 1, shadowRadius: 12 }, pin: { alignItems: 'center', backgroundColor: colors.primarySoft, borderRadius: radius.pill, height: 42, justifyContent: 'center', width: 42 }, copy: { flex: 1, gap: spacing.xs }, footer: { backgroundColor: colors.surface, borderTopColor: colors.border, borderTopWidth: 1, padding: spacing.xl } });
