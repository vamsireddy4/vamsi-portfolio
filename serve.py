#!/usr/bin/env python3
"""
HTTP server with pretty-URL + SPA sub-path support.

Rules:
  /                         → index.html
  /portfolio                → index.html
  /portfolio/about          → index.html  (SPA section)
  /portfolio/experience     → index.html  (SPA section)
  /portfolio/projects       → index.html  (SPA section)
  /<project>                → <project>.html (clean URL)
"""
import http.server
import os

PORT = 8000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

# ONLY these sub-paths are SPA section routes → serve index.html
SPA_SECTIONS = {'about', 'experience', 'projects', 'flagship'}


class PrettyURLHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        # Normalize path
        path = self.path.split("?")[0].split("#")[0].strip("/")
        parts = [p for p in path.split("/") if p]

        # 1. Root → index.html
        if len(parts) == 0:
            self.path = "/index.html"
            return super().do_GET()

        # 2. /portfolio (no sub-path) → index.html
        if parts == ['portfolio']:
            self.path = "/index.html"
            return super().do_GET()

        # 3. /portfolio/<section> — SPA sections
        if len(parts) == 2 and parts[0] == 'portfolio':
            segment = parts[1]
            if segment in SPA_SECTIONS:
                self.path = "/index.html"
                return super().do_GET()

        # 4. /<project> — check for <project>.html
        # This handles top-level clean URLs like /aios, /ltes, etc.
        if len(parts) == 1:
            slug = parts[0]
            if "." not in slug:
                local_path = os.path.join(DIRECTORY, slug + ".html")
                if os.path.isfile(local_path):
                    self.path = "/" + slug + ".html"
                    return super().do_GET()

        # 5. Fallback for static assets or nested paths
        return super().do_GET()

    def log_message(self, format, *args):
        print(f"  {self.address_string()} - {format % args}")


if __name__ == "__main__":
    with http.server.HTTPServer(("", PORT), PrettyURLHandler) as httpd:
        print(f"🚀  Serving at http://localhost:{PORT}")
        print(f"📁  Root: {DIRECTORY}")
        print("    Ctrl+C to stop\n")
        httpd.serve_forever()
