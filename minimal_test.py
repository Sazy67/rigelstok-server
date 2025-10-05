#!/usr/bin/env python3
"""
Minimal test to verify delete functionality
"""

import os
import sys
import sqlite3

# Add the project directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

def test_delete_directly():
    """Test delete functionality directly with SQLite"""
    try:
        # Connect directly to the database
        db_path = 'stok_takip_dev.db'
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        
        # Create test data
        print("1. Creating test reservation note...")
        conn.execute('''
            INSERT OR REPLACE INTO urun_rezervasyon_notlari 
            (urun_kodu, renk, rezervasyon_notu) 
            VALUES (?, ?, ?)
        ''', ('TEST-URUN', 'Kırmızı', 'Test notu'))
        conn.commit()
        
        # Verify it was created
        result = conn.execute('''
            SELECT * FROM urun_rezervasyon_notlari 
            WHERE urun_kodu = ? AND renk = ?
        ''', ('TEST-URUN', 'Kırmızı')).fetchone()
        
        if result:
            print("   ✅ Test reservation note created successfully")
        else:
            print("   ❌ Failed to create test reservation note")
            return False
        
        # Test the delete operation directly
        print("2. Testing delete operation...")
        conn.execute('''
            DELETE FROM urun_rezervasyon_notlari 
            WHERE urun_kodu = ? AND renk = ?
        ''', ('TEST-URUN', 'Kırmızı'))
        conn.commit()
        
        # Verify it was deleted
        result = conn.execute('''
            SELECT * FROM urun_rezervasyon_notlari 
            WHERE urun_kodu = ? AND renk = ?
        ''', ('TEST-URUN', 'Kırmızı')).fetchone()
        
        if result is None:
            print("   ✅ Test reservation note deleted successfully")
            print("✅ All direct database tests passed!")
            return True
        else:
            print("   ❌ Failed to delete test reservation note")
            return False
        
    except Exception as e:
        print(f"❌ Direct database test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    success = test_delete_directly()
    if success:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)