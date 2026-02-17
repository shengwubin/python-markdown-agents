"""Tests for the core conversion logic."""

import pytest

from markdown_agents.core import (
    accepts_markdown,
    build_markdown_headers,
    convert_html_to_markdown,
    estimate_tokens,
    is_html_content_type,
)

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


class TestAcceptsMarkdown:
    @pytest.mark.parametrize(
        "accept,expected",
        [
            ("text/markdown", True),
            ("text/markdown, text/html", True),
            ("text/html, text/markdown;q=0.9", True),
            ("text/html", False),
            ("application/json", False),
            ("", False),
        ],
    )
    def test_accept_header_detection(self, accept: str, expected: bool):
        assert accepts_markdown(accept) == expected


class TestIsHtmlContentType:
    @pytest.mark.parametrize(
        "ct,expected",
        [
            ("text/html", True),
            ("text/html; charset=utf-8", True),
            ("application/json", False),
            ("text/plain", False),
            ("", False),
        ],
    )
    def test_content_type_detection(self, ct: str, expected: bool):
        assert is_html_content_type(ct) == expected


class TestConvertHtmlToMarkdown:
    def test_basic_conversion(self):
        md = convert_html_to_markdown(TEST_HTML)
        assert "# Hello World" in md
        assert "**test**" in md

    def test_strips_nav(self):
        md = convert_html_to_markdown(TEST_HTML)
        assert "Navigation" not in md

    def test_strips_footer(self):
        md = convert_html_to_markdown(TEST_HTML)
        assert "Footer" not in md

    def test_strips_script(self):
        html = "<html><body><script>alert('xss')</script><p>Content</p></body></html>"
        md = convert_html_to_markdown(html)
        assert "alert" not in md
        assert "Content" in md

    def test_strips_style(self):
        html = "<html><body><style>body{color:red}</style><p>Content</p></body></html>"
        md = convert_html_to_markdown(html)
        assert "color" not in md
        assert "Content" in md

    def test_table_support(self):
        html = "<table><tr><th>Name</th><th>Age</th></tr><tr><td>Alice</td><td>30</td></tr></table>"
        md = convert_html_to_markdown(html)
        assert "Name" in md
        assert "Alice" in md


class TestEstimateTokens:
    def test_basic_estimation(self):
        # 20 chars -> 5 tokens
        assert estimate_tokens("a" * 20) == 5

    def test_empty_string(self):
        assert estimate_tokens("") == 0

    def test_integer_division(self):
        # 7 chars -> 1 token (floor division)
        assert estimate_tokens("a" * 7) == 1


class TestBuildMarkdownHeaders:
    def test_headers_complete(self):
        md = "# Hello\n\nSome content here."
        headers = build_markdown_headers(md)
        assert headers["Content-Type"] == "text/markdown; charset=utf-8"
        assert headers["Vary"] == "Accept"
        assert headers["X-Markdown-Tokens"] == str(len(md) // 4)
        assert "Content-Length" in headers
