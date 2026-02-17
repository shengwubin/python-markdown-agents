"""Django test server for markdown-agents middleware."""

import django
from django.conf import settings

settings.configure(
    DEBUG=True,
    SECRET_KEY="demo-secret-key-not-for-production",
    ROOT_URLCONF=__name__,
    MIDDLEWARE=[
        "markdown_agents.django.MarkdownAgentsMiddleware",
    ],
    ALLOWED_HOSTS=["*"],
)
django.setup()

from django.http import HttpResponse, JsonResponse
from django.urls import path

SAMPLE_HTML = """<!DOCTYPE html>
<html>
<head><title>Django Demo</title></head>
<body>
<nav><a href="/">Home</a> | <a href="/about">About</a></nav>
<h1>Welcome to Django</h1>
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


def index(request):
    return HttpResponse(SAMPLE_HTML, content_type="text/html; charset=utf-8")


def about(request):
    return HttpResponse("""<!DOCTYPE html>
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
</html>""", content_type="text/html; charset=utf-8")


def api_data(request):
    """JSON endpoint - should pass through unchanged."""
    return JsonResponse({"message": "This JSON response is not converted", "status": "ok"})


urlpatterns = [
    path("", index),
    path("about", about),
    path("api/data", api_data),
]

if __name__ == "__main__":
    from django.core.management import execute_from_command_line

    print("Django server running on http://localhost:8781")
    print("Test with: curl http://localhost:8781/")
    print("Test with: curl -H 'Accept: text/markdown' http://localhost:8781/")
    execute_from_command_line(["manage.py", "runserver", "8781", "--noreload"])
