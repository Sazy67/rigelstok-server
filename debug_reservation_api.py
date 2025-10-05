import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

# Set up Flask application context
from app import create_app
app = create_app()

with app.app_context():
    from utils.database import (
        save_urun_rezervasyon_notu, 
        get_urun_rezervasyon_notu
    )

    def test_reservation_api_directly():
        """Test the reservation API functions directly"""
        print("Testing reservation API functions directly...")
        
        # Test data
        test_urun_kodu = "DEBUG-TEST-001"
        test_renk = "Yeşil"
        test_note = "Debug test notu"
        
        # Save reservation note directly using the database function
        print(f"Saving reservation note directly...")
        result = save_urun_rezervasyon_notu(test_urun_kodu, test_renk, test_note)
        print(f"Save result: {result}")
        
        if result:
            print("✅ Direct save successful")
            
            # Retrieve reservation note
            print(f"Retrieving reservation note...")
            retrieved_note = get_urun_rezervasyon_notu(test_urun_kodu, test_renk)
            print(f"Retrieved note: {retrieved_note}")
            
            if retrieved_note == test_note:
                print("✅ Direct retrieve successful")
                return True
            else:
                print("❌ Direct retrieve failed")
                return False
        else:
            print("❌ Direct save failed")
            return False

    if __name__ == "__main__":
        try:
            success = test_reservation_api_directly()
            if success:
                print("\n✅ Direct API test passed!")
                sys.exit(0)
            else:
                print("\n❌ Direct API test failed!")
                sys.exit(1)
        except Exception as e:
            print(f"\n❌ Direct API test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)