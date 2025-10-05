#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Debug script to check stock movements
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from utils.database import get_db_connection

def check_stock_movements():
    app = create_app()
    with app.app_context():
        try:
            db = get_db_connection()
            
            # Stok hareketleri tablosu var mı?
            table_exists = db.execute('''
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='stok_hareketleri'
            ''').fetchone()
            
            print(f"Tablo mevcut: {table_exists is not None}")
            
            if table_exists:
                # Toplam kayıt sayısı
                count = db.execute('SELECT COUNT(*) as total FROM stok_hareketleri').fetchone()
                print(f"Toplam hareket kaydı: {count['total']}")
                
                # İlk 3 kaydı göster
                movements = db.execute('''
                    SELECT urun_kodu, hareket_tipi, miktar, tarih 
                    FROM stok_hareketleri 
                    ORDER BY tarih DESC 
                    LIMIT 3
                ''').fetchall()
                
                print("İlk 3 hareket:")
                for mov in movements:
                    print(f"- {mov['urun_kodu']}: {mov['hareket_tipi']} {mov['miktar']} ({mov['tarih']})")
                
                # Test the stock movements query directly
                print("\n=== Testing stock movements query ===")
                test_query = '''
                    SELECT COUNT(DISTINCT h.id) as total 
                    FROM stok_hareketleri h
                    WHERE 1=1
                '''
                result = db.execute(test_query).fetchone()
                print(f"Count result: {result}")
                print(f"Count value: {result['total'] if result else 'None'}")
                
                # Test movements with details
                movements_detail_query = '''
                    SELECT DISTINCT h.id, h.urun_kodu, h.hareket_tipi, h.miktar, 
                           h.onceki_miktar, h.yeni_miktar, h.konum, h.aciklama, 
                           h.kullanici, h.tarih,
                           (SELECT s2.urun_adi FROM stoklar s2 WHERE s2.urun_kodu = h.urun_kodu LIMIT 1) as urun_adi,
                           DATE(h.tarih) as tarih_str,
                           TIME(h.tarih) as saat_str
                    FROM stok_hareketleri h
                    WHERE 1=1
                    ORDER BY h.tarih DESC
                    LIMIT 5
                '''
                detailed_movements = db.execute(movements_detail_query).fetchall()
                print(f"\nDetailed movements count: {len(detailed_movements)}")
                for mov in detailed_movements:
                    mov_dict = dict(mov)
                    print(f"Movement: {mov_dict}")
                
                # Stoklar tablosunda kayıt var mı?
                stocks_count = db.execute('SELECT COUNT(*) as total FROM stoklar').fetchone()
                print(f"\nToplam stok kaydı: {stocks_count['total']}")
                
                # Örnek stok kayıtları
                stocks = db.execute('''
                    SELECT urun_kodu, urun_adi, adet, konum 
                    FROM stoklar 
                    LIMIT 3
                ''').fetchall()
                
                print("İlk 3 stok:")
                for stock in stocks:
                    print(f"- {stock['urun_kodu']}: {stock['urun_adi']} - {stock['adet']} adet ({stock['konum']})")
            
            db.close()
            
        except Exception as e:
            print(f"Hata: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    check_stock_movements()