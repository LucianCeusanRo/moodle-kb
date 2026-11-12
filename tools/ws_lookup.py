#!/usr/bin/env python3
"""Search the verified Moodle web-service function map (functions_verified.json).

Examples:
  python tools/ws_lookup.py quiz              # every function whose name/description contains "quiz"
  python tools/ws_lookup.py attempt --type read
  python tools/ws_lookup.py --cap mod/quiz:view
"""
import argparse, json, pathlib

DATA = pathlib.Path(__file__).resolve().parent.parent / "functions_verified.json"

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("term", nargs="?", default="", help="text to search in name or description")
    ap.add_argument("--type", choices=["read", "write"], help="only read or write functions")
    ap.add_argument("--cap", default="", help="only functions requiring this capability (substring)")
    a = ap.parse_args()
    d = json.loads(DATA.read_text(encoding="utf-8"))
    rows = []
    for name, f in sorted(d["functions"].items()):
        text = f"{name} {f.get('description', '')}".lower()
        if a.term.lower() not in text: continue
        if a.type and f.get("type") != a.type: continue
        if a.cap and a.cap not in (f.get("capabilities") or ""): continue
        rows.append((name, f))
    for name, f in rows:
        print(f"{name}  [{f.get('type')}]")
        print(f"    {f.get('description', '')}")
        if f.get("capabilities"): print(f"    caps: {f['capabilities']}")
    print(f"\n{len(rows)} of {len(d['functions'])} functions (Moodle {d.get('moodle_branch')}, verified {d.get('generated')})")

if __name__ == "__main__":
    main()
