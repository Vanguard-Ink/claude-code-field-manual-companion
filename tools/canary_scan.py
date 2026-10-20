#!/usr/bin/env python3
"""Find a canary string anywhere in an OTLP export. Standard library only.

    python3 tools/canary_scan.py <export.jsonl> <canary>

Reads the file otlp_sink.py writes (one {"path", "body"} per line) and
prints the JSON path of every value that contains the canary: attributes,
span events, log bodies, anything. Exit 0 = not found, 1 = found,
2 = nothing to scan. Use it after a run whose prompt, a file it read, and
a command it ran all carry the same made-up secret (Chapter 15).
"""
import json
import sys


def walk(node, path, canary, hits):
    if isinstance(node, dict):
        # OTLP attributes are lists of {"key", "value"}: name them by key.
        if "key" in node and "value" in node:
            path = f"{path}[{node['key']}]"
            walk(node["value"], path, canary, hits)
            return
        for k, v in node.items():
            walk(v, f"{path}.{k}", canary, hits)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            walk(v, f"{path}[{i}]", canary, hits)
    elif isinstance(node, str) and canary in node:
        hits.append(path)


def main() -> int:
    src, canary = sys.argv[1], sys.argv[2]
    hits: list[str] = []
    lines = 0
    with open(src, encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            if not line.strip():
                continue
            lines += 1
            rec = json.loads(line)
            walk(rec.get("body", rec), f"line{n}:{rec.get('path', '')}",
                 canary, hits)
    if lines == 0:
        print("nothing to scan: the export is empty")
        return 2
    for h in hits:
        print(h)
    print(f"{len(hits)} hit(s) in {lines} export line(s)")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
