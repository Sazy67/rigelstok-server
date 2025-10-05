"""
Geliştirilmiş Hata Yönetimi ve Logging Sistemi
Enhanced Error Handling and Logging System
"""

import logging
import traceback
import functools
from datetime import datetime
from flask import flash, request, session

# Logging konfigürasyonu
def setup_logging():
    """Logging sistemini kur"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/app.log'),
            logging.StreamHandler()
        ]
    )
    
    # Farklı log seviyeleri için farklı dosyalar
    error_handler = logging.FileHandler('logs/error.log')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    
    logger = logging.getLogger()
    logger.addHandler(error_handler)

def log_user_action(action, details=None):
    """Kullanıcı işlemlerini logla"""
    user = session.get('username', 'Anonim')
    user_ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', 'Unknown')
    
    log_message = f"Kullanıcı: {user} | IP: {user_ip} | İşlem: {action}"
    if details:
        log_message += f" | Detay: {details}"
    
    logging.info(log_message)

def handle_database_error(func):
    """Veritabanı hatalarını yakala ve işle"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_msg = f"Veritabanı hatası: {str(e)}"
            logging.error(f"{func.__name__} - {error_msg}")
            logging.error(f"Traceback: {traceback.format_exc()}")
            
            # Kullanıcıya dost hata mesajı
            flash('Bir veritabanı hatası oluştu. Lütfen tekrar deneyin.', 'error')
            return None
    return wrapper

def handle_general_error(func):
    """Genel hataları yakala ve işle"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_msg = f"Sistem hatası: {str(e)}"
            logging.error(f"{func.__name__} - {error_msg}")
            logging.error(f"Traceback: {traceback.format_exc()}")
            
            # Kullanıcıya dost hata mesajı
            flash('Beklenmeyen bir hata oluştu. Sistem yöneticisine başvurun.', 'error')
            return None
    return wrapper

def validate_form_data(required_fields, form_data):
    """Form verilerini validate et"""
    errors = []
    
    for field in required_fields:
        if field not in form_data or not form_data[field].strip():
            errors.append(f"{field} alanı zorunludur.")
    
    return errors

def sanitize_input(text):
    """Kullanıcı girişini temizle"""
    if not text:
        return ""
    
    # Tehlikeli karakterleri temizle
    dangerous_chars = ['<', '>', '"', "'", '&', '\\', '/']
    for char in dangerous_chars:
        text = text.replace(char, '')
    
    return text.strip()

class ErrorHandler:
    """Merkezi hata yönetim sınıfı"""
    
    @staticmethod
    def log_error(error, context=None):
        """Hata logla"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user = session.get('username', 'Anonim')
        
        log_entry = {
            'timestamp': timestamp,
            'user': user,
            'error': str(error),
            'context': context or 'Genel',
            'traceback': traceback.format_exc()
        }
        
        logging.error(f"Hata kaydı: {log_entry}")
        return log_entry
    
    @staticmethod
    def handle_stock_error(error, operation):
        """Stok işlemi hatalarını işle"""
        error_messages = {
            'insufficient_stock': 'Yetersiz stok miktarı.',
            'product_not_found': 'Ürün bulunamadı.',
            'invalid_quantity': 'Geçersiz miktar girdiniz.',
            'location_error': 'Konum bilgisi hatalı.',
            'duplicate_entry': 'Bu ürün zaten mevcut.',
        }
        
        # Hata tipini belirle
        error_type = 'general'
        error_str = str(error).lower()
        
        for key, message in error_messages.items():
            if key in error_str:
                error_type = key
                break
        
        user_message = error_messages.get(error_type, 'Stok işlemi sırasında hata oluştu.')
        
        ErrorHandler.log_error(error, f"Stok İşlemi: {operation}")
        flash(user_message, 'error')
        
        return error_type
    
    @staticmethod
    def handle_auth_error(error, operation):
        """Kimlik doğrulama hatalarını işle"""
        auth_errors = {
            'invalid_credentials': 'Kullanıcı adı veya şifre hatalı.',
            'user_not_found': 'Kullanıcı bulunamadı.',
            'access_denied': 'Bu işlem için yetkiniz bulunmuyor.',
            'session_expired': 'Oturumunuzun süresi dolmuş. Lütfen tekrar giriş yapın.',
        }
        
        error_str = str(error).lower()
        error_type = 'general'
        
        for key in auth_errors:
            if key in error_str:
                error_type = key
                break
        
        user_message = auth_errors.get(error_type, 'Kimlik doğrulama hatası.')
        
        ErrorHandler.log_error(error, f"Auth: {operation}")
        flash(user_message, 'error')
        
        return error_type

# Kullanım örnekleri için decorator'lar
def log_stock_operation(operation_name):
    """Stok işlemlerini logla"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                log_user_action(operation_name, "Başarılı")
                return result
            except Exception as e:
                ErrorHandler.handle_stock_error(e, operation_name)
                return None
        return wrapper
    return decorator

def log_auth_operation(operation_name):
    """Auth işlemlerini logla"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                log_user_action(operation_name, "Başarılı")
                return result
            except Exception as e:
                ErrorHandler.handle_auth_error(e, operation_name)
                return None
        return wrapper
    return decorator