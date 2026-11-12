"""
Idempotent Seeder for Real-Device Integration Testing (Milestone 3.1)
=====================================================================
Sets up:
1. One Test Passenger (+919876543210)
2. One Test Driver (+919876543220) with active status, initially offline
3. One Verified Test Vehicle (MN-01-AB-1234, Hatchback) assigned to Driver
4. Four Verified Mandatory Driver Documents (DL, RC, Aadhaar, Insurance)
5. Six Active Virgo Rate Cards and Imphal Ride Categories
"""

import sys
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

# Add backend directory to sys.path
backend_root = Path(__file__).resolve().parents[1]
if str(backend_root) not in sys.path:
    sys.path.insert(0, str(backend_root))

from pwdlib import PasswordHash
from sqlalchemy import select

from app.db import SessionLocal, initialize_database
from app.models.ride_hailing import (
    Driver,
    DriverDocument,
    DriverVehicleAssignment,
    Vehicle,
)
from app.models.user import Passenger
from app.services.home_seed_service import HomeSeedService

password_hasher = PasswordHash.recommended()

PASSENGER_PHONE = "+919876543210"
PASSENGER_NAME = "Test Passenger"
PASSENGER_PASSWORD = "TestPassenger@123"

DRIVER_PHONE = "+919876543220"
DRIVER_NAME = "Test Driver"
DRIVER_UID = "test_driver_uid_9876543220"
VEHICLE_REG = "MN01AB1234"


def seed_test_accounts():
    print("=" * 60)
    print("VIRGO - REAL DEVICE TEST ACCOUNTS SEEDER")
    print("=" * 60)

    # 1. Ensure migrations are up to date
    print("\n[1/5] Checking database schema & migrations...")
    initialize_database()
    print("  -> Database schema verified.")

    db = SessionLocal()
    try:
        # 2. Seed / Verify Test Passenger
        print(f"\n[2/5] Seeding Test Passenger ({PASSENGER_PHONE})...")
        passenger = db.scalar(
            select(Passenger).where(Passenger.phone_number == PASSENGER_PHONE).limit(1)
        )
        if not passenger:
            passenger = Passenger(
                full_name=PASSENGER_NAME,
                phone_number=PASSENGER_PHONE,
                password_hash=password_hasher.hash(PASSENGER_PASSWORD),
                is_phone_verified=True,
                status="active",
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )
            db.add(passenger)
            db.flush()
            print(f"  -> Created new test passenger: ID {passenger.id}")
        else:
            passenger.full_name = PASSENGER_NAME
            passenger.is_phone_verified = True
            passenger.status = "active"
            passenger.deleted_at = None
            db.flush()
            print(f"  -> Updated existing test passenger: ID {passenger.id}")

        # Seed categories, rate cards, and saved places via HomeSeedService
        home_seed_service = HomeSeedService()
        home_seed_service.ensure(db, passenger)
        print("  -> Verified saved places (Home/Work) and Virgo rate cards.")

        # 3. Seed / Verify Test Vehicle
        print(f"\n[3/5] Seeding Test Vehicle ({VEHICLE_REG})...")
        vehicle = db.scalar(
            select(Vehicle).where(Vehicle.registration_number == VEHICLE_REG).limit(1)
        )
        if not vehicle:
            vehicle = Vehicle(
                registration_number=VEHICLE_REG,
                make="Maruti Suzuki",
                model="Swift",
                year=2022,
                color="White",
                category_code="hatchback",
                seat_count=4,
                verification_status="verified",
            )
            db.add(vehicle)
            db.flush()
            print(f"  -> Created verified vehicle: ID {vehicle.id} ({VEHICLE_REG})")
        else:
            vehicle.verification_status = "verified"
            vehicle.category_code = "hatchback"
            db.flush()
            print(f"  -> Verified vehicle: ID {vehicle.id} ({VEHICLE_REG})")

        # 4. Seed / Verify Test Driver
        print(f"\n[4/5] Seeding Test Driver ({DRIVER_PHONE})...")
        driver = db.scalar(
            select(Driver).where(Driver.phone_number == DRIVER_PHONE).limit(1)
        )
        if not driver:
            driver = Driver(
                firebase_uid=DRIVER_UID,
                full_name=DRIVER_NAME,
                phone_number=DRIVER_PHONE,
                email="test.driver@virgocabs.com",
                status="active",
                operating_city="Imphal",
                rating_average=Decimal("4.90"),
                completed_rides_count=12,
                is_online=False,  # Requirement: Driver initially offline
            )
            db.add(driver)
            db.flush()
            print(f"  -> Created active test driver: ID {driver.id} (initially offline)")
        else:
            driver.status = "active"
            driver.operating_city = "Imphal"
            driver.is_online = False  # Ensure driver starts offline
            db.flush()
            print(f"  -> Updated active test driver: ID {driver.id} (status: active, offline)")

        # Link Vehicle Assignment
        assignment = db.scalar(
            select(DriverVehicleAssignment)
            .where(
                DriverVehicleAssignment.driver_id == driver.id,
                DriverVehicleAssignment.ended_at.is_(None),
            )
            .limit(1)
        )
        if not assignment:
            assignment = DriverVehicleAssignment(
                driver_id=driver.id,
                vehicle_id=vehicle.id,
                started_at=datetime.now(UTC) - timedelta(days=30),
                ended_at=None,
            )
            db.add(assignment)
            db.flush()
            print(f"  -> Assigned vehicle {vehicle.registration_number} to driver {driver.full_name}")
        else:
            assignment.vehicle_id = vehicle.id
            db.flush()
            print(f"  -> Confirmed active vehicle assignment ID {assignment.id}")

        # 5. Seed / Verify Test Driver Documents
        print(f"\n[5/5] Seeding Driver Documents for ID {driver.id}...")
        now = datetime.now(UTC)
        documents_spec = [
            ("driving_licence", "MN-DL-2022-0012345", "test/docs/dl_9876543220.pdf", now + timedelta(days=1825)),
            ("vehicle_registration", "MN-01-AB-1234", "test/docs/rc_9876543220.pdf", now + timedelta(days=2500)),
            ("aadhaar", "XXXXXXXX1234", "test/docs/aadhaar_9876543220.pdf", None),
            ("vehicle_insurance", "INS-2026-98765432", "test/docs/insurance_9876543220.pdf", now + timedelta(days=730)),
        ]

        for doc_type, doc_num, s_key, expires in documents_spec:
            doc = db.scalar(
                select(DriverDocument).where(
                    DriverDocument.driver_id == driver.id,
                    DriverDocument.document_type == doc_type,
                ).limit(1)
            )
            if not doc:
                doc = DriverDocument(
                    driver_id=driver.id,
                    document_type=doc_type,
                    document_number=doc_num,
                    storage_key=s_key,
                    verification_status="verified",
                    reviewed_by="Virgo Admin",
                    reviewed_at=now,
                    expires_at=expires,
                    original_filename=f"{doc_type}.pdf",
                    mime_type="application/pdf",
                    file_size_bytes=102400,
                )
                db.add(doc)
                print(f"  -> Added verified {doc_type}: {doc_num}")
            else:
                doc.verification_status = "verified"
                doc.reviewed_by = "Virgo Admin"
                doc.reviewed_at = now
                doc.expires_at = expires
                print(f"  -> Confirmed verified {doc_type}: {doc_num}")

        db.commit()

        print("\n" + "=" * 60)
        print("TEST ACCOUNTS SEEDED SUCCESSFULLY")
        print("=" * 60)
        print("PASSENGER ACCOUNT:")
        print(f"  Phone Number : {PASSENGER_PHONE}")
        print(f"  Display Name : {PASSENGER_NAME}")
        print("  Status       : Active, Verified")
        print("  Saved Places : Home (Paona Bazar), Work (RIMS Lamphelpat)")
        print("\nDRIVER ACCOUNT:")
        print(f"  Phone Number : {DRIVER_PHONE}")
        print(f"  Display Name : {DRIVER_NAME}")
        print("  Status       : Active (Ready to go online)")
        print(f"  Initial State: OFFLINE (is_online=False)")
        print(f"  Vehicle      : {vehicle.make} {vehicle.model} ({vehicle.registration_number}) - Verified")
        print("  Documents    : DL, RC, Aadhaar, Insurance - All Verified")
        print("=" * 60)

    except Exception as e:
        db.rollback()
        print(f"\n[ERROR] Seeding failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_test_accounts()

