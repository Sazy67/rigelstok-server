#!/usr/bin/env python3
"""
Test script to verify the reservation API endpoints
"""

import sys
import os
import json
from unittest.mock import Mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app import create_app

def test_reservation_api():
    """Test the reservation API endpoints directly"""
    print("=== Testing Reservation API Endpoints ===")
    
    app = create_app()
    client = app.test_client()
    
    with app.app_context():
        # Test data
        test_cases = [
            {
                "name": "Product with color",
                "data": {
                    "urun_kodu": "API-TEST-001",
                    "renk": "Kırmızı",
                    "note": "API test note with color"
                }
            },
            {
                "name": "Product with empty color",
                "data": {
                    "urun_kodu": "API-TEST-002",
                    "renk": "",
                    "note": "API test note with empty color"
                }
            },
            {
                "name": "Product with null color",
                "data": {
                    "urun_kodu": "API-TEST-003",
                    "renk": None,
                    "note": "API test note with null color"
                }
            }
        ]
        
        for test_case in test_cases:
            print(f"\n--- {test_case['name']} ---")
            data = test_case['data']
            urun_kodu = data['urun_kodu']
            renk = data['renk']
            note = data['note']
            
            print(f"Sending data: {data}")
            
            # Test saving
            print("Testing save endpoint...")
            save_response = client.post(
                '/api/rezervasyon-notu-kaydet',
                data=json.dumps(data),
                content_type='application/json'
            )
            
            print(f"Save response status: {save_response.status_code}")
            save_data = json.loads(save_response.data)
            print(f"Save response data: {save_data}")
            
            if save_data.get('success'):
                print("✓ Save successful")
                
                # Test retrieving
                print("Testing retrieve endpoint...")
                get_params = f"urun_kodu={urun_kodu}"
                if renk is not None:
                    get_params += f"&renk={renk}"
                    
                get_response = client.get(f'/api/rezervasyon-notu-getir?{get_params}')
                print(f"Get response status: {get_response.status_code}")
                get_data = json.loads(get_response.data)
                print(f"Get response data: {get_data}")
                
                if get_data.get('success') and get_data.get('rezervasyon_notu') == note:
                    print("✓ Retrieve successful")
                else:
                    print("✗ Retrieve failed")
                    print(f"  Expected: {repr(note)}")
                    print(f"  Got: {repr(get_data.get('rezervasyon_notu'))}")
            else:
                print("✗ Save failed")

if __name__ == "__main__":
    test_reservation_api()