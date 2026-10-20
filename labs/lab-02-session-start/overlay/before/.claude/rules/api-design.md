# API design rules

- Handlers return Response(status, body).
- 404 for missing resources, 400 for bad input.
- Never leak stack traces in bodies.
- New handlers need a test in packages/web/tests/.
