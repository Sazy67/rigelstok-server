# Rigel Stok Takip Sistemi

Modern web tabanlı stok yönetim sistemi. Excel tabanlı stok verilerinizi modern bir web uygulamasına dönüştürür.

## Özellikler

### ✅ Tamamlanan Özellikler

- **Dashboard**: Stok istatistikleri ve son hareketler
- **Stok Listesi**: Sayfalama, arama ve filtreleme ile stok görüntüleme
- **Excel Import**: Excel dosyalarından toplu veri aktarımı
- **Stok Girişi**: Manuel stok giriş formu
- **Arama ve Filtreleme**: Ürün kodu, ürün adı, konum ve renk filtreleri
- **Otomatik Hesaplamalar**: BOY KG ve Toplam KG hesaplamaları
- **Responsive Tasarım**: Bootstrap 5 ile mobil uyumlu arayüz
- **Ürün Bazlı Rezervasyon Notları**: Artık rezervasyon notları konum bazlı değil, ürün bazlıdır
- **Rezervasyon Notu Yönetimi**: Rezervasyon notlarını kaydetme, görüntüleme ve silme

### 🚧 Geliştirme Aşamasında

- Stok çıkış işlemleri
- Konum bazlı stok yönetimi
- Raporlama sistemi
- Excel export
- Gelişmiş hata yönetimi

## Kurulum

### Yerel Geliştirme

#### Gereksinimler
- Python 3.8+
- pip

#### Adımlar

1. **Projeyi klonlayın**
   ```bash
   git clone <repository-url>
   cd stok-takip-sistemi
   ```

2. **Bağımlılıkları yükleyin**
   ```bash
   pip install -r requirements.txt
   ```

3. **Uygulamayı çalıştırın**
   ```bash
   python app.py
   ```

4. **Tarayıcıda açın**
   ```
   http://localhost:5001
   ```

### Railway Deployment

Bu uygulama Railway'de kolayca deploy edilebilir:

1. **Railway hesabı oluşturun:** [railway.app](https://railway.app)
2. **GitHub ile giriş yapın**
3. **"New Project" → "Deploy from GitHub repo"**
4. **Bu repository'yi seçin**
5. **Environment Variables ekleyin:**
   - `FLASK_ENV`: `production`
   - `SECRET_KEY`: Güvenli bir secret key
6. **Deploy otomatik olarak başlar**

**Railway Avantajları:**
- ✅ Otomatik HTTPS
- ✅ SQLite veritabanı korunur
- ✅ Git push ile otomatik deploy
- ✅ Ücretsiz başlangıç kredisi ($5/ay)
- ✅ Custom domain desteği



## Kullanım

### Excel Import

1. Ana sayfadan "Excel Import" butonuna tıklayın
2. Excel dosyanızı seçin (.xlsx veya .xls)
3. Dosya otomatik olarak işlenecek ve veritabanına aktarılacaktır

**Excel Format Gereksinimleri:**
- Sayfa adı: "3"
- Veri aralığı: Y7:AJ357 (sütun 25-35)
- Y sütunu (25): Ürün Kodu
- Z sütunu (26): Tedarikçi
- AA sütunu (27): Sistem Seri
- AB sütunu (28): Ürün Adı
- AC sütunu (29): Renk
- AD sütunu (30): Uzunluk
- AE sütunu (31): MT/KG
- AF sütunu (32): BOY KG
- AG sütunu (33): Adet
- AH sütunu (34): Toplam KG
- AI sütunu (35): Konum

### Manuel Stok Girişi

1. "Stok Girişi" sayfasına gidin
2. Gerekli alanları doldurun
3. BOY KG ve Toplam KG otomatik hesaplanacaktır
4. "Stok Girişi Yap" butonuna tıklayın

### Stok Listesi ve Arama

1. "Stok Listesi" sayfasında tüm stokları görüntüleyebilirsiniz
2. Arama kutusuna ürün kodu veya adı yazarak arama yapabilirsiniz
3. Konum ve renk filtrelerini kullanabilirsiniz
4. Sayfalama ile büyük veri setlerinde gezinebilirsiniz

## Teknik Detaylar

### Teknolojiler

- **Backend**: Flask (Python)
- **Frontend**: Bootstrap 5, HTML5, JavaScript
- **Veritabanı**: SQLite
- **Excel İşleme**: pandas, openpyxl

### Proje Yapısı

```
stok-takip-sistemi/
├── app.py                 # Ana Flask uygulaması
├── requirements.txt       # Python bağımlılıkları
├── utils/
│   ├── database.py       # Veritabanı işlemleri
│   └── excel_processor.py # Excel işleme fonksiyonları
├── routes/
│   ├── main.py          # Ana route'lar
│   └── reservation.py   # Rezervasyon route'ları
├── templates/           # HTML template'leri
│   ├── base.html
│   ├── index.html
│   ├── stock_list.html
│   ├── stock_entry.html
│   ├── excel_import.html
│   └── placeholder.html
└── uploads/            # Geçici dosya yükleme klasörü
```

### Veritabanı Şeması

**stoklar** tablosu:
- id (PRIMARY KEY)
- urun_kodu (TEXT, NOT NULL)
- urun_adi (TEXT, NOT NULL)
- sistem_seri (TEXT)
- renk (TEXT)
- uzunluk (INTEGER)
- mt_kg (REAL)
- boy_kg (REAL)
- adet (INTEGER)
- toplam_kg (REAL)
- konum (TEXT)
- kritik_stok_siniri (INTEGER, DEFAULT 5)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)

**stok_hareketleri** tablosu:
- id (PRIMARY KEY)
- urun_kodu (TEXT, NOT NULL)
- hareket_tipi (TEXT, CHECK: GIRIS/CIKIS/TRANSFER)
- miktar (INTEGER, NOT NULL)
- onceki_miktar (INTEGER)
- yeni_miktar (INTEGER)
- konum (TEXT)
- aciklama (TEXT)
- kullanici (TEXT)
- tarih (TIMESTAMP)

**urun_rezervasyon_notlari** tablosu (yeni):
- id (PRIMARY KEY)
- urun_kodu (TEXT, NOT NULL)
- renk (TEXT)
- rezervasyon_notu (TEXT)
- olusturulma_tarihi (TIMESTAMP)
- guncelleme_tarihi (TIMESTAMP)

## Geliştirme

### Test

Uygulamayı test etmek için:

```bash
python app.py
```

Tarayıcıda `http://localhost:5000` adresine gidin.

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/yeni-ozellik`)
3. Commit edin (`git commit -am 'Yeni özellik eklendi'`)
4. Branch'i push edin (`git push origin feature/yeni-ozellik`)
5. Pull Request oluşturun

## Destek
suatayaz@gmail.com
https://x.com/suatayaz_
Herhangi bir sorun yaşarsanız, lütfen GitHub Issues bölümünde bildirin.
