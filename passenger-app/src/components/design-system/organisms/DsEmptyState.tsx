import type { ReactNode } from 'react';
import { StyleSheet, View } from 'react-native';

import { colors, spacing } from '../../../theme';
import { DsButton } from '../atoms/DsButton';
import { DsText } from '../atoms/DsText';

type DsEmptyStateProps = { title: string; description?: string; illustration?: ReactNode; actionLabel?: string; onAction?: () => void };

/** Centre-aligned no-data organism with an optional illustration and recovery action. */
export function DsEmptyState({ title, description, illustration, actionLabel, onAction }: DsEmptyStateProps) {
  return <View accessibilityRole="summary" style={styles.container}>{illustration}{<DsText variant="h2" style={styles.title}>{title}</DsText>}{description && <DsText color={colors.textSecondary} style={styles.description}>{description}</DsText>}{actionLabel && onAction && <DsButton label={actionLabel} onPress={onAction} size="medium" />}</View>;
}

const styles = StyleSheet.create({ container: { alignItems: 'center', gap: spacing.md, justifyContent: 'center', padding: spacing.xxxl }, title: { textAlign: 'center' }, description: { textAlign: 'center' } });
