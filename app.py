from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs

from backend.generator import generate_excuse


# app.pyが置かれているプロジェクト直下
BASE_DIR = Path(__file__).parent

# HTMLとCSSのファイルパス
START_HTML_FILE = BASE_DIR / "templates" / "start.html"
INDEX_HTML_FILE = BASE_DIR / "templates" / "index.html"
CSS_FILE = BASE_DIR / "static" / "style.css"


class AppHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 最初のカテゴリ選択画面を表示する
        if self.path == "/":
            html = START_HTML_FILE.read_text(encoding="utf-8")

            self.send_response(200)
            self.send_header(
                "Content-Type",
                "text/html; charset=utf-8"
            )
            self.end_headers()

            self.wfile.write(html.encode("utf-8"))
            return

        # CSSファイルを返す
        if self.path == "/static/style.css":
            css = CSS_FILE.read_text(encoding="utf-8")

            self.send_response(200)
            self.send_header(
                "Content-Type",
                "text/css; charset=utf-8"
            )
            self.end_headers()

            self.wfile.write(css.encode("utf-8"))
            return

        self.send_error(404, "Not Found")

    def do_POST(self):
        # カテゴリ選択後、入力画面を表示する
        if self.path == "/input":
            content_length = int(
                self.headers.get("Content-Length", 0)
            )

            body = self.rfile.read(
                content_length
            ).decode("utf-8")

            form_data = parse_qs(body)

            category = (
                form_data.get("category", ["general"])[0]
            )

            html = INDEX_HTML_FILE.read_text(
                encoding="utf-8"
            )

            html = html.replace(
                "{{ category }}",
                category
            )
            html = html.replace(
                "{{ input_value }}",
                ""
            )
            html = html.replace("{{ row_1 }}", "")
            html = html.replace("{{ row_2 }}", "")
            html = html.replace("{{ row_3 }}", "")
            html = html.replace("{{ row_4 }}", "")

            self.send_response(200)
            self.send_header(
                "Content-Type",
                "text/html; charset=utf-8"
            )
            self.end_headers()

            self.wfile.write(html.encode("utf-8"))
            return

        # 入力内容から言い訳を生成する
        if self.path == "/generate":
            content_length = int(
                self.headers.get("Content-Length", 0)
            )

            body = self.rfile.read(
                content_length
            ).decode("utf-8")

            form_data = parse_qs(body)

            input_value = (
                form_data.get("result", [""])[0].strip()
            )

            category = (
                form_data.get("category", ["general"])[0]
            )

            excuse = generate_excuse()

            html = INDEX_HTML_FILE.read_text(
                encoding="utf-8"
            )

            html = html.replace(
                "{{ category }}",
                category
            )
            html = html.replace(
                "{{ input_value }}",
                input_value
            )
            html = html.replace(
                "{{ row_1 }}",
                excuse["row_1"]
            )
            html = html.replace(
                "{{ row_2 }}",
                excuse["row_2"]
            )
            html = html.replace(
                "{{ row_3 }}",
                excuse["row_3"]
            )
            html = html.replace(
                "{{ row_4 }}",
                input_value
            )

            self.send_response(200)
            self.send_header(
                "Content-Type",
                "text/html; charset=utf-8"
            )
            self.end_headers()

            self.wfile.write(html.encode("utf-8"))
            return

        self.send_error(404, "Not Found")


def run():
    host = "0.0.0.0"
    port = 8000

    server = HTTPServer(
        (host, port),
        AppHandler
    )

    print(
        f"サーバーを起動しました: "
        f"http://localhost:{port}"
    )

    server.serve_forever()


if __name__ == "__main__":
    run()