"""FastAPI test server for markdown-agents middleware."""

import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse

from markdown_agents.fastapi import MarkdownAgentsMiddleware

app = FastAPI(title="Markdown Agents Demo")
app.add_middleware(MarkdownAgentsMiddleware)

SAMPLE_HTML = """<!DOCTYPE html>
<html>
<head><title>FastAPI Demo</title></head>
<body>
<nav><a href="/">Home</a> | <a href="/about">About</a></nav>
<h1>Welcome to FastAPI</h1>
<p>This is a <strong>demo page</strong> showing the markdown-agents middleware.</p>
<h2>Features</h2>
<ul>
    <li>Automatic HTML to Markdown conversion</li>
    <li>Strips navigation, scripts, and footers</li>
    <li>Token count estimation</li>
</ul>
<script>console.log("this will be stripped");</script>
<footer><p>Footer content - will be stripped</p></footer>
</body>
</html>"""


@app.get("/")
async def index():
    return HTMLResponse(SAMPLE_HTML)


@app.get("/about")
async def about():
    return HTMLResponse("""<!DOCTYPE html>
<html>
<head><title>About</title></head>
<body>
<nav><a href="/">Home</a></nav>
<h1>About This Project</h1>
<p>This middleware converts <em>HTML</em> responses to <strong>Markdown</strong>
when the client sends <code>Accept: text/markdown</code>.</p>
<h2>How It Works</h2>
<ol>
    <li>Check the Accept header</li>
    <li>Convert HTML to Markdown</li>
    <li>Return with proper headers</li>
</ol>
<footer><p>Copyright 2025</p></footer>
</body>
</html>""")


@app.get("/api/data")
async def api_data():
    """JSON endpoint - should pass through unchanged."""
    return JSONResponse({"message": "This JSON response is not converted", "status": "ok"})


if __name__ == "__main__":
    print("FastAPI server running on http://localhost:8782")
    print("Test with: curl http://localhost:8782/")
    print("Test with: curl -H 'Accept: text/markdown' http://localhost:8782/")
    uvicorn.run(app, host="0.0.0.0", port=8782)
