import { useEffect, useState } from 'react';
import { Linking, Pressable, SafeAreaView, ScrollView, StyleSheet, View } from 'react-native';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';

import { DsCard, DsEmptyState, DsLoading, DsText } from '../../../components/design-system';
import { AppPageHeader } from '../../../components/navigation/AppPageHeader';
import { colors, radius, spacing } from '../../../theme';
import { emergencyContactsApi, type EmergencyContact } from '../data/emergencyContactsApi';

type EmergencyContactsScreenProps = { onBack: () => void; onMenuPress: () => void };

export function EmergencyContactsScreen({ onBack, onMenuPress }: EmergencyContactsScreenProps) {
  const [contacts, setContacts] = useState<EmergencyContact[]>([]);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    void emergencyContactsApi
      .list()
      .then(setContacts)
      .catch(() => setError('Unable to load emergency contacts.'));
  }, []);
  if (error)
    return (
      <SafeAreaView style={styles.safe}>
        <DsEmptyState actionLabel="Back" onAction={onBack} title={error} />
      </SafeAreaView>
    );
  if (!contacts.length)
    return (
      <SafeAreaView style={styles.safe}>
        <DsLoading fullScreen label="Loading emergency contacts…" />
      </SafeAreaView>
    );
  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.content}>
        <AppPageHeader onBack={onBack} onMenuPress={onMenuPress} title="Emergency Contacts" />
        <DsCard elevated style={styles.notice}>
          <MaterialCommunityIcons color={colors.primary} name="shield-account-outline" size={28} />
          <DsText color={colors.textSecondary} style={styles.noticeCopy}>
            These trusted contacts will be notified during a future emergency flow.
          </DsText>
        </DsCard>
        {contacts.map((contact) => (
          <DsCard elevated key={contact.id} style={styles.contact}>
            <View style={styles.avatar}>
              <DsText color={colors.primary} variant="h2">
                {contact.name.charAt(0)}
              </DsText>
            </View>
            <View style={styles.contactCopy}>
              <DsText variant="h3">{contact.name}</DsText>
              <DsText color={colors.textSecondary}>
                {contact.relationship ?? 'Emergency contact'}
              </DsText>
              <DsText color={colors.textTertiary}>{contact.phone_number}</DsText>
            </View>
            <Pressable accessibilityLabel={`Call ${contact.name}`} onPress={() => void Linking.openURL(`tel:${contact.phone_number.replace(/[^0-9+]/g, '')}`)} style={styles.callButton}>
              <MaterialCommunityIcons color={colors.success} name="phone" size={21} />
            </Pressable>
          </DsCard>
        ))}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { backgroundColor: colors.background, flex: 1 },
  content: { gap: spacing.lg, padding: spacing.xl, paddingBottom: spacing.massive },
  notice: { alignItems: 'center', flexDirection: 'row', gap: spacing.md },
  noticeCopy: { flex: 1 },
  contact: { alignItems: 'center', flexDirection: 'row', gap: spacing.md },
  avatar: {
    alignItems: 'center',
    backgroundColor: colors.primarySoft,
    borderColor: colors.primary,
    borderRadius: radius.pill,
    borderWidth: 1,
    height: 48,
    justifyContent: 'center',
    width: 48,
  },
  contactCopy: { flex: 1, gap: spacing.xxs },
  callButton: { alignItems: 'center', borderColor: colors.success, borderRadius: radius.pill, borderWidth: 1, height: 44, justifyContent: 'center', width: 44 },
});
