# PythonAnywhere Deployment Rehberi

## 1. Hesap Oluşturma
1. [pythonanywhere.com](https://pythonanywhere.com) → "Pricing & signup"
2. **"Create a Beginner account"** (Ücretsiz)
3. Kullanıcı adı ve şifre oluşturun

## 2. Kodu Yükleme
### Yöntem 1: Git Clone (Önerilen)
1. **"Consoles"** → **"Bash"**
2. Komutları çalıştırın:
```bash
git clone https://github.com/Sazy67/rigelstok-server.git
cd rigelstok-server
pip3.9 install --user -r requirements.txt
```

### Yöntem 2: Zip Upload
1. GitHub'dan "Download ZIP"
2. **"Files"** → **"Upload a file"**
3. Zip'i upload edin ve extract edin

## 3. Web App Oluşturma
1. **"Web"** tab'ına gidin
2. **"Add a new web app"**
3. **"Next"** (domain otomatik)
4. **"Flask"** seçin
5. **"Python 3.9"** seçin
6. **"Next"** (path otomatik)

## 4. WSGI Dosyasını Düzenleme
1. **"Web"** tab'ında **"WSGI configuration file"** linkine tıklayın
2. Dosyayı tamamen silin ve şu kodu yapıştırın:

```python
#!/usr/bin/python3.9

import sys
import os

# Path'i kendi kullanıcı adınızla değiştirin
path = '/home/KULLANICI_ADINIZ/rigelstok-server'
if path not in sys.path:
    sys.path.insert(0, path)

# Environment variables
os.environ['FLASK_ENV'] = 'production'
os.environ['SECRET_KEY'] = 'pythonanywhere-secret-key-change-this'

from app import app as application

if __name__ == "__main__":
    application.run()
```

3. **"Save"** butonuna tıklayın

## 5. Static Files (Opsiyonel)
1. **"Web"** tab'ında **"Static files"** bölümüne:
   - URL: `/static/`
   - Directory: `/home/KULLANICI_ADINIZ/rigelstok-server/static/`

## 6. Reload ve Test
1. **"Web"** tab'ında **"Reload"** butonuna tıklayın
2. **"Configuration"** bölümündeki URL'ye gidin
3. Uygulama çalışmalı!

## Sorun Giderme
- **Error logs:** "Web" tab → "Error log"
- **Server logs:** "Web" tab → "Server log"
- **Console:** "Consoles" → "Bash"

## Güncelleme
```bash
cd rigelstok-server
git pull origin master
# Web tab'ında "Reload" butonuna tıklayın
```

## Sınırlar
- 1 web app
- 512MB disk
- Custom domain yok
- CPU sınırlı
- Günlük restart