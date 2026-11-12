"""Unit and CLI tests for the offline Moodle function lookup tool."""
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import ws_lookup  # noqa: E402

EXPECTED = 492


class TestSearch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = ws_lookup.load_data()

    def test_load_data(self):
        self.assertEqual(len(self.data["functions"]), EXPECTED)

    def test_quiz_search_returns_quiz_functions(self):
        rows = ws_lookup.search(self.data, term="quiz")
        self.assertGreaterEqual(len(rows), 10)
        for name, fn in rows:
            blob = f"{name} {fn.get('description', '')}".lower()
            self.assertIn("quiz", blob)
        names = [n for n, _ in rows]
        self.assertTrue(any(n.startswith("mod_quiz_") for n in names))

    def test_type_filter(self):
        reads = ws_lookup.search(self.data, typ="read")
        writes = ws_lookup.search(self.data, typ="write")
        self.assertTrue(reads and writes)
        self.assertTrue(all(fn["type"] == "read" for _, fn in reads))
        self.assertTrue(all(fn["type"] == "write" for _, fn in writes))
        self.assertEqual(len(reads) + len(writes), EXPECTED)

    def test_capability_filter(self):
        rows = ws_lookup.search(self.data, cap="mod/quiz")
        self.assertTrue(rows)
        for _, fn in rows:
            self.assertIn("mod/quiz", fn.get("capabilities") or "")

    def test_combined_filters(self):
        rows = ws_lookup.search(self.data, term="attempt", typ="read", cap="mod/quiz")
        self.assertTrue(rows)
        for name, fn in rows:
            self.assertEqual(fn["type"], "read")
            self.assertIn("mod/quiz", fn.get("capabilities") or "")
            self.assertIn("attempt", f"{name} {fn.get('description', '')}".lower())

    def test_unknown_term_is_empty(self):
        rows = ws_lookup.search(self.data, term="zzzxnotafunctionqxyz")
        self.assertEqual(rows, [])

    def test_format_results_includes_totals(self):
        rows = ws_lookup.search(self.data, term="quiz")
        out = ws_lookup.format_results(self.data, rows)
        self.assertIn(f"of {EXPECTED} functions", out)
        self.assertIn(rows[0][0], out)

    def test_cli_quiz_search(self):
        out = subprocess.check_output(
            [sys.executable, str(ROOT / "tools" / "ws_lookup.py"), "quiz"],
            text=True,
        )
        self.assertIn(f"of {EXPECTED} functions", out)
        self.assertIn("mod_quiz_", out)


class TestWsCallHasNoHardcodedSecrets(unittest.TestCase):
    def test_ws_call_reads_env_only(self):
        src = (ROOT / "tools" / "ws_call.py").read_text(encoding="utf-8")
        self.assertIn("MOODLE_TOKEN", src)
        self.assertIn("MOODLE_URL", src)
        self.assertNotRegex(src, r"wstoken['\"]?\s*[:=]\s*['\"][A-Za-z0-9]{8,}")
        example = (ROOT / ".env.example").read_text(encoding="utf-8")
        self.assertIn("MOODLE_URL", example)
        self.assertIn("MOODLE_TOKEN", example)
        # Example file must not contain a real URL with a token.
        self.assertNotRegex(example, r"wstoken=")


if __name__ == "__main__":
    unittest.main()
