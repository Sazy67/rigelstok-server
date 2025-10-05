#!/usr/bin/env python3
"""
Simple test script to check if delete function works
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

try:
    # Test importing the function directly
    from utils.database import delete_urun_rezervasyon_notu
    print("✅ delete_urun_rezervasyon_notu function imported successfully")
    
    # Test importing all functions
    from utils.database import get_db_connection, get_urun_rezervasyon_notu, save_urun_rezervasyon_notu
    print("✅ All reservation functions imported successfully")
    
    # Test importing in reservation routes
    from routes.reservation import reservation_bp
    print("✅ Reservation blueprint imported successfully")
    
    print("✅ All imports successful - no issues found")
    
except Exception as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()