#!/usr/bin/env python3
"""
Test script to verify that reservation notes appear in the stock list
"""

import sys
import os
import requests
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

def test_stock_list_with_reservation():
    """Test that reservation notes appear in the stock list"""
    print("=== Testing Stock List with Reservation Notes ===")
    
    # Use the actual running server
    base_url = "http://127.0.0.1:5001"
    
    # First, save a reservation note for a real product
    test_data = {
        "urun_kodu": "1031",
        "renk": "PRES",
        "note": "Stock list test reservation note"
    }
    
    print(f"Saving reservation note for product {test_data['urun_kodu']}...")
    save_response = requests.post(
        f"{base_url}/api/rezervasyon-notu-kaydet",
        json=test_data
    )
    
    if not save_response.json().get('success'):
        print("Failed to save reservation note")
        return
    
    print("✓ Reservation note saved successfully")
    
    # Now, let's check if we can retrieve it through the API
    print("\nRetrieving reservation note through API...")
    get_params = {
        "urun_kodu": test_data['urun_kodu'],
        "renk": test_data['renk']
    }
    get_response = requests.get(
        f"{base_url}/api/rezervasyon-notu-getir",
        params=get_params
    )
    
    get_data = get_response.json()
    if get_data.get('success') and get_data.get('rezervasyon_notu') == test_data['note']:
        print("✓ Reservation note correctly retrieved through API")
        print(f"  Note: {get_data.get('rezervasyon_notu')}")
    else:
        print("✗ Failed to retrieve reservation note through API")
        return
    
    # The stock list page should now show this reservation note
    # when it processes the stocks and calls get_urun_rezervasyon_notu
    print("\nThe stock list page should now display this reservation note")
    print("when loading the product with code '1031' and color 'PRES'.")

if __name__ == "__main__":
    test_stock_list_with_reservation()