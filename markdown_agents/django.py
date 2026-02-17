"""Django middleware for Markdown for Agents."""

from __future__ import annotations

from markdown_agents.core import (
    accepts_markdown,
    build_markdown_headers,
    convert_html_to_markdown,
    is_html_content_type,
    logger,
)


class MarkdownAgentsMiddleware:
    """Django middleware that converts HTML responses to Markdown for AI agents.

    Usage in settings.py::

        MIDDLEWARE = [
            "markdown_agents.django.MarkdownAgentsMiddleware",
            ...
        ]
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        accept = request.META.get("HTTP_ACCEPT", "")
        if not accepts_markdown(accept):
            return response

        content_type = response.get("Content-Type", "")
        if not is_html_content_type(content_type):
            return response

        html = response.content.decode("utf-8", errors="replace")

        try:
            markdown = convert_html_to_markdown(html)
        except Exception:
            logger.warning("markdown conversion failed, falling back to original HTML", exc_info=True)
            return response

        response.content = markdown.encode("utf-8")
        for key, value in build_markdown_headers(markdown).items():
            response[key] = value

        return response
