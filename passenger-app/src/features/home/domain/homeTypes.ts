export type SavedPlace = { id: number; label: string; formatted_address: string; latitude: number; longitude: number };
export type RideCategory = { id: number; code: string; display_name: string; seat_count: number; base_fare_paise: number; estimated_arrival_minutes: number; icon_key: string };
export type RecentRide = { id: number; pickup_address: string; destination_address: string; completed_at: string | null; final_duration_seconds: number | null; fare_paise: number };
export type PassengerHome = { passenger_name: string; saved_places: SavedPlace[]; ride_categories: RideCategory[]; recent_rides: RecentRide[] };
