#!/usr/bin/env python3
"""LAB-13 part A: compare what OpenTelemetry reported with the transcripts.

    python3 labs/lab-13-governance/compare_otel.py <otel.jsonl> <run-dir> [<run-dir> ...]

Reads the sink file written by tools/otlp_sink.py and sums:
- claude_code.token.usage by type, and claude_code.cost.usage, per session.id
  (cumulative series: last value per series; delta series: summed);
- claude_code.user_prompt events, and whether any carried prompt text.
Then recounts the same sessions from their stream-json transcripts
(cumulative modelUsage, as tools/recount_usage.py does) and prints both.
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

sink, runs = Path(sys.argv[1]), [Path(p) for p in sys.argv[2:]]


def attrs(lst):
    out = {}
    for a in lst or []:
        v = a.get("value", {})
        out[a.get("key")] = next(iter(v.values()), None) if v else None
    return out


series = {}            # (metric, frozen attrs) -> value (cumulative) or summed (delta)
prompts = defaultdict(lambda: {"events": 0, "with_text": 0, "assistant_text": 0})


def real_text(v):
    """True for actual content; redacted placeholders don't count."""
    return bool(v) and str(v).strip() not in ("<REDACTED>", "REDACTED", "[REDACTED]")
for ln in sink.read_text().splitlines():
    rec = json.loads(ln)
    body = rec["body"]
    for rm in body.get("resourceMetrics", []):
        for sm in rm.get("scopeMetrics", []):
            for m in sm.get("metrics", []):
                data = m.get("sum") or m.get("gauge") or {}
                delta = data.get("aggregationTemporality") == 1
                for dp in data.get("dataPoints", []):
                    v = float(dp.get("asDouble", dp.get("asInt", 0)))
                    a = attrs(dp.get("attributes"))
                    k = (m["name"], tuple(sorted((x, str(y)) for x, y in a.items()
                                                 if x in ("session.id", "type", "model"))))
                    series[k] = series.get(k, 0.0) + v if delta else v
    for rl in body.get("resourceLogs", []):
        for sl in rl.get("scopeLogs", []):
            for r in sl.get("logRecords", []):
                a = attrs(r.get("attributes"))
                name = a.get("event.name") or (r.get("body") or {}).get("stringValue", "")
                sid = str(a.get("session.id", "?"))
                if str(name).endswith("user_prompt"):
                    prompts[sid]["events"] += 1
                    if real_text(a.get("prompt")) or real_text(a.get("prompt_text")):
                        prompts[sid]["with_text"] += 1
                if str(name).endswith("assistant_response") and (
                        real_text(a.get("response")) or real_text(a.get("text"))):
                    prompts[sid]["assistant_text"] += 1

otel = defaultdict(lambda: defaultdict(float))
for (name, a), v in series.items():
    sid = dict(a).get("session.id", "?")
    if name.endswith("token.usage"):
        otel[sid]["tokens"] += v
        otel[sid]["t_" + dict(a).get("type", "?")] += v
    elif name.endswith("cost.usage"):
        otel[sid]["cost"] += v

trans = {}
for run in runs:
    best = {}
    for t in sorted((run / "transcripts").glob("*.jsonl")):
        for ln in t.read_text(errors="replace").splitlines():
            try:
                o = json.loads(ln)
            except ValueError:
                continue
            if o.get("type") == "result":
                sid = o.get("session_id")
                if sid not in best or (o.get("total_cost_usd") or 0) >= (best[sid].get("total_cost_usd") or 0):
                    best[sid] = o
    for sid, o in best.items():
        mu = o.get("modelUsage") or {}
        typ = {"input": sum(v["inputTokens"] for v in mu.values()),
               "output": sum(v["outputTokens"] for v in mu.values()),
               "cacheRead": sum(v["cacheReadInputTokens"] for v in mu.values()),
               "cacheCreation": sum(v["cacheCreationInputTokens"] for v in mu.values())}
        trans[sid] = {"run": run.name, "tokens": sum(typ.values()), "types": typ,
                      "cost": o.get("total_cost_usd") or 0.0}

print(f"{'session':<38} {'run':<34} {'tokens(transcript)':>18} {'tokens(otel)':>13} {'cost(tr)':>9} {'cost(otel)':>10}")
for sid, t in trans.items():
    o = otel.get(sid, {})
    print(f"{sid:<38} {t['run'][:34]:<34} {t['tokens']:>18,.0f} {o.get('tokens', 0):>13,.0f} "
          f"{t['cost']:>9.4f} {o.get('cost', 0):>10.4f}")
missing = [s for s in trans if s not in otel]
print(f"sessions in transcripts: {len(trans)}; with OTel token data: {len(trans) - len(missing)}")
print()
print("By token type (transcript / OTel):")
for sid, t in trans.items():
    o = otel.get(sid, {})
    cells = "  ".join(f"{k}={t['types'][k]:,}/{o.get('t_' + k, 0):,.0f}" for k in t["types"])
    print(f"  {t['run'][:34]:<34} {cells}")
print()
print("Prompt and response text in OTel events, per session (redacted values don't count):")
for sid, t in trans.items():
    p = prompts.get(sid, {"events": 0, "with_text": 0, "assistant_text": 0})
    print(f"  {t['run'][:34]:<34} user_prompt events={p['events']} with text={p['with_text']} "
          f"responses with text={p['assistant_text']}")
other = {k: v for k, v in prompts.items() if k not in trans}
if other:
    print(f"  events from sessions not in these runs: {sum(v['events'] for v in other.values())}")
