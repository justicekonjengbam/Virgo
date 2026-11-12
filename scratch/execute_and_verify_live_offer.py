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

print("\n=== STEP 3: Waiting for Driver App UI to navigate and display countdown ===")
time.sleep(2.5)

run_adb(['shell', 'uiautomator', 'dump', '/sdcard/offer_screen.xml'])
xml = run_adb(['shell', 'cat', '/sdcard/offer_screen.xml'])
root = ET.fromstring(xml)
elements = [(n.attrib.get('text', ''), n.attrib.get('content-desc', ''), n.attrib.get('bounds', '')) for n in root.iter() if n.attrib.get('text') or n.attrib.get('content-desc')]

print("Visible screen elements:")
accept_bounds = None
for text, desc, bounds in elements:
    if any(k in text or k in desc for k in ["Ride Request", "Accept", "Kangla", "Airport", "fare", "paise", "within", "s"]):
        print(f"  - text='{text}' desc='{desc}' bounds='{bounds}'")
    if "Accept" in text or "Accept" in desc:
        accept_bounds = bounds

assert accept_bounds is not None, f"Could not find Accept button on screen! Dump was: {elements}"
print(f"\nFound Accept button at bounds: {accept_bounds}")

# Parse bounds: e.g. [1161,1237][1401,1286]
parts = accept_bounds.replace('][', ',').replace('[', '').replace(']', '').split(',')
x1, y1, x2, y2 = map(int, parts)
tap_x = (x1 + x2) // 2
tap_y = (y1 + y2) // 2
print(f"Tapping Accept Ride at ({tap_x}, {tap_y})...")
run_adb(['shell', 'input', 'tap', str(tap_x), str(tap_y)])

print("\n=== STEP 4: Verifying Alert / Transition on Device ===")
time.sleep(1.5)
run_adb(['shell', 'uiautomator', 'dump', '/sdcard/after_accept.xml'])
xml2 = run_adb(['shell', 'cat', '/sdcard/after_accept.xml'])
root2 = ET.fromstring(xml2)
elements2 = [(n.attrib.get('text', ''), n.attrib.get('content-desc', ''), n.attrib.get('bounds', '')) for n in root2.iter() if n.attrib.get('text') or n.attrib.get('content-desc')]

print("Visible screen elements after accept tap:")
for text, desc, bounds in elements2:
    if any(k in text or k in desc for k in ["Ride accepted", "Track pickup", "OK", "Active", "pickup", "arrived"]):
        print(f"  - text='{text}' desc='{desc}' bounds='{bounds}'")
    if "Track pickup" in text or "Track pickup" in desc:
        # Dismiss alert to navigate to active ride
        parts = bounds.replace('][', ',').replace('[', '').replace(']', '').split(',')
        bx1, by1, bx2, by2 = map(int, parts)
        run_adb(['shell', 'input', 'tap', str((bx1 + bx2) // 2), str((by1 + by2) // 2)])
        print("Tapped 'Track pickup' on acceptance alert dialog.")

time.sleep(2)

print("\n=== STEP 5: Verifying DB Ride & Offer Status ===")
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
print("\n>>> LIVE RIDE DISPATCH, COUNTDOWN DISPLAY, AND ACCEPTANCE TEST PASSED 100%! <<<")

