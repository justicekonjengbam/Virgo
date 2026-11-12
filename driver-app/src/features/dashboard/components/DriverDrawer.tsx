import { Component } from 'react';
import { Animated, Dimensions, Modal, Pressable, SafeAreaView, StyleSheet, View } from 'react-native';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';

import { DriverText } from '../../../components/DriverText';
import { colors, radius, shadows, spacing } from '../../../theme';

type DriverDrawerProps = { onClose: () => void; onOpenDocuments: () => void; onOpenEarnings: () => void; onOpenHelp: () => void; onOpenOutstation: () => void; onOpenRideRequest: () => void; onOpenSettings: () => void; onOpenTripHistory: () => void; onSignOut: () => void; visible: boolean };
const drawerWidth = Math.min(Dimensions.get('window').width * 0.82, 340);
const menuItems = [
  ['Dashboard', 'view-dashboard-outline'],
  ['Ride requests', 'car-clock'],
  ['Earnings', 'wallet-outline'],
  ['Trip history', 'history'],
  ['Outstation schedule', 'road-variant'],
  ['Documents & compliance', 'file-document-outline'],
  ['Settings', 'cog-outline'],
  ['Help & support', 'headphones'],
] as const;

/** Left navigation drawer for the Driver app. Every visible destination has a working route. */
export class DriverDrawer extends Component<DriverDrawerProps> {
  private readonly translateX = new Animated.Value(-drawerWidth);

  componentDidMount() {
    if (this.props.visible) this.open();
  }

  componentDidUpdate(previousProps: DriverDrawerProps) {
    if (!previousProps.visible && this.props.visible) this.open();
  }

  private open() {
    this.translateX.setValue(-drawerWidth);
    Animated.timing(this.translateX, { toValue: 0, duration: 220, useNativeDriver: true }).start();
  }

  private dismiss = (afterClose?: () => void) => {
    Animated.timing(this.translateX, { toValue: -drawerWidth, duration: 180, useNativeDriver: true }).start(({ finished }) => {
      if (!finished) return;
      this.props.onClose();
      afterClose?.();
    });
  };

  private choose = (label: string) => {
    if (label === 'Dashboard') return this.dismiss();
    if (label === 'Ride requests') return this.dismiss(this.props.onOpenRideRequest);
    if (label === 'Earnings') return this.dismiss(this.props.onOpenEarnings);
    if (label === 'Trip history') return this.dismiss(this.props.onOpenTripHistory);
    if (label === 'Outstation schedule') return this.dismiss(this.props.onOpenOutstation);
    if (label === 'Documents & compliance') return this.dismiss(this.props.onOpenDocuments);
    if (label === 'Settings') return this.dismiss(this.props.onOpenSettings);
    if (label === 'Help & support') return this.dismiss(this.props.onOpenHelp);
  };

  render() {
    const { visible } = this.props;
    return <Modal animationType="none" onRequestClose={() => this.dismiss()} transparent visible={visible}><View style={styles.overlay}><Animated.View style={[styles.drawerAnimation, { transform: [{ translateX: this.translateX }] }]}><SafeAreaView style={styles.drawer}><View style={styles.topBar}><Pressable accessibilityLabel="Close menu" onPress={() => this.dismiss()} style={styles.closeButton}><MaterialCommunityIcons color={colors.primary} name="chevron-left" size={30}/></Pressable><DriverText color={colors.primary} size={20} weight="700">Virgo Driver</DriverText><View style={styles.spacer}/></View><View style={styles.menu}>{menuItems.map(([label, icon], index) => <Pressable accessibilityRole="button" key={label} onPress={() => this.choose(label)} style={[styles.menuItem, index === 0 && styles.activeItem]}><MaterialCommunityIcons color={index === 0 ? colors.primary : colors.textSecondary} name={icon} size={25}/><DriverText color={index === 0 ? colors.primary : colors.textSecondary} weight={index === 0 ? '700' : '400'}>{label}</DriverText></Pressable>)}</View><View style={styles.footer}><Pressable accessibilityRole="button" onPress={() => this.dismiss(this.props.onSignOut)} style={styles.logout}><MaterialCommunityIcons color={colors.danger} name="logout" size={25}/><DriverText color={colors.danger}>Sign out</DriverText></Pressable><DriverText color={colors.textTertiary} size={13}>Virgo Driver • Happy Cabbing • v0.0.1</DriverText></View></SafeAreaView></Animated.View><Pressable accessibilityLabel="Close menu overlay" onPress={() => this.dismiss()} style={styles.backdrop}/></View></Modal>;
  }
}

const styles = StyleSheet.create({
  overlay: { backgroundColor: colors.overlay, flex: 1, flexDirection: 'row' }, drawerAnimation: { width: drawerWidth }, drawer: { ...shadows.floating, backgroundColor: colors.surface, minHeight: '100%', paddingHorizontal: spacing.xl, width: '100%' }, topBar: { alignItems: 'center', flexDirection: 'row', justifyContent: 'space-between', paddingTop: spacing.md }, closeButton: { alignItems: 'center', borderColor: colors.primary, borderRadius: radius.md, borderWidth: 1, height: 48, justifyContent: 'center', width: 48 }, spacer: { width: 48 }, menu: { gap: spacing.xs, marginTop: spacing.xxl }, menuItem: { alignItems: 'center', borderRadius: radius.md, flexDirection: 'row', gap: spacing.md, minHeight: 58, paddingHorizontal: spacing.md }, activeItem: { backgroundColor: colors.primarySoft }, footer: { gap: spacing.xl, marginTop: 'auto', paddingBottom: spacing.xxl }, logout: { alignItems: 'center', flexDirection: 'row', gap: spacing.md, minHeight: 48, paddingHorizontal: spacing.md }, backdrop: { flex: 1 },
});
