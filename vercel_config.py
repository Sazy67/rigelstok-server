import os
from datetime import timedelta

class VercelConfig:
    """Vercel deployment için özel konfigürasyon"""
    
    # Flask konfigürasyonu
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'vercel-production-secret-key-change-this'
    
    # Vercel'de geçici dosya sistemi kullanımı
    DATABASE_PATH = '/tmp/stok_takip_vercel.db'
    
    # Upload konfigürasyonu - Vercel'de /tmp kullanılır
    UPLOAD_FOLDER = '/tmp/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
    
    # Session konfigürasyonu
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Sayfalama konfigürasyonu
    ITEMS_PER_PAGE = 50
    
    # Excel işleme konfigürasyonu
    EXCEL_SHEET_NAME = '3'
    EXCEL_RANGE_START = 'CR7'
    EXCEL_RANGE_END = 'DB1000'
    
    # Production ayarları
    DEBUG = False
    TESTING = False