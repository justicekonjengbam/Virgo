import { Pressable, StyleSheet, View } from 'react-native';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';

import { DsCard, DsText } from '../../../components/design-system';
import { colors, spacing } from '../../../theme';
import type { LocationOption } from '../../booking/data/bookingApi';

/** Pickup and destination selector used on the Passenger home screen. */
export function LocationCard({ pickup, destination, onPickupPress, onDestinationPress }: { pickup: LocationOption | null; destination: LocationOption | null; onPickupPress: () => void; onDestinationPress: () => void }) {
  return (
    <DsCard elevated style={styles.card}>
      <View style={styles.pinColumn}>
        <MaterialCommunityIcons color={colors.primary} name="map-marker" size={28} />
        <View style={styles.connector} />
        <MaterialCommunityIcons color={colors.textTertiary} name="map-marker" size={28} />
      </View>
      <View style={styles.locations}>
        <Pressable accessibilityRole="button" onPress={onPickupPress} style={styles.locationPressable}>
        <DsText color={colors.textTertiary} variant="caption">Pickup Location</DsText>
        <DsText numberOfLines={1} variant="h3">{pickup?.name ?? 'Choose pickup'}</DsText>
        </Pressable>
        <View style={styles.divider} />
        <Pressable accessibilityRole="button" onPress={onDestinationPress} style={styles.locationPressable}>
        <DsText color={colors.textTertiary} variant="caption">Destination</DsText>
        <DsText color={destination ? colors.textPrimary : colors.textTertiary} numberOfLines={1} variant="h3">{destination?.name ?? 'Where to?'}</DsText>
        </Pressable>
      </View>
      <MaterialCommunityIcons color={colors.primary} name="chevron-right" size={26} />
    </DsCard>
  );
}

const styles = StyleSheet.create({
  card: { alignItems: 'center', flexDirection: 'row', gap: spacing.md, padding: spacing.lg },
  connector: { backgroundColor: colors.borderStrong, height: 22, marginVertical: -2, width: 1 },
  divider: { backgroundColor: colors.border, height: 1, marginVertical: spacing.sm },
  locations: { flex: 1 },
  locationPressable: { minHeight: 42, justifyContent: 'center' },
  pinColumn: { alignItems: 'center' },
});
