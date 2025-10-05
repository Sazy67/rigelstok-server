import os
from datetime import timedelta

class Config:
    # Flask konfigürasyonu
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Veritabanı konfigürasyonu
    DATABASE_PATH = os.environ.get('DATABASE_PATH') or 'stok_takip.db'
    
    # Excel upload konfigürasyonu
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'uploads'
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

class DevelopmentConfig(Config):
    DEBUG = True
    DATABASE_PATH = 'stok_takip_dev.db'

class ProductionConfig(Config):
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or Config.SECRET_KEY

# Konfigürasyon seçimi
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}