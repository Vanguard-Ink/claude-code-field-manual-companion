#!/usr/bin/env python3
"""Self-test for the runner's usage accounting (no Claude calls).

Two resumed calls in one session: `modelUsage` and `total_cost_usd` are
cumulative and include a subagent model; per-call figures must be deltas.
"""
import importlib.util, json, pathlib, sys

here = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("rl", here / "run-labs.py")
rl = importlib.util.module_from_spec(spec); spec.loader.exec_module(rl)


def stream(cost, sonnet, haiku):
    mu = {"claude-sonnet-x": {"inputTokens": 0, "outputTokens": sonnet, "cacheReadInputTokens": 0, "cacheCreationInputTokens": 0}}
    if haiku:
        mu["claude-haiku-x"] = {"inputTokens": 0, "outputTokens": haiku, "cacheReadInputTokens": 0, "cacheCreationInputTokens": 0}
    ev = {"type": "result", "session_id": "s1", "total_cost_usd": cost, "result": "ok",
          "usage": {"input_tokens": 0, "output_tokens": 0}, "modelUsage": mu}
    return json.dumps(ev)


turns, sid = [], None
for raw in (stream(0.10, 100, 50), stream(0.25, 300, 50)):
    t = rl.parse_stream(raw)
    rl.apply_delta(t, turns, sid)
    sid = t["session_id"]; turns.append(t)
got = ([t["total_tokens"] for t in turns], [round(t["cost_usd"], 2) for t in turns],
       [t["other_model_tokens"] for t in turns])
want = ([150, 200], [0.10, 0.15], [50, 0])
print("got", got, "want", want)
sys.exit(0 if got == want else 1)
