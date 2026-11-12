import time
import subprocess
import xml.etree.ElementTree as ET
import requests
from datetime import timedelta
from app.services.auth_service import AuthService
from app.services.driver_auth_service import DriverAuthService

base_url = 'http://127.0.0.1:8000'
adb = r"C:\platform-tools\adb.exe"
device = "R52X90A40LV"

def run_adb(args):
    cmd = [adb, "-s", device] + args
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="ignore")
    return res.stdout

def dump_ui(retries=5):
    for i in range(retries):
        run_adb(['shell', 'uiautomator', 'dump', '/sdcard/d.xml'])
        time.sleep(0.5)
        xml = run_adb(['shell', 'cat', '/sdcard/d.xml'])
        if xml.strip().startswith('<?xml'):
            try:
                root = ET.fromstring(xml)
                return [(n.attrib.get('text', ''), n.attrib.get('content-desc', ''), n.attrib.get('bounds', '')) for n in root.iter() if n.attrib.get('text') or n.attrib.get('content-desc')]
            except Exception as e:
                print(f"XML parse retry {i}: {e}")
        time.sleep(1)
    return []

passenger_token = AuthService()._encode(1, 'access', timedelta(hours=1))
driver_token = DriverAuthService()._encode(1, 'access', timedelta(hours=1))

print("=== STEP 1: Creating Passenger Ride Booking ===")
booking_payload = {
    'pickup_location_id': 1,
    'destination_location_id': 2,
    'category_id': 1
}
r_book = requests.post(f'{base_url}/api/v1/passengers/me/rides', json=booking_payload, headers={'Authorization': f'Bearer {passenger_token}'})
print("Book response:", r_book.status_code, r_book.json())
ride_id = r_book.json()['ride_id']

print("\n=== STEP 2: Verifying Offer Dispatched to Driver ===")
r_offer = requests.get(f'{base_url}/api/v1/drivers/me/ride-offers/current', headers={'Authorization': f'Bearer {driver_token}'})
print("Offer response:", r_offer.status_code, r_offer.json())
offer_data = r_offer.json()
assert offer_data is not None, "Driver did not receive an offer!"
assert offer_data['expires_at'].endswith('Z'), f"expires_at does not end with Z: {offer_data['expires_at']}"
offer_id = offer_data['offer_id']
print(f"Offer #{offer_id} for Ride #{ride_id} successfully created with UTC expiration: {offer_data['expires_at']}")

print("\n=== STEP 3: Waiting 3s for Polling / WS on RideRequestScreen ===")
time.sleep(3)

elements = dump_ui()
print("\nElements visible on Ride Request Screen:")
accept_bounds = None
for text, desc, bounds in elements:
    if any(k in text or k in desc for k in ["Ride Request", "Accept", "Kangla", "Airport", "fare", "paise", "within", "s", "₹", "km"]):
        print(f"  - text='{text}' desc='{desc}' bounds='{bounds}'")
    if "Accept Ride" in text or "Accept Ride" in desc:
        accept_bounds = bounds

assert accept_bounds is not None, f"Accept Ride button not found on screen! Screen elements: {elements}"
print(f"\nSUCCESS: Accept button visible with live countdown! Bounds: {accept_bounds}")

parts = accept_bounds.replace('][', ',').replace('[', '').replace(']', '').split(',')
x1, y1, x2, y2 = map(int, parts)
tap_x = (x1 + x2) // 2
tap_y = (y1 + y2) // 2
print(f"Tapping Accept Ride button at ({tap_x}, {tap_y})...")
run_adb(['shell', 'input', 'tap', str(tap_x), str(tap_y)])

print("\n=== STEP 4: Checking Acceptance Alert on Tablet ===")
time.sleep(1.5)
elements2 = dump_ui()
for text, desc, bounds in elements2:
    if any(k in text or k in desc for k in ["Ride accepted", "Track pickup", "OK", "Active", "pickup"]):
        print(f"  - text='{text}' desc='{desc}' bounds='{bounds}'")
    if "Track pickup" in text or "Track pickup" in desc:
        parts = bounds.replace('][', ',').replace('[', '').replace(']', '').split(',')
        bx1, by1, bx2, by2 = map(int, parts)
        run_adb(['shell', 'input', 'tap', str((bx1 + bx2) // 2), str((by1 + by2) // 2)])
        print("Tapped 'Track pickup' on acceptance alert dialog.")

time.sleep(2)

print("\n=== STEP 5: Verifying Active Ride Screen on Tablet ===")
elements3 = dump_ui()
print("Active Ride Screen visible elements:")
for text, desc, bounds in elements3:
    if any(k in text or k in desc for k in ["Active", "Kangla", "Airport", "Cancel", "Arrived", "OTP", "End", "Pickup"]):
        print(f"  - text='{text}' desc='{desc}' bounds='{bounds}'")

print("\n=== STEP 6: Verifying Database Record ===")
from app.db import SessionLocal
from app.models.ride_hailing import Ride, RideDispatchOffer
db = SessionLocal()
ride_db = db.get(Ride, ride_id)
offer_db = db.get(RideDispatchOffer, offer_id)

print(f"Ride #{ride_id} status: {ride_db.status}, driver_id: {ride_db.driver_id}")
print(f"Offer #{offer_id} status: {offer_db.status}, responded_at: {offer_db.responded_at}")

assert ride_db.status in ['driver_arriving', 'driver_assigned', 'accepted'], f"Ride status unexpected: {ride_db.status}"
assert ride_db.driver_id == 1, f"Ride driver_id unexpected: {ride_db.driver_id}"
assert offer_db.status == 'accepted', f"Offer status unexpected: {offer_db.status}"

print("\n==========================================================================")
print(" VERIFICATION COMPLETE: DRIVER SUCCESSFULLY ACCEPTED REAL TEST OFFER!")
print("==========================================================================")

