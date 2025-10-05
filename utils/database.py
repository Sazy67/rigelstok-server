# WSGI configuration for your app
import sys
import os

# Proje dizininizi sys.path'e ekleyin
project_home = '/home/kullanici-adiniz/rigelstok-server-deployment'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path
import sqlite3
import threading
from flask import current_app, g
from contextlib import contextmanager
import logging

# Thread-safe connection pool
_connection_pool = threading.local()

# Logger setup
logger = logging.getLogger(__name__)

def get_db_connection():
    """Veritabanı bağlantısı al - Flask context içinde"""
    if 'db' not in g:
        db_path = current_app.config.get('DATABASE_PATH', 'stok_takip_dev.db')
        g.db = sqlite3.connect(
            db_path,
            check_same_thread=False,
            timeout=20.0
        )
        g.db.row_factory = sqlite3.Row
        # WAL mode for better concurrency
        g.db.execute('PRAGMA journal_mode=WAL')
        # Foreign key support
        g.db.execute('PRAGMA foreign_keys=ON')
        g.db.commit()
    return g.db

def get_direct_connection():
    """Direct veritabanı bağlantısı - Flask context dışında kullanım için"""
    if not hasattr(_connection_pool, 'connection'):
        db_path = os.environ.get('DATABASE_PATH', 'stok_takip_dev.db')
        _connection_pool.connection = sqlite3.connect(
            db_path,
            check_same_thread=False,
            timeout=20.0
        )
        _connection_pool.connection.row_factory = sqlite3.Row
        _connection_pool.connection.execute('PRAGMA journal_mode=WAL')
        _connection_pool.connection.execute('PRAGMA foreign_keys=ON')
        _connection_pool.connection.commit()
    return _connection_pool.connection

@contextmanager
def get_db_transaction():
    """Transaction context manager"""
    db = get_db_connection()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise

def close_db(error):
    """Veritabanı bağlantısını kapat"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def save_urun_rezervasyon_notu(urun_kodu, renk, rezervasyon_notu):
    """Ürün bazlı rezervasyon notu kaydet"""
    db = get_db_connection()
    
    try:
        logger.info(f"Saving reservation note for product: {urun_kodu}, color: {renk}, note: {rezervasyon_notu}")
        
        # Önce var mı kontrol et - daha tutarlı bir şekilde kontrol et
        if renk and renk.strip():
            # Renk varsa ve boş değilse
            existing = db.execute(
                'SELECT id FROM urun_rezervasyon_notlari WHERE urun_kodu = ? AND renk = ?',
                (urun_kodu, renk)
            ).fetchone()
            logger.info(f"Checking existing record with color - Found: {existing is not None}")
        else:
            # Renk yoksa veya boşsa NULL ile kontrol et
            existing = db.execute(
                'SELECT id FROM urun_rezervasyon_notlari WHERE urun_kodu = ? AND (renk IS NULL OR renk = ?)',
                (urun_kodu, '')
            ).fetchone()
            logger.info(f"Checking existing record without color - Found: {existing is not None}")
        
        if existing:
            # Güncelle
            if renk and renk.strip():
                result = db.execute(
                    'UPDATE urun_rezervasyon_notlari SET rezervasyon_notu = ?, guncelleme_tarihi = CURRENT_TIMESTAMP WHERE urun_kodu = ? AND renk = ?',
                    (rezervasyon_notu, urun_kodu, renk)
                )
                logger.info(f"Updated existing reservation note for {urun_kodu} with color {renk}, rows affected: {result.rowcount}")
            else:
                result = db.execute(
                    'UPDATE urun_rezervasyon_notlari SET rezervasyon_notu = ?, guncelleme_tarihi = CURRENT_TIMESTAMP WHERE urun_kodu = ? AND (renk IS NULL OR renk = ?)',
                    (rezervasyon_notu, urun_kodu, '')
                )
                logger.info(f"Updated existing reservation note for {urun_kodu} without color, rows affected: {result.rowcount}")
        else:
            # Yeni ekle
            result = db.execute(
                'INSERT INTO urun_rezervasyon_notlari (urun_kodu, renk, rezervasyon_notu) VALUES (?, ?, ?)',
                (urun_kodu, renk if renk and renk.strip() else None, rezervasyon_notu)
            )
            logger.info(f"Inserted new reservation note for {urun_kodu} with color {renk}, lastrowid: {result.lastrowid}")
        
        db.commit()
        logger.info(f"Successfully saved reservation note for {urun_kodu}")
        return True
    except Exception as e:
        logger.error(f"Ürün rezervasyon notu kaydetme hatası: {str(e)}")
        logger.error(f"Traceback: ", exc_info=True)
        return False

def get_urun_rezervasyon_notu(urun_kodu, renk=None):
    """Ürün bazlı rezervasyon notu getir"""
    db = get_db_connection()
    
    try:
        logger.info(f"Retrieving reservation note for product: {urun_kodu}, color: {renk}")
        
        if renk and renk.strip():
            # Renk varsa ve boş değilse
            result = db.execute(
                'SELECT rezervasyon_notu FROM urun_rezervasyon_notlari WHERE urun_kodu = ? AND renk = ?',
                (urun_kodu, renk)
            ).fetchone()
        else:
            # Renk yoksa veya boşsa NULL ile kontrol et
            result = db.execute(
                'SELECT rezervasyon_notu FROM urun_rezervasyon_notlari WHERE urun_kodu = ? AND (renk IS NULL OR renk = ?)',
                (urun_kodu, '')
            ).fetchone()
        
        if result:
            logger.info(f"Found reservation note: {result['rezervasyon_notu']}")
            return result['rezervasyon_notu']
        else:
            logger.info("No reservation note found")
            return None
    except Exception as e:
        logger.error(f"Ürün rezervasyon notu getirme hatası: {str(e)}")
        return None

def delete_urun_rezervasyon_notu(urun_kodu, renk=None):
    """Ürün bazlı rezervasyon notu sil"""
    db = get_db_connection()
    
    try:
        if renk and renk.strip():
            # Renk varsa ve boş değilse
            db.execute(
                'DELETE FROM urun_rezervasyon_notlari WHERE urun_kodu = ? AND renk = ?',
                (urun_kodu, renk)
            )
        else:
            # Renk yoksa veya boşsa NULL ile kontrol et
            db.execute(
                'DELETE FROM urun_rezervasyon_notlari WHERE urun_kodu = ? AND (renk IS NULL OR renk = ?)',
                (urun_kodu, '')
            )
        
        db.commit()
        return True
    except Exception as e:
        logger.error(f"Ürün rezervasyon notu silme hatası: {str(e)}")
        return False

def migrate_rezervasyon_notlari():
    """Mevcut stoklardaki rezervasyon notlarını yeni tabloya taşır"""
    db = get_db_connection()
    
    try:
        # Aynı ürün kodu ve renk kombinasyonlarına sahip kayıtlardan birini al
        records = db.execute('''
            SELECT urun_kodu, renk, rezervasyon_notu
            FROM stoklar
            WHERE rezervasyon_notu IS NOT NULL AND rezervasyon_notu != ''
            GROUP BY urun_kodu, renk
        ''').fetchall()
        
        for record in records:
            # Yeni tabloya ekle
            try:
                db.execute(
                    'INSERT OR IGNORE INTO urun_rezervasyon_notlari (urun_kodu, renk, rezervasyon_notu) VALUES (?, ?, ?)',
                    (record['urun_kodu'], record['renk'], record['rezervasyon_notu'])
                )
            except Exception as e:
                logger.error(f"Rezervasyon notu taşıma hatası ({record['urun_kodu']}): {str(e)}")
        
        db.commit()
        logger.info(f"{len(records)} adet rezervasyon notu yeni tabloya taşındı")
        return True
    except Exception as e:
        logger.error(f"Rezervasyon notları taşıma hatası: {str(e)}")
        return False

def init_db():
    """Veritabanını başlat"""
    db = get_db_connection()
    
    # Stoklar tablosu
    db.execute('''
        CREATE TABLE IF NOT EXISTS stoklar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            urun_kodu TEXT NOT NULL,
            urun_adi TEXT NOT NULL,
            sistem_seri TEXT,
            renk TEXT,
            uzunluk INTEGER,
            mt_kg REAL,
            boy_kg REAL,
            adet INTEGER DEFAULT 0,
            toplam_kg REAL,
            konum TEXT,
            kritik_stok_siniri INTEGER DEFAULT 5,
            rezervasyon_notu TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(urun_kodu, renk, konum)
        )
    ''')
    
    # Stok hareketleri tablosu
    db.execute('''
        CREATE TABLE IF NOT EXISTS stok_hareketleri (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            urun_kodu TEXT NOT NULL,
            hareket_tipi TEXT NOT NULL CHECK (hareket_tipi IN ('GIRIS', 'CIKIS', 'TRANSFER')),
            miktar INTEGER NOT NULL CHECK (miktar > 0),
            onceki_miktar INTEGER,
            yeni_miktar INTEGER,
            konum TEXT,
            aciklama TEXT,
            kullanici TEXT,
            tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (urun_kodu) REFERENCES stoklar(urun_kodu)
        )
    ''')
    
    # Stoklar tablosu indeksleri
    db.execute('CREATE INDEX IF NOT EXISTS idx_stoklar_urun_kodu ON stoklar(urun_kodu)')
    db.execute('CREATE INDEX IF NOT EXISTS idx_stoklar_konum ON stoklar(konum)')
    db.execute('CREATE INDEX IF NOT EXISTS idx_stoklar_urun_adi ON stoklar(urun_adi)')
    db.execute('CREATE INDEX IF NOT EXISTS idx_stoklar_renk ON stoklar(renk)')
    db.execute('CREATE INDEX IF NOT EXISTS idx_stoklar_created_at ON stoklar(created_at)')
    
    # Stok hareketleri tablosu indeksleri
    db.execute('CREATE INDEX IF NOT EXISTS idx_hareketler_urun_kodu ON stok_hareketleri(urun_kodu)')
    db.execute('CREATE INDEX IF NOT EXISTS idx_hareketler_tarih ON stok_hareketleri(tarih)')
    db.execute('CREATE INDEX IF NOT EXISTS idx_hareketler_hareket_tipi ON stok_hareketleri(hareket_tipi)')
    
    # Ürün bazlı rezervasyon notları tablosu
    db.execute('''
        CREATE TABLE IF NOT EXISTS urun_rezervasyon_notlari (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            urun_kodu TEXT NOT NULL,
            renk TEXT,
            rezervasyon_notu TEXT,
            olusturulma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            guncelleme_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Ürün bazlı rezervasyon notları indeksi
    db.execute('CREATE INDEX IF NOT EXISTS idx_urun_rezervasyon_urun_kodu ON urun_rezervasyon_notlari(urun_kodu)')
    db.execute('CREATE INDEX IF NOT EXISTS idx_urun_rezervasyon_renk ON urun_rezervasyon_notlari(renk)')
    
    # Ürün bazlı rezervasyon notları için UNIQUE indeks (ürün kodu + renk kombinasyonu için)
    db.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_urun_rezervasyon_unique ON urun_rezervasyon_notlari(urun_kodu, COALESCE(renk, ""))')
    
    # Kritik stok sınırı sütunu ekleme (mevcut tablolar için)
    try:
        db.execute('ALTER TABLE stoklar ADD COLUMN kritik_stok_siniri INTEGER DEFAULT 5')
        db.commit()
    except sqlite3.OperationalError:
        # Sütun zaten mevcut
        pass
    
    db.commit()

    # Rezervasyon notlarını yeni tabloya taşı
    # try:
    #     migrate_rezervasyon_notlari()
    # except Exception as e:
    #     logger.error(f"Rezervasyon notları taşıma hatası: {str(e)}")

def create_stok_hareketi(urun_kodu, hareket_tipi, miktar, onceki_miktar, yeni_miktar, konum=None, aciklama=None, kullanici=None, islem_tarihi=None):
    """Stok hareketi kaydı oluştur"""
    from datetime import datetime
    db = get_db_connection()
    
    if islem_tarihi:
        # Belirtilen tarih kullan - eğer sadece tarih verilmişse saat ekle
        if len(islem_tarihi) == 10:  # Format: YYYY-MM-DD
            # Mevcut saati ekle
            current_time = datetime.now().strftime('%H:%M:%S')
            islem_tarihi = f"{islem_tarihi} {current_time}"
        
        db.execute('''
            INSERT INTO stok_hareketleri 
            (urun_kodu, hareket_tipi, miktar, onceki_miktar, yeni_miktar, konum, aciklama, kullanici, tarih)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (urun_kodu, hareket_tipi, miktar, onceki_miktar, yeni_miktar, konum, aciklama, kullanici, islem_tarihi))
    else:
        # Mevcut sistem tarihi ve saati kullan
        current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        db.execute('''
            INSERT INTO stok_hareketleri 
            (urun_kodu, hareket_tipi, miktar, onceki_miktar, yeni_miktar, konum, aciklama, kullanici, tarih)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (urun_kodu, hareket_tipi, miktar, onceki_miktar, yeni_miktar, konum, aciklama, kullanici, current_datetime))
    
    db.commit()

def get_stok_by_urun_kodu(urun_kodu):
    """Ürün koduna göre stok bilgisi getir"""
    db = get_db_connection()
    return db.execute(
        'SELECT * FROM stoklar WHERE urun_kodu = ?', (urun_kodu,)
    ).fetchone()

def get_stok_by_urun_kodu_konum(urun_kodu, konum, renk=None):
    """Ürün kodu ve konum bazında stok bilgisi getir"""
    db = get_db_connection()
    if renk:
        return db.execute(
            'SELECT * FROM stoklar WHERE urun_kodu = ? AND konum = ? AND renk = ?', 
            (urun_kodu, konum, renk)
        ).fetchone()
    else:
        return db.execute(
            'SELECT * FROM stoklar WHERE urun_kodu = ? AND konum = ?', 
            (urun_kodu, konum)
        ).fetchone()

def get_all_locations_for_product(urun_kodu, renk=None):
    """Bir ürünün tüm konumlardaki stok bilgilerini getir"""
    db = get_db_connection()
    if renk:
        return db.execute(
            '''SELECT konum, adet, toplam_kg FROM stoklar 
               WHERE urun_kodu = ? AND renk = ? AND adet > 0
               ORDER BY konum''', 
            (urun_kodu, renk)
        ).fetchall()
    else:
        return db.execute(
            '''SELECT konum, renk, adet, toplam_kg FROM stoklar 
               WHERE urun_kodu = ? AND adet > 0
               ORDER BY konum, renk''', 
            (urun_kodu,)
        ).fetchall()

def stok_giris(urun_kodu, urun_adi, renk, konum, adet, mt_kg=None, uzunluk=None, 
              sistem_seri=None, kullanici=None, islem_tarihi=None):
    """Stok giriş işlemi - mevcut stokla birleştirir veya yeni kayıt oluşturur"""
    db = get_db_connection()
    
    # Boy KG ve Toplam KG hesaplama
    boy_kg = 0
    if uzunluk and mt_kg:
        boy_kg = (uzunluk / 1000) * mt_kg
    
    toplam_kg = adet * boy_kg if boy_kg else 0
    
    try:
        # Mevcut kaydı kontrol et
        existing = db.execute(
            'SELECT * FROM stoklar WHERE urun_kodu = ? AND renk = ? AND konum = ?',
            (urun_kodu, renk, konum)
        ).fetchone()
        
        if existing:
            # Mevcut kayıt güncelle
            onceki_adet = existing['adet']
            yeni_adet = onceki_adet + adet
            yeni_toplam_kg = existing['toplam_kg'] + toplam_kg
            
            db.execute(
                '''UPDATE stoklar SET 
                   adet = ?, toplam_kg = ?, updated_at = CURRENT_TIMESTAMP
                   WHERE urun_kodu = ? AND renk = ? AND konum = ?''',
                (yeni_adet, yeni_toplam_kg, urun_kodu, renk, konum)
            )
            
            # Hareket kaydı oluştur
            create_stok_hareketi(
                urun_kodu=urun_kodu,
                hareket_tipi='GIRIS',
                miktar=adet,
                onceki_miktar=onceki_adet,
                yeni_miktar=yeni_adet,
                konum=konum,
                aciklama=f'Stok girişi: {adet} adet eklendi',
                kullanici=kullanici,
                islem_tarihi=islem_tarihi
            )
        else:
            # Yeni kayıt oluştur
            db.execute(
                '''INSERT INTO stoklar 
                   (urun_kodu, urun_adi, sistem_seri, renk, uzunluk, mt_kg, 
                    boy_kg, adet, toplam_kg, konum)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (urun_kodu, urun_adi, sistem_seri, renk, uzunluk, mt_kg,
                 boy_kg, adet, toplam_kg, konum)
            )
            
            # Hareket kaydı oluştur
            create_stok_hareketi(
                urun_kodu=urun_kodu,
                hareket_tipi='GIRIS',
                miktar=adet,
                onceki_miktar=0,
                yeni_miktar=adet,
                konum=konum,
                aciklama=f'İlk stok girişi: {adet} adet',
                kullanici=kullanici,
                islem_tarihi=islem_tarihi
            )
        
        db.commit()
        return {'success': True, 'message': 'Stok girişi başarılı'}
        
    except Exception as e:
        db.rollback()
        return {'success': False, 'message': f'Stok giriş hatası: {str(e)}'}

def stok_cikis(urun_kodu, renk, konum, adet, kullanici=None, aciklama=None, islem_tarihi=None):
    """Stok çıkış işlemi"""
    db = get_db_connection()
    
    try:
        # Mevcut kaydı kontrol et
        existing = db.execute(
            'SELECT * FROM stoklar WHERE urun_kodu = ? AND renk = ? AND konum = ?',
            (urun_kodu, renk, konum)
        ).fetchone()
        
        if not existing:
            return {'success': False, 'message': 'Bu konumda stok bulunamadı'}
        
        onceki_adet = existing['adet']
        if onceki_adet < adet:
            return {'success': False, 'message': f'Yetersiz stok! Mevcut: {onceki_adet}, İstenen: {adet}'}
        
        yeni_adet = onceki_adet - adet
        
        # Boy KG başına düşen ağırlığı hesapla
        birim_agirlik = existing['toplam_kg'] / onceki_adet if onceki_adet > 0 else 0
        cikan_agirlik = adet * birim_agirlik
        yeni_toplam_kg = existing['toplam_kg'] - cikan_agirlik
        
        # Stok güncelle
        db.execute(
            '''UPDATE stoklar SET 
               adet = ?, toplam_kg = ?, updated_at = CURRENT_TIMESTAMP
               WHERE urun_kodu = ? AND renk = ? AND konum = ?''',
            (yeni_adet, yeni_toplam_kg, urun_kodu, renk, konum)
        )
        
        # Hareket kaydı oluştur
        create_stok_hareketi(
            urun_kodu=urun_kodu,
            hareket_tipi='CIKIS',
            miktar=adet,
            onceki_miktar=onceki_adet,
            yeni_miktar=yeni_adet,
            konum=konum,
            aciklama=aciklama or f'Stok çıkışı: {adet} adet',
            kullanici=kullanici,
            islem_tarihi=islem_tarihi
        )
        
        db.commit()
        return {'success': True, 'message': 'Stok çıkışı başarılı'}
        
    except Exception as e:
        db.rollback()
        return {'success': False, 'message': f'Stok çıkış hatası: {str(e)}'}

def stok_transfer(urun_kodu, renk, kaynak_konum, hedef_konum, adet, kullanici=None, islem_tarihi=None):
    """Konumlar arası stok transferi"""
    db = get_db_connection()
    
    try:
        # Kaynak konumdaki stoku kontrol et
        kaynak_stok = db.execute(
            'SELECT * FROM stoklar WHERE urun_kodu = ? AND renk = ? AND konum = ?',
            (urun_kodu, renk, kaynak_konum)
        ).fetchone()
        
        if not kaynak_stok:
            return {'success': False, 'message': 'Kaynak konumda stok bulunamadı'}
        
        if kaynak_stok['adet'] < adet:
            return {'success': False, 'message': f'Kaynak konumda yetersiz stok! Mevcut: {kaynak_stok["adet"]}'}
        
        # Birim ağırlığı hesapla
        birim_agirlik = kaynak_stok['toplam_kg'] / kaynak_stok['adet'] if kaynak_stok['adet'] > 0 else 0
        transfer_agirlik = adet * birim_agirlik
        
        # Hedef konumdaki stoku kontrol et
        hedef_stok = db.execute(
            'SELECT * FROM stoklar WHERE urun_kodu = ? AND renk = ? AND konum = ?',
            (urun_kodu, renk, hedef_konum)
        ).fetchone()
        
        # Kaynak konumdan düş
        yeni_kaynak_adet = kaynak_stok['adet'] - adet
        yeni_kaynak_agirlik = kaynak_stok['toplam_kg'] - transfer_agirlik
        
        db.execute(
            '''UPDATE stoklar SET 
               adet = ?, toplam_kg = ?, updated_at = CURRENT_TIMESTAMP
               WHERE urun_kodu = ? AND renk = ? AND konum = ?''',
            (yeni_kaynak_adet, yeni_kaynak_agirlik, urun_kodu, renk, kaynak_konum)
        )
        
        if hedef_stok:
            # Hedef konumda stok var, ekle
            yeni_hedef_adet = hedef_stok['adet'] + adet
            yeni_hedef_agirlik = hedef_stok['toplam_kg'] + transfer_agirlik
            
            db.execute(
                '''UPDATE stoklar SET 
                   adet = ?, toplam_kg = ?, updated_at = CURRENT_TIMESTAMP
                   WHERE urun_kodu = ? AND renk = ? AND konum = ?''',
                (yeni_hedef_adet, yeni_hedef_agirlik, urun_kodu, renk, hedef_konum)
            )
        else:
            # Hedef konumda stok yok, yeni kayıt oluştur
            db.execute(
                '''INSERT INTO stoklar 
                   (urun_kodu, urun_adi, sistem_seri, renk, uzunluk, mt_kg, 
                    boy_kg, adet, toplam_kg, konum)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (urun_kodu, kaynak_stok['urun_adi'], kaynak_stok['sistem_seri'], 
                 renk, kaynak_stok['uzunluk'], kaynak_stok['mt_kg'], 
                 kaynak_stok['boy_kg'], adet, transfer_agirlik, hedef_konum)
            )
        
        # Hareket kayıtları oluştur
        create_stok_hareketi(
            urun_kodu=urun_kodu,
            hareket_tipi='TRANSFER',
            miktar=adet,
            onceki_miktar=kaynak_stok['adet'],
            yeni_miktar=yeni_kaynak_adet,
            konum=kaynak_konum,
            aciklama=f'Transfer çıkış: {hedef_konum} konumuna {adet} adet',
            kullanici=kullanici,
            islem_tarihi=islem_tarihi
        )
        
        hedef_onceki = hedef_stok['adet'] if hedef_stok else 0
        hedef_yeni = hedef_onceki + adet
        
        create_stok_hareketi(
            urun_kodu=urun_kodu,
            hareket_tipi='TRANSFER',
            miktar=adet,
            onceki_miktar=hedef_onceki,
            yeni_miktar=hedef_yeni,
            konum=hedef_konum,
            aciklama=f'Transfer giriş: {kaynak_konum} konumundan {adet} adet',
            kullanici=kullanici,
            islem_tarihi=islem_tarihi
        )
        
        db.commit()
        return {'success': True, 'message': 'Stok transferi başarılı'}
        
    except Exception as e:
        db.rollback()
        return {'success': False, 'message': f'Stok transfer hatası: {str(e)}'}

def get_product_stock_summary(urun_kodu=None, renk=None):
    """Ürün bazında stok özeti - tüm konumlarda ne kadar var"""
    db = get_db_connection()
    
    where_conditions = []
    params = []
    
    if urun_kodu:
        where_conditions.append('urun_kodu = ?')
        params.append(urun_kodu)
    
    if renk:
        where_conditions.append('renk = ?')
        params.append(renk)
    
    where_clause = ' AND '.join(where_conditions) if where_conditions else '1=1'
    
    query = f'''
        SELECT 
            urun_kodu,
            urun_adi,
            renk,
            konum,
            adet,
            toplam_kg,
            SUM(adet) OVER (PARTITION BY urun_kodu, renk) as toplam_adet,
            SUM(toplam_kg) OVER (PARTITION BY urun_kodu, renk) as toplam_agirlik
        FROM stoklar 
        WHERE {where_clause} AND adet > 0
        ORDER BY urun_kodu, renk, konum
    '''
    
    return db.execute(query, params).fetchall()

def init_app(app):
    """Flask uygulamasına veritabanı fonksiyonlarını kaydet"""
    app.teardown_appcontext(close_db)

# ==== REZERVASYON İŞLEVLERİ ====

def rezervasyon_olustur(urun_kodu, urun_adi, renk, konum, adet, rezerve_eden, aciklama=None):
    """Yeni rezervasyon oluştur"""
    db = get_db_connection()
    
    try:
        # Mevcut stok kontrolü
        mevcut_stok = get_stok_by_urun_kodu_konum(urun_kodu, konum, renk)
        if not mevcut_stok:
            return {'success': False, 'message': 'Bu konumda stok bulunamadı'}
        
        # Mevcut rezervasyonları kontrol et
        rezerve_adet = db.execute('''
            SELECT COALESCE(SUM(adet), 0) as toplam_rezerve
            FROM rezervasyonlar 
            WHERE urun_kodu = ? AND konum = ? AND durum = 'AKTIF'
              AND (renk = ? OR (renk IS NULL AND ? IS NULL))
        ''', (urun_kodu, konum, renk, renk)).fetchone()['toplam_rezerve']
        
        musait_adet = mevcut_stok['adet'] - rezerve_adet
        
        if musait_adet < adet:
            return {
                'success': False, 
                'message': f'Yetersiz müsait stok! Mevcut: {mevcut_stok["adet"]}, Rezerveli: {rezerve_adet}, Müsait: {musait_adet}'
            }
        
        # Rezervasyon oluştur
        cursor = db.execute('''
            INSERT INTO rezervasyonlar 
            (urun_kodu, urun_adi, renk, konum, adet, rezerve_eden, aciklama)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (urun_kodu, urun_adi, renk, konum, adet, rezerve_eden, aciklama))
        
        rezervasyon_id = cursor.lastrowid
        
        # Rezervasyon hareket kaydı
        db.execute('''
            INSERT INTO rezervasyon_hareketleri
            (rezervasyon_id, hareket_tipi, urun_kodu, renk, konum, adet, kullanici, aciklama)
            VALUES (?, 'REZERVE', ?, ?, ?, ?, ?, ?)
        ''', (rezervasyon_id, urun_kodu, renk, konum, adet, rezerve_eden, aciklama or 'Yeni rezervasyon'))
        
        db.commit()
        return {
            'success': True, 
            'message': 'Rezervasyon başarıyla oluşturuldu',
            'rezervasyon_id': rezervasyon_id
        }
        
    except Exception as e:
        db.rollback()
        return {'success': False, 'message': f'Rezervasyon oluşturma hatası: {str(e)}'}

def rezervasyon_iptal(rezervasyon_id, kullanici, aciklama=None):
    """Rezervasyonu iptal et"""
    db = get_db_connection()
    
    try:
        # Rezervasyonu kontrol et
        rezervasyon = db.execute(
            'SELECT * FROM rezervasyonlar WHERE id = ? AND durum = "AKTIF"',
            (rezervasyon_id,)
        ).fetchone()
        
        if not rezervasyon:
            return {'success': False, 'message': 'Aktif rezervasyon bulunamadı'}
        
        # Rezervasyonu iptal et
        db.execute(
            'UPDATE rezervasyonlar SET durum = "IPTAL", son_guncelleme = CURRENT_TIMESTAMP WHERE id = ?',
            (rezervasyon_id,)
        )
        
        # Hareket kaydı
        db.execute('''
            INSERT INTO rezervasyon_hareketleri
            (rezervasyon_id, hareket_tipi, urun_kodu, renk, konum, adet, kullanici, aciklama)
            VALUES (?, 'IPTAL', ?, ?, ?, ?, ?, ?)
        ''', (rezervasyon_id, rezervasyon['urun_kodu'], rezervasyon['renk'], 
              rezervasyon['konum'], rezervasyon['adet'], kullanici, 
              aciklama or 'Rezervasyon iptali'))
        
        db.commit()
        return {'success': True, 'message': 'Rezervasyon iptal edildi'}
        
    except Exception as e:
        db.rollback()
        return {'success': False, 'message': f'Rezervasyon iptal hatası: {str(e)}'}

def rezervasyon_tamamla(rezervasyon_id, kullanici, aciklama=None):
    """Rezervasyonu tamamla - stoktan çıkar"""
    db = get_db_connection()
    
    try:
        # Rezervasyonu kontrol et
        rezervasyon = db.execute(
            'SELECT * FROM rezervasyonlar WHERE id = ? AND durum = "AKTIF"',
            (rezervasyon_id,)
        ).fetchone()
        
        if not rezervasyon:
            return {'success': False, 'message': 'Aktif rezervasyon bulunamadı'}
        
        # Stok çıkış işlemi yap
        stok_sonuc = stok_cikis(
            urun_kodu=rezervasyon['urun_kodu'],
            renk=rezervasyon['renk'],
            konum=rezervasyon['konum'],
            adet=rezervasyon['adet'],
            kullanici=kullanici,
            aciklama=f"Rezervasyon tamamlandı (ID: {rezervasyon_id})"
        )
        
        if not stok_sonuc['success']:
            return stok_sonuc
        
        # Rezervasyonu tamamla
        db.execute(
            'UPDATE rezervasyonlar SET durum = "TAMAMLANDI", son_guncelleme = CURRENT_TIMESTAMP WHERE id = ?',
            (rezervasyon_id,)
        )
        
        # Hareket kaydı
        db.execute('''
            INSERT INTO rezervasyon_hareketleri
            (rezervasyon_id, hareket_tipi, urun_kodu, renk, konum, adet, kullanici, aciklama)
            VALUES (?, 'TAMAMLANDI', ?, ?, ?, ?, ?, ?)
        ''', (rezervasyon_id, rezervasyon['urun_kodu'], rezervasyon['renk'], 
              rezervasyon['konum'], rezervasyon['adet'], kullanici, 
              aciklama or 'Rezervasyon tamamlandı ve stoktan çıkarıldı'))
        
        db.commit()
        return {'success': True, 'message': 'Rezervasyon tamamlandı ve stoktan çıkarıldı'}
        
    except Exception as e:
        db.rollback()
        return {'success': False, 'message': f'Rezervasyon tamamlama hatası: {str(e)}'}

def get_aktif_rezervasyonlar(urun_kodu=None, konum=None, rezerve_eden=None):
    """Aktif rezervasyonları listele"""
    db = get_db_connection()
    
    where_conditions = ['durum = "AKTIF"']
    params = []
    
    if urun_kodu:
        where_conditions.append('urun_kodu = ?')
        params.append(urun_kodu)
    
    if konum:
        where_conditions.append('konum = ?')
        params.append(konum)
    
    if rezerve_eden:
        where_conditions.append('rezerve_eden = ?')
        params.append(rezerve_eden)
    
    where_clause = ' AND '.join(where_conditions)
    
    return db.execute(f'''
        SELECT r.*, 
               s.adet as mevcut_stok,
               (SELECT COALESCE(SUM(adet), 0) 
                FROM rezervasyonlar r2 
                WHERE r2.urun_kodu = r.urun_kodu 
                  AND r2.konum = r.konum 
                  AND r2.durum = 'AKTIF'
                  AND (r2.renk = r.renk OR (r2.renk IS NULL AND r.renk IS NULL))
               ) as toplam_rezerve
        FROM rezervasyonlar r
        LEFT JOIN stoklar s ON (r.urun_kodu = s.urun_kodu 
                               AND r.konum = s.konum 
                               AND (r.renk = s.renk OR (r.renk IS NULL AND s.renk IS NULL)))
        WHERE {where_clause}
        ORDER BY r.rezerve_tarihi DESC
    ''', params).fetchall()

def get_urun_rezervasyon_durumu(urun_kodu, renk=None, konum=None):
    """Ürün için rezervasyon durumu özeti - artık yeni tablodan"""
    db = get_db_connection()
    
    # Yeni tablodan rezervasyon notunu al
    rezervasyon_notu = get_urun_rezervasyon_notu(urun_kodu, renk)
    
    where_conditions = ['s.urun_kodu = ?']
    params = [urun_kodu]
    
    if renk:
        where_conditions.append('(s.renk = ? OR s.renk IS NULL)')
        params.append(renk)
    
    if konum:
        where_conditions.append('s.konum = ?')
        params.append(konum)
    
    where_clause = ' AND '.join(where_conditions)
    
    results = db.execute(f'''
        SELECT 
            s.urun_kodu,
            s.urun_adi,
            s.renk,
            s.konum,
            s.adet as mevcut_stok,
            COALESCE(SUM(CASE WHEN r.durum = 'AKTIF' THEN r.adet ELSE 0 END), 0) as rezerveli_adet,
            s.adet - COALESCE(SUM(CASE WHEN r.durum = 'AKTIF' THEN r.adet ELSE 0 END), 0) as musait_adet
        FROM stoklar s
        LEFT JOIN rezervasyonlar r ON (s.urun_kodu = r.urun_kodu 
                                      AND s.konum = r.konum 
                                      AND (s.renk = r.renk OR (s.renk IS NULL AND r.renk IS NULL)))
        WHERE {where_clause} AND s.adet > 0
        GROUP BY s.urun_kodu, s.urun_adi, s.renk, s.konum, s.adet
        ORDER BY s.konum
    ''', params).fetchall()
    
    # Rezervasyon notunu sonuçlara ekle
    for result in results:
        result['rezervasyon_notu'] = rezervasyon_notu
    
    return results


class DatabaseManager:
    """Veritabanı yönetim sınıfı - auth modülü için"""
    
    def __init__(self, db_path=None):
        self.db_path = db_path or 'stok_takip_dev.db'
        self._connection = None
    
    def get_connection(self):
        """Veritabanı bağlantısı al"""
        if not self._connection:
            self._connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                timeout=20.0
            )
            self._connection.row_factory = sqlite3.Row
            self._connection.execute('PRAGMA journal_mode=WAL')
            self._connection.execute('PRAGMA foreign_keys=ON')
            self._connection.commit()
        return self._connection
    
    def execute_query(self, query, params=None):
        """SQL sorgusu çalıştır"""
        conn = self.get_connection()
        try:
            if params:
                conn.execute(query, params)
            else:
                conn.execute(query)
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
    
    def fetch_one(self, query, params=None):
        """Tek satır getir"""
        conn = self.get_connection()
        if params:
            result = conn.execute(query, params).fetchone()
        else:
            result = conn.execute(query).fetchone()
        return dict(result) if result else None
    
    def fetch_all(self, query, params=None):
        """Tüm satırları getir"""
        conn = self.get_connection()
        if params:
            results = conn.execute(query, params).fetchall()
        else:
            results = conn.execute(query).fetchall()
        return [dict(row) for row in results]
    
    def close(self):
        """Bağlantıyı kapat"""
        if self._connection:
            self._connection.close()
            self._connection = None