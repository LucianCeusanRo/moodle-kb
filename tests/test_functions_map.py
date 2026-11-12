"""Validate the checked-in Moodle web-service function map and catalog."""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXPECTED = 492
NAME_RE = re.compile(r"^[a-z][a-z0-9]+(_[a-z0-9]+)+$")
SOURCE_PREFIX = "https://github.com/moodle/moodle/blob/"
REQUIRED_FIELDS = ("description", "type", "capabilities", "source")


def load() -> tuple[dict, dict]:
    fv = json.loads((ROOT / "functions_verified.json").read_text(encoding="utf-8"))
    catalog = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
    return fv, catalog


class TestFunctionsMap(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fv, cls.catalog = load()
        cls.fns: dict = cls.fv["functions"]

    def test_expected_count_and_metadata(self):
        self.assertEqual(len(self.fns), EXPECTED)
        self.assertTrue(self.fv.get("moodle_branch"))
        self.assertTrue(self.fv.get("generated"))
        self.assertEqual(self.fv["moodle_branch"], self.catalog.get("moodle_branch_verified"))
        self.assertEqual(self.fv["generated"], self.catalog.get("generated"))

    def test_every_function_has_required_fields(self):
        types = set()
        missing_desc = 0
        for name, fn in self.fns.items():
            with self.subTest(name=name):
                for field in REQUIRED_FIELDS:
                    self.assertIn(field, fn, f"{name} missing {field}")
                self.assertTrue((fn.get("description") or "").strip(), f"{name} empty description")
                self.assertIn(fn.get("type"), {"read", "write"})
                types.add(fn["type"])
                self.assertTrue(str(fn.get("source") or "").startswith(SOURCE_PREFIX), fn.get("source"))
                self.assertTrue(NAME_RE.match(name), name)
                # capabilities may be empty (core functions without a cap) but the key must exist
                self.assertIsInstance(fn.get("capabilities"), (str, type(None)))
        self.assertEqual(types, {"read", "write"})

    def test_catalog_docs_exist(self):
        docs = self.catalog.get("docs") or []
        self.assertGreaterEqual(len(docs), 7)
        for rel in docs:
            path = ROOT / rel
            with self.subTest(doc=rel):
                self.assertTrue(path.is_file(), rel)
                self.assertGreater(path.stat().st_size, 50)

    def test_relevant_functions_match_the_verified_map(self):
        relevant = self.catalog.get("relevant_functions") or {}
        self.assertGreaterEqual(len(relevant), 20)
        for name, meta in relevant.items():
            with self.subTest(name=name):
                self.assertIn(name, self.fns)
                verified = self.fns[name]
                self.assertEqual(meta.get("type"), verified.get("type"))
                self.assertEqual(meta.get("description"), verified.get("description"))

    def test_exam_mode_urls_are_paths(self):
        off = self.catalog.get("exam_mode_urls_off") or []
        learn = self.catalog.get("exam_mode_urls_learn") or []
        self.assertTrue(off and learn)
        for url in list(off) + list(learn):
            self.assertTrue(url.startswith("/"), url)
        self.assertIn("/mod/quiz/attempt.php", off)
        self.assertIn("/mod/quiz/review.php", learn)
        self.assertNotIn("/mod/quiz/review.php", off)

    def test_catalog_lists_limitations_and_sources(self):
        cannot = self.catalog.get("stock_ws_cannot") or []
        self.assertGreaterEqual(len(cannot), 3)
        sources = self.catalog.get("sources") or {}
        self.assertIn("web_services", sources)
        for key, url in sources.items():
            with self.subTest(source=key):
                self.assertTrue(str(url).startswith("https://"), url)

    def test_json_is_stable_utf8(self):
        # Reloading must not invent or drop functions.
        raw = json.loads((ROOT / "functions_verified.json").read_text(encoding="utf-8"))
        self.assertEqual(set(raw["functions"]), set(self.fns))


if __name__ == "__main__":
    unittest.main()
