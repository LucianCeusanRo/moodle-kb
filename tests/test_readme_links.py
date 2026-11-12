"""Relative links in Moodle KB docs must point at files that exist."""
from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MD_LINK = re.compile(r"!\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)|\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
HTML_ATTR = re.compile(r"""(?:src|href)\s*=\s*["']([^"']+)["']""", re.I)


def markdown_files() -> list[Path]:
    return [ROOT / "README.md", *sorted((ROOT / "docs").glob("*.md"))]


def extract(path: Path) -> list[tuple[str, Path]]:
    text = path.read_text(encoding="utf-8")
    visible, fencing = [], False
    for line in text.splitlines():
        if line.startswith("```"):
            fencing = not fencing
            continue
        if not fencing:
            visible.append(line)
    body = "\n".join(visible)
    urls = [m.group(1) or m.group(2) for m in MD_LINK.finditer(body)]
    urls += [m.group(1) for m in HTML_ATTR.finditer(body)]
    out = []
    for url in urls:
        if not url or url.startswith(("#", "mailto:", "http://", "https://", "data:", "//")):
            continue
        target = (path.parent / url.split("#", 1)[0].split("?", 1)[0]).resolve()
        out.append((url, target))
    return out


class TestDocsLinks(unittest.TestCase):
    def test_relative_links_resolve(self):
        checked = 0
        for md in markdown_files():
            self.assertTrue(md.is_file(), md)
            for url, target in extract(md):
                checked += 1
                with self.subTest(file=str(md.relative_to(ROOT)), url=url):
                    self.assertTrue(target.exists(), f"{md.name} -> {url} missing")
        self.assertGreaterEqual(checked, 5)

    def test_fences_balanced(self):
        for md in markdown_files():
            fences = sum(1 for line in md.read_text(encoding="utf-8").splitlines() if line.startswith("```"))
            with self.subTest(file=md.name):
                self.assertEqual(fences % 2, 0, f"{md.name} has an unclosed fence")


if __name__ == "__main__":
    unittest.main()
