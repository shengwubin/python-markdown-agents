"""Tests for the Flask middleware."""

from flask import Flask

from markdown_agents.flask import MarkdownAgents

TEST_HTML = """<!DOCTYPE html>
<html>
<head><title>Test Page</title></head>
<body>
<nav>Navigation</nav>
<h1>Hello World</h1>
<p>This is a <strong>test</strong> paragraph.</p>
<footer>Footer content</footer>
</body>
</html>"""


def create_app():
    app = Flask(__name__)

    @app.route("/")
    def index():
        return TEST_HTML, 200, {"Content-Type": "text/html; charset=utf-8"}

    @app.route("/json")
    def json_endpoint():
        return '{"key": "value"}', 200, {"Content-Type": "application/json"}

    app.wsgi_app = MarkdownAgents(app.wsgi_app)
    return app


class TestFlaskMarkdownConversion:
    def test_markdown_request_converts_html(self):
        app = create_app()
        client = app.test_client()
        resp = client.get("/", headers={"Accept": "text/markdown"})

        assert resp.content_type == "text/markdown; charset=utf-8"
        body = resp.data.decode()
        assert "# Hello World" in body
        assert "**test**" in body
        assert "Navigation" not in body
        assert "Footer" not in body

    def test_regular_request_passes_through(self):
        app = create_app()
        client = app.test_client()
        resp = client.get("/", headers={"Accept": "text/html"})

        body = resp.data.decode()
        assert "<h1>Hello World</h1>" in body

    def test_non_html_passes_through(self):
        app = create_app()
        client = app.test_client()
        resp = client.get("/json", headers={"Accept": "text/markdown"})

        assert resp.content_type == "application/json"
        assert resp.data == b'{"key": "value"}'

    def test_vary_header_is_set(self):
        app = create_app()
        client = app.test_client()
        resp = client.get("/", headers={"Accept": "text/markdown"})

        assert "Accept" in resp.headers.get("Vary", "")

    def test_token_count_header(self):
        app = create_app()
        client = app.test_client()
        resp = client.get("/", headers={"Accept": "text/markdown"})

        token_str = resp.headers.get("X-Markdown-Tokens")
        assert token_str is not None
        tokens = int(token_str)
        expected = len(resp.data.decode()) // 4
        assert tokens == expected
