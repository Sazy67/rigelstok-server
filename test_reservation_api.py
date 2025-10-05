import requests
import json

# Test the reservation note save API endpoint
url = "http://localhost:5001/api/rezervasyon-notu-kaydet"

# Test data
data = {
    "urun_kodu": "API_TEST001",
    "renk": "Mavi",
    "note": "Bu bir API test notudur"
}

headers = {
    "Content-Type": "application/json"
}

try:
    response = requests.post(url, data=json.dumps(data), headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")