# python-markdown-agents

Python middleware that implements **Markdown for Agents** — when an AI agent requests `Accept: text/markdown`, the middleware converts HTML responses to Markdown on the fly, reducing token consumption by ~80%.

Supports **Flask**, **Django**, and **FastAPI** from a single package.

Inspired by [Cloudflare's Markdown for Agents](https://blog.cloudflare.com/markdown-for-agents/) and [caddy-markdown-agents](https://github.com/shengwubin/caddy-markdown-agents).

## Why?

Feeding raw HTML to an AI agent is wasteful. A simple `## About Us` heading costs ~3 tokens in Markdown versus 12-15 tokens wrapped in HTML `<div>` tags, navigation bars, and scripts. For a typical web page, Markdown delivers the same content at **~80% fewer tokens**.

AI agents like [Claude Code](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview), [OpenCode](https://github.com/opencode-ai/opencode), and [Gemini CLI](https://github.com/google-gemini/gemini-cli) already send `Accept: text/markdown` headers when fetching web pages. This middleware lets your Python web app respond in kind — minimal code changes required.

## How It Works

```
Request → Accept: text/markdown?
  ├─ No  → Pass through unchanged
  └─ Yes → Get response → Is it text/html? → Convert to Markdown → Respond
```

The middleware:
1. Checks the `Accept` header for `text/markdown`
2. Only converts responses with `Content-Type: text/html`
3. Strips non-content elements: `<script>`, `<style>`, `<nav>`, `<footer>`, `<iframe>`, `<noscript>`
4. Returns Markdown with proper response headers

Regular browser requests are completely unaffected.

**Error handling**: If the HTML-to-Markdown conversion fails, the middleware falls back to serving the original HTML response and logs a warning. Your site never breaks because of a conversion issue.

## Installation

```bash
# Pick your framework
pip install markdown-agents[flask]
pip install markdown-agents[django]
pip install markdown-agents[fastapi]

# Or install all frameworks
pip install markdown-agents[flask,django,fastapi]
```

## Usage

### Flask

```python
from flask import Flask
from markdown_agents.flask import MarkdownAgents

app = Flask(__name__)
app.wsgi_app = MarkdownAgents(app.wsgi_app)
```

### Django

```python
# settings.py
MIDDLEWARE = [
    "markdown_agents.django.MarkdownAgentsMiddleware",
    # ... other middleware
]
```

### FastAPI

```python
from fastapi import FastAPI
from markdown_agents.fastapi import MarkdownAgentsMiddleware

app = FastAPI()
app.add_middleware(MarkdownAgentsMiddleware)
```

## Response Headers

| Header | Value | Purpose |
|---|---|---|
| `Content-Type` | `text/markdown; charset=utf-8` | Declares response format |
| `Vary` | `Accept` | Prevents cache poisoning — tells caches the same URL has multiple representations |
| `X-Markdown-Tokens` | `<integer>` | Estimated token count (`content_length / 4`) for agent context window management |

## Quick Demo

```bash
pip install markdown-agents[flask]
```

```python
# demo.py
from flask import Flask
from markdown_agents.flask import MarkdownAgents

app = Flask(__name__)
app.wsgi_app = MarkdownAgents(app.wsgi_app)

@app.route("/")
def index():
    return "<html><body><h1>Hello</h1><p>This is a <strong>test</strong>.</p></body></html>"

if __name__ == "__main__":
    app.run(port=8780)
```

```bash
# Regular request — returns HTML
curl http://localhost:8780/

# Agent request — returns Markdown
curl -H "Accept: text/markdown" http://localhost:8780/
```

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Lint
ruff check .

# Format
ruff format .
```

## Requirements

- Python 3.10+
- One of: Flask >= 2.0, Django >= 4.0, FastAPI >= 0.100

## License

[MIT](LICENSE)
