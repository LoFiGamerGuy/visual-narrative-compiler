#!/usr/bin/env python3
"""Deterministic, read-only measurements for the 2026-09-06 total review.

Does not modify source images. Writes JSON under the review evidence folder.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path

REVIEW_ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = REVIEW_ROOT / "docs" / "research" / "anime-pipeline-total-review" / "evidence"
PHONE_WIDTHS = (390, 430, 800)

TSPAN_RE = re.compile(r"<tspan\b([^>]*)>(.*?)</tspan>", re.I | re.S)
TEXT_RE = re.compile(r"<text\b([^>]*)>(.*?)</text>", re.I | re.S)
FONT_RE = re.compile(r'font-size="([0-9.]+)"', re.I)
VIEWBOX_RE = re.compile(r'viewBox="([^"]+)"', re.I)
PATH_RE = re.compile(r"<path\b", re.I)
IMAGE_HREF_RE = re.compile(r'(?:href|xlink:href)="([^"]+)"', re.I)
WORD_RE = re.compile(r"[A-Za-z0-9']+")


def png_size(path: Path) -> tuple[int, int] | None:
    try:
        with path.open("rb") as fh:
            sig = fh.read(24)
        if sig[:8] != b"\x89PNG\r\n\x1a\n":
            return None
        w, h = struct.unpack(">II", sig[16:24])
        return int(w), int(h)
    except OSError:
        return None


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_svg(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    vb = VIEWBOX_RE.search(text)
    viewbox = None
    if vb:
        parts = [float(x) for x in vb.group(1).replace(",", " ").split() if x]
        if len(parts) == 4:
            viewbox = {"x": parts[0], "y": parts[1], "w": parts[2], "h": parts[3]}
    font_sizes = [float(x) for x in FONT_RE.findall(text)]
    tspans = TSPAN_RE.findall(text)
    tspan_copy = []
    for attrs, body in tspans:
        clean = re.sub(r"<[^>]+>", " ", body)
        clean = re.sub(r"&amp;", "&", clean)
        clean = re.sub(r"&lt;", "<", clean)
        clean = re.sub(r"&#x27;", "'", clean)
        tspan_copy.append(re.sub(r"\s+", " ", clean).strip())
    words = []
    for chunk in tspan_copy:
        words.extend(WORD_RE.findall(chunk))
    hrefs = IMAGE_HREF_RE.findall(text)
    phone = {}
    if viewbox and viewbox["w"]:
        for w in PHONE_WIDTHS:
            scale = w / viewbox["w"]
            phone[str(w)] = {
                "min_font_px": round(min(font_sizes) * scale, 2) if font_sizes else None,
                "max_font_px": round(max(font_sizes) * scale, 2) if font_sizes else None,
                "median_font_px": round(sorted(font_sizes)[len(font_sizes) // 2] * scale, 2)
                if font_sizes
                else None,
            }
    return {
        "path": str(path.relative_to(REVIEW_ROOT)).replace("\\", "/"),
        "bytes": path.stat().st_size,
        "viewbox": viewbox,
        "font_sizes_svg": font_sizes,
        "path_count": len(PATH_RE.findall(text)),
        "tspan_count": len(tspans),
        "word_count": len(words),
        "words": words,
        "copy": tspan_copy,
        "image_hrefs": hrefs,
        "has_embedded_raster": any(h.startswith("data:image") for h in hrefs),
        "phone_font_px": phone,
    }


def walk_svgs(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(p for p in root.rglob("*.svg") if p.is_file())


def measure_png_dir(label: str, root: Path, limit: int | None = None) -> dict:
    if not root.exists():
        return {"label": label, "root": str(root), "exists": False, "count": 0}
    files = sorted(p for p in root.rglob("*.png") if p.is_file())
    if limit:
        files = files[:limit]
    hashes = []
    dims = Counter()
    missing_ihdr = 0
    sizes = []
    for p in files:
        digest = sha256_file(p)
        hashes.append(digest)
        dim = png_size(p)
        if dim is None:
            missing_ihdr += 1
        else:
            dims[f"{dim[0]}x{dim[1]}"] += 1
        sizes.append(p.stat().st_size)
    counts = Counter(hashes)
    exact_dup_groups = {h: n for h, n in counts.items() if n > 1}
    return {
        "label": label,
        "root": str(root),
        "exists": True,
        "count": len(files),
        "unique_sha256": len(counts),
        "exact_duplicate_files": sum(n - 1 for n in exact_dup_groups.values()),
        "exact_duplicate_groups": len(exact_dup_groups),
        "dimensions": dict(dims),
        "missing_ihdr": missing_ihdr,
        "bytes_total": int(sum(sizes)),
        "bytes_mean": int(sum(sizes) / len(sizes)) if sizes else 0,
    }


def summarize_svg_group(label: str, paths: list[Path]) -> dict:
    parsed = [parse_svg(p) for p in paths]
    words = [p["word_count"] for p in parsed]
    fonts_390 = []
    below_14 = 0
    below_12 = 0
    silent = 0
    for p in parsed:
        if p["word_count"] == 0 and p["tspan_count"] == 0:
            silent += 1
        px = (p.get("phone_font_px") or {}).get("390") or {}
        mn = px.get("min_font_px")
        if mn is not None:
            fonts_390.append(mn)
            if mn < 14:
                below_14 += 1
            if mn < 12:
                below_12 += 1
    return {
        "label": label,
        "svg_count": len(parsed),
        "word_count_sum": int(sum(words)),
        "word_count_mean": round(sum(words) / len(words), 2) if words else 0,
        "silent_or_no_tspan": silent,
        "min_phone_font_390_min": min(fonts_390) if fonts_390 else None,
        "min_phone_font_390_median": sorted(fonts_390)[len(fonts_390) // 2] if fonts_390 else None,
        "panels_min_font_390_below_14px": below_14,
        "panels_min_font_390_below_12px": below_12,
        "panels": parsed,
    }


def main() -> int:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    volume = REVIEW_ROOT / "docs" / "reimaginings" / "ember-lattice" / "volume" / "chapters"
    premium = REVIEW_ROOT / "docs" / "reimaginings" / "ember-lattice" / "premium-rd"
    groups = []
    if volume.exists():
        for ch in sorted(volume.iterdir()):
            panels = ch / "panels"
            if panels.is_dir():
                groups.append(summarize_svg_group(f"volume-{ch.name}", walk_svgs(panels)))
    for sub in ("hybrid", "original-lettering", "baseline", "raw"):
        p = premium / "panels" / sub
        if p.exists():
            groups.append(summarize_svg_group(f"premium-{sub}", walk_svgs(p)))

    png_reports = [
        measure_png_dir(
            "ember-pilot-source",
            Path(r"C:\AgentWorkspaces\anime-pipeline-litrpg-manhwa-20260904-001211\experiments\reimaginings\ember-lattice\pilot\source"),
        ),
        measure_png_dir(
            "ember-volume-sources",
            Path(r"C:\AgentWorkspaces\anime-pipeline-litrpg-manhwa-20260904-001211\experiments\reimaginings\ember-lattice\volume"),
        ),
        measure_png_dir(
            "ember-premium-editorial",
            Path(r"C:\AgentWorkspaces\anime-pipeline-ember-lattice-editorial-gear-20260904\experiments\reimaginings\ember-lattice\premium-rd"),
        ),
        measure_png_dir(
            "ember-premium-rd",
            Path(r"C:\AgentWorkspaces\anime-pipeline-ember-lattice-premium-rd-20260904-150943\experiments\reimaginings\ember-lattice"),
        ),
        measure_png_dir(
            "borrowed-down",
            Path(r"C:\AgentWorkspaces\anime-pipeline-reimagining-20260903\experiments\reimaginings\borrowed-down"),
        ),
        measure_png_dir(
            "city-keeps-oaths",
            Path(r"C:\AgentWorkspaces\anime-pipeline-reimagining-clean-webtoon-20260903-213010\experiments\reimaginings\the-city-keeps-oaths"),
        ),
    ]

    html_readers = []
    docs = REVIEW_ROOT / "docs" / "reimaginings"
    if docs.exists():
        for p in sorted(docs.rglob("*.html")):
            html_readers.append(str(p.relative_to(REVIEW_ROOT)).replace("\\", "/"))

    out = {
        "tool": "src/research/anime_pipeline_total_review/measure.py",
        "access_date": "2026-09-06",
        "notes": [
            "Phone font sizes are geometric conversions from SVG user units using viewBox width.",
            "Volume CSS uses width:min(100%,430px) for the phone column, so 390px is a stricter test than the shipped reader.",
            "PNG hashes are of gitignored sibling-worktree files; files were not copied into this worktree.",
            "Edge density / beauty proxies are intentionally not computed.",
        ],
        "svg_groups_summary": [
            {k: v for k, v in g.items() if k != "panels"} for g in groups
        ],
        "svg_groups": groups,
        "png_inventories": png_reports,
        "tracked_html_readers": html_readers,
    }
    dest = EVIDENCE / "measurements.json"
    dest.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    summary = EVIDENCE / "measurements-summary.json"
    slim = {
        "svg_groups_summary": out["svg_groups_summary"],
        "png_inventories": png_reports,
        "tracked_html_reader_count": len(html_readers),
        "notes": out["notes"],
    }
    summary.write_text(json.dumps(slim, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(slim, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
