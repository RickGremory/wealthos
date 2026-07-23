#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
uv run uvicorn wealthos.main:app --reload --app-dir src --host 0.0.0.0 --port 8000
