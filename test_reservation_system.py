#!/usr/bin/env python3
"""
Test script for the reservation system
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

# Set up Flask application context
from app import create_app
app = create_app()

with app.app_context():
    from utils.database import (
        init_db, 
        save_urun_rezervasyon_notu, 
        get_urun_rezervasyon_notu,
        get_db_connection
    )

    def test_reservation_system():
        """Test the product-based reservation system"""
        print("Testing product-based reservation system...")
        
        # Initialize database
        init_db()
        print("Database initialized successfully")
        
        # Test data
        test_urun_kodu = "TEST-URUN-001"
        test_renk = "Kırmızı"
        test_note = "Bu bir test rezervasyon notudur"
        
        # Save reservation note
        print(f"Saving reservation note for product {test_urun_kodu}...")
        result = save_urun_rezervasyon_notu(test_urun_kodu, test_renk, test_note)
        if result:
            print("Reservation note saved successfully")
        else:
            print("Failed to save reservation note")
            return False
        
        # Retrieve reservation note
        print(f"Retrieving reservation note for product {test_urun_kodu}...")
        retrieved_note = get_urun_rezervasyon_notu(test_urun_kodu, test_renk)
        
        if retrieved_note == test_note:
            print("Reservation note retrieved successfully and matches")
            print(f"Retrieved note: {retrieved_note}")
        else:
            print("Failed to retrieve correct reservation note")
            print(f"Expected: {test_note}")
            print(f"Got: {retrieved_note}")
            return False
        
        # Test updating reservation note
        print("Testing reservation note update...")
        updated_note = "Bu güncellenmiş bir test rezervasyon notudur"
        result = save_urun_rezervasyon_notu(test_urun_kodu, test_renk, updated_note)
        
        if result:
            print("Reservation note updated successfully")
            # Verify update
            retrieved_note = get_urun_rezervasyon_notu(test_urun_kodu, test_renk)
            if retrieved_note == updated_note:
                print("Reservation note update verified successfully")
            else:
                print("Failed to verify reservation note update")
                return False
        else:
            print("Failed to update reservation note")
            return False
        
        # Test with None color
        print("Testing reservation note with None color...")
        test_urun_kodu_2 = "TEST-URUN-002"
        result = save_urun_rezervasyon_notu(test_urun_kodu_2, None, "Renksiz ürün notu")
        
        if result:
            retrieved_note = get_urun_rezervasyon_notu(test_urun_kodu_2, None)
            if retrieved_note == "Renksiz ürün notu":
                print("Reservation note with None color works correctly")
            else:
                print("Failed to handle reservation note with None color")
                return False
        else:
            print("Failed to save reservation note with None color")
            return False
        
        print("All tests passed successfully!")
        return True

    if __name__ == "__main__":
        try:
            success = test_reservation_system()
            if success:
                print("\n✅ All tests passed!")
                sys.exit(0)
            else:
                print("\n❌ Some tests failed!")
                sys.exit(1)
        except Exception as e:
            print(f"\n❌ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)