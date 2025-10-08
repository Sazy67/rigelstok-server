import sys
import os

# Proje kök dizinini Python path'e ekle
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Vercel environment variable'ını set et
os.environ['VERCEL'] = '1'
os.environ['FLASK_ENV'] = 'production'

try:
    # Ana uygulamayı import et
    from app import create_app
    
    # Vercel için app instance'ı oluştur
    app = create_app()
    
except Exception as e:
    # Hata durumunda basit Flask app
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def error():
        return f"Import Error: {str(e)}", 500