"""Tests for the Django middleware."""

import django
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.test import RequestFactory

from markdown_agents.django import MarkdownAgentsMiddleware

# Minimal Django configuration for tests.
if not settings.configured:
    settings.configure(
        DEBUG=True,
        DATABASES={},
        INSTALLED_APPS=[],
        ROOT_URLCONF=None,
    )
    django.setup()

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

factory = RequestFactory()


def html_view(request):
    return HttpResponse(TEST_HTML, content_type="text/html; charset=utf-8")


def json_view(request):
    return JsonResponse({"key": "value"})


def make_middleware(view_func):
    return MarkdownAgentsMiddleware(view_func)


class TestDjangoMarkdownConversion:
    def test_markdown_request_converts_html(self):
        middleware = make_middleware(html_view)
        request = factory.get("/", HTTP_ACCEPT="text/markdown")
        resp = middleware(request)

        assert resp["Content-Type"] == "text/markdown; charset=utf-8"
        body = resp.content.decode()
        assert "# Hello World" in body
        assert "**test**" in body
        assert "Navigation" not in body
        assert "Footer" not in body

    def test_regular_request_passes_through(self):
        middleware = make_middleware(html_view)
        request = factory.get("/", HTTP_ACCEPT="text/html")
        resp = middleware(request)

        body = resp.content.decode()
        assert "<h1>Hello World</h1>" in body

    def test_non_html_passes_through(self):
        middleware = make_middleware(json_view)
        request = factory.get("/api/data", HTTP_ACCEPT="text/markdown")
        resp = middleware(request)

        assert "application/json" in resp["Content-Type"]

    def test_vary_header_is_set(self):
        middleware = make_middleware(html_view)
        request = factory.get("/", HTTP_ACCEPT="text/markdown")
        resp = middleware(request)

        assert "Accept" in resp.get("Vary", "")

    def test_token_count_header(self):
        middleware = make_middleware(html_view)
        request = factory.get("/", HTTP_ACCEPT="text/markdown")
        resp = middleware(request)

        token_str = resp.get("X-Markdown-Tokens")
        assert token_str is not None
        tokens = int(token_str)
        expected = len(resp.content.decode()) // 4
        assert tokens == expected
