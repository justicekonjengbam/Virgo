import unittest

from app.schemas.auth import normalize_phone


class TestPhoneNormalization(unittest.TestCase):
    def test_indian_phone_numbers_have_one_canonical_database_format(self):
        for value in ['9876543210', '+91 98765 43210', '919876543210']:
            with self.subTest(value=value):
                self.assertEqual(normalize_phone(value), '+919876543210')


if __name__ == '__main__':
    unittest.main()
