import requests
import json

# Test the reservation note save API endpoint with more detailed debugging
url = "http://localhost:5001/api/rezervasyon-notu-kaydet"

# Test data
test_cases = [
    {
        "name": "Test with color",
        "data": {
            "urun_kodu": "API_TEST001",
            "renk": "Mavi",
            "note": "Bu bir API test notudur"
        }
    },
    {
        "name": "Test without color",
        "data": {
            "urun_kodu": "API_TEST002",
            "renk": "",
            "note": "Renksiz ürün testi"
        }
    },
    {
        "name": "Test with null color",
        "data": {
            "urun_kodu": "API_TEST003",
            "renk": None,
            "note": "Null renk testi"
        }
    }
]

headers = {
    "Content-Type": "application/json"
}

for test_case in test_cases:
    print(f"\n=== {test_case['name']} ===")
    print(f"Sending data: {test_case['data']}")
    
    try:
        response = requests.post(url, data=json.dumps(test_case['data']), headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        if response.status_code == 200:
            try:
                json_response = response.json()
                print(f"JSON Response: {json_response}")
            except:
                print("Response is not valid JSON")
    except Exception as e:
        print(f"Error: {e}")