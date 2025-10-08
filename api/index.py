from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        html = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Vercel Test</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                h1 { color: #0070f3; }
            </style>
        </head>
        <body>
            <h1>🚀 Vercel Python Test</h1>
            <p>Python uygulaması Vercel'de çalışıyor!</p>
            <p>Path: {}</p>
            <p>Method: {}</p>
        </body>
        </html>
        '''.format(self.path, self.command)
        
        self.wfile.write(html.encode())
        return

    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            'status': 'ok',
            'message': 'POST request received',
            'path': self.path
        }
        
        self.wfile.write(json.dumps(response).encode())
        return