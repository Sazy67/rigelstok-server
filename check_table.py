from app import create_app
from utils.database import get_direct_connection

app = create_app()

with app.app_context():
    db = get_direct_connection()
    print('Tablo yapısı:')
    cols = db.execute('PRAGMA table_info(urun_rezervasyon_notlari)').fetchall()
    for col in cols:
        print(dict(col))
    
    print('\nİndeksler:')
    indexes = db.execute("SELECT name, sql FROM sqlite_master WHERE type='index' AND tbl_name='urun_rezervasyon_notlari'").fetchall()
    for idx in indexes:
        print(dict(idx))