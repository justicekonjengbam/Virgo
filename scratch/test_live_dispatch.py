import requests
from datetime import timedelta
from app.services.auth_service import AuthService
from app.services.driver_auth_service import DriverAuthService

# 1. Create tokens
passenger_token = AuthService()._encode(1, 'access', timedelta(hours=1))
driver_token = DriverAuthService()._encode(1, 'access', timedelta(hours=1))

base_url = 'http://127.0.0.1:8000'

# 2. Check Driver current offer before booking
r_pre = requests.get(f'{base_url}/api/v1/drivers/me/ride-offers/current', headers={'Authorization': f'Bearer {driver_token}'})
print('Pre-booking current offer:', r_pre.status_code, r_pre.json())

# 3. Create Ride booking as Passenger
booking_payload = {
    'pickup_location_id': 1,
    'destination_location_id': 2,
    'category_id': 1
}
r_book = requests.post(f'{base_url}/api/v1/passengers/me/rides', json=booking_payload, headers={'Authorization': f'Bearer {passenger_token}'})
print('Book ride status:', r_book.status_code)
book_data = r_book.json()
print('Book ride data:', book_data)

# 4. Check Driver current offer immediately after booking
r_offer = requests.get(f'{base_url}/api/v1/drivers/me/ride-offers/current', headers={'Authorization': f'Bearer {driver_token}'})
print('Driver offer status:', r_offer.status_code)
offer_data = r_offer.json()
print('Driver offer data:', offer_data)

if offer_data:
    expires_at = offer_data.get('expires_at')
    print('expires_at value:', expires_at)
    print('Does expires_at end with Z?:', expires_at.endswith('Z'))
    print('Offer ID:', offer_data.get('offer_id'))

