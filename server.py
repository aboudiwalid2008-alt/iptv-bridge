import json
from urllib.parse import parse_qs, urlparse
from http.server import HTTPServer, BaseHTTPRequestHandler
import os

class SmartIPTVHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        query_params = parse_qs(parsed_path.query)
        
        freq = query_params.get('freq', [None])[0]
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        stream_url = None
        
        if freq == "12562":
            stream_url = "https://bsh.live-stream.com/live/iraqia-sport/index.m3u8"
        elif freq == "11013":
            stream_url = "https://bsh.live-stream.com/live/iraqia-sport/index.m3u8"
        
        if stream_url:
            response_data = {
                "status": "success",
                "frequency": freq,
                "url": stream_url
            }
        else:
            response_data = {
                "status": "error",
                "message": "Frequency not found or stream unavailable",
                "frequency": freq
            }
            
        self.wfile.write(json.dumps(response_data).encode('utf-8'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5050))
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, SmartIPTVHandler)
    print(f"Server is running on port {port}...")
    httpd.serve_forever()
    
