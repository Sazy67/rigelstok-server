#!/usr/bin/env python3
"""
PythonAnywhere One-Click Deploy Script
Kullanım: python3 one_click_deploy.py
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Komut çalıştır ve sonucu göster"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} tamamlandı")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} başarısız: {e}")
        print(f"Hata: {e.stderr}")
        return None

def main():
    print("🚀 PythonAnywhere One-Click Deploy")
    print("=" * 50)
    
    # Kullanıcı adını al
    username = input("PythonAnywhere kullanıcı adınız: ").strip()
    if not username:
        print("❌ Kullanıcı adı gerekli!")
        sys.exit(1)
    
    # Ana dizine git
    os.chdir(Path.home())
    
    # Eski projeyi sil
    run_command("rm -rf rigelstok-server", "Eski proje temizleniyor")
    
    # GitHub'dan klon
    if not run_command("git clone https://github.com/Sazy67/rigelstok-server.git", "GitHub'dan kod indiriliyor"):
        sys.exit(1)
    
    # Proje dizinine git
    os.chdir("rigelstok-server")
    
    # Paketleri yükle
    if not run_command("pip3.9 install --user -r requirements.txt", "Python paketleri yükleniyor"):
        sys.exit(1)
    
    # WSGI dosyası oluştur
    wsgi_content = f'''#!/usr/bin/python3.9

import sys
import os

# Path ayarları
path = '/home/{username}/rigelstok-server'
if path not in sys.path:
    sys.path.insert(0, path)

# Environment variables
os.environ['FLASK_ENV'] = 'production'
os.environ['SECRET_KEY'] = 'pythonanywhere-secret-key-{os.urandom(16).hex()}'

from app import app as application

if __name__ == "__main__":
    application.run()
'''
    
    with open('wsgi.py', 'w') as f:
        f.write(wsgi_content)
    print("✅ WSGI dosyası oluşturuldu")
    
    # Klasörleri oluştur
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    print("✅ Klasörler oluşturuldu")
    
    print("\n🎉 Setup tamamlandı!")
    print("=" * 50)
    print("📋 Şimdi yapmanız gerekenler:")
    print("1. Web tab'ına gidin")
    print("2. 'Add a new web app' tıklayın")
    print("3. Flask → Python 3.9 seçin")
    print("4. WSGI configuration file'ı düzenleyin")
    print("5. Static files ekleyin")
    print("6. Reload butonuna tıklayın")
    print(f"\n🌐 URL'niz: https://{username}.pythonanywhere.com")
    print(f"📝 WSGI dosyası: /home/{username}/rigelstok-server/wsgi.py")

if __name__ == "__main__":
    main()