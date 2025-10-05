"""
User Authentication and Authorization System
Kullanıcı kimlik doğrulama ve yetkilendirme sistemi
"""

from functools import wraps
from flask import session, redirect, url_for, flash, request
import hashlib
import secrets

class UserManager:
    """Kullanıcı yönetimi sınıfı"""
    
    def __init__(self, db_manager):
        self.db = db_manager
        self.init_users_table()
        self.create_default_admin()
    
    def init_users_table(self):
        """Kullanıcılar tablosunu oluştur"""
        query = """
        CREATE TABLE IF NOT EXISTS kullanicilar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kullanici_adi TEXT UNIQUE NOT NULL,
            sifre_hash TEXT NOT NULL,
            rol TEXT NOT NULL DEFAULT 'user',
            aktif INTEGER DEFAULT 1,
            olusturma_tarihi DATETIME DEFAULT CURRENT_TIMESTAMP,
            son_giris DATETIME
        )
        """
        self.db.execute_query(query)
    
    def create_default_admin(self):
        """Varsayılan admin kullanıcısını oluştur"""
        # Admin kullanıcısı var mı kontrol et
        admin_exists = self.db.fetch_one(
            "SELECT id FROM kullanicilar WHERE kullanici_adi = ?", 
            ("admin",)
        )
        
        if not admin_exists:
            # Varsayılan admin oluştur (şifre: admin123)
            admin_password = "admin123"
            password_hash = self.hash_password(admin_password)
            
            self.db.execute_query(
                """INSERT INTO kullanicilar (kullanici_adi, sifre_hash, rol) 
                   VALUES (?, ?, ?)""",
                ("admin", password_hash, "admin")
            )
            print("✅ Varsayılan admin kullanıcısı oluşturuldu - Kullanıcı Adı: admin, Şifre: admin123")
    
    def hash_password(self, password):
        """Şifreyi hashle"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac('sha256', 
                                           password.encode('utf-8'), 
                                           salt.encode('utf-8'), 
                                           100000)
        return salt + password_hash.hex()
    
    def verify_password(self, password, password_hash):
        """Şifreyi doğrula"""
        salt = password_hash[:32]
        stored_hash = password_hash[32:]
        password_hash_check = hashlib.pbkdf2_hmac('sha256',
                                                 password.encode('utf-8'),
                                                 salt.encode('utf-8'),
                                                 100000)
        return stored_hash == password_hash_check.hex()
    
    def authenticate_user(self, username, password):
        """Kullanıcı kimlik doğrulaması"""
        user = self.db.fetch_one(
            "SELECT * FROM kullanicilar WHERE kullanici_adi = ? AND aktif = 1",
            (username,)
        )
        
        if user and self.verify_password(password, user['sifre_hash']):
            # Son giriş zamanını güncelle
            self.db.execute_query(
                "UPDATE kullanicilar SET son_giris = CURRENT_TIMESTAMP WHERE id = ?",
                (user['id'],)
            )
            return user
        return None
    
    def create_user(self, username, password, role='user'):
        """Yeni kullanıcı oluştur"""
        password_hash = self.hash_password(password)
        try:
            self.db.execute_query(
                """INSERT INTO kullanicilar (kullanici_adi, sifre_hash, rol) 
                   VALUES (?, ?, ?)""",
                (username, password_hash, role)
            )
            return True
        except Exception as e:
            print(f"Kullanıcı oluşturma hatası: {e}")
            return False
    
    def get_all_users(self):
        """Tüm kullanıcıları getir"""
        return self.db.fetch_all(
            """SELECT id, kullanici_adi, rol, aktif, olusturma_tarihi, son_giris 
               FROM kullanicilar ORDER BY olusturma_tarihi DESC"""
        )
    
    def toggle_user_status(self, user_id):
        """Kullanıcı durumunu aktif/pasif yap"""
        self.db.execute_query(
            "UPDATE kullanicilar SET aktif = 1 - aktif WHERE id = ?",
            (user_id,)
        )
    
    def delete_user(self, user_id):
        """Kullanıcıyı sil"""
        self.db.execute_query("DELETE FROM kullanicilar WHERE id = ?", (user_id,))


def login_required(f):
    """Giriş yapma zorunluluğu decorator'ı"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Bu sayfayı görüntülemek için giriş yapmalısınız.', 'warning')
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Admin yetkisi zorunluluğu decorator'ı"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Bu sayfayı görüntülemek için giriş yapmalısınız.', 'warning')
            return redirect(url_for('main.login'))
        
        if session.get('user_role') != 'admin':
            flash('Bu işlemi gerçekleştirmek için admin yetkisi gereklidir.', 'error')
            return redirect(url_for('main.dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function


def get_current_user():
    """Mevcut kullanıcı bilgilerini getir"""
    if 'user_id' in session:
        return {
            'id': session['user_id'],
            'username': session['username'],
            'role': session['user_role']
        }
    return None


def is_admin():
    """Mevcut kullanıcı admin mi kontrol et"""
    return session.get('user_role') == 'admin'


def can_access_page(page_name):
    """Kullanıcının sayfaya erişim yetkisi var mı kontrol et"""
    if not is_logged_in():
        return False
    
    # Admin her sayfaya erişebilir
    if is_admin():
        return True
    
    # Normal kullanıcılar sadece stok raporu sayfasını görebilir
    allowed_pages_for_user = [
        'stock_report',  # Stok raporu
        'dashboard',     # Ana sayfa (basit görünüm)
        'logout'         # Çıkış
    ]
    
    return page_name in allowed_pages_for_user


def is_logged_in():
    """Kullanıcı giriş yapmış mı kontrol et"""
    return 'user_id' in session