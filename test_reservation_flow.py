#!/usr/bin/env python3
"""
Test script to simulate the complete reservation note flow from frontend to database
"""

import sys
import os
import json
from unittest.mock import Mock

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app import create_app
from utils.database import (
    save_urun_rezervasyon_notu, 
    get_urun_rezervasyon_notu, 
    delete_urun_rezervasyon_notu
)

def test_reservation_flow():
    """Test the complete reservation note flow"""
    print("=== Testing Reservation Note Flow ===")
    
    # Create Flask app context
    app = create_app()
    
    with app.app_context():
        # Test data - using a real product code that might be having issues
        test_cases = [
            {
                "urun_kodu": "TEST-PRODUCT-001",
                "renk": "Kırmızı",
                "note": "Test reservation note with color"
            },
            {
                "urun_kodu": "TEST-PRODUCT-002",
                "renk": None,
                "note": "Test reservation note without color"
            },
            {
                "urun_kodu": "TEST-PRODUCT-003",
                "renk": "",
                "note": "Test reservation note with empty color"
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n--- Test Case {i} ---")
            urun_kodu = test_case["urun_kodu"]
            renk = test_case["renk"]
            note = test_case["note"]
            
            print(f"Product: {urun_kodu}")
            print(f"Color: {repr(renk)}")
            print(f"Note: {note}")
            
            # Delete any existing note first
            print("Deleting any existing note...")
            delete_result = delete_urun_rezervasyon_notu(urun_kodu, renk)
            print(f"Delete result: {delete_result}")
            
            # Save the reservation note
            print("Saving reservation note...")
            save_result = save_urun_rezervasyon_notu(urun_kodu, renk, note)
            print(f"Save result: {save_result}")
            
            # Verify by retrieving
            print("Retrieving saved note...")
            retrieved_note = get_urun_rezervasyon_notu(urun_kodu, renk)
            print(f"Retrieved note: {repr(retrieved_note)}")
            
            # Check if they match
            if retrieved_note == note:
                print("✓ SUCCESS: Note was saved and retrieved correctly")
            else:
                print("✗ FAILURE: Note mismatch")
                print(f"  Expected: {repr(note)}")
                print(f"  Got: {repr(retrieved_note)}")
            
            print("-" * 40)

def simulate_api_call():
    """Simulate what happens in the API endpoint"""
    print("\n=== Simulating API Call ===")
    
    app = create_app()
    
    with app.app_context():
        # Simulate the data that comes from the frontend
        test_data = {
            "urun_kodu": "SIM-TEST-001",
            "renk": "Mavi",
            "note": "Simulated API call note"
        }
        
        print(f"Simulating API request with data: {test_data}")
        
        # Process the data like the API does
        urun_kodu = test_data.get('urun_kodu', '').strip()
        renk = test_data.get('renk', '').strip() if test_data.get('renk') else None
        note = test_data.get('note', '').strip()
        
        print(f"Processed data - Product: '{urun_kodu}', Color: '{renk}', Note: '{note}'")
        
        # Delete any existing note
        delete_urun_rezervasyon_notu(urun_kodu, renk)
        
        # Save the note
        result = save_urun_rezervasyon_notu(urun_kodu, renk, note)
        print(f"Save function returned: {result}")
        
        # Verify
        saved_note = get_urun_rezervasyon_notu(urun_kodu, renk)
        print(f"Verification - Retrieved note: '{saved_note}'")
        
        if result and saved_note == note:
            print("✓ API simulation successful")
        else:
            print("✗ API simulation failed")

if __name__ == "__main__":
    test_reservation_flow()
    simulate_api_call()
    print("\n=== Test Complete ===")