import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
from .database import get_db_connection

logger = logging.getLogger(__name__)

def process_st_xlsx_data(file_path: str = 'st.xlsx', sheet_name: str = '8', cell_range: str = 'A1:K801'):
    """
    st.xlsx dosyasının belirtilen sayfasından veri okur ve veritabanına aktarır
    """
    try:
        # Excel dosyasını oku
        logger.info(f"{file_path} dosyasının {sheet_name} sayfasından {cell_range} aralığı okunuyor...")
        
        # Sayfa isimlerini kontrol et
        xl_file = pd.ExcelFile(file_path)
        available_sheets = xl_file.sheet_names
        
        # Sayfa 8'i bul (string ya da integer olabilir)
        target_sheet = None
        if '8' in available_sheets:
            target_sheet = '8'
        elif 8 in available_sheets:
            target_sheet = 8
        else:
            # Sayfa index'i ile dene (8. sayfa = index 7)
            if len(available_sheets) >= 8:
                target_sheet = available_sheets[7]
            else:
                raise ValueError(f"8 numaralı sayfa bulunamadı. Mevcut sayfalar: {available_sheets}")
        
        logger.info(f"Hedef sayfa: {target_sheet}")
        
        # Belirtilen aralıktan veriyi oku
        # A1:K801 = 0:10 sütun, 0:800 satır (0-indexli)
        data = pd.read_excel(
            file_path,
            sheet_name=target_sheet,
            usecols="A:K",  # A'dan K'ya kadar sütunlar
            nrows=801,      # 801 satır
            header=None     # Header yok
        )
        
        logger.info(f"Veri başarıyla okundu: {len(data)} satır, {len(data.columns)} sütun")
        
        # İlk birkaç satırı kontrol et (header'ı bul)
        logger.info("İlk 10 satır:")
        for i in range(min(10, len(data))):
            logger.info(f"Satır {i}: {data.iloc[i].tolist()}")
        
        return {
            'success': True,
            'data': data,
            'sheet_name': target_sheet,
            'available_sheets': available_sheets,
            'shape': data.shape,
            'message': f"{len(data)} satır veri başarıyla okundu"
        }
        
    except Exception as e:
        error_msg = f"Excel okuma hatası: {str(e)}"
        logger.error(error_msg)
        return {
            'success': False,
            'message': error_msg,
            'data': None
        }

def clear_existing_stock_data():
    """
    Mevcut stok verilerini temizle
    """
    try:
        db = get_db_connection()
        
        # Önce hareketleri sil (foreign key constraint nedeniyle)
        result1 = db.execute('DELETE FROM stok_hareketleri')
        deleted_movements = result1.rowcount
        
        # Sonra stokları sil
        result2 = db.execute('DELETE FROM stoklar')
        deleted_stocks = result2.rowcount
        
        # Rezervasyonları da sil (varsa)
        try:
            result3 = db.execute('DELETE FROM rezervasyonlar')
            deleted_reservations = result3.rowcount
        except:
            deleted_reservations = 0
        
        try:
            result4 = db.execute('DELETE FROM rezervasyon_hareketleri')
            deleted_reservation_movements = result4.rowcount
        except:
            deleted_reservation_movements = 0
        
        db.commit()
        
        logger.info(f"Veriler temizlendi: {deleted_stocks} stok, {deleted_movements} hareket")
        
        return {
            'success': True,
            'deleted_stocks': deleted_stocks,
            'deleted_movements': deleted_movements,
            'deleted_reservations': deleted_reservations,
            'deleted_reservation_movements': deleted_reservation_movements,
            'message': f"{deleted_stocks} stok kaydı ve {deleted_movements} hareket kaydı silindi"
        }
        
    except Exception as e:
        error_msg = f"Veri temizleme hatası: {str(e)}"
        logger.error(error_msg)
        return {
            'success': False,
            'message': error_msg
        }

class ExcelProcessor:
    """Excel dosyalarını işlemek için sınıf"""
    
    # Sütun eşleme - Excel sütunları -> veritabanı alanları
    # Veriler sütun 25-35 arasında (Y:AI)
    COLUMN_MAPPING = {
        25: 'urun_kodu',      # MAĞAZA PRES STOK
        26: 'tedarikci',      # TEDARİKÇİ  
        27: 'sistem_seri',    # SİSTEM SERİ
        28: 'urun_adi',       # ÜRÜN ADI
        29: 'renk',           # RENK
        30: 'uzunluk',        # UZUNLUK
        31: 'mt_kg',          # MT KG
        32: 'boy_kg',         # BOY KG
        33: 'adet',           # ADET
        34: 'toplam_kg',      # TOPLAM KG
        35: 'konum'           # KONUM
    }
    
    def __init__(self):
        self.data = None
        self.errors = []
        self.processed_count = 0
        
    def read_excel_file(self, file_path: str, sheet_name: str = '3') -> bool:
        """Excel dosyasını oku - Gerçek veri sütunlarından"""
        try:
            # Tüm veriyi oku
            full_data = pd.read_excel(
                file_path,
                sheet_name=sheet_name,
                header=None  # Header yok, ham veri
            )
            
            # Gerçek veri sütunları: 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 93
            # Bu sütunlar bizim mapping'imize karşılık geliyor
            data_columns = [95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 93]
            
            if len(full_data.columns) < max(data_columns) + 1:
                raise ValueError(f"Excel dosyasında yeterli sütun yok. Bulunan: {len(full_data.columns)}, Gerekli: {max(data_columns) + 1}")
            
            # İlgili sütunları seç ve satır 6'dan sonrasını al
            selected_data = full_data.iloc[6:, data_columns].copy()  # 6. satırdan sonra
            
            # Sütun isimlerini ata (mapping'e göre)
            column_names = ['urun_kodu', 'urun_adi', 'sistem_seri', 'renk', 'uzunluk', 
                          'mt_kg', 'boy_kg', 'adet', 'toplam_kg', 'konum']
            selected_data.columns = column_names
            
            # Index'i sıfırla
            selected_data.reset_index(drop=True, inplace=True)
            
            self.data = selected_data
            
            logger.info(f"Excel dosyası başarıyla okundu: {len(self.data)} satır")
            return True
            
        except Exception as e:
            error_msg = f"Excel dosyası okuma hatası: {str(e)}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            return False
    
    def validate_data(self) -> Tuple[pd.DataFrame, List[str]]:
        """Veri validasyonu yap"""
        if self.data is None:
            return None, ["Veri yüklenmemiş"]
        
        valid_data = self.data.copy()
        validation_errors = []
        
        # Boş satırları temizle
        valid_data = valid_data.dropna(how='all')
        
        # Zorunlu alanları kontrol et
        required_fields = ['urun_kodu', 'urun_adi']
        for field in required_fields:
            if field in valid_data.columns:
                null_count = valid_data[field].isnull().sum()
                if null_count > 0:
                    validation_errors.append(f"{field} alanında {null_count} boş kayıt var")
                    # Boş kayıtları çıkar
                    valid_data = valid_data.dropna(subset=[field])
        
        # Sayısal alanları kontrol et ve dönüştür
        numeric_fields = ['uzunluk', 'mt_kg', 'boy_kg', 'adet', 'toplam_kg']
        for field in numeric_fields:
            if field in valid_data.columns:
                # Sayısal olmayan değerleri 0 yap
                valid_data[field] = pd.to_numeric(valid_data[field], errors='coerce').fillna(0)
        
        # Ürün kodu formatını kontrol et
        if 'urun_kodu' in valid_data.columns:
            # Boşlukları temizle ve büyük harfe çevir
            valid_data['urun_kodu'] = valid_data['urun_kodu'].astype(str).str.strip().str.upper()
            
        # String alanları temizle
        string_fields = ['urun_adi', 'sistem_seri', 'renk', 'konum']
        for field in string_fields:
            if field in valid_data.columns:
                valid_data[field] = valid_data[field].astype(str).str.strip()
                # 'nan' string'lerini None yap
                valid_data[field] = valid_data[field].replace('nan', None)
        
        self.processed_count = len(valid_data)
        logger.info(f"Veri validasyonu tamamlandı: {self.processed_count} geçerli kayıt")
        
        return valid_data, validation_errors
    
    def calculate_derived_fields(self, data: pd.DataFrame) -> pd.DataFrame:
        """Türetilmiş alanları hesapla"""
        if data is None:
            return None
            
        result_data = data.copy()
        
        # BOY KG hesaplama: uzunluk/1000 * mt_kg
        if all(col in result_data.columns for col in ['uzunluk', 'mt_kg']):
            result_data['boy_kg'] = (result_data['uzunluk'] / 1000) * result_data['mt_kg']
            result_data['boy_kg'] = result_data['boy_kg'].round(3)
        
        # TOPLAM KG hesaplama: adet * boy_kg
        if all(col in result_data.columns for col in ['adet', 'boy_kg']):
            result_data['toplam_kg'] = result_data['adet'] * result_data['boy_kg']
            result_data['toplam_kg'] = result_data['toplam_kg'].round(3)
        
        return result_data
    
    def get_summary_stats(self, data: pd.DataFrame) -> Dict:
        """Özet istatistikleri hesapla"""
        if data is None or data.empty:
            return {}
        
        stats = {
            'total_records': len(data),
            'total_products': data['urun_kodu'].nunique() if 'urun_kodu' in data.columns else 0,
            'total_quantity': data['adet'].sum() if 'adet' in data.columns else 0,
            'total_weight': data['toplam_kg'].sum() if 'toplam_kg' in data.columns else 0,
            'locations': data['konum'].nunique() if 'konum' in data.columns else 0,
            'colors': data['renk'].nunique() if 'renk' in data.columns else 0
        }
        
        return stats
    
    def process_excel_file(self, file_path: str, sheet_name: str = '3') -> Tuple[Optional[pd.DataFrame], List[str], Dict]:
        """Excel dosyasını tam olarak işle"""
        self.errors = []
        
        # 1. Excel dosyasını oku
        if not self.read_excel_file(file_path, sheet_name):
            return None, self.errors, {}
        
        # 2. Veri validasyonu yap
        valid_data, validation_errors = self.validate_data()
        self.errors.extend(validation_errors)
        
        if valid_data is None or valid_data.empty:
            self.errors.append("Geçerli veri bulunamadı")
            return None, self.errors, {}
        
        # 3. Türetilmiş alanları hesapla
        processed_data = self.calculate_derived_fields(valid_data)
        
        # 4. Özet istatistikleri hesapla
        stats = self.get_summary_stats(processed_data)
        
        return processed_data, self.errors, stats

class DatabaseImporter:
    """Veritabanına veri import işlemleri"""
    
    def __init__(self, db_connection):
        self.db = db_connection
        self.imported_count = 0
        self.updated_count = 0
        self.errors = []
    
    def import_to_database(self, data: pd.DataFrame, batch_size: int = 100) -> Dict:
        """Verileri veritabanına batch halinde import et"""
        if data is None or data.empty:
            return {'success': False, 'message': 'Veri bulunamadı'}
        
        self.imported_count = 0
        self.updated_count = 0
        self.errors = []
        
        try:
            # Transaction başlat
            self.db.execute('BEGIN TRANSACTION')
            
            # Batch halinde işle
            for i in range(0, len(data), batch_size):
                batch = data.iloc[i:i+batch_size]
                self._process_batch(batch)
            
            # Transaction commit
            self.db.commit()
            
            result = {
                'success': True,
                'imported': self.imported_count,
                'updated': self.updated_count,
                'errors': len(self.errors),
                'error_details': self.errors
            }
            
            logger.info(f"Import tamamlandı: {self.imported_count} yeni, {self.updated_count} güncelleme")
            return result
            
        except Exception as e:
            # Hata durumunda rollback
            self.db.rollback()
            error_msg = f"Import hatası: {str(e)}"
            logger.error(error_msg)
            return {'success': False, 'message': error_msg}
    
    def _process_batch(self, batch: pd.DataFrame):
        """Bir batch'i işle"""
        for index, row in batch.iterrows():
            try:
                self._process_single_record(row)
            except Exception as e:
                error_msg = f"Satır {index + 1}: {str(e)}"
                self.errors.append(error_msg)
                logger.warning(error_msg)
    
    def _process_single_record(self, row):
        """Tek bir kaydı işle"""
        # Mevcut kaydı kontrol et
        existing = self.db.execute('''
            SELECT id, adet FROM stoklar 
            WHERE urun_kodu = ? AND renk = ? AND konum = ?
        ''', (row['urun_kodu'], row['renk'], row['konum'])).fetchone()
        
        if existing:
            # Mevcut kayıt var - güncelle
            old_quantity = existing['adet']
            new_quantity = int(row['adet'])
            
            self.db.execute('''
                UPDATE stoklar SET
                    urun_adi = ?, sistem_seri = ?, uzunluk = ?, mt_kg = ?,
                    boy_kg = ?, adet = ?, toplam_kg = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (
                row['urun_adi'], row['sistem_seri'], int(row['uzunluk']), 
                float(row['mt_kg']), float(row['boy_kg']), new_quantity,
                float(row['toplam_kg']), existing['id']
            ))
            
            # Stok hareketi kaydet (eğer miktar değiştiyse)
            if old_quantity != new_quantity:
                self._create_stock_movement(
                    row['urun_kodu'], 'GIRIS' if new_quantity > old_quantity else 'CIKIS',
                    abs(new_quantity - old_quantity), old_quantity, new_quantity,
                    row['konum'], 'Excel import güncelleme'
                )
            
            self.updated_count += 1
            
        else:
            # Yeni kayıt - ekle
            self.db.execute('''
                INSERT INTO stoklar (
                    urun_kodu, urun_adi, sistem_seri, renk, uzunluk,
                    mt_kg, boy_kg, adet, toplam_kg, konum, rezervasyon_notu
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                row['urun_kodu'], row['urun_adi'], row['sistem_seri'],
                row['renk'], int(row['uzunluk']), float(row['mt_kg']),
                float(row['boy_kg']), int(row['adet']), float(row['toplam_kg']),
                row['konum'], row['rezervasyon_notu'] if 'rezervasyon_notu' in row else None
            ))
            
            # Stok hareketi kaydet
            if int(row['adet']) > 0:
                self._create_stock_movement(
                    row['urun_kodu'], 'GIRIS', int(row['adet']), 0, int(row['adet']),
                    row['konum'], 'Excel import yeni kayıt'
                )
            
            self.imported_count += 1
    
    def _create_stock_movement(self, urun_kodu, hareket_tipi, miktar, onceki_miktar, yeni_miktar, konum, aciklama):
        """Stok hareketi kaydı oluştur"""
        from datetime import datetime
        current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        self.db.execute('''
            INSERT INTO stok_hareketleri (
                urun_kodu, hareket_tipi, miktar, onceki_miktar, 
                yeni_miktar, konum, aciklama, kullanici, tarih
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (urun_kodu, hareket_tipi, miktar, onceki_miktar, yeni_miktar, konum, aciklama, 'System', current_datetime))
    
    def check_duplicates(self, data: pd.DataFrame) -> List[Dict]:
        """Duplicate kayıtları kontrol et"""
        if data is None or data.empty:
            return []
        
        # Aynı ürün kodu, renk, konum kombinasyonlarını bul
        duplicates = data.groupby(['urun_kodu', 'renk', 'konum']).size()
        duplicate_groups = duplicates[duplicates > 1]
        
        duplicate_info = []
        for (urun_kodu, renk, konum), count in duplicate_groups.items():
            duplicate_info.append({
                'urun_kodu': urun_kodu,
                'renk': renk,
                'konum': konum,
                'count': count
            })
        
        return duplicate_info