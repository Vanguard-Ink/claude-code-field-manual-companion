"""Find loop signals in Claude Code transcripts (stream-json or session JSONL).

    python3 loopscan.py <transcript.jsonl> [...]

Prints one summary line: test runs, failing test runs, the longest streak of
consecutive test runs that failed the same way, and the most edits to one file.
A streak of 3 or more counts as a loop incident.
"""

import json
import re
import sys
from collections import Counter

TEST = re.compile(r"\bpytest\b|make\b.*\b(test|check)\b")
calls: dict[str, tuple[str, str]] = {}
runs: list[tuple[bool, str]] = []
edits: Counter[str] = Counter()

for path in sys.argv[1:]:
    for raw in open(path, errors="replace"):
        try:
            ev = json.loads(raw)
        except json.JSONDecodeError:
            continue
        content = (ev.get("message") or {}).get("content")
        if not isinstance(content, list):
            continue
        for c in content:
            if c.get("type") == "tool_use":
                inp = c.get("input") or {}
                calls[c.get("id", "")] = (c.get("name", ""), inp.get("command") or inp.get("file_path") or "")
                if c.get("name") in ("Edit", "Write", "MultiEdit"):
                    edits[inp.get("file_path", "")] += 1
            elif c.get("type") == "tool_result":
                name, arg = calls.get(c.get("tool_use_id", ""), ("", ""))
                if name != "Bash" or not TEST.search(arg):
                    continue
                body = c.get("content")
                if isinstance(body, list):
                    body = "\n".join(b.get("text", "") for b in body if isinstance(b, dict))
                body = str(body or "")
                failed = bool(c.get("is_error")) or bool(re.search(r"\d+ failed|Error \d|FAILED", body))
                ids = sorted(set(re.findall(r"^(?:FAILED|ERROR) (\S+)", body, re.M)))
                tail = body.strip().splitlines()[-1] if body.strip() else ""
                sig = arg + "|" + (" ".join(ids) if ids else tail)
                runs.append((failed, sig))

streak = best = 0
last = None
for failed, sig in runs:
    if failed and sig == last:
        streak += 1
    else:
        streak = 1 if failed else 0
    last = sig if failed else None
    best = max(best, streak)
top = edits.most_common(1)
top_s = f"{top[0][1]} ({top[0][0].rsplit('/', 1)[-1]})" if top else "0"
print(f"tests {len(runs)}, failed {sum(f for f, _ in runs)}, same-fail streak {best}"
      f"{' LOOP' if best >= 3 else ''}, max edits {top_s}")
