#!/usr/bin/env python3
"""
Test script for reservation note delete API
"""

import requests
import json

def test_delete_api():
    """Test the reservation note delete API"""
    url = "http://localhost:5001/api/rezervasyon-notu-sil"
    
    # First, create a test reservation note
    save_url = "http://localhost:5001/api/rezervasyon-notu-kaydet"
    save_data = {
        "urun_kodu": "API-TEST-URUN",
        "renk": "Mavi",
        "note": "Test rezervasyon notu"
    }
    
    print("1. Saving test reservation note...")
    save_response = requests.post(save_url, json=save_data)
    print(f"   Save response: {save_response.status_code} - {save_response.json()}")
    
    # Now test deleting the reservation note
    delete_data = {
        "urun_kodu": "API-TEST-URUN",
        "renk": "Mavi"
    }
    
    print("2. Testing reservation note deletion...")
    delete_response = requests.post(url, json=delete_data)
    print(f"   Delete response: {delete_response.status_code} - {delete_response.json()}")
    
    if delete_response.status_code == 200 and delete_response.json().get('success'):
        print("   ✅ Reservation note deletion successful")
    else:
        print("   ❌ Reservation note deletion failed")
        return False
    
    # Test deleting a non-existent reservation note
    print("3. Testing deletion of non-existent reservation note...")
    delete_data_nonexistent = {
        "urun_kodu": "NON-EXISTENT-URUN",
        "renk": "Yeşil"
    }
    
    delete_response_nonexistent = requests.post(url, json=delete_data_nonexistent)
    print(f"   Non-existent delete response: {delete_response_nonexistent.status_code} - {delete_response_nonexistent.json()}")
    
    # This should also return success (deleting non-existent is not an error)
    if delete_response_nonexistent.status_code == 200:
        print("   ✅ Non-existent reservation note deletion handled correctly")
    else:
        print("   ❌ Non-existent reservation note deletion not handled correctly")
        return False
    
    print("\n✅ All API tests passed!")
    return True

if __name__ == "__main__":
    try:
        success = test_delete_api()
        if success:
            print("\n✅ All API tests passed!")
        else:
            print("\n❌ Some API tests failed!")
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()