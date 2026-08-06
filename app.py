from html import escape
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs

from backend.generator import generate_excuse


# app.pyが置かれているプロジェクト直下
BASE_DIR = Path(__file__).parent

# HTMLファイル
START_HTML_FILE = BASE_DIR / "templates" / "start.html"
TUTORIAL_HTML_FILE = BASE_DIR / "templates" / "tutorial.html"
INDEX_HTML_FILE = BASE_DIR / "templates" / "index.html"
REPLY_HTML_FILE = BASE_DIR / "templates" / "reply.html"

# CSSファイル
START_CSS_FILE = BASE_DIR / "static" / "start.css"
STYLE_CSS_FILE = BASE_DIR / "static" / "style.css"
TUTORIAL_CSS_FILE = BASE_DIR / "static" / "tutorial.css"


VALID_CATEGORIES = {
    "movement",
    "submission",
    "communication",
    "general",
}


REPLIES = {
    "movement": [
        "わかりました。次からは時間に余裕を持って来てください。",
        "事情はわかりました。次回からは気をつけてください。",
    ],
    "submission": [
        "わかりました。提出期限を少し伸ばすので、早めに提出してください。",
        "事情はわかりました。できるだけ早く提出してください。",
    ],
    "communication": [
        "わかりました。次回からは事前に連絡してください。",
        "事情はわかりました。今後は早めに連絡してください。",
    ],
    "general": [
        "わかりました。次からは気をつけてください。",
        "事情はわかりました。次回から注意してください。",
    ],
}


def normalize_category(category):
    """
    不正なカテゴリーが渡された場合はgeneralに戻す。
    """
    if category in VALID_CATEGORIES:
        return category

    return "general"


def read_form_data(handler):
    """
    POSTされたフォームデータを読み取る。
    """
    content_length = int(
        handler.headers.get(
            "Content-Length",
            0,
        )
    )

    body = handler.rfile.read(
        content_length
    ).decode("utf-8")

    return parse_qs(body)


def get_form_value(form_data, name, default=""):
    """
    フォームデータから指定された値を1つ取り出す。
    """
    return form_data.get(
        name,
        [default],
    )[0].strip()


def render_template(file_path, values=None):
    """
    HTMLファイルを読み込み、
    プレースホルダーを指定された値で置換する。
    """
    html = file_path.read_text(
        encoding="utf-8"
    )

    if values is None:
        return html

    for key, value in values.items():
        placeholder = "{{ " + key + " }}"

        html = html.replace(
            placeholder,
            escape(str(value)),
        )

    return html


def send_response(
    handler,
    content,
    content_type,
    status_code=200,
):
    """
    指定された内容をHTTPレスポンスとして返す。
    """
    handler.send_response(
        status_code
    )

    handler.send_header(
        "Content-Type",
        content_type,
    )

    handler.end_headers()

    handler.wfile.write(
        content.encode("utf-8")
    )


def send_html(
    handler,
    html,
    status_code=200,
):
    """
    HTMLレスポンスを返す。
    """
    send_response(
        handler,
        html,
        "text/html; charset=utf-8",
        status_code,
    )


def send_css(
    handler,
    css,
    status_code=200,
):
    """
    CSSレスポンスを返す。
    """
    send_response(
        handler,
        css,
        "text/css; charset=utf-8",
        status_code,
    )


def choose_reply(category):
    """
    カテゴリーに対応する先生の返答を選ぶ。
    現時点では先頭の返答を使用する。
    """
    category = normalize_category(
        category
    )

    return REPLIES[category][0]


def build_completed_text(
    row_1,
    row_2,
    row_3,
    input_value,
):
    """
    生成された言い訳とユーザー入力を連結する。
    """
    return (
        row_1
        + row_2
        + row_3
        + input_value
    )


class AppHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 1ページ目：カテゴリー選択画面
        if self.path == "/":
            html = render_template(
                START_HTML_FILE
            )

            send_html(
                self,
                html,
            )
            return

        # 共通CSS
        if self.path == "/static/style.css":
            css = STYLE_CSS_FILE.read_text(
                encoding="utf-8"
            )

            send_css(
                self,
                css,
            )
            return

        # 1ページ目専用CSS
        if self.path == "/static/start.css":
            css = START_CSS_FILE.read_text(
                encoding="utf-8"
            )

            send_css(
                self,
                css,
            )
            return


        # 2ページ目専用CSS
        if self.path == "/static/tutorial.css":
            css = TUTORIAL_CSS_FILE.read_text(
                encoding="utf-8"
            )

            send_css(
                self,
                css,
            )
            return

        self.send_error(
            404,
            "Not Found",
        )

    def do_POST(self):
        # 1ページ目から2ページ目へ進む
        if self.path == "/input":
            form_data = read_form_data(
                self
            )

            category = get_form_value(
                form_data,
                "category",
                "general",
            )

            category = normalize_category(
                category
            )

            html = render_template(
                TUTORIAL_HTML_FILE,
                {
                    "category": category,
                    "input_value": "",
                    "error_message": "",
                },
            )

            send_html(
                self,
                html,
            )
            return

        # 2ページ目の入力から言い訳を生成する
        # 3ページ目の再生成にも使用する
        if self.path == "/generate":
            form_data = read_form_data(
                self
            )

            input_value = get_form_value(
                form_data,
                "result",
            )

            category = get_form_value(
                form_data,
                "category",
                "general",
            )

            category = normalize_category(
                category
            )

            # 未入力なら2ページ目を再表示する
            if not input_value:
                html = render_template(
                    TUTORIAL_HTML_FILE,
                    {
                        "category": category,
                        "input_value": "",
                        "error_message": "※入力してください。",
                    },
                )

                send_html(
                    self,
                    html,
                    400,
                )
                return

            excuse = generate_excuse(
                category
            )

            html = render_template(
                INDEX_HTML_FILE,
                {
                    "category": category,
                    "input_value": input_value,
                    "row_1": excuse["row_1"],
                    "row_2": excuse["row_2"],
                    "row_3": excuse["row_3"],
                    "row_4": input_value,
                },
            )

            send_html(
                self,
                html,
            )
            return

        # 3ページ目で確定した言い訳を4ページ目へ送る
        if self.path == "/reply":
            form_data = read_form_data(
                self
            )

            category = get_form_value(
                form_data,
                "category",
                "general",
            )

            category = normalize_category(
                category
            )

            input_value = get_form_value(
                form_data,
                "result",
            )

            row_1 = get_form_value(
                form_data,
                "row_1",
            )

            row_2 = get_form_value(
                form_data,
                "row_2",
            )

            row_3 = get_form_value(
                form_data,
                "row_3",
            )

            completed_text = build_completed_text(
                row_1,
                row_2,
                row_3,
                input_value,
            )

            reply_text = choose_reply(
                category
            )

            html = render_template(
                REPLY_HTML_FILE,
                {
                    "category": category,
                    "input_value": input_value,
                    "row_1": row_1,
                    "row_2": row_2,
                    "row_3": row_3,
                    "completed_text": completed_text,
                    "reply_text": reply_text,
                },
            )

            send_html(
                self,
                html,
            )
            return

        # 4ページ目から同じ内容の3ページ目へ戻る
        if self.path == "/back":
            form_data = read_form_data(
                self
            )

            category = get_form_value(
                form_data,
                "category",
                "general",
            )

            category = normalize_category(
                category
            )

            input_value = get_form_value(
                form_data,
                "result",
            )

            row_1 = get_form_value(
                form_data,
                "row_1",
            )

            row_2 = get_form_value(
                form_data,
                "row_2",
            )

            row_3 = get_form_value(
                form_data,
                "row_3",
            )

            html = render_template(
                INDEX_HTML_FILE,
                {
                    "category": category,
                    "input_value": input_value,
                    "row_1": row_1,
                    "row_2": row_2,
                    "row_3": row_3,
                    "row_4": input_value,
                },
            )

            send_html(
                self,
                html,
            )
            return

        self.send_error(
            404,
            "Not Found",
        )


def run():
    host = "0.0.0.0"
    port = 8000

    server = HTTPServer(
        (host, port),
        AppHandler,
    )

    print(
        f"サーバーを起動しました: "
        f"http://localhost:{port}"
    )

    server.serve_forever()


if __name__ == "__main__":
    run()