import json
import urllib.request
import urllib.error
from app.core.config import settings
from app.core.security import verify_token

LOGIN_URL = 'http://127.0.0.1:8000/api/v1/auth/login'
ME_URL = 'http://127.0.0.1:8000/api/v1/auth/me'

payload = json.dumps({"username":"admin@clinic.com","password":"admin123"}).encode('utf-8')
req = urllib.request.Request(LOGIN_URL, data=payload, headers={'Content-Type':'application/json'})

try:
    with urllib.request.urlopen(req) as resp:
        body = resp.read().decode('utf-8')
        print('LOGIN status', resp.status)
        data = json.loads(body)
        token = data.get('access_token')
        print('TOKEN:', token[:40] + '...')
except urllib.error.HTTPError as e:
    print('LOGIN failed', e.code, e.read().decode())
    raise SystemExit(1)

# decode token
decoded = verify_token(token)
print('DECODED TOKEN:', decoded)

# call /me
req2 = urllib.request.Request(ME_URL, headers={'Authorization': f'Bearer {token}'})
try:
    with urllib.request.urlopen(req2) as resp2:
        body2 = resp2.read().decode('utf-8')
        print('ME status', resp2.status)
        print('ME body', body2)
except urllib.error.HTTPError as e:
    print('ME failed', e.code, e.read().decode())
    raise SystemExit(1)
