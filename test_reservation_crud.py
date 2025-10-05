#!/usr/bin/env python3
"""
Test script for reservation note CRUD operations
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
        delete_urun_rezervasyon_notu
    )

    def test_reservation_crud():
        """Test reservation note CRUD operations"""
        print("Testing reservation note CRUD operations...")
        
        # Initialize database
        init_db()
        print("Database initialized successfully")
        
        # Test data
        test_urun_kodu = "TEST-URUN-003"
        test_renk = "Mavi"
        test_note = "Bu bir test rezervasyon notudur"
        
        # 1. Save reservation note
        print(f"1. Saving reservation note for product {test_urun_kodu}...")
        result = save_urun_rezervasyon_notu(test_urun_kodu, test_renk, test_note)
        if result:
            print("   Reservation note saved successfully")
        else:
            print("   Failed to save reservation note")
            return False
        
        # 2. Retrieve reservation note
        print(f"2. Retrieving reservation note for product {test_urun_kodu}...")
        retrieved_note = get_urun_rezervasyon_notu(test_urun_kodu, test_renk)
        
        if retrieved_note == test_note:
            print("   Reservation note retrieved successfully and matches")
        else:
            print("   Failed to retrieve correct reservation note")
            print(f"   Expected: {test_note}")
            print(f"   Got: {retrieved_note}")
            return False
        
        # 3. Update reservation note
        print("3. Testing reservation note update...")
        updated_note = "Bu güncellenmiş bir test rezervasyon notudur"
        result = save_urun_rezervasyon_notu(test_urun_kodu, test_renk, updated_note)
        
        if result:
            print("   Reservation note updated successfully")
            # Verify update
            retrieved_note = get_urun_rezervasyon_notu(test_urun_kodu, test_renk)
            if retrieved_note == updated_note:
                print("   Reservation note update verified successfully")
            else:
                print("   Failed to verify reservation note update")
                return False
        else:
            print("   Failed to update reservation note")
            return False
        
        # 4. Delete reservation note
        print("4. Testing reservation note deletion...")
        result = delete_urun_rezervasyon_notu(test_urun_kodu, test_renk)
        
        if result:
            print("   Reservation note deleted successfully")
            # Verify deletion
            retrieved_note = get_urun_rezervasyon_notu(test_urun_kodu, test_renk)
            if retrieved_note is None:
                print("   Reservation note deletion verified successfully")
            else:
                print("   Failed to verify reservation note deletion")
                return False
        else:
            print("   Failed to delete reservation note")
            return False
        
        # 5. Test with None color
        print("5. Testing reservation operations with None color...")
        test_urun_kodu_2 = "TEST-URUN-004"
        result = save_urun_rezervasyon_notu(test_urun_kodu_2, None, "Renksiz ürün notu")
        
        if result:
            retrieved_note = get_urun_rezervasyon_notu(test_urun_kodu_2, None)
            if retrieved_note == "Renksiz ürün notu":
                print("   Reservation note with None color works correctly")
                
                # Test deletion with None color
                result = delete_urun_rezervasyon_notu(test_urun_kodu_2, None)
                if result:
                    print("   Reservation note with None color deleted successfully")
                else:
                    print("   Failed to delete reservation note with None color")
                    return False
            else:
                print("   Failed to handle reservation note with None color")
                return False
        else:
            print("   Failed to save reservation note with None color")
            return False
        
        print("All CRUD tests passed successfully!")
        return True

    if __name__ == "__main__":
        try:
            success = test_reservation_crud()
            if success:
                print("\n✅ All CRUD tests passed!")
                sys.exit(0)
            else:
                print("\n❌ Some CRUD tests failed!")
                sys.exit(1)
        except Exception as e:
            print(f"\n❌ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)