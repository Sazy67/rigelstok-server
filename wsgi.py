#!/usr/bin/python3.9

import sys
import os

# PythonAnywhere için path ayarları
path = '/home/yourusername/rigelstok-server'  # Bu kısmı PythonAnywhere'de güncelleyeceksiniz
if path not in sys.path:
    sys.path.insert(0, path)

# Environment variables
os.environ['FLASK_ENV'] = 'production'
os.environ['SECRET_KEY'] = 'pythonanywhere-secret-key-change-this'

from app import app as application

if __name__ == "__main__":
    application.run()