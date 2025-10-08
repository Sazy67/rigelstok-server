#!/bin/bash

echo "🚀 PythonAnywhere Otomatik Setup Başlıyor..."

# Renk kodları
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Kullanıcı adını al
echo -e "${BLUE}PythonAnywhere kullanıcı adınızı girin:${NC}"
read -p "Kullanıcı adı: " USERNAME

echo -e "${YELLOW}📁 Proje dizini oluşturuluyor...${NC}"
cd ~
rm -rf rigelstok-server 2>/dev/null

echo -e "${YELLOW}📥 GitHub'dan kod indiriliyor...${NC}"
git clone https://github.com/Sazy67/rigelstok-server.git
cd rigelstok-server

echo -e "${YELLOW}📦 Python paketleri yükleniyor...${NC}"
pip3.9 install --user -r requirements.txt

echo -e "${YELLOW}🔧 WSGI dosyası oluşturuluyor...${NC}"
cat > wsgi.py << EOF
#!/usr/bin/python3.9

import sys
import os

# Path ayarları
path = '/home/${USERNAME}/rigelstok-server'
if path not in sys.path:
    sys.path.insert(0, path)

# Environment variables
os.environ['FLASK_ENV'] = 'production'
os.environ['SECRET_KEY'] = 'pythonanywhere-secret-key-$(date +%s)'

from app import app as application

if __name__ == "__main__":
    application.run()
EOF

echo -e "${YELLOW}📁 Upload klasörü oluşturuluyor...${NC}"
mkdir -p uploads
chmod 755 uploads

echo -e "${YELLOW}💾 Veritabanı dizini hazırlanıyor...${NC}"
mkdir -p data
chmod 755 data

echo -e "${GREEN}✅ Setup tamamlandı!${NC}"
echo -e "${BLUE}📋 Şimdi yapmanız gerekenler:${NC}"
echo "1. Web tab'ına gidin"
echo "2. 'Add a new web app' tıklayın"
echo "3. Flask → Python 3.9 seçin"
echo "4. WSGI configuration file'ı düzenleyin:"
echo "   - Dosyayı tamamen silin"
echo "   - ~/rigelstok-server/wsgi.py içeriğini kopyalayın"
echo "5. Static files ekleyin:"
echo "   - URL: /static/"
echo "   - Directory: /home/${USERNAME}/rigelstok-server/static/"
echo "6. Reload butonuna tıklayın"
echo ""
echo -e "${GREEN}🌐 URL'niz: https://${USERNAME}.pythonanywhere.com${NC}"
echo ""
echo -e "${YELLOW}📝 WSGI dosyası yolu: /home/${USERNAME}/rigelstok-server/wsgi.py${NC}"