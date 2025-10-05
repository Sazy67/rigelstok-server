#!/usr/bin/env python3
"""
Test script for reservation note delete function at database level
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

    def test_delete_function():
        """Test reservation note delete function at database level"""
        print("Testing reservation note delete function at database level...")
        
        # Initialize database
        init_db()
        print("Database initialized successfully")
        
        # Test data
        test_urun_kodu = "DB-TEST-URUN"
        test_renk = "Sarı"
        test_note = "Veritabanı seviyesinde test notu"
        
        # 1. Save reservation note
        print(f"1. Saving reservation note for product {test_urun_kodu}...")
        result = save_urun_rezervasyon_notu(test_urun_kodu, test_renk, test_note)
        if result:
            print("   Reservation note saved successfully")
        else:
            print("   Failed to save reservation note")
            return False
        
        # 2. Verify reservation note exists
        print(f"2. Verifying reservation note exists...")
        retrieved_note = get_urun_rezervasyon_notu(test_urun_kodu, test_renk)
        if retrieved_note == test_note:
            print("   Reservation note verified successfully")
        else:
            print("   Failed to verify reservation note")
            return False
        
        # 3. Delete reservation note
        print(f"3. Deleting reservation note...")
        delete_result = delete_urun_rezervasyon_notu(test_urun_kodu, test_renk)
        if delete_result:
            print("   Reservation note deleted successfully")
        else:
            print("   Failed to delete reservation note")
            return False
        
        # 4. Verify reservation note is deleted
        print(f"4. Verifying reservation note is deleted...")
        retrieved_note_after_delete = get_urun_rezervasyon_notu(test_urun_kodu, test_renk)
        if retrieved_note_after_delete is None:
            print("   Reservation note deletion verified successfully")
            print("✅ All database level tests passed!")
            return True
        else:
            print("   Failed to verify reservation note deletion")
            print(f"   Expected: None")
            print(f"   Got: {retrieved_note_after_delete}")
            return False

    if __name__ == "__main__":
        try:
            success = test_delete_function()
            if success:
                print("\n✅ All database level tests passed!")
                sys.exit(0)
            else:
                print("\n❌ Some database level tests failed!")
                sys.exit(1)
        except Exception as e:
            print(f"\n❌ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)