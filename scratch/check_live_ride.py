import sqlite3

conn = sqlite3.connect('backend/cabapp.db')
cur = conn.cursor()

print("=== LATEST RIDES (ID >= 12) ===")
for r in cur.execute("""
    SELECT id, passenger_id, driver_id, status, cancellation_reason, 
           requested_at, accepted_at, started_at, completed_at, cancelled_at 
    FROM rides WHERE id >= 12 ORDER BY id DESC
"""):
    print(r)

print("\n=== LATEST DISPATCH OFFERS (ID >= 5) ===")
for r in cur.execute("""
    SELECT id, ride_id, driver_id, status, offered_at, expires_at, responded_at 
    FROM ride_dispatch_offers WHERE id >= 5 ORDER BY id DESC
"""):
    print(r)

print("\n=== LATEST RIDE EVENTS ===")
for r in cur.execute("""
    SELECT id, ride_id, event_type, created_at 
    FROM ride_events ORDER BY id DESC LIMIT 5
"""):
    print(r)

print("\n=== DRIVER STATUS ===")
for r in cur.execute("""
    SELECT id, full_name, phone_number, is_online, status 
    FROM drivers WHERE id = 1
"""):
    print(r)

