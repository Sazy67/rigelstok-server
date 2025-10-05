#!/usr/bin/env python3
"""
Debug script to check what data is being sent to the frontend template
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app import create_app
from utils.database import get_urun_rezervasyon_notu

def debug_template_data():
    """Debug what data is being sent to the template"""
    print("=== Debugging Template Data ===")
    
    app = create_app()
    
    with app.app_context():
        from utils.database import get_db_connection
        
        db = get_db_connection()
        
        # Get a few sample stocks
        stocks = db.execute('SELECT * FROM stoklar LIMIT 5').fetchall()
        
        print("Sample stocks from database:")
        for i, stock in enumerate(stocks, 1):
            print(f"\n--- Stock {i} ---")
            print(f"urun_kodu: {stock['urun_kodu']}")
            print(f"renk: {repr(stock['renk'])}")
            print(f"adet: {stock['adet']}")
            print(f"konum: {stock['konum']}")
            
            # Check what reservation note we get for this stock
            rezervasyon_notu = get_urun_rezervasyon_notu(stock['urun_kodu'], stock['renk'] if stock['renk'] else None)
            print(f"rezervasyon_notu from database: {repr(rezervasyon_notu)}")
        
        # Also check what's in the reservation notes table
        print("\n=== All Reservation Notes in Database ===")
        notes = db.execute('SELECT * FROM urun_rezervasyon_notlari').fetchall()
        
        if notes:
            for note in notes:
                print(f"ID: {note['id']}, Ürün: {note['urun_kodu']}, Renk: {repr(note['renk'])}, Not: {repr(note['rezervasyon_notu'])}")
        else:
            print("No reservation notes found in database")

if __name__ == "__main__":
    debug_template_data()