import { useState } from 'react';
import { Pressable, SafeAreaView, ScrollView, StyleSheet, View } from 'react-native';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';

import { AuthHeader } from '../../../components/auth/AuthHeader';
import { DsCard, DsText } from '../../../components/design-system';
import { colors, spacing } from '../../../theme';

type FaqScreenProps = { onBack: () => void };

const questions = [
  [
    'How do I book a ride?',
    'Enter your pickup and destination, compare available ride options, then confirm the fare shown before your ride starts.',
  ],
  [
    'How is my fare shown?',
    'The app shows an estimated fare before confirmation. It helps passengers in Tier 2 and Tier 3 cities make informed choices before booking.',
  ],
  [
    'How do you keep rides safe?',
    'Verified phone access, clear ride details, safety prompts, and in-app support help create a trusted experience for passengers and drivers.',
  ],
  [
    'What if I need help during a ride?',
    'Use Support or Emergency Contacts from the menu. Keep your location and ride information available when contacting assistance.',
  ],
  [
    'How does Virgo support drivers?',
    'Drivers receive clear ride requests, transparent earnings information, and quick access to support—designed for dependable work in Tier 2 and Tier 3 cities.',
  ],
] as const;

export function FaqScreen({ onBack }: FaqScreenProps) {
  const [openIndex, setOpenIndex] = useState<number | null>(0);
  return (
    <SafeAreaView style={styles.safeArea}>
      <AuthHeader onBack={onBack} />
      <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
        <DsText color={colors.primary} variant="display" style={styles.title}>
          How can we help?
        </DsText>
        <DsText color={colors.textSecondary} style={styles.subtitle}>
          Simple, secure, and built for everyday travel.
        </DsText>
        <DsCard elevated style={styles.audienceCard}>
          <MaterialCommunityIcons color={colors.primary} name="map-marker-radius" size={30} />
          <View style={styles.audienceCopy}>
            <DsText color={colors.primary} variant="h3">
              Built for Tier 2 & Tier 3 Cities of India
            </DsText>
            <DsText color={colors.textSecondary}>
              Reliable local travel for passengers, and fair, clear opportunities for drivers.
            </DsText>
          </View>
        </DsCard>
        <DsText variant="h2">Frequently asked questions</DsText>
        <View style={styles.questionList}>
          {questions.map(([question, answer], index) => (
            <FaqItem
              answer={answer}
              isOpen={openIndex === index}
              key={question}
              onPress={() => setOpenIndex(openIndex === index ? null : index)}
              question={question}
            />
          ))}
        </View>
        <DsCard style={styles.supportCard}>
          <MaterialCommunityIcons color={colors.success} name="shield-check-outline" size={28} />
          <View style={styles.supportCopy}>
            <DsText variant="bodyMedium">Trust matters to us</DsText>
            <DsText color={colors.textSecondary} variant="caption">
              We are building a transparent, dependable service for every ride.
            </DsText>
          </View>
        </DsCard>
      </ScrollView>
    </SafeAreaView>
  );
}

function FaqItem({
  question,
  answer,
  isOpen,
  onPress,
}: {
  question: string;
  answer: string;
  isOpen: boolean;
  onPress: () => void;
}) {
  return (
    <DsCard style={styles.questionCard}>
      <Pressable accessibilityRole="button" onPress={onPress} style={styles.question}>
        <DsText style={styles.questionText} variant="bodyMedium">
          {question}
        </DsText>
        <MaterialCommunityIcons
          color={colors.primary}
          name={isOpen ? 'chevron-up' : 'chevron-down'}
          size={24}
        />
      </Pressable>
      {isOpen ? (
        <DsText color={colors.textSecondary} style={styles.answer}>
          {answer}
        </DsText>
      ) : null}
    </DsCard>
  );
}

const styles = StyleSheet.create({
  answer: { paddingTop: spacing.md },
  audienceCard: {
    alignItems: 'center',
    backgroundColor: colors.primarySoft,
    borderColor: colors.primary,
    flexDirection: 'row',
    gap: spacing.md,
  },
  audienceCopy: { flex: 1, gap: spacing.xs },
  content: { gap: spacing.lg, padding: spacing.xl, paddingBottom: spacing.massive },
  question: { alignItems: 'center', flexDirection: 'row', gap: spacing.md },
  questionCard: { padding: spacing.lg },
  questionList: { gap: spacing.md },
  questionText: { flex: 1 },
  safeArea: { backgroundColor: colors.surface, flex: 1 },
  subtitle: { marginTop: -spacing.md, textAlign: 'center' },
  supportCard: {
    alignItems: 'center',
    backgroundColor: colors.successSoft,
    flexDirection: 'row',
    gap: spacing.md,
  },
  supportCopy: { flex: 1, gap: spacing.xs },
  title: { textAlign: 'center' },
});
