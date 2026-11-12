#!/usr/bin/env python3
"""Call one Moodle REST web-service function with a token from .env / environment.

  export MOODLE_URL=https://moodle.example.edu MOODLE_TOKEN=...   (or put them in .env)
  python tools/ws_call.py core_webservice_get_site_info
  python tools/ws_call.py mod_quiz_get_quizzes_by_courses courseids[0]=2
"""
import json, os, pathlib, sys, urllib.parse, urllib.request

def load_env() -> None:
    env = pathlib.Path(__file__).resolve().parent.parent / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

def main() -> None:
    load_env()
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    url, token = os.environ.get("MOODLE_URL", "").rstrip("/"), os.environ.get("MOODLE_TOKEN", "")
    if not url or not token:
        sys.exit("Set MOODLE_URL and MOODLE_TOKEN (see .env.example)")
    params = {"wstoken": token, "wsfunction": sys.argv[1], "moodlewsrestformat": "json"}
    for arg in sys.argv[2:]:
        k, _, v = arg.partition("=")
        params[k] = v
    req = urllib.request.Request(f"{url}/webservice/rest/server.php", data=urllib.parse.urlencode(params).encode())
    with urllib.request.urlopen(req, timeout=30) as r:
        print(json.dumps(json.loads(r.read().decode()), indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
