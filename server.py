import json
import urllib.request
from urllib.parse import parse_qs, urlparse
from http.server import HTTPServer, BaseHTTPRequestHandler
import os

class IPTVOrgProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        query_params = parse_qs(parsed_path.query)
        path = parsed_path.path
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response_data = {"status": "error", "message": "Endpoint not found"}
        
        # 1. مسار جلب كل قنوات الدولة (القديم)
        if path == '/channels':
            country = query_params.get('country', ['iq'])[0]
            iptv_url = f"https://raw.githubusercontent.com/iptv-org/iptv/master/streams/{country}.m3u"
            channels = []
            try:
                req = urllib.request.Request(iptv_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req) as response:
                    m3u_data = response.read().decode('utf-8', errors='ignore')
                    lines = m3u_data.splitlines()
                    current_name = ''
                    for line in lines:
                        line = line.strip()
                        if line.startswith('#EXTINF:'):
                            if ',' in line:
                                current_name = line.split(',')[-1].strip()
                        elif line and not line.startswith('#'):
                            if current_name:
                                channels.append({"name": current_name, "urls": [line]})
                                current_name = ''
                response_data = {"status": "success", "count": len(channels), "channels": channels}
            except Exception as e:
                response_data = {"status": "error", "message": str(e), "channels": []}

        # 2. مسار البحث الذكي عن قناة معينة وتوفير روابط متعددة
        elif path == '/search':
            query = query_params.get('q', [''])[0].lower()
            country = query_params.get('country', ['iq'])[0]
            iptv_url = f"https://raw.githubusercontent.com/iptv-org/iptv/master/streams/{country}.m3u"
            
            matched_channels = []
            try:
                req = urllib.request.Request(iptv_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req) as response:
                    m3u_data = response.read().decode('utf-8', errors='ignore')
                    lines = m3u_data.splitlines()
                    current_name = ''
                    for line in lines:
                        line = line.strip()
                        if line.startswith('#EXTINF:'):
                            if ',' in line:
                                current_name = line.split(',')[-1].strip()
                        elif line and not line.startswith('#'):
                            if current_name:
                                # إذا اسم القناة مطابق للبحث، نجمع الروابط الاحتياطية
                                if query in current_name.lower():
                                    # ندور إذا القناة موجودة مسبقاً حتى نضيف الروابط كاحتياط
                                    existing = next((ch for ch in matched_channels if ch["name"].lower() == current_name.lower()), None)
                                    if existing:
                                        existing["urls"].append(line)
                                    else:
                                        matched_channels.append({
                                            "name": current_name,
                                            "urls": [line] # قائمة روابط متعددة لتجنب الانقطاع
                                        })
                                current_name = ''
                                
                response_data = {
                    "status": "success", 
                    "query": query,
                    "count": len(matched_channels),
                    "channels": matched_channels
                }
            except Exception as e:
                response_data = {"status": "error", "message": str(e), "channels": []}

        self.wfile.write(json.dumps(response_data).encode('utf-8'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5050))
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, IPTVOrgProxyHandler)
    print(f"Smart IPTV Proxy Server is running on port {port}...")
    httpd.serve_forever()
                
