# LAB-13 — Telemetry you can trust, and a team eval suite (Chapters 15–16)

## Part A — OpenTelemetry against the transcripts (Chapter 15)

**Measures:**
- Whether Claude Code's OpenTelemetry token and cost metrics agree with the totals counted from the stream-json transcripts of the same sessions.
- Whether the user-prompt events carry prompt text, with default redaction and with `OTEL_LOG_USER_PROMPTS=1`.

**How:** the runner starts `tools/otlp_sink.py`, a local OTLP/HTTP-JSON receiver on 127.0.0.1:4318. Nothing leaves the machine. With telemetry pointed at the receiver, it runs:
- three LAB-07 tasks (T01–T03, prompt variant) with default settings;
- one more task with `OTEL_LOG_USER_PROMPTS=1`.

Then it runs:

```bash
python3 labs/lab-13-governance/compare_otel.py $CCFM_RUNS/_results/otel-lab13.jsonl $CCFM_RUNS/lab-13-*
```

**Time:** about 10 minutes, 4 sessions.

## Part B — a team eval suite from runs you already have (Chapter 16)

No tokens are used. The script re-grades every finished LAB-07 and LAB-10 run with the current graders and recounts tokens from the transcripts. It reports, per task:
- pass rate,
- pass^k,
- median tokens,
- cost per passing run.

It also prints a go/no-go line for each variant.

```bash
python3 labs/lab-13-governance/evalsuite.py --labs lab-07,lab-10 --gate "pass_rate>=0.9,flaky<=1"
```

Chapter 16 shows how to grow this into your own suite of 20–50 tasks, drawn from real failures.
