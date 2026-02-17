"""Flask middleware for Markdown for Agents."""

from __future__ import annotations

from markdown_agents.core import (
    accepts_markdown,
    build_markdown_headers,
    convert_html_to_markdown,
    is_html_content_type,
    logger,
)


class MarkdownAgents:
    """WSGI middleware that converts HTML responses to Markdown for AI agents.

    Usage::

        from markdown_agents.flask import MarkdownAgents
        app.wsgi_app = MarkdownAgents(app.wsgi_app)
    """

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        accept = environ.get("HTTP_ACCEPT", "")
        if not accepts_markdown(accept):
            return self.app(environ, start_response)

        # Capture the response from the wrapped app.
        status_line = None
        response_headers = None
        body_chunks: list[bytes] = []

        def capturing_start_response(status, headers, exc_info=None):
            nonlocal status_line, response_headers
            status_line = status
            response_headers = headers
            # Return a dummy write callable (required by WSGI spec but rarely used).
            return lambda s: body_chunks.append(s)

        app_iter = self.app(environ, capturing_start_response)
        try:
            for chunk in app_iter:
                body_chunks.append(chunk)
        finally:
            if hasattr(app_iter, "close"):
                app_iter.close()

        # Check if upstream response is HTML.
        headers_dict = dict(response_headers)
        content_type = headers_dict.get("Content-Type", "")

        if not is_html_content_type(content_type):
            # Pass through non-HTML responses unchanged.
            start_response(status_line, response_headers)
            return body_chunks

        html = b"".join(body_chunks).decode("utf-8", errors="replace")

        try:
            markdown = convert_html_to_markdown(html)
        except Exception:
            logger.warning("markdown conversion failed, falling back to original HTML", exc_info=True)
            start_response(status_line, response_headers)
            return body_chunks

        md_headers = build_markdown_headers(markdown)

        # Rebuild headers: replace Content-Type and Content-Length, add Vary and token count.
        new_headers = [
            (k, v) for k, v in response_headers if k not in ("Content-Type", "Content-Length")
        ]
        for k, v in md_headers.items():
            new_headers.append((k, v))

        start_response(status_line, new_headers)
        return [markdown.encode("utf-8")]
