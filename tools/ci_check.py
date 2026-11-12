#!/usr/bin/env python3
"""Validate the checked-in function map and that offline search still runs."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXPECTED = 492


def main() -> int:
    fv = json.loads((ROOT / "functions_verified.json").read_text(encoding="utf-8"))
    catalog = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
    n = len(fv["functions"])
    if n != EXPECTED:
        print(f"expected {EXPECTED} functions, got {n}")
        return 1
    if not catalog:
        print("empty catalog.json")
        return 1
    out = subprocess.check_output(
        [sys.executable, str(ROOT / "tools" / "ws_lookup.py"), "quiz"],
        text=True,
    )
    if f"of {EXPECTED} functions" not in out:
        print("ws_lookup unexpected output:\n", out[-500:])
        return 1
    print(f"OK {n} functions; catalog keys={list(catalog)[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
