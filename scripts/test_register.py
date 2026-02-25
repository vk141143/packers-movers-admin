import json
import urllib.request

url = 'http://127.0.0.1:8001/api/auth/register/admin'
payload = {
    "email": "bindugd2001@gmail.com",
    "full_name": "bindu",
    "password": "Bindu@123",
    "phone_number": "+918431135145"
}

data = json.dumps(payload).encode('utf-8')
req = urllib.request.Request(url, data=data, headers={'Content-Type':'application/json'})
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        print('STATUS', resp.status)
        print(resp.read().decode())
except Exception as e:
    import traceback
    traceback.print_exc()
    print('ERROR', e)
