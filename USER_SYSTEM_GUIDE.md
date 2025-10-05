# Rigelstok Kullanıcı Yönetim Sistemi

Bu döküman Rigelstok stok yönetim sistemine eklenen kullanıcı kimlik doğrulama ve yetkilendirme sistemini açıklar.

## 🔐 Sistem Özellikleri

### Kullanıcı Rolleri

**1. Admin (Yönetici)**
- ✅ Tüm sistem özelliklerine erişim
- ✅ Stok ekleme, çıkarma, transfer işlemleri
- ✅ Stok listesi ve tüm raporlar
- ✅ Excel import/export
- ✅ Kullanıcı yönetimi
- ✅ Sistem ayarları
- ✅ Arama ve filtreleme

**2. User (Kullanıcı)**
- ✅ Sadece "Detaylı Stok Raporu" görüntüleme
- ❌ Stok değişiklikleri yapamaz
- ❌ Excel işlemleri yapamaz
- ❌ Kullanıcı yönetimi yapamaz
- ❌ Sistem ayarlarına erişemez
- ❌ Arama fonksiyonu yok

## 🚀 İlk Kurulum

### Varsayılan Admin Hesabı
Sistem ilk çalıştırıldığında otomatik olarak admin hesabı oluşturulur:
- **Kullanıcı Adı:** `admin`
- **Şifre:** `admin123`

> **⚠️ Güvenlik Uyarısı:** İlk girişten sonra bu şifreyi mutlaka değiştirin!

### Veritabanı Tabloları
Sistem otomatik olarak `kullanicilar` tablosunu oluşturur:
```sql
CREATE TABLE kullanicilar (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kullanici_adi TEXT UNIQUE NOT NULL,
    sifre_hash TEXT NOT NULL,
    rol TEXT NOT NULL DEFAULT 'user',
    aktif INTEGER DEFAULT 1,
    olusturma_tarihi DATETIME DEFAULT CURRENT_TIMESTAMP,
    son_giris DATETIME
);
```

## 📱 Kullanım Kılavuzu

### Admin İşlemleri

**1. Giriş Yapma:**
- `/login` sayfasına gidin
- Admin bilgileri ile giriş yapın
- Otomatik olarak ana sayfaya yönlendirilirsiniz

**2. Kullanıcı Ekleme:**
- Navbar'da "Kullanıcılar" menüsüne tıklayın
- "Yeni Kullanıcı Ekle" formunu doldurun
- Rol seçin (Admin/Kullanıcı)
- "Ekle" butonuna basın

**3. Kullanıcı Yönetimi:**
- Kullanıcıları aktif/pasif yapabilirsiniz
- Kullanıcıları silebilirsiniz (admin hariç)
- Son giriş bilgilerini görüntüleyebilirsiniz

### Normal Kullanıcı İşlemleri

**1. Giriş Yapma:**
- `/login` sayfasına gidin
- Kullanıcı bilgileri ile giriş yapın
- Otomatik olarak Stok Raporu sayfasına yönlendirilirsiniz

**2. Stok Raporu Görüntüleme:**
- Sadece stok bilgilerini görüntüleyebilirsiniz
- Filtreleme yapabilirsiniz
- Sıralama yapabilirsiniz
- Hiçbir değişiklik yapamazsınız

## 🛡️ Güvenlik Özellikleri

### Şifre Güvenliği
- Şifreler PBKDF2-SHA256 algoritması ile hashlenir
- Her şifre için rastgele salt kullanılır
- 100,000 iterasyon ile güçlü hashlenme

### Oturum Yönetimi
- Flask session kullanılır
- Güvenli secret key ile korunur
- Otomatik çıkış mekanizması

### Erişim Kontrolü
- `@login_required`: Giriş yapma zorunluluğu
- `@admin_required`: Admin yetkisi zorunluluğu
- Sayfa bazında rol kontrolü

## 🎨 Kullanıcı Arayüzü

### Navbar Değişiklikleri
**Admin görünümü:**
- Tüm menü öğeleri görünür
- "Kullanıcılar" menüsü eklendi
- Arama kutusu aktif
- Admin badge ile kullanıcı bilgisi

**Kullanıcı görünümü:**
- Sadece "Ana Sayfa" ve "Raporlar" menüleri
- "Stok Durumu" raporu erişilebilir
- Arama kutusu gizli
- User badge ile kullanıcı bilgisi

### Login Sayfası
- Modern gradient tasarım
- Responsive layout
- Şifre göster/gizle özelliği
- Varsayılan giriş bilgileri gösterimi
- Error/success mesajları

### Kullanıcı Yönetimi Sayfası
- Kullanıcı kartları ile görsel tasarım
- İstatistik kartları
- Yeni kullanıcı ekleme formu
- Durum değiştirme butonları
- Rol badge'leri

## 🔧 Teknik Detaylar

### Dosya Yapısı
```
utils/
└── auth.py              # Kimlik doğrulama modülü

templates/
├── login.html           # Giriş sayfası
├── user_management.html # Kullanıcı yönetimi
└── base.html           # Güncellenen navbar

routes/
└── main.py             # Güncellenmiş rotalar
```

### Yeni Route'lar
- `GET/POST /login` - Giriş sayfası
- `GET /logout` - Çıkış işlemi
- `GET /user-management` - Kullanıcı yönetimi (admin)
- `POST /add-user` - Yeni kullanıcı ekleme (admin)
- `POST /toggle-user-status/<id>` - Kullanıcı durumu (admin)
- `POST /delete-user/<id>` - Kullanıcı silme (admin)

### Database Manager Bağımlılığı
Auth sistemi `utils.database.DatabaseManager` sınıfını kullanır.

## 🚨 Önemli Notlar

1. **İlk Kurulum:** Sistem ilk çalıştığında admin hesabı otomatik oluşturulur
2. **Güvenlik:** Production'da mutlaka güçlü SECRET_KEY kullanın
3. **Yetkilendirme:** Normal kullanıcılar sadece stok raporu görebilir
4. **Admin Koruma:** Admin kullanıcısı silinemez ve pasifleştirilemez
5. **Session Güvenliği:** Çıkış yapılmadığında session aktif kalır

## 🔄 Deployment Notları

Railway.app deployment için:
1. Tüm dosyalar `rigelstok-deploy` klasöründe hazır
2. Environment variables zaten configured
3. Auth sistemi production-ready
4. Database otomatik initialize edilir

## 📞 Destek

Herhangi bir sorun yaşarsanız:
1. Login sayfasında varsayılan admin bilgilerini kullanın
2. Database'de `kullanicilar` tablosunu kontrol edin
3. Flask session ve secret key ayarlarını doğrulayın