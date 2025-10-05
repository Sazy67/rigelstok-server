#!/usr/bin/env python3
"""
Test script to save a reservation note for a real product and verify it can be retrieved
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

def test_real_product_reservation():
    """Test saving a reservation note for a real product"""
    print("=== Testing Real Product Reservation ===")
    
    app = create_app()
    
    with app.app_context():
        from utils.database import get_db_connection
        
        db = get_db_connection()
        
        # Get the first product from the database
        stock = db.execute('SELECT * FROM stoklar LIMIT 1').fetchone()
        
        if not stock:
            print("No stocks found in database")
            return
            
        urun_kodu = stock['urun_kodu']
        renk = stock['renk'] if stock['renk'] else None
        
        print(f"Testing with product: {urun_kodu}")
        print(f"Color: {repr(renk)}")
        
        # Delete any existing reservation note for this product
        print("Deleting any existing reservation note...")
        delete_urun_rezervasyon_notu(urun_kodu, renk)
        
        # Save a new reservation note
        test_note = "Test reservation note for real product"
        print(f"Saving reservation note: {test_note}")
        result = save_urun_rezervasyon_notu(urun_kodu, renk, test_note)
        print(f"Save result: {result}")
        
        # Verify by retrieving
        print("Retrieving saved note...")
        retrieved_note = get_urun_rezervasyon_notu(urun_kodu, renk)
        print(f"Retrieved note: {repr(retrieved_note)}")
        
        if retrieved_note == test_note:
            print("✓ SUCCESS: Note was saved and retrieved correctly")
        else:
            print("✗ FAILURE: Note mismatch")
            print(f"  Expected: {repr(test_note)}")
            print(f"  Got: {repr(retrieved_note)}")
        
        # Also check what's in the database directly
        print("\nChecking database directly...")
        if renk and renk.strip():
            db_note = db.execute(
                'SELECT rezervasyon_notu FROM urun_rezervasyon_notlari WHERE urun_kodu = ? AND renk = ?',
                (urun_kodu, renk)
            ).fetchone()
        else:
            db_note = db.execute(
                'SELECT rezervasyon_notu FROM urun_rezervasyon_notlari WHERE urun_kodu = ? AND (renk IS NULL OR renk = ?)',
                (urun_kodu, '')
            ).fetchone()
        
        if db_note:
            print(f"Direct database query result: {repr(db_note['rezervasyon_notu'])}")
        else:
            print("No note found in database with direct query")

if __name__ == "__main__":
    test_real_product_reservation()