from app import create_app
from utils.database import get_db_connection

app = create_app()

with app.app_context():
    db = get_db_connection()
    
    print("Tüm rezervasyon notları:")
    notes = db.execute('SELECT * FROM urun_rezervasyon_notlari').fetchall()
    
    if notes:
        for note in notes:
            print(f"ID: {note['id']}, Ürün: {note['urun_kodu']}, Renk: {note['renk']}, Not: {note['rezervasyon_notu']}")
    else:
        print("Veritabanında hiç rezervasyon notu bulunamadı.")