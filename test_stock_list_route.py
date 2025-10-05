#!/usr/bin/env python3
"""
Test script to simulate what happens in the stock list route
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app import create_app
from utils.database import get_urun_rezervasyon_notu

def test_stock_list_logic():
    """Test the logic used in the stock list route"""
    print("=== Testing Stock List Route Logic ===")
    
    app = create_app()
    
    with app.app_context():
        from utils.database import get_db_connection
        
        db = get_db_connection()
        
        # Simulate what happens in the stock list route
        # Get a few sample stocks (same query as in routes/main.py)
        query = '''
            SELECT s.*, s.kritik_stok_siniri
            FROM stoklar s
            LIMIT 5
        '''
        stocks = db.execute(query).fetchall()
        
        print("Processing stocks as in stock_list route:")
        stocks_with_reservations = []
        for stock in stocks:
            stock_dict = dict(stock)
            # Ürün bazlı rezervasyon notunu al (same as in routes/main.py)
            rezervasyon_notu = get_urun_rezervasyon_notu(stock['urun_kodu'], stock['renk'] if stock['renk'] else None)
            stock_dict['rezervasyon_notu'] = rezervasyon_notu
            
            # Rezervasyon olup olmadığını kontrol et (same as in routes/main.py)
            stock_dict['has_reservations'] = rezervasyon_notu is not None and rezervasyon_notu.strip() != ''
            
            print(f"\nStock: {stock['urun_kodu']} (Color: {repr(stock['renk'])})")
            print(f"  Reservation note: {repr(rezervasyon_notu)}")
            print(f"  Has reservations: {stock_dict['has_reservations']}")
            
            stocks_with_reservations.append(stock_dict)
        
        print(f"\nTotal stocks processed: {len(stocks_with_reservations)}")

if __name__ == "__main__":
    test_stock_list_logic()