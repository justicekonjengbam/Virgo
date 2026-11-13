import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator, type NativeStackScreenProps } from '@react-navigation/native-stack';

import { DriverLoginScreen } from '../features/auth/screens/DriverLoginScreen';
import { DriverOnboardingScreen } from '../features/auth/screens/DriverOnboardingScreen';
import { DriverSignupScreen } from '../features/auth/screens/DriverSignupScreen';
import { driverAuthService } from '../features/auth/services/driverAuthService';
import { DriverHomeScreen } from '../features/dashboard/screens/DriverHomeScreen';
import { DriverEarningsScreen } from '../features/earnings/screens/DriverEarningsScreen';
import { DriverTripHistoryScreen } from '../features/rides/screens/DriverTripHistoryScreen';
import { DriverSessionProvider } from '../features/dashboard/state/DriverSessionContext';
import { RideRequestScreen } from '../features/rides/screens/RideRequestScreen';
import { DriverActiveRideScreen } from '../features/rides/screens/DriverActiveRideScreen';
import { DriverOutstationScreen } from '../features/rides/screens/DriverOutstationScreen';
import { DriverSplashScreen } from '../features/splash/screens/DriverSplashScreen';
import { DriverHelpScreen } from '../features/support/screens/DriverHelpScreen';
import { DriverSettingsScreen } from '../features/profile/screens/DriverSettingsScreen';
import { DriverDocumentsScreen } from '../features/profile/screens/DriverDocumentsScreen';
import { useAppMode } from '../../context/AppModeContext';
import type { DriverStackParamList } from './types';

const Stack = createNativeStackNavigator<DriverStackParamList>();

function SplashRoute({ navigation }: NativeStackScreenProps<DriverStackParamList, 'Splash'>) {
  return <DriverSplashScreen onContinue={() => navigation.replace('Login')} />;
}

function LoginRoute({ navigation }: NativeStackScreenProps<DriverStackParamList, 'Login'>) {
  return <DriverLoginScreen onAuthenticated={session => navigation.reset({ index: 0, routes: [{ name: session.driver.onboarding_completed ? 'Home' : 'Onboarding' }] })} onBack={() => navigation.replace('Splash')} onHelp={() => navigation.navigate('Help')} onSignup={() => navigation.replace('Signup')} />;
}

function SignupRoute({ navigation }: NativeStackScreenProps<DriverStackParamList, 'Signup'>) {
  return <DriverSignupScreen onAuthenticated={session => navigation.reset({ index: 0, routes: [{ name: session.driver.onboarding_completed ? 'Home' : 'Onboarding' }] })} onBack={() => navigation.replace('Login')} onHelp={() => navigation.navigate('Help')} onLogin={() => navigation.replace('Login')} />;
}

function HelpRoute({ navigation }: NativeStackScreenProps<DriverStackParamList, 'Help'>) {
  return <DriverHelpScreen onBack={() => navigation.goBack()} />;
}

function OnboardingRoute({ navigation }: NativeStackScreenProps<DriverStackParamList, 'Onboarding'>) {
  return <DriverOnboardingScreen onCompleted={() => navigation.reset({ index: 0, routes: [{ name: 'Home' }] })} />;
}

function HomeRoute({ navigation }: NativeStackScreenProps<DriverStackParamList, 'Home'>) {
  const { switchToPassenger } = useAppMode();
  const logout = async () => {
    await driverAuthService.clearSession();
    navigation.reset({ index: 0, routes: [{ name: 'Login' }] });
  };
  return <DriverHomeScreen onLogout={() => void logout()} onOpenActiveRide={() => navigation.navigate('ActiveRide')} onOpenDocuments={() => navigation.navigate('Documents')} onOpenEarnings={() => navigation.navigate('Earnings')} onOpenHelp={() => navigation.navigate('Help')} onOpenOutstation={() => navigation.navigate('Outstation')} onOpenRequest={() => navigation.navigate('RideRequest')} onOpenSettings={() => navigation.navigate('Settings')} onOpenTripHistory={() => navigation.navigate('TripHistory')} onSwitchToPassenger={switchToPassenger} />;
}

function RideRequestRoute({ navigation }: NativeStackScreenProps<DriverStackParamList, 'RideRequest'>) {
  return <RideRequestScreen onAccepted={() => navigation.replace('ActiveRide')} onBack={() => navigation.goBack()} />;
}

function ActiveRideRoute({ navigation }: NativeStackScreenProps<DriverStackParamList, 'ActiveRide'>) { return <DriverActiveRideScreen onBack={() => navigation.goBack()} onFinished={() => navigation.reset({ index: 0, routes: [{ name: 'Home' }] })}/>; }

function EarningsRoute({ navigation }: NativeStackScreenProps<DriverStackParamList, 'Earnings'>) {
  return <DriverEarningsScreen onBack={() => navigation.goBack()} />;
}

function TripHistoryRoute({ navigation }: NativeStackScreenProps<DriverStackParamList, 'TripHistory'>) {
  return <DriverTripHistoryScreen onBack={() => navigation.goBack()} />;
}

function OutstationRoute({ navigation }: NativeStackScreenProps<DriverStackParamList, 'Outstation'>) { return <DriverOutstationScreen onBack={() => navigation.goBack()}/>; }

function SettingsRoute({ navigation }: NativeStackScreenProps<DriverStackParamList, 'Settings'>) {
  const { switchToPassenger } = useAppMode();
  return <DriverSettingsScreen onBack={() => navigation.goBack()} onSwitchToPassenger={switchToPassenger} />;
}

function DocumentsRoute({ navigation }: NativeStackScreenProps<DriverStackParamList, 'Documents'>) {
  return <DriverDocumentsScreen onBack={() => navigation.goBack()} />;
}

export function DriverNavigator() {
  return <DriverSessionProvider><NavigationContainer><Stack.Navigator initialRouteName="Splash" screenOptions={{ animation: 'slide_from_right', headerShown: false }}><Stack.Screen component={SplashRoute} name="Splash"/><Stack.Screen component={LoginRoute} name="Login"/><Stack.Screen component={SignupRoute} name="Signup"/><Stack.Screen component={HelpRoute} name="Help"/><Stack.Screen component={OnboardingRoute} name="Onboarding"/><Stack.Screen component={HomeRoute} name="Home"/><Stack.Screen component={RideRequestRoute} name="RideRequest"/><Stack.Screen component={ActiveRideRoute} name="ActiveRide"/><Stack.Screen component={EarningsRoute} name="Earnings"/><Stack.Screen component={TripHistoryRoute} name="TripHistory"/><Stack.Screen component={OutstationRoute} name="Outstation"/><Stack.Screen component={SettingsRoute} name="Settings"/><Stack.Screen component={DocumentsRoute} name="Documents"/></Stack.Navigator></NavigationContainer></DriverSessionProvider>;
}
