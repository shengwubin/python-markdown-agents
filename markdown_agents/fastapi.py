"""FastAPI/Starlette middleware for Markdown for Agents."""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from markdown_agents.core import (
    accepts_markdown,
    build_markdown_headers,
    convert_html_to_markdown,
    is_html_content_type,
    logger,
)


class MarkdownAgentsMiddleware(BaseHTTPMiddleware):
    """Starlette/FastAPI middleware that converts HTML responses to Markdown for AI agents.

    Usage::

        from markdown_agents.fastapi import MarkdownAgentsMiddleware
        app.add_middleware(MarkdownAgentsMiddleware)
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        accept = request.headers.get("accept", "")
        if not accepts_markdown(accept):
            return await call_next(request)

        response = await call_next(request)

        content_type = response.headers.get("content-type", "")
        if not is_html_content_type(content_type):
            return response

        # Read the streaming body.
        body_chunks: list[bytes] = []
        async for chunk in response.body_iterator:
            if isinstance(chunk, str):
                chunk = chunk.encode("utf-8")
            body_chunks.append(chunk)

        html = b"".join(body_chunks).decode("utf-8", errors="replace")

        try:
            markdown = convert_html_to_markdown(html)
        except Exception:
            logger.warning("markdown conversion failed, falling back to original HTML", exc_info=True)
            return Response(
                content=html,
                status_code=response.status_code,
                headers=dict(response.headers),
            )

        md_headers = build_markdown_headers(markdown)
        # Merge: keep original headers, override with markdown-specific ones.
        headers = dict(response.headers)
        headers.update(md_headers)

        return Response(
            content=markdown,
            status_code=response.status_code,
            headers=headers,
        )
