#!/usr/bin/env python3
"""Benchmark critical Dashboard/Goals endpoints against the load-test org.

Usage (from backend/):
  uv run python scripts/perf/benchmark_http.py
  uv run python scripts/perf/benchmark_http.py --iterations 20 --base-url http://127.0.0.1:8000
"""

from __future__ import annotations

import argparse
import os
import statistics
import sys
import time
from pathlib import Path

import httpx
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

os.environ.setdefault("DB_ECHO", "false")
os.environ.setdefault("DEBUG", "false")
os.environ.setdefault("REQUEST_TIMING_ENABLED", "false")

from wealthos.main import app  # noqa: E402

LOAD_EMAIL = "loadtest@wealthos.local"
LOAD_PASSWORD = "WealthOS-Load-2026"


def _percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(int(round((pct / 100) * (len(ordered) - 1))), len(ordered) - 1)
    return ordered[index]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--iterations", type=int, default=10)
    parser.add_argument(
        "--base-url",
        default="",
        help="If set, hit a live server; otherwise use in-process TestClient.",
    )
    parser.add_argument("--email", default=LOAD_EMAIL)
    parser.add_argument("--password", default=LOAD_PASSWORD)
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    if args.base_url:
        client: httpx.Client | TestClient = httpx.Client(
            base_url=args.base_url,
            timeout=60.0,
        )
    else:
        client = TestClient(app)

    login = client.post(
        "/api/v1/auth/login",
        data={"username": args.email, "password": args.password},
    )
    if login.status_code != 200:
        raise SystemExit(
            f"Login failed ({login.status_code}). Run seed_load.py first.\n{login.text}"
        )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    org_id = client.get("/api/v1/me/organizations", headers=headers).json()["items"][0]["id"]

    endpoints = [
        ("GET", f"/api/v1/organizations/{org_id}/dashboard/summary", {"period": "this_year"}),
        (
            "GET",
            f"/api/v1/organizations/{org_id}/dashboard/cash-flow",
            {"period": "this_year", "granularity": "month"},
        ),
        (
            "GET",
            f"/api/v1/organizations/{org_id}/dashboard/spending-by-category",
            {"period": "this_year", "limit": "10"},
        ),
        ("GET", f"/api/v1/organizations/{org_id}/dashboard/accounts", None),
        (
            "GET",
            f"/api/v1/organizations/{org_id}/dashboard/recent-transactions",
            {"limit": "20"},
        ),
        ("GET", f"/api/v1/organizations/{org_id}/dashboard/goals", None),
        ("GET", f"/api/v1/organizations/{org_id}/goals", None),
    ]

    print(f"organization_id={org_id}")
    print(f"iterations={args.iterations}")
    print()
    print(f"{'endpoint':<55} {'p50_ms':>8} {'p95_ms':>8} {'max_ms':>8}")
    print("-" * 85)

    for method, path, params in endpoints:
        samples: list[float] = []
        for _ in range(args.iterations):
            started = time.perf_counter()
            response = client.request(method, path, headers=headers, params=params)
            elapsed_ms = (time.perf_counter() - started) * 1000
            if response.status_code >= 400:
                raise SystemExit(f"{method} {path} -> {response.status_code}: {response.text}")
            samples.append(elapsed_ms)
        label = path.split("/organizations/")[-1]
        print(
            f"{label:<55} "
            f"{_percentile(samples, 50):8.1f} "
            f"{_percentile(samples, 95):8.1f} "
            f"{max(samples):8.1f}"
        )
        _ = statistics.mean(samples)

    if isinstance(client, httpx.Client):
        client.close()


if __name__ == "__main__":
    main()
