from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs


# index.htmlのパス。後から変わる
HTML_FILE = Path(__file__).parent / "index.html"


class AppHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # トップページへのアクセスだけ
        if self.path == "/":
            html = HTML_FILE.read_text(encoding="utf-8")

            html = html.replace("{{ input_value }}", "")
            html = html.replace("{{ row_1 }}", "")
            html = html.replace("{{ row_2 }}", "")
            html = html.replace("{{ row_3 }}", "")
            html = html.replace("{{ row_4 }}", "")

            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()

            self.wfile.write(html.encode("utf-8"))
            return

        self.send_error(404, "Not Found")

    def do_POST(self):
        if self.path == "/generate":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")

            form_data = parse_qs(body)
            input_value = form_data.get("result", [""])[0].strip()

            html = HTML_FILE.read_text(encoding="utf-8")

            html = html.replace("{{ input_value }}", input_value)
            html = html.replace("{{ row_1 }}", "鳩が")
            html = html.replace("{{ row_2 }}", "電車を")
            html = html.replace("{{ row_3 }}", "占拠したため、")
            html = html.replace("{{ row_4 }}", input_value)

            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()

            self.wfile.write(html.encode("utf-8"))
            return

        self.send_error(404, "Not Found")

def run():
    host = "0.0.0.0"
    port = 8000

    server = HTTPServer((host, port), AppHandler)

    print(f"サーバーを起動しました: http://localhost:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run()