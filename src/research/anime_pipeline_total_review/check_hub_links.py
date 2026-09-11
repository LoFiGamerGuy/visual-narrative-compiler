#!/usr/bin/env python3
"""Resolve local hrefs in the review hub and proof page."""
from __future__ import annotations

import re
from pathlib import Path

REVIEW = Path(__file__).resolve().parents[3] / "docs" / "research" / "anime-pipeline-total-review"
HREF = re.compile(r'href="([^"]+)"', re.I)


def check(page: Path) -> list[str]:
    html = page.read_text(encoding="utf-8")
    missing = []
    for href in HREF.findall(html):
        if href.startswith("#") or href.startswith("http://") or href.startswith("https://") or href.startswith("mailto:"):
            continue
        target = (page.parent / href).resolve()
        if not target.exists():
            missing.append(f"{page.name} -> {href}")
    return missing


def main() -> int:
    missing = check(REVIEW / "index.html") + check(REVIEW / "proof" / "index.html")
    if missing:
        print("FAIL")
        for item in missing:
            print(" -", item)
        return 1
    print("PASS local hub links")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
