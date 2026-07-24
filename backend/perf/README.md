# Stabilization tools

Scripts and EXPLAIN outputs for the post-Goals stabilization milestone.

## Quick start

```bash
cd backend
make migrate
uv run python scripts/perf/seed_load.py --reset --transactions 50000
uv run python scripts/perf/explain_analyze.py
uv run python scripts/perf/benchmark_http.py --iterations 10
```

Load-test credentials (created by seed):

- email: `loadtest@wealthos.local`
- password: `WealthOS-Load-2026`

Plans land in `perf/explain/latest/`.
