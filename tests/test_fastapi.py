"""Tests for the FastAPI/Starlette middleware."""

import pytest
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from httpx import ASGITransport, AsyncClient

from markdown_agents.fastapi import MarkdownAgentsMiddleware

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
    app = FastAPI()
    app.add_middleware(MarkdownAgentsMiddleware)

    @app.get("/")
    async def index():
        return HTMLResponse(TEST_HTML)

    @app.get("/json")
    async def json_endpoint():
        return JSONResponse({"key": "value"})

    return app


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
async def client(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


class TestFastAPIMarkdownConversion:
    async def test_markdown_request_converts_html(self, client):
        resp = await client.get("/", headers={"Accept": "text/markdown"})

        assert "text/markdown" in resp.headers["content-type"]
        body = resp.text
        assert "# Hello World" in body
        assert "**test**" in body
        assert "Navigation" not in body
        assert "Footer" not in body

    async def test_regular_request_passes_through(self, client):
        resp = await client.get("/", headers={"Accept": "text/html"})

        assert "<h1>Hello World</h1>" in resp.text

    async def test_non_html_passes_through(self, client):
        resp = await client.get("/json", headers={"Accept": "text/markdown"})

        assert "application/json" in resp.headers["content-type"]

    async def test_vary_header_is_set(self, client):
        resp = await client.get("/", headers={"Accept": "text/markdown"})

        assert "Accept" in resp.headers.get("vary", "")

    async def test_token_count_header(self, client):
        resp = await client.get("/", headers={"Accept": "text/markdown"})

        token_str = resp.headers.get("x-markdown-tokens")
        assert token_str is not None
        tokens = int(token_str)
        expected = len(resp.text) // 4
        assert tokens == expected
