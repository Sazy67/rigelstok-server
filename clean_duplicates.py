from app import create_app
from utils.database import get_direct_connection

app = create_app()

with app.app_context():
    db = get_direct_connection()
    
    # Önce tekrarlayan kayıtları temizleyelim
    # Aynı ürün kodu ve renk kombinasyonundan sadece birini tutalım (en yeni olanı)
    db.execute('''
        DELETE FROM urun_rezervasyon_notlari
        WHERE id NOT IN (
            SELECT MAX(id)
            FROM urun_rezervasyon_notlari
            GROUP BY urun_kodu, COALESCE(renk, '')
        )
    ''')
    
    db.commit()
    print("Tekrarlayan kayıtlar temizlendi")
    
    # Şimdi UNIQUE indeks oluştur
    try:
        db.execute('DROP INDEX IF EXISTS idx_urun_rezervasyon_unique')
        db.execute('CREATE UNIQUE INDEX idx_urun_rezervasyon_unique ON urun_rezervasyon_notlari(urun_kodu, COALESCE(renk, ""))')
        db.commit()
        print("UNIQUE indeks oluşturuldu")
    except Exception as e:
        print(f"UNIQUE indeks oluşturulurken hata: {e}")