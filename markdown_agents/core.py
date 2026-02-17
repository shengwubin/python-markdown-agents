"""Core logic for Markdown for Agents: header detection, HTML conversion, response headers."""

from __future__ import annotations

import logging
from typing import Any

from markdownify import MarkdownConverter

logger = logging.getLogger("markdown_agents")

# Tags to strip during conversion — these are non-content boilerplate.
STRIP_TAGS = ["script", "style", "nav", "footer", "iframe", "noscript"]

MARKDOWN_CONTENT_TYPE = "text/markdown; charset=utf-8"


class _AgentConverter(MarkdownConverter):
    """Custom converter that strips boilerplate tags."""

    def convert_script(self, el: Any, text: str, parent_tags: set[str]) -> str:
        return ""

    def convert_style(self, el: Any, text: str, parent_tags: set[str]) -> str:
        return ""

    def convert_nav(self, el: Any, text: str, parent_tags: set[str]) -> str:
        return ""

    def convert_footer(self, el: Any, text: str, parent_tags: set[str]) -> str:
        return ""

    def convert_iframe(self, el: Any, text: str, parent_tags: set[str]) -> str:
        return ""

    def convert_noscript(self, el: Any, text: str, parent_tags: set[str]) -> str:
        return ""


def accepts_markdown(accept: str) -> bool:
    """Check whether the Accept header includes text/markdown."""
    return "text/markdown" in accept


def is_html_content_type(content_type: str) -> bool:
    """Check whether the Content-Type indicates HTML."""
    return "text/html" in content_type


def convert_html_to_markdown(html: str) -> str:
    """Convert HTML to Markdown, stripping boilerplate elements.

    Returns the Markdown string. Raises on conversion failure.
    """
    return _AgentConverter(heading_style="ATX").convert(html).strip()


def estimate_tokens(text: str) -> int:
    """Estimate token count using char_count / 4 (aligned with Cloudflare's approach)."""
    return len(text) // 4


def build_markdown_headers(markdown: str) -> dict[str, str]:
    """Build the response headers for a converted Markdown response."""
    return {
        "Content-Type": MARKDOWN_CONTENT_TYPE,
        "Vary": "Accept",
        "X-Markdown-Tokens": str(estimate_tokens(markdown)),
        "Content-Length": str(len(markdown.encode("utf-8"))),
    }
