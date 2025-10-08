from flask import Flask

# Basit test uygulaması
app = Flask(__name__)

@app.route('/')
def hello():
    return '''
    <h1>🚀 Vercel Flask Test</h1>
    <p>Flask uygulaması Vercel'de çalışıyor!</p>
    <p>Ana uygulama yakında aktif olacak...</p>
    '''

@app.route('/health')
def health():
    return {'status': 'ok', 'message': 'Vercel deployment working'}

if __name__ == '__main__':
    app.run()