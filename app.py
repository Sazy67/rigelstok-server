from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from utils.database import init_db, get_db_connection, init_app
from utils.excel_processor import ExcelProcessor, DatabaseImporter
import os
import logging
from datetime import datetime

# Logging konfigürasyonu
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    
    # Environment-based configuration
    env = os.environ.get('FLASK_ENV', 'development')
    
    if env == 'production':
        # Production configuration
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'change-this-secret-key-in-production')
        app.config['DATABASE_PATH'] = os.environ.get('DATABASE_PATH', 'stok_takip_prod.db')
        app.config['DEBUG'] = False
    else:
        # Development configuration
        app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
        app.config['DATABASE_PATH'] = 'stok_takip_dev.db'
        app.config['DEBUG'] = True
    
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # Upload klasörünü oluştur
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Veritabanı bağlantısını başlat
    init_app(app)
    
    # Blueprint'leri kaydet
    from routes.main import main_bp
    from routes.reservation import reservation_bp
    app.register_blueprint(reservation_bp)  # Register reservation first
    app.register_blueprint(main_bp)         # Register main second
    
    # Veritabanını başlat
    with app.app_context():
        init_db()
    
    # Health check endpoint for deployment platforms
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'environment': env
        })
    
    return app

# Railway/Gunicorn için app instance
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    app.run(debug=debug, host='0.0.0.0', port=port)