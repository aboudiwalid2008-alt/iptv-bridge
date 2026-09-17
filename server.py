import json
from urllib.parse import parse_qs, urlparse
from http.server import HTTPServer, BaseHTTPRequestHandler

class StreamBridgeHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        query_params = parse_qs(parsed_path.query)

        if 'freq' in query_params:
            freq = query_params['freq'][0]
            
            channels_db = {
                "11013": "https://bsh.live-s-t-r-e-a-m.com/live/bein-sports-2/playlist.m3u8",
            }

            stream_url = channels_db.get(freq)

            if stream_url:
                response = json.dumps({"status": "success", "freq": freq, "url": stream_url})
                self.send_response(200)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(response.encode('utf-8'))
            else:
                response = json.dumps({"status": "error", "message": "Frequency not found"})
                self.send_response(404)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(response.encode('utf-8'))
        else:
            response = json.dumps({"status": "error", "message": "Provide ?freq=XXXX"})
            self.send_response(400)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(response.encode('utf-8'))

def run():
    server_address = ('0.0.0.0', 8080)
    httpd = HTTPServer(server_address, StreamBridgeHandler)
    print("Abdullah Live Bridge Server running on port 8080...")
    httpd.serve_forever()

if __name__ == '__main__':
    run()
          
