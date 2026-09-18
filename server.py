import json
import urllib.request
from urllib.parse import parse_qs, urlparse
from http.server import HTTPServer, BaseHTTPRequestHandler
import os

class IPTVOrgProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        query_params = parse_qs(parsed_path.query)
        
        # استلام رمز الدولة مثل iq, sa, eg وغيرها
        country = query_params.get('country', ['iq'])[0]
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # رابط الجيت هاب الرسمي لـ iptv-org الخاص بالدولة المطلوبة
        iptv_url = f"https://raw.githubusercontent.com/iptv-org/iptv/master/streams/{country}.m3u"
        
        channels = []
        try:
            # السيرفر هو راح يسحب الملف من جيت هاب مباشرة
            req = urllib.request.Request(iptv_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                m3u_data = response.read().decode('utf-8')
                
                # تحليل ملف الـ M3U واستخراج القنوات الحقيقية
                lines = m3u_data.split('\n')
                current_name = ''
                for line in lines:
                    line = line.strip()
                    if line.startswith('#EXTINF:'):
                        parts = line.split(',')
                        current_name = parts[-1]
                    elif line and not line.startswith('#'):
                        if current_name:
                            channels.append({
                                "name": current_name,
                                "url": line
                            })
                            current_name = ''
                            
            response_data = {
                "status": "success",
                "country": country,
                "count": len(channels),
                "channels": channels
            }
        except Exception as e:
            response_data = {
                "status": "error",
                "message": str(e),
                "channels": []
            }
            
        self.wfile.write(json.dumps(response_data).encode('utf-8'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5050))
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, IPTVOrgProxyHandler)
    print(f"IPTV-Org Proxy Server is running on port {port}...")
    httpd.serve_forever()
    
