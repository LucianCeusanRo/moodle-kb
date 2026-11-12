#!/usr/bin/env python3
"""Search the verified Moodle web-service function map (functions_verified.json).

Examples:
  python tools/ws_lookup.py quiz              # every function whose name/description contains "quiz"
  python tools/ws_lookup.py attempt --type read
  python tools/ws_lookup.py --cap mod/quiz:view
"""
from __future__ import annotations

import argparse
import json
import pathlib
from typing import Any

DATA = pathlib.Path(__file__).resolve().parent.parent / "functions_verified.json"


def load_data(path: pathlib.Path = DATA) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def search(
    data: dict[str, Any],
    term: str = "",
    typ: str | None = None,
    cap: str = "",
) -> list[tuple[str, dict[str, Any]]]:
    """Return (name, function) pairs that match the text / type / capability filters."""
    needle = (term or "").lower()
    rows: list[tuple[str, dict[str, Any]]] = []
    for name, fn in sorted(data["functions"].items()):
        text = f"{name} {fn.get('description', '')}".lower()
        if needle not in text:
            continue
        if typ and fn.get("type") != typ:
            continue
        if cap and cap not in (fn.get("capabilities") or ""):
            continue
        rows.append((name, fn))
    return rows


def format_results(data: dict[str, Any], rows: list[tuple[str, dict[str, Any]]]) -> str:
    lines: list[str] = []
    for name, fn in rows:
        lines.append(f"{name}  [{fn.get('type')}]")
        lines.append(f"    {fn.get('description', '')}")
        if fn.get("capabilities"):
            lines.append(f"    caps: {fn['capabilities']}")
    total = len(data["functions"])
    lines.append("")
    lines.append(
        f"{len(rows)} of {total} functions (Moodle {data.get('moodle_branch')}, verified {data.get('generated')})"
    )
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("term", nargs="?", default="", help="text to search in name or description")
    ap.add_argument("--type", dest="typ", choices=["read", "write"], help="only read or write functions")
    ap.add_argument("--cap", default="", help="only functions requiring this capability (substring)")
    a = ap.parse_args()
    data = load_data()
    rows = search(data, term=a.term, typ=a.typ, cap=a.cap)
    print(format_results(data, rows))


if __name__ == "__main__":
    main()
