import { ActivityIndicator, SafeAreaView, ScrollView, StyleSheet, View } from 'react-native';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';

import { DriverPageHeader } from '../../../components/DriverPageHeader';
import { DriverCard } from '../../../components/DriverCard';
import { DriverText } from '../../../components/DriverText';
import { colors, spacing } from '../../../theme';
import { useDriverDashboard } from '../../dashboard/hooks/useDriverDashboard';

export function DriverEarningsScreen({ onBack }: { onBack: () => void }) {
  const { dashboard, isLoading } = useDriverDashboard();
  return <SafeAreaView style={styles.safe}><DriverPageHeader onBack={onBack} title="Earnings"/><ScrollView contentContainerStyle={styles.content}>{isLoading || !dashboard ? <ActivityIndicator color={colors.primary} size="large"/> : <><DriverCard style={styles.total}><DriverText color={colors.white}>This month</DriverText><DriverText color={colors.white} size={34} weight="700">{rupees(dashboard.month_earnings_paise)}</DriverText><DriverText color={colors.white}>{dashboard.month_completed_rides} completed rides</DriverText></DriverCard><DriverText size={22} weight="700">Earnings breakdown</DriverText><DriverCard style={styles.breakdown}><Metric icon="calendar-today" label="Today" value={rupees(dashboard.today_earnings_paise)}/><Metric icon="car-check" label="Completed rides today" value={String(dashboard.today_completed_rides)}/><Metric icon="wallet-outline" label="Monthly earnings" value={rupees(dashboard.month_earnings_paise)}/></DriverCard><DriverCard style={styles.notice}><MaterialCommunityIcons color={colors.primary} name="information-outline" size={24}/><DriverText color={colors.textSecondary} style={styles.noticeText}>Final fares from completed rides are added here automatically.</DriverText></DriverCard></>}</ScrollView></SafeAreaView>;
}
function Metric({ icon, label, value }: { icon: string; label: string; value: string }) { return <View style={styles.metric}><MaterialCommunityIcons color={colors.primary} name={icon} size={24}/><View style={styles.metricCopy}><DriverText color={colors.textSecondary}>{label}</DriverText><DriverText color={colors.textPrimary} size={20} weight="700">{value}</DriverText></View></View>; }
function rupees(paise: number) { return `₹${Math.round(paise / 100).toLocaleString('en-IN')}`; }
const styles = StyleSheet.create({ safe: { backgroundColor: colors.background, flex: 1 }, content: { gap: spacing.lg, padding: spacing.xl, paddingBottom: spacing.massive }, total: { backgroundColor: colors.primary, gap: spacing.sm, padding: spacing.xl }, breakdown: { gap: spacing.lg, padding: spacing.lg }, metric: { alignItems: 'center', flexDirection: 'row', gap: spacing.md }, metricCopy: { flex: 1, gap: spacing.xxs }, notice: { alignItems: 'center', backgroundColor: colors.primarySoft, flexDirection: 'row', gap: spacing.sm, padding: spacing.md }, noticeText: { flex: 1 } });
