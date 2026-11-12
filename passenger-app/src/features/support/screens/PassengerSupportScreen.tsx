import { SafeAreaView, ScrollView, StyleSheet, View } from 'react-native';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';
import { DsCard, DsText } from '../../../components/design-system';
import { AppPageHeader } from '../../../components/navigation/AppPageHeader';
import { colors, radius, spacing } from '../../../theme';
type PassengerSupportScreenProps = { onBack: () => void; onMenuPress: () => void };
const topics = [
  ['How do I request a ride?', 'Choose pickup, destination and vehicle, then confirm the fare.'],
  ['How are fares shown?', 'The estimated fare is shown before you confirm a ride.'],
  [
    'How does ride safety work?',
    'Emergency contacts and ride details are available from the app menu.',
  ],
  [
    'Who can use Virgo?',
    'Virgo – Happy Cabbing is designed for convenient and accessible transportation across Imphal and regional cities.',
  ],
  ['How can I get help?', 'Use this Support area or add emergency contacts for safety needs.'],
];
export function PassengerSupportScreen({ onBack, onMenuPress }: PassengerSupportScreenProps) {
  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.content}>
        <AppPageHeader onBack={onBack} onMenuPress={onMenuPress} title="Support" />
        <DsCard elevated style={styles.hero}>
          <View style={styles.heroIcon}>
            <MaterialCommunityIcons color={colors.primary} name="headphones" size={28} />
          </View>
          <View>
            <DsText variant="h3">We are here to help</DsText>
            <DsText color={colors.textSecondary}>
              Find answers to your questions.
            </DsText>
          </View>
        </DsCard>
        {topics.map(([question, answer]) => (
          <DsCard elevated key={question} style={styles.topic}>
            <DsText variant="bodyMedium">{question}</DsText>
            <DsText color={colors.textSecondary}>{answer}</DsText>
          </DsCard>
        ))}
      </ScrollView>
    </SafeAreaView>
  );
}
const styles = StyleSheet.create({
  safe: { backgroundColor: colors.background, flex: 1 },
  content: { gap: spacing.lg, padding: spacing.xl, paddingBottom: spacing.massive },
  hero: { alignItems: 'center', flexDirection: 'row', gap: spacing.md },
  heroIcon: {
    alignItems: 'center',
    backgroundColor: colors.primarySoft,
    borderColor: colors.primary,
    borderRadius: radius.sm,
    borderWidth: 1,
    height: 52,
    justifyContent: 'center',
    width: 52,
  },
  topic: { gap: spacing.sm },
});
