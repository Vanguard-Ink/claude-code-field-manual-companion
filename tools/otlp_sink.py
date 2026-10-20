#!/usr/bin/env python3
"""A tiny OTLP/HTTP-JSON receiver for LAB-13. Standard library only.

    python3 tools/otlp_sink.py <out.jsonl> [port]

Listens on 127.0.0.1:<port> (default 4318) and appends every POST to
/v1/metrics, /v1/logs or /v1/traces as one JSON line: {"path", "body"}.
Point Claude Code at it with:
    CLAUDE_CODE_ENABLE_TELEMETRY=1
    OTEL_METRICS_EXPORTER=otlp  OTEL_LOGS_EXPORTER=otlp
    OTEL_EXPORTER_OTLP_PROTOCOL=http/json
    OTEL_EXPORTER_OTLP_ENDPOINT=http://127.0.0.1:4318
Nothing leaves the machine. Stop it with Ctrl+C (or kill).
"""
import gzip
import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

OUT = sys.argv[1]
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 4318


class Sink(BaseHTTPRequestHandler):
    def do_POST(self):  # noqa: N802
        n = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(n)
        if self.headers.get("Content-Encoding") == "gzip":
            raw = gzip.decompress(raw)
        try:
            body = json.loads(raw or b"{}")
        except ValueError:
            body = {"undecodable_bytes": len(raw)}
        with open(OUT, "a", encoding="utf-8") as f:
            f.write(json.dumps({"path": self.path, "body": body}) + "\n")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b"{}")

    def log_message(self, *a):  # keep the console quiet
        pass


if __name__ == "__main__":
    HTTPServer(("127.0.0.1", PORT), Sink).serve_forever()
