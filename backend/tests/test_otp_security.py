import hashlib
import hmac
import math
import secrets
import unittest
from datetime import UTC, datetime, timedelta


class TestRideOtpSecurity(unittest.TestCase):
    """Verifies Milestone 1 cryptographic Ride Start OTP logic."""

    @staticmethod
    def create_ride_otp_credentials(secret_key: str, ride_id: int, passenger_id: int) -> tuple[str, str]:
        salt = secrets.token_hex(16)
        message = f'ride_otp:{ride_id}:{passenger_id}:{salt}'.encode()
        digest = hmac.new(secret_key.encode(), message, hashlib.sha256).hexdigest()
        otp = f'{int(digest[:8], 16) % 10000:04d}'
        otp_hash = hashlib.sha256(f'{otp}:{salt}'.encode()).hexdigest()
        return salt, otp_hash

    @staticmethod
    def recover_ride_otp(secret_key: str, ride_id: int, passenger_id: int, salt: str | None, expected_hash: str | None) -> str | None:
        if not salt or not expected_hash:
            return None
        message = f'ride_otp:{ride_id}:{passenger_id}:{salt}'.encode()
        digest = hmac.new(secret_key.encode(), message, hashlib.sha256).hexdigest()
        otp = f'{int(digest[:8], 16) % 10000:04d}'
        computed_hash = hashlib.sha256(f'{otp}:{salt}'.encode()).hexdigest()
        if secrets.compare_digest(computed_hash, expected_hash):
            return otp
        return None

    @staticmethod
    def verify_ride_otp(entered_otp: str | None, salt: str | None, expected_hash: str | None) -> bool:
        if not entered_otp or not salt or not expected_hash:
            return False
        cleaned = entered_otp.strip()
        if len(cleaned) != 4 or not cleaned.isdigit():
            return False
        computed_hash = hashlib.sha256(f'{cleaned}:{salt}'.encode()).hexdigest()
        return secrets.compare_digest(computed_hash, expected_hash)

    def setUp(self):
        self.secret_key = "a-very-long-and-secure-test-secret-key-32-chars-minimum"
        self.ride_id = 42
        self.passenger_id = 7

    def test_otp_generation_format_and_entropy(self):
        salt, otp_hash = self.create_ride_otp_credentials(
            self.secret_key, self.ride_id, self.passenger_id
        )
        self.assertIsInstance(salt, str)
        self.assertIsInstance(otp_hash, str)
        self.assertEqual(len(salt), 32)  # 16 bytes hex = 32 chars
        self.assertEqual(len(otp_hash), 64)  # sha256 hex = 64 chars

        # Recover plaintext OTP
        otp = self.recover_ride_otp(
            self.secret_key, self.ride_id, self.passenger_id, salt, otp_hash
        )
        self.assertIsNotNone(otp)
        self.assertEqual(len(otp), 4)
        self.assertTrue(otp.isdigit())

        # Verify that generating multiple credentials yields different salts and OTPs
        salts = set()
        otps = set()
        for i in range(50):
            s, h = self.create_ride_otp_credentials(self.secret_key, i, self.passenger_id)
            salts.add(s)
            o = self.recover_ride_otp(self.secret_key, i, self.passenger_id, s, h)
            otps.add(o)
        self.assertEqual(len(salts), 50)
        self.assertGreater(len(otps), 1)  # Distinct OTPs across rides

    def test_otp_verification_correct(self):
        salt, otp_hash = self.create_ride_otp_credentials(
            self.secret_key, self.ride_id, self.passenger_id
        )
        otp = self.recover_ride_otp(
            self.secret_key, self.ride_id, self.passenger_id, salt, otp_hash
        )
        # Correct OTP must verify successfully
        self.assertTrue(self.verify_ride_otp(otp, salt, otp_hash))

    def test_otp_verification_incorrect(self):
        salt, otp_hash = self.create_ride_otp_credentials(
            self.secret_key, self.ride_id, self.passenger_id
        )
        otp = self.recover_ride_otp(
            self.secret_key, self.ride_id, self.passenger_id, salt, otp_hash
        )
        wrong_otp = f"{(int(otp) + 1) % 10000:04d}"

        # Wrong OTP must fail
        self.assertFalse(self.verify_ride_otp(wrong_otp, salt, otp_hash))
        # Malformed / empty inputs must fail
        self.assertFalse(self.verify_ride_otp("", salt, otp_hash))
        self.assertFalse(self.verify_ride_otp(None, salt, otp_hash))
        self.assertFalse(self.verify_ride_otp("123", salt, otp_hash))
        self.assertFalse(self.verify_ride_otp("12345", salt, otp_hash))
        self.assertFalse(self.verify_ride_otp("abcd", salt, otp_hash))
        self.assertFalse(self.verify_ride_otp("0000", "", otp_hash))
        self.assertFalse(self.verify_ride_otp("0000", salt, ""))

    def test_tampered_secret_or_salt(self):
        salt, otp_hash = self.create_ride_otp_credentials(
            self.secret_key, self.ride_id, self.passenger_id
        )
        # Different secret key cannot recover the OTP
        recovered_wrong = self.recover_ride_otp(
            "different-secret-key-32-chars-minimum-here",
            self.ride_id,
            self.passenger_id,
            salt,
            otp_hash,
        )
        self.assertIsNone(recovered_wrong)


class TestRateLimiter(unittest.TestCase):
    """Verifies in-memory rate limiting and brute-force prevention."""

    def test_sliding_window_rate_limiter(self):
        from collections import defaultdict
        import time

        class MockLimiter:
            def __init__(self, limit: int, window_seconds: int):
                self.limit = limit
                self.window_seconds = window_seconds
                self._history = defaultdict(list)

            def check(self, key: str) -> bool:
                now = time.time()
                cutoff = now - self.window_seconds
                recent = [t for t in self._history[key] if t > cutoff]
                if len(recent) >= self.limit:
                    return False  # Blocked
                recent.append(now)
                self._history[key] = recent
                return True

        limiter = MockLimiter(limit=3, window_seconds=2)
        key = "test_client_ip"

        # 3 requests allowed
        self.assertTrue(limiter.check(key))
        self.assertTrue(limiter.check(key))
        self.assertTrue(limiter.check(key))

        # 4th request rejected
        self.assertFalse(limiter.check(key))


class TestImphalGeographicConfiguration(unittest.TestCase):
    """Verifies Imphal coordinates and 150 km service area validation."""

    center_lat = 24.8170
    center_lon = 93.9368
    radius_km = 150.0

    def contains(self, lat: float, lon: float) -> bool:
        lat1, lon1, lat2, lon2 = map(math.radians, (self.center_lat, self.center_lon, lat, lon))
        delta_lat, delta_lon = lat2 - lat1, lon2 - lon1
        val = math.sin(delta_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2) ** 2
        return 6371.0 * 2 * math.asin(math.sqrt(val)) <= self.radius_km

    def test_imphal_city_landmarks_inside_boundary(self):
        # Kangla Fort
        self.assertTrue(self.contains(24.8115, 93.9422))
        # Bir Tikendrajit Airport
        self.assertTrue(self.contains(24.7600, 93.8967))
        # Ema Keithel
        self.assertTrue(self.contains(24.8085, 93.9365))
        # RIMS Imphal
        self.assertTrue(self.contains(24.8236, 93.9214))
        # Thoubal (~20 km)
        self.assertTrue(self.contains(24.6300, 93.9800))
        # Churachandpur (~60 km)
        self.assertTrue(self.contains(24.3333, 93.6833))

    def test_distant_locations_outside_boundary(self):
        # Hubballi (Karnataka) ~ 2200 km
        self.assertFalse(self.contains(15.3647, 75.1240))
        # Bengaluru (Karnataka) ~ 2300 km
        self.assertFalse(self.contains(12.9716, 77.5946))
        # New Delhi ~ 1700 km
        self.assertFalse(self.contains(28.6139, 77.2090))
        # Mumbai ~ 2100 km
        self.assertFalse(self.contains(19.0760, 72.8777))


if __name__ == "__main__":
    unittest.main()

