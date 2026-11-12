import os
import sys
import types
import unittest
from datetime import datetime

# Shims for offline execution
try:
    from fastapi import HTTPException
except ImportError:
    class FakeHTTPException(Exception):
        def __init__(self, status_code: int = 500, detail: str = ""):
            self.status_code = status_code
            self.detail = detail
            super().__init__(f"{status_code}: {detail}")

    for _m in ['fastapi', 'httpx', 'sqlalchemy', 'sqlalchemy.orm', 'pydantic', 'pydantic_settings']:
        if _m not in sys.modules:
            sys.modules[_m] = types.ModuleType(_m)

    sys.modules['fastapi'].HTTPException = FakeHTTPException
    sys.modules['fastapi'].status = types.SimpleNamespace(HTTP_400_BAD_REQUEST=400, HTTP_409_CONFLICT=409, HTTP_422_UNPROCESSABLE_ENTITY=422)
    HTTPException = FakeHTTPException

backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if backend_root not in sys.path:
    sys.path.insert(0, backend_root)

from app.services.booking_service import BookingService
from app.services.map_provider_service import MapProviderService


class TestBookingPolicy(unittest.TestCase):
    def test_service_area_accepts_imphal_locations(self):
        service = MapProviderService()
        self.assertTrue(service.contains(24.8170, 93.9368))
        self.assertTrue(service.contains(24.8115, 93.9422))
        self.assertTrue(service.contains(24.7600, 93.8967))

    def test_service_area_rejects_locations_beyond_150_km(self):
        service = MapProviderService()
        with self.assertRaises(HTTPException) as ctx:
            service.ensure_in_service_area(12.9716, 77.5946)
        self.assertEqual(ctx.exception.status_code, 422)

    def test_night_charge_window(self):
        cases = [(0, True), (4, True), (5, False), (21, False), (22, True)]
        for hour, expected in cases:
            with self.subTest(hour=hour):
                self.assertEqual(BookingService._is_night(datetime(2026, 8, 13, hour, 0)), expected)


if __name__ == '__main__':
    unittest.main()
