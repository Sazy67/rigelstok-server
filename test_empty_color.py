#!/usr/bin/env python3
"""
Test script to verify handling of empty color values
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app import create_app
from utils.database import (
    save_urun_rezervasyon_notu, 
    get_urun_rezervasyon_notu, 
    delete_urun_rezervasyon_notu
)

def test_empty_color_handling():
    """Test how the system handles empty color values"""
    print("=== Testing Empty Color Handling ===")
    
    app = create_app()
    
    with app.app_context():
        # Test case 1: Product with empty color string
        urun_kodu = "TEST-EMPTY-COLOR"
        renk = ""  # Empty string
        note = "Test note with empty color"
        
        print(f"Test 1: Product {urun_kodu} with empty color string")
        print(f"  Color value: {repr(renk)}")
        print(f"  Color type: {type(renk)}")
        
        # Delete any existing note
        delete_urun_rezervasyon_notu(urun_kodu, renk)
        
        # Save note
        result = save_urun_rezervasyon_notu(urun_kodu, renk, note)
        print(f"  Save result: {result}")
        
        # Retrieve note
        retrieved = get_urun_rezervasyon_notu(urun_kodu, renk)
        print(f"  Retrieved note: {repr(retrieved)}")
        
        # Test case 2: Product with None color
        urun_kodu2 = "TEST-NONE-COLOR"
        renk2 = None
        note2 = "Test note with None color"
        
        print(f"\nTest 2: Product {urun_kodu2} with None color")
        print(f"  Color value: {repr(renk2)}")
        print(f"  Color type: {type(renk2)}")
        
        # Delete any existing note
        delete_urun_rezervasyon_notu(urun_kodu2, renk2)
        
        # Save note
        result2 = save_urun_rezervasyon_notu(urun_kodu2, renk2, note2)
        print(f"  Save result: {result2}")
        
        # Retrieve note
        retrieved2 = get_urun_rezervasyon_notu(urun_kodu2, renk2)
        print(f"  Retrieved note: {repr(retrieved2)}")
        
        # Test case 3: Retrieve with empty string when saved with None
        print(f"\nTest 3: Retrieving {urun_kodu2} with empty string (saved with None)")
        retrieved3 = get_urun_rezervasyon_notu(urun_kodu2, "")
        print(f"  Retrieved note: {repr(retrieved3)}")
        
        # Test case 4: Retrieve with None when saved with empty string
        print(f"\nTest 4: Retrieving {urun_kodu} with None (saved with empty string)")
        retrieved4 = get_urun_rezervasyon_notu(urun_kodu, None)
        print(f"  Retrieved note: {repr(retrieved4)}")

if __name__ == "__main__":
    test_empty_color_handling()