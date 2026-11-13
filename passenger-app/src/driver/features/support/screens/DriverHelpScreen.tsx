import { useEffect, useState } from 'react';
import { ActivityIndicator, Pressable, SafeAreaView, ScrollView, StyleSheet } from 'react-native';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';

import { DriverPageHeader } from '../../../components/DriverPageHeader';
import { DriverCard } from '../../../components/DriverCard';
import { DriverText } from '../../../components/DriverText';
import { colors, spacing } from '../../../theme';
import { driverMenuService, type DriverSupportArticle } from '../../dashboard/services/driverMenuService';

export function DriverHelpScreen({ onBack }: { onBack: () => void }) {
  const [articles, setArticles] = useState<DriverSupportArticle[] | null>(null);
  useEffect(() => { void driverMenuService.getSupport().then(setArticles).catch(() => setArticles([])); }, []);
  return <SafeAreaView style={styles.safe}><DriverPageHeader onBack={onBack} title="Help & Support"/><ScrollView contentContainerStyle={styles.content}><DriverText color={colors.primary} size={28} style={styles.title} weight="700">How can we help?</DriverText><DriverText color={colors.textSecondary} style={styles.subtitle}>Support for safe, dependable Driver experiences.</DriverText>{articles === null ? <ActivityIndicator color={colors.primary} size="large"/> : articles.map(article => <HelpItem article={article} key={article.id}/>)}</ScrollView></SafeAreaView>;
}

function HelpItem({ article }: { article: DriverSupportArticle }) { const [open, setOpen] = useState(false); return <DriverCard style={styles.card}><Pressable accessibilityRole="button" onPress={() => setOpen(value => !value)} style={styles.row}><DriverText style={styles.question} weight="600">{article.title}</DriverText><MaterialCommunityIcons color={colors.primary} name={open ? 'chevron-up' : 'chevron-down'} size={24}/></Pressable>{open ? <DriverText color={colors.textSecondary} style={styles.answer}>{article.body}</DriverText> : null}</DriverCard>; }
const styles = StyleSheet.create({ safe: { backgroundColor: colors.surface, flex: 1 }, content: { gap: spacing.md, padding: spacing.xl, paddingBottom: spacing.massive }, title: { textAlign: 'center' }, subtitle: { marginBottom: spacing.lg, textAlign: 'center' }, card: { padding: spacing.lg }, row: { alignItems: 'center', flexDirection: 'row', gap: spacing.md }, question: { flex: 1 }, answer: { marginTop: spacing.md } });
