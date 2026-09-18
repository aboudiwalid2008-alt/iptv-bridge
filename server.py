import json
from urllib.parse import parse_qs, urlparse
from http.server import HTTPServer, BaseHTTPRequestHandler

class StreamBridgeHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        query_params = parse_qs(parsed_path.query)
        
        # قاعدة بيانات القنوات والروابط المحمية
        channels_db = {
            "11013": "https://bsh.live-stream.com/live/iraqia-sport/index.m3u8"
        }
        
        freq = query_params.get('freq', [None])[0]
        
        if freq in channels_db:
            stream_url = channels_db[freq]
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response_data = {"status": "success", "url": stream_url}
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response_data = {"status": "error", "message": "Channel not found"}
            self.wfile.write(json.dumps(response_data).encode('utf-8'))

if __name__ == '__main__':
    server_address = ('0.0.0.0', 5050)
    httpd = HTTPServer(server_address, StreamBridgeHandler)
    print("خادم عبد الله الجسر يعمل على المنفذ 5050...")
    httpd.serve_forever()
    
