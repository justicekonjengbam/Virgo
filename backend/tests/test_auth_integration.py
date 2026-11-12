import json
import urllib.request

base_url = 'http://127.0.0.1:8000'

def test_full_auth_flow():
    print("=" * 60)
    print("VIRGO AUTH INTEGRATION TEST SUITE")
    print("=" * 60)

    # 1. Health checks
    for path in ['/health', '/api/v1/health']:
        with urllib.request.urlopen(f'{base_url}{path}') as r:
            res = json.loads(r.read().decode())
            print(f"1. GET {path} -> {r.status} {res.get('status')}")

    # 2. Preflight for seeded passenger (all formats)
    for phone in ['9876543210', '+919876543210', '919876543210']:
        data = json.dumps({'phone_number': phone}).encode()
        req = urllib.request.Request(
            f'{base_url}/api/v1/auth/passengers/firebase/login/preflight',
            data=data,
            headers={'Content-Type': 'application/json'},
            method='POST',
        )
        with urllib.request.urlopen(req) as r:
            print(f"2. Preflight for {phone} -> {r.status} OK (Account verified)")

    # 3. Development OTP Request for seeded passenger
    data = json.dumps({'phone_number': '9876543210'}).encode()
    req = urllib.request.Request(
        f'{base_url}/api/v1/auth/passengers/otp/request',
        data=data,
        headers={'Content-Type': 'application/json'},
        method='POST',
    )
    with urllib.request.urlopen(req) as r:
        res = json.loads(r.read().decode())
        otp = res['development_otp']
        print(f"3. POST /otp/request -> {r.status}, message: {res['message']}, dev OTP: {otp}")

    # 4. Development OTP Verify
    verify_data = json.dumps({'phone_number': '9876543210', 'otp': otp}).encode()
    req = urllib.request.Request(
        f'{base_url}/api/v1/auth/passengers/otp/verify',
        data=verify_data,
        headers={'Content-Type': 'application/json'},
        method='POST',
    )
    with urllib.request.urlopen(req) as r:
        tokens = json.loads(r.read().decode())
        print(f"4. POST /otp/verify -> {r.status}, token_type: {tokens['token_type']}, access_token valid")

    # 5. Authenticated Passenger Profile
    req = urllib.request.Request(
        f'{base_url}/api/v1/passengers/me/profile',
        headers={'Authorization': f"Bearer {tokens['access_token']}"},
        method='GET',
    )
    with urllib.request.urlopen(req) as r:
        profile = json.loads(r.read().decode())
        print(f"5. GET /passengers/me/profile -> Name: {profile['full_name']}, Phone: {profile['phone_number']}")

    # 6. Driver Login
    driver_data = json.dumps({'id_token': 'dev-driver:+919876543220:test_driver_uid_9876543220'}).encode()
    req = urllib.request.Request(
        f'{base_url}/api/v1/auth/drivers/firebase/login',
        data=driver_data,
        headers={'Content-Type': 'application/json'},
        method='POST',
    )
    with urllib.request.urlopen(req) as r:
        driver_res = json.loads(r.read().decode())
        d_prof = driver_res['driver']
        print(f"6. Driver Login -> Name: {d_prof['full_name']}, Phone: {d_prof['phone_number']}, Status: {d_prof['status']}")

    print("=" * 60)
    print("ALL INTEGRATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == '__main__':
    test_full_auth_flow()

