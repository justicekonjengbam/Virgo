import { Alert, Linking, SafeAreaView, ScrollView, StyleSheet, View } from 'react-native';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';

import { DsButton, DsCard, DsText } from '../../../components/design-system';
import { AppPageHeader } from '../../../components/navigation/AppPageHeader';
import { colors, radius, spacing } from '../../../theme';

type InstantRideScreenProps = { onBack: () => void; onMenuPress: () => void };

const supportNumber = '+916009060341';
const bookingDetails = [
  ['Pickup location', 'Tell us where you would like the driver to meet you.'],
  ['Drop location', 'Share your destination with the support executive.'],
  ['Ride time', 'Specify whether you need the ride now or at a later time.'],
];

/** Manual ride-booking path for passengers who prefer to arrange a ride with Virgo Support. */
export function InstantRideScreen({ onBack, onMenuPress }: InstantRideScreenProps) {
  const callSupport = async () => {
    const phoneUrl = `tel:${supportNumber}`;
    const supported = await Linking.canOpenURL(phoneUrl);
    if (!supported) {
      Alert.alert('Calling unavailable', 'This device cannot start a phone call. Please call +91 6009060341 from your phone.');
      return;
    }
    await Linking.openURL(phoneUrl);
  };

  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
        <AppPageHeader onBack={onBack} onMenuPress={onMenuPress} title="Book instant ride" />
        <DsCard elevated style={styles.hero}>
          <View style={styles.heroIcon}>
            <MaterialCommunityIcons color={colors.primary} name="headset" size={34} />
          </View>
          <View style={styles.heroCopy}>
            <DsText variant="h2">Book with support</DsText>
            <DsText color={colors.textSecondary}>
              A Virgo executive will arrange the ride and coordinate the driver for you.
            </DsText>
          </View>
        </DsCard>

        <View style={styles.section}>
          <DsText variant="h3">Keep these details ready</DsText>
          <DsText color={colors.textSecondary}>
            This helps our support team book your ride accurately and quickly.
          </DsText>
        </View>

        <View style={styles.details}>
          {bookingDetails.map(([title, description], index) => (
            <DsCard elevated key={title} style={styles.detailCard}>
              <View style={styles.step}><DsText color={colors.white} variant="label">{index + 1}</DsText></View>
              <View style={styles.detailCopy}>
                <DsText variant="bodyMedium">{title}</DsText>
                <DsText color={colors.textSecondary} variant="caption">{description}</DsText>
              </View>
            </DsCard>
          ))}
        </View>

        <DsCard style={styles.note}>
          <MaterialCommunityIcons color={colors.primary} name="information-outline" size={24} />
          <DsText color={colors.textSecondary} style={styles.noteCopy} variant="caption">
            Support confirms the available vehicle, estimated fare, and driver details during the call.
          </DsText>
        </DsCard>

        <DsButton accessibilityLabel="Call +91 6009060341" label="Call +91 6009060341" leading={<MaterialCommunityIcons color={colors.white} name="phone" size={20} />} onPress={() => void callSupport()} />
        <DsText color={colors.textTertiary} style={styles.phone} variant="caption">+91 6009060341 · Calls may be charged by your network provider.</DsText>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { backgroundColor: colors.background, flex: 1 },
  content: { gap: spacing.lg, padding: spacing.xl, paddingBottom: spacing.massive },
  hero: { alignItems: 'center', flexDirection: 'row', gap: spacing.md, padding: spacing.lg },
  heroIcon: { alignItems: 'center', backgroundColor: colors.primarySoft, borderColor: colors.primary, borderRadius: radius.md, borderWidth: 1, height: 64, justifyContent: 'center', width: 64 },
  heroCopy: { flex: 1, gap: spacing.xxs },
  section: { gap: spacing.xxs },
  details: { gap: spacing.md },
  detailCard: { alignItems: 'center', flexDirection: 'row', gap: spacing.md, padding: spacing.md },
  step: { alignItems: 'center', backgroundColor: colors.primary, borderRadius: radius.pill, height: 30, justifyContent: 'center', width: 30 },
  detailCopy: { flex: 1, gap: spacing.xxs },
  note: { alignItems: 'flex-start', backgroundColor: colors.primarySoft, flexDirection: 'row', gap: spacing.sm, padding: spacing.md },
  noteCopy: { flex: 1 },
  phone: { textAlign: 'center' },
});
