from app import create_app
from utils.database import save_urun_rezervasyon_notu, get_urun_rezervasyon_notu

app = create_app()

with app.app_context():
    # Test saving a reservation note
    result = save_urun_rezervasyon_notu("TEST001", "Kırmızı", "Bu bir test notudur")
    print(f"Save result: {result}")
    
    # Test retrieving the reservation note
    note = get_urun_rezervasyon_notu("TEST001", "Kırmızı")
    print(f"Retrieved note: {note}")
    
    # Test saving without color
    result2 = save_urun_rezervasyon_notu("TEST002", None, "Renksiz ürün notu")
    print(f"Save result (no color): {result2}")
    
    # Test retrieving the reservation note without color
    note2 = get_urun_rezervasyon_notu("TEST002", None)
    print(f"Retrieved note (no color): {note2}")