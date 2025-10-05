#!/usr/bin/env python3
"""
Script to drop the urun_rezervasyon_notlari table
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

# Set up Flask application context
from app import create_app
app = create_app()

with app.app_context():
    import sqlite3
    from utils.database import get_db_connection
    
    try:
        db = get_db_connection()
        db.execute('DROP TABLE IF EXISTS urun_rezervasyon_notlari')
        db.commit()
        print('Table dropped successfully')
    except Exception as e:
        print(f"Error dropping table: {e}")