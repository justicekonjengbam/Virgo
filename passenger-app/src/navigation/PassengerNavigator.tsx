import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from 'react';
import { NavigationContainer, type NavigationProp } from '@react-navigation/native';
import { createNativeStackNavigator, type NativeStackScreenProps } from '@react-navigation/native-stack';

import { LoginScreen } from '../features/auth/screens/LoginScreen';
import { SignupScreen } from '../features/auth/screens/SignupScreen';
import { authService } from '../features/auth/services/authService';
import { BookingStatusScreen } from '../features/booking/screens/BookingStatusScreen';
import { FareEstimateScreen } from '../features/booking/screens/FareEstimateScreen';
import { LocationSelectionScreen } from '../features/booking/screens/LocationSelectionScreen';
import type { LocationOption, RideStatus } from '../features/booking/data/bookingApi';
import { bookingApi } from '../features/booking/data/bookingApi';
import { EmergencyContactsScreen } from '../features/emergency/screens/EmergencyContactsScreen';
import { HomeDrawer, type DrawerDestination } from '../features/home/components/HomeDrawer';
import { PassengerHomeScreen } from '../features/home/screens/PassengerHomeScreen';
import { MyRidesScreen } from '../features/rides/screens/MyRidesScreen';
import { SplashScreen } from '../features/splash/screens/SplashScreen';
import { PassengerSupportScreen } from '../features/support/screens/PassengerSupportScreen';
import { FaqScreen } from '../features/support/screens/FaqScreen';
import { InstantRideScreen } from '../features/support/screens/InstantRideScreen';
import { OutstationBookingScreen } from '../features/outstation/screens/OutstationBookingScreen';
import { NotificationsScreen } from '../features/notifications/screens/NotificationsScreen';
import { SavedAddressesScreen } from '../features/addresses/screens/SavedAddressesScreen';
import { PassengerSettingsScreen } from '../features/profile/screens/PassengerSettingsScreen';
import { DsLoading } from '../components/design-system';
import type { BookingDraft, PassengerStackParamList } from './types';

const Stack = createNativeStackNavigator<PassengerStackParamList>();
type DraftStore = BookingDraft & { setPickup: (value: LocationOption | null) => void; setDestination: (value: LocationOption | null) => void; setCategoryId: (value: number | null) => void; setOutstationPickup:(value:LocationOption|null)=>void; setOutstationDestination:(value:LocationOption|null)=>void };
const BookingDraftContext = createContext<DraftStore | null>(null);

function useBookingDraft(): DraftStore { const value = useContext(BookingDraftContext); if (!value) throw new Error('Booking draft is unavailable.'); return value; }
function resetToHome(navigation: NavigationProp<PassengerStackParamList>) { navigation.reset({ index: 0, routes: [{ name: 'Home' }] }); }
function navigateToDestination(navigation: NavigationProp<PassengerStackParamList>, destination: DrawerDestination) {
  if (destination === 'home') navigation.navigate('Home');
  else if (destination === 'rides') navigation.navigate('Rides');
  else if (destination === 'addresses') navigation.navigate('Addresses');
  else if (destination === 'emergency') navigation.navigate('Emergency');
  else if (destination === 'support') navigation.navigate('Support');
  else navigation.navigate('Settings');
}

function AuthenticatedShell({ activeDestination, children, navigation }: { activeDestination: DrawerDestination; children: (openMenu: () => void) => ReactNode; navigation: NavigationProp<PassengerStackParamList> }) {
  const [menuVisible, setMenuVisible] = useState(false);
  const logout = async () => { await authService.clearSession(); setMenuVisible(false); navigation.reset({ index: 0, routes: [{ name: 'Login' }] }); };
  return <>{children(() => setMenuVisible(true))}<HomeDrawer activeDestination={activeDestination} onClose={() => setMenuVisible(false)} onLogout={() => void logout()} onNavigate={(destination) => navigateToDestination(navigation, destination)} visible={menuVisible} /></>;
}

function SplashRoute({ navigation }: NativeStackScreenProps<PassengerStackParamList, 'Splash'>) { return <SplashScreen onContinue={() => { void authService.hasSession().then(hasSession => navigation.replace(hasSession ? 'Home' : 'Login')); }} />; }
function LoginRoute({ navigation }: NativeStackScreenProps<PassengerStackParamList, 'Login'>) { return <LoginScreen onAuthenticated={() => resetToHome(navigation)} onBack={() => navigation.navigate('Splash')} onHelp={() => navigation.navigate('Faq')} onSignup={() => navigation.navigate('Signup')} />; }
function SignupRoute({ navigation }: NativeStackScreenProps<PassengerStackParamList, 'Signup'>) { return <SignupScreen onAuthenticated={() => resetToHome(navigation)} onBack={() => navigation.goBack()} onHelp={() => navigation.navigate('Faq')} onLogin={() => navigation.replace('Login')} />; }
function FaqRoute({ navigation }: NativeStackScreenProps<PassengerStackParamList, 'Faq'>) { return <FaqScreen onBack={() => navigation.goBack()} />; }
function HomeRoute({ navigation }: NativeStackScreenProps<PassengerStackParamList, 'Home'>) { const draft = useBookingDraft(); const [activeRide, setActiveRide] = useState<RideStatus | null>(null); useEffect(() => { void bookingApi.activeRide().then(setActiveRide).catch(() => undefined); }, []); const resume = () => activeRide && navigation.navigate('Booking', { ride: { ride_id: activeRide.ride_id, status: activeRide.status, pickup_address: activeRide.pickup_address, destination_address: activeRide.destination_address, fare_paise: activeRide.fare_paise, requested_at: new Date().toISOString(), message: activeRide.message } }); return <PassengerHomeScreen activeRideId={activeRide?.ride_id} destination={draft.destination} onBookInstantRide={() => navigation.navigate('InstantRide')} onBookOutstation={() => navigation.navigate('Outstation')} onContinueToFare={(categoryId) => { draft.setCategoryId(categoryId); navigation.navigate('Fare'); }} onEditSavedPlace={(place) => navigation.navigate('SavedPlace', { place })} onLogout={() => navigation.reset({ index: 0, routes: [{ name: 'Login' }] })} onMenuNavigate={(destination) => navigateToDestination(navigation, destination)} onOpenNotifications={() => navigation.navigate('Notifications')} onResumeRide={resume} onSelectDestination={() => navigation.navigate('Destination')} onSelectPickup={() => navigation.navigate('Pickup')} pickup={draft.pickup} />; }
function PickupRoute({ navigation }: NativeStackScreenProps<PassengerStackParamList, 'Pickup'>) { const draft = useBookingDraft(); return <AuthenticatedShell activeDestination="home" navigation={navigation}>{openMenu => <LocationSelectionScreen onBack={() => navigation.goBack()} onMenuPress={openMenu} onSelected={(location) => { draft.setPickup(location); navigation.goBack(); }} title="Choose pickup" />}</AuthenticatedShell>; }
function DestinationRoute({ navigation }: NativeStackScreenProps<PassengerStackParamList, 'Destination'>) { const draft = useBookingDraft(); return <AuthenticatedShell activeDestination="home" navigation={navigation}>{openMenu => <LocationSelectionScreen onBack={() => navigation.goBack()} onMenuPress={openMenu} onSelected={(location) => { draft.setDestination(location); navigation.goBack(); }} title="Choose destination" />}</AuthenticatedShell>; }
function SavedPlaceRoute({ navigation, route }: NativeStackScreenProps<PassengerStackParamList, 'SavedPlace'>) { return <AuthenticatedShell activeDestination="addresses" navigation={navigation}>{openMenu => <LocationSelectionScreen onBack={() => navigation.goBack()} onMenuPress={openMenu} onSelected={async location => { await bookingApi.updateSavedPlace(route.params.place.id, location); navigation.goBack(); }} title={`Set ${route.params.place.label} address`} />}</AuthenticatedShell>; }
function FareRoute({ navigation }: NativeStackScreenProps<PassengerStackParamList, 'Fare'>) { const draft = useBookingDraft(); const ready = !!draft.pickup && !!draft.destination && !!draft.categoryId; useEffect(() => { if (!ready) resetToHome(navigation); }, [navigation, ready]); if (!ready) return <DsLoading fullScreen label="Returning to your ride details…" />; return <AuthenticatedShell activeDestination="home" navigation={navigation}>{openMenu => <FareEstimateScreen categoryId={draft.categoryId!} destination={draft.destination!} onBack={() => navigation.goBack()} onBooked={ride => navigation.replace('Booking', { ride })} onMenuPress={openMenu} pickup={draft.pickup!} />}</AuthenticatedShell>; }
function BookingRoute({ navigation, route }: NativeStackScreenProps<PassengerStackParamList, 'Booking'>) { return <AuthenticatedShell activeDestination="home" navigation={navigation}>{openMenu => <BookingStatusScreen onDone={() => resetToHome(navigation)} onMenuPress={openMenu} ride={route.params.ride} />}</AuthenticatedShell>; }
function RidesRoute({ navigation }: NativeStackScreenProps<PassengerStackParamList, 'Rides'>) { return <AuthenticatedShell activeDestination="rides" navigation={navigation}>{openMenu => <MyRidesScreen onBack={() => navigation.goBack()} onMenuPress={openMenu} />}</AuthenticatedShell>; }
function AddressesRoute({ navigation }: NativeStackScreenProps<PassengerStackParamList, 'Addresses'>) { return <AuthenticatedShell activeDestination="addresses" navigation={navigation}>{openMenu => <SavedAddressesScreen onBack={() => navigation.goBack()} onEdit={place => navigation.navigate('SavedPlace', { place })} onMenuPress={openMenu} />}</AuthenticatedShell>; }
function EmergencyRoute({ navigation }: NativeStackScreenProps<PassengerStackParamList, 'Emergency'>) { return <AuthenticatedShell activeDestination="emergency" navigation={navigation}>{openMenu => <EmergencyContactsScreen onBack={() => navigation.goBack()} onMenuPress={openMenu} />}</AuthenticatedShell>; }
function SupportRoute({ navigation }: NativeStackScreenProps<PassengerStackParamList, 'Support'>) { return <AuthenticatedShell activeDestination="support" navigation={navigation}>{openMenu => <PassengerSupportScreen onBack={() => navigation.goBack()} onMenuPress={openMenu} />}</AuthenticatedShell>; }
function InstantRideRoute({ navigation }: NativeStackScreenProps<PassengerStackParamList, 'InstantRide'>) { return <AuthenticatedShell activeDestination="support" navigation={navigation}>{openMenu => <InstantRideScreen onBack={() => navigation.goBack()} onMenuPress={openMenu} />}</AuthenticatedShell>; }
function OutstationRoute({ navigation }: NativeStackScreenProps<PassengerStackParamList, 'Outstation'>) { const draft=useBookingDraft(); return <AuthenticatedShell activeDestination="home" navigation={navigation}>{openMenu => <OutstationBookingScreen destination={draft.outstationDestination} onBack={() => navigation.goBack()} onClearLocations={()=>{draft.setOutstationPickup(null);draft.setOutstationDestination(null);}} onMenuPress={openMenu} onSelectDestination={()=>navigation.navigate('OutstationDestination')} onSelectPickup={()=>navigation.navigate('OutstationPickup')} pickup={draft.outstationPickup}/>}</AuthenticatedShell>; }
function OutstationPickupRoute({navigation}:NativeStackScreenProps<PassengerStackParamList,'OutstationPickup'>){const draft=useBookingDraft();return <AuthenticatedShell activeDestination="home" navigation={navigation}>{openMenu=><LocationSelectionScreen onBack={()=>navigation.goBack()} onMenuPress={openMenu} onSelected={location=>{draft.setOutstationPickup(location);navigation.goBack();}} scope="outstation" title="Outstation pickup"/>}</AuthenticatedShell>;}
function OutstationDestinationRoute({navigation}:NativeStackScreenProps<PassengerStackParamList,'OutstationDestination'>){const draft=useBookingDraft();return <AuthenticatedShell activeDestination="home" navigation={navigation}>{openMenu=><LocationSelectionScreen onBack={()=>navigation.goBack()} onMenuPress={openMenu} onSelected={location=>{draft.setOutstationDestination(location);navigation.goBack();}} scope="outstation" title="Outstation destination"/>}</AuthenticatedShell>;}
function NotificationsRoute({ navigation }: NativeStackScreenProps<PassengerStackParamList, 'Notifications'>) { return <AuthenticatedShell activeDestination="home" navigation={navigation}>{openMenu => <NotificationsScreen onBack={() => navigation.goBack()} onMenuPress={openMenu}/>}</AuthenticatedShell>; }
function SettingsRoute({ navigation }: NativeStackScreenProps<PassengerStackParamList, 'Settings'>) { return <AuthenticatedShell activeDestination="settings" navigation={navigation}>{openMenu => <PassengerSettingsScreen onBack={() => navigation.goBack()} onMenuPress={openMenu} />}</AuthenticatedShell>; }

export function PassengerNavigator() {
  const [pickup, setPickup] = useState<LocationOption | null>(null); const [destination, setDestination] = useState<LocationOption | null>(null); const [categoryId, setCategoryId] = useState<number | null>(null);
  const [outstationPickup,setOutstationPickup]=useState<LocationOption|null>(null); const [outstationDestination,setOutstationDestination]=useState<LocationOption|null>(null);
  const value = useMemo(() => ({ pickup, destination, categoryId, outstationPickup, outstationDestination, setPickup, setDestination, setCategoryId, setOutstationPickup, setOutstationDestination }), [pickup, destination, categoryId, outstationPickup, outstationDestination]);
  return <BookingDraftContext.Provider value={value}><NavigationContainer><Stack.Navigator initialRouteName="Splash" screenOptions={{ animation: 'slide_from_right', headerShown: false }}><Stack.Screen component={SplashRoute} name="Splash" /><Stack.Screen component={LoginRoute} name="Login" /><Stack.Screen component={SignupRoute} name="Signup" /><Stack.Screen component={FaqRoute} name="Faq" /><Stack.Screen component={HomeRoute} name="Home" /><Stack.Screen component={PickupRoute} name="Pickup" /><Stack.Screen component={DestinationRoute} name="Destination" /><Stack.Screen component={SavedPlaceRoute} name="SavedPlace" /><Stack.Screen component={FareRoute} name="Fare" /><Stack.Screen component={BookingRoute} name="Booking" /><Stack.Screen component={RidesRoute} name="Rides" /><Stack.Screen component={AddressesRoute} name="Addresses" /><Stack.Screen component={EmergencyRoute} name="Emergency" /><Stack.Screen component={SupportRoute} name="Support" /><Stack.Screen component={InstantRideRoute} name="InstantRide" /><Stack.Screen component={OutstationRoute} name="Outstation" /><Stack.Screen component={OutstationPickupRoute} name="OutstationPickup" /><Stack.Screen component={OutstationDestinationRoute} name="OutstationDestination" /><Stack.Screen component={NotificationsRoute} name="Notifications" /><Stack.Screen component={SettingsRoute} name="Settings" /></Stack.Navigator></NavigationContainer></BookingDraftContext.Provider>;
}
