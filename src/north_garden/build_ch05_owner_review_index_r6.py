"""Build append-only local CH05 owner review hub r6 over r5."""
from __future__ import annotations

import hashlib
import html
import json
import os
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[2]
R5 = ROOT / "experiments/review-packets/ch05-owner-review-index-r5/owner-review-index-r5-packet.json"
CONTRACT = ROOT / "production/comic/review/ch05-owner-decision-contract-r1.json"
OUT = ROOT / "experiments/review-packets/ch05-owner-review-index-r6"
INDEX = OUT / "index.html"
PACKET = OUT / "owner-review-index-r6-packet.json"
LINKS = [
    ("index_r5", "Complete owner hub r5", "HTML", "experiments/review-packets/ch05-owner-review-index-r5/index.html", "All prior art, continuity, lettering, pilot, and lifecycle review links."),
    ("duration_capacity", "Chapter generation-duration capacity", "IMAGE", "experiments/review-packets/ch05-chapter-production-duration-capacity-r1/ch05-chapter-duration-capacity-map-r1.png", "Measured p10/median/p90 generation-only ranges for 12 batches and four production waves."),
    ("operating_playbook", "Chapter production operating playbook", "TEXT", "docs/research/ch05-chapter-production-operating-playbook-r1.md", "Twelve ordered steps separating local validation, owner action, agent-only rendering, review, repair, and release."),
    ("delivery_summary", "Current overnight delivery summary r2", "TEXT", "docs/research/ch05-overnight-delivery-summary-r2.md", "Measured art, ranked engineering route, direct links, exact owner frontier, spend, and limitations."),
    ("delivery_bundle", "Exact overnight delivery bundle r2", "TEXT", "production/comic/handoff/ch05-overnight-delivery-bundle-r2.json", "Hash-bound current handoff across art, review, lifecycle, capacity, cost, source, and frozen integrity."),
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return Path(os.path.relpath(path, OUT)).as_posix()


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    thumbs = OUT / "thumbnails"
    thumbs.mkdir(exist_ok=True)
    items = []
    for item_id, title, kind, path_text, summary in LINKS:
        source = ROOT / path_text
        if not source.is_file():
            raise SystemExit(f"missing review link {source}")
        row = {
            "id": item_id, "title": title, "kind": kind, "path": path_text, "sha256": sha(source),
            "href": rel(source), "summary": summary, "thumbnail_path": None, "thumbnail_sha256": None,
        }
        if kind == "IMAGE":
            with Image.open(source) as opened:
                thumb = ImageOps.contain(opened.convert("RGB"), (900, 520), Image.Resampling.LANCZOS)
            canvas = Image.new("RGB", (920, 540), (26, 32, 40))
            canvas.paste(thumb, ((920 - thumb.width) // 2, (540 - thumb.height) // 2))
            target = thumbs / f"{item_id}.png"
            canvas.save(target, optimize=False, compress_level=9)
            row.update(thumbnail_path=target.relative_to(ROOT).as_posix(), thumbnail_sha256=sha(target), thumbnail_href=rel(target))
        items.append(row)
    cards = []
    for row in items:
        visual = (f'<img src="{html.escape(row.get("thumbnail_href", ""))}" alt="{html.escape(row["title"])}">'
                  if row["kind"] == "IMAGE" else f'<div class="type">LOCAL {row["kind"]}</div>')
        cards.append(f'<article><a href="{html.escape(row["href"])}">{visual}<h2>{html.escape(row["title"])}</h2></a><p>{html.escape(row["summary"])}</p><code>{row["sha256"]}</code></article>')
    page = '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>CH05 owner review index r6</title><style>body{margin:0;background:#10151c;color:#edf1f5;font:15px/1.45 system-ui,sans-serif}header,main,footer{max-width:1480px;margin:auto;padding:26px}header{background:#18202a;border-bottom:1px solid #33404f}h1{margin:0 0 10px}.boundary{color:#ffd18a}.stats{display:flex;gap:12px;flex-wrap:wrap}.stats span{background:#253140;border-radius:8px;padding:8px 12px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(360px,1fr));gap:18px}article{background:#19222d;border:1px solid #33404f;border-radius:12px;padding:14px;overflow:hidden}article img,.type{width:100%;height:230px;object-fit:contain;background:#0e1319;border-radius:8px}.type{display:grid;place-items:center;color:#8ecbff;font-size:26px;font-weight:800}a{color:#91ceff;text-decoration:none}code{display:block;color:#8794a3;font-size:10px;overflow-wrap:anywhere}footer{color:#97a2af}</style></head><body><header><h1>North Garden CH05 · owner review index r6</h1><p class="boundary">Local-only engineering evidence. Art remains unaccepted and commercially uncleared; production prompts and executable panels remain zero.</p><div class="stats"><span>29 candidates</span><span>50 plans</span><span>12 batches</span><span>112 prior links</span><span>58 release checks</span><span>0 executable</span></div></header><main><div class="grid">''' + "".join(cards) + '''</div></main><footer>R6 extends immutable r5 · no remote assets · no network code · no upload · no recorded owner decision</footer></body></html>'''
    INDEX.write_text(page, encoding="utf-8", newline="\n")
    r5 = json.loads(R5.read_text(encoding="utf-8"))
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    artifacts = [{"path": INDEX.relative_to(ROOT).as_posix(), "sha256": sha(INDEX), "bytes": INDEX.stat().st_size}]
    artifacts += [{"path": x["thumbnail_path"], "sha256": x["thumbnail_sha256"], "bytes": (ROOT / x["thumbnail_path"]).stat().st_size} for x in items if x["thumbnail_path"]]
    packet = {
        "record_type": "CH05OwnerReviewIndexPacket", "schema_version": "6.0", "record_id": "ng-ch05-owner-review-index-r6",
        "state": "LOCAL_CURRENT_DELIVERY_REVIEW_HUB_EXTENDS_R5_OWNER_PENDING",
        "extends": {"path": R5.relative_to(ROOT).as_posix(), "sha256": sha(R5), "link_count": r5["link_count"]},
        "contract": {"path": CONTRACT.relative_to(ROOT).as_posix(), "sha256": sha(CONTRACT), "completed_decisions": contract["summary"]["completed_decisions"], "events": contract["summary"]["events"], "human_review_minutes": contract["summary"]["human_review_minutes"]},
        "link_count": len(items), "image_link_count": sum(x["kind"] == "IMAGE" for x in items),
        "html_link_count": sum(x["kind"] == "HTML" for x in items), "text_link_count": sum(x["kind"] == "TEXT" for x in items),
        "links": items, "artifact_count": len(artifacts), "artifacts": artifacts,
        "index": {"path": INDEX.relative_to(ROOT).as_posix(), "sha256": sha(INDEX), "bytes": INDEX.stat().st_size},
        "owner_decisions": 0, "accepted_candidates": 0, "executable_panels": 0, "provider_calls": 0, "uploads": 0, "cost_usd": 0,
        "boundary": "Append-only local hub; r5, empty decision contract, generated pixels, and production state remain unchanged.",
    }
    PACKET.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"CH05 owner review index r6: 5 links / {len(artifacts)} artifacts; index {sha(INDEX)} packet {sha(PACKET)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
