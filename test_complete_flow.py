#!/usr/bin/env python3
"""
Test script to simulate the complete flow of saving a reservation note through the web interface
"""

import sys
import os
import requests
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

def test_complete_flow():
    """Test the complete flow of saving and retrieving a reservation note"""
    print("=== Testing Complete Flow ===")
    
    # Use the actual running server
    base_url = "http://127.0.0.1:5001"
    
    # Test data - using a real product from the database
    test_data = {
        "urun_kodu": "1031",  # This is a real product code from the logs
        "renk": "PRES",       # This is a real color from the logs
        "note": "Test reservation note through complete flow"
    }
    
    print(f"Testing with product: {test_data['urun_kodu']}")
    print(f"Color: {test_data['renk']}")
    print(f"Note: {test_data['note']}")
    
    # Save the reservation note
    print("\n1. Saving reservation note...")
    save_response = requests.post(
        f"{base_url}/api/rezervasyon-notu-kaydet",
        json=test_data
    )
    
    print(f"Save response status: {save_response.status_code}")
    save_data = save_response.json()
    print(f"Save response data: {save_data}")
    
    if save_data.get('success'):
        print("✓ Save successful")
        
        # Retrieve the note
        print("\n2. Retrieving reservation note...")
        get_params = {
            "urun_kodu": test_data['urun_kodu'],
            "renk": test_data['renk']
        }
        get_response = requests.get(
            f"{base_url}/api/rezervasyon-notu-getir",
            params=get_params
        )
        
        print(f"Get response status: {get_response.status_code}")
        get_data = get_response.json()
        print(f"Get response data: {get_data}")
        
        if get_data.get('success') and get_data.get('rezervasyon_notu') == test_data['note']:
            print("✓ Retrieve successful")
            print(f"✓ Note correctly saved and retrieved: {get_data.get('rezervasyon_notu')}")
        else:
            print("✗ Retrieve failed")
            print(f"  Expected: {repr(test_data['note'])}")
            print(f"  Got: {repr(get_data.get('rezervasyon_notu'))}")
    else:
        print("✗ Save failed")
        print(f"  Error: {save_data.get('message')}")

if __name__ == "__main__":
    test_complete_flow()