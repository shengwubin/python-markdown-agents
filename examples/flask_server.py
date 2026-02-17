"""Flask test server for markdown-agents middleware."""

from flask import Flask

from markdown_agents.flask import MarkdownAgents

app = Flask(__name__)
app.wsgi_app = MarkdownAgents(app.wsgi_app)

SAMPLE_HTML = """<!DOCTYPE html>
<html>
<head><title>Flask Demo</title></head>
<body>
<nav><a href="/">Home</a> | <a href="/about">About</a></nav>
<h1>Welcome to Flask</h1>
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


@app.route("/")
def index():
    return SAMPLE_HTML


@app.route("/about")
def about():
    return """<!DOCTYPE html>
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
</html>"""


@app.route("/api/data")
def api_data():
    """JSON endpoint - should pass through unchanged."""
    return {"message": "This JSON response is not converted", "status": "ok"}


if __name__ == "__main__":
    print("Flask server running on http://localhost:8780")
    print("Test with: curl http://localhost:8780/")
    print("Test with: curl -H 'Accept: text/markdown' http://localhost:8780/")
    app.run(port=8780)
