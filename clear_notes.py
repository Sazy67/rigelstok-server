from app import create_app
from utils.database import get_direct_connection

app = create_app()

with app.app_context():
    db = get_direct_connection()
    db.execute('DELETE FROM urun_rezervasyon_notlari')
    db.commit()
    print('Rezervasyon notları temizlendi')