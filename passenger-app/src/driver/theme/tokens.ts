export const colors = {
  primary: '#952B7D',
  primaryPressed: '#7E2269',
  primarySoft: '#FBF2F8',
  primaryLight: '#F3D8EC',
  primaryShadow: 'rgba(149, 43, 125, 0.20)',
  background: '#FAF7FA',
  surface: '#FFFFFF',
  surfaceMuted: '#F7F2F6',
  textPrimary: '#1B141D',
  textSecondary: '#6B5E6E',
  textTertiary: '#9E91A1',
  border: '#ECE3EC',
  borderStrong: '#D6C5D6',
  success: '#1EA566',
  successSoft: '#EBF8F1',
  warning: '#E09310',
  warningSoft: '#FFF8EB',
  error: '#D93848',
  errorSoft: '#FDEEF0',
  info: '#952B7D',
  overlay: 'rgba(27, 20, 29, 0.52)',
  transparent: 'transparent',
  white: '#FFFFFF',
  black: '#000000',
  // Compatibility aliases used by the Driver screens.
  text: '#1B141D',
  danger: '#D93848',
  dangerSoft: '#FDEEF0',
} as const;

export const spacing = { xxs: 2, xs: 4, sm: 8, md: 12, lg: 16, xl: 20, xxl: 24, xxxl: 32, huge: 40, massive: 48 } as const;
export const radius = { none: 0, xs: 4, sm: 8, md: 12, lg: 16, xl: 20, pill: 999 } as const;
export const typography = {
  family: { regular: 'Poppins-Regular', medium: 'Poppins-Medium', semibold: 'Poppins-SemiBold', bold: 'Poppins-Bold' },
  display: { fontSize: 32, lineHeight: 42, fontFamily: 'Poppins-Bold' },
  h1: { fontSize: 24, lineHeight: 32, fontFamily: 'Poppins-SemiBold' },
  h2: { fontSize: 20, lineHeight: 28, fontFamily: 'Poppins-SemiBold' },
  h3: { fontSize: 18, lineHeight: 26, fontFamily: 'Poppins-SemiBold' },
  body: { fontSize: 14, lineHeight: 22, fontFamily: 'Poppins-Regular' },
  bodyMedium: { fontSize: 14, lineHeight: 22, fontFamily: 'Poppins-Medium' },
  label: { fontSize: 14, lineHeight: 20, fontFamily: 'Poppins-Medium' },
  caption: { fontSize: 12, lineHeight: 18, fontFamily: 'Poppins-Regular' },
} as const;
export const shadows = {
  card: { elevation: 2, shadowColor: colors.primaryShadow, shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.08, shadowRadius: 6 },
  raised: { elevation: 4, shadowColor: colors.primaryShadow, shadowOffset: { width: 0, height: 4 }, shadowOpacity: 0.12, shadowRadius: 10 },
  floating: { elevation: 8, shadowColor: colors.primaryShadow, shadowOffset: { width: 0, height: 8 }, shadowOpacity: 0.16, shadowRadius: 18 },
} as const;
