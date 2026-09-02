"""Build append-only local CH05 owner review hub r3."""
from __future__ import annotations

import hashlib
import html
import json
import os
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[2]
R2_PACKET = ROOT / "experiments/review-packets/ch05-owner-review-index-r2/owner-review-index-r2-packet.json"
CONTRACT = ROOT / "production/comic/review/ch05-owner-decision-contract-r1.json"
OUT = ROOT / "experiments/review-packets/ch05-owner-review-index-r3"
INDEX = OUT / "index.html"
PACKET = OUT / "owner-review-index-r3-packet.json"
LINKS = [
    ("index_r2", "Prior owner hub r2", "HTML", "experiments/review-packets/ch05-owner-review-index-r2/index.html", "All earlier candidate, continuity, scale, repair, and preflight review links."),
    ("worksheet", "39-subject decision worksheet", "HTML", "experiments/review-packets/ch05-owner-decision-worksheet-r1/index.html", "Offline draft export only; no decision is recorded or accepted."),
    ("cadence_clean", "Selected 14 · clean vertical cadence", "IMAGE", "experiments/review-packets/ch05-variable-cadence-assembly-r1/ch05-variable-cadence-scroll-clean-r1.png", "Three connected sequences across eight widths; no lettering treatment."),
    ("cadence_phone", "Selected 14 · 390px phone cadence", "IMAGE", "experiments/review-packets/ch05-variable-cadence-assembly-r1/ch05-variable-cadence-phone-scroll-390px-r1.png", "Actual 390px review footprint for rhythm and readability."),
    ("continuity_all", "Continuity atlas · all 26 CH05 candidates", "IMAGE", "experiments/review-packets/ch05-manual-continuity-atlas-r1/ch05-continuity-atlas-all-26-r1.png", "Alternates grouped by plan for hair, wardrobe, roles, hands, causality, and lettering."),
    ("continuity_selected", "Continuity atlas · selected 14", "IMAGE", "experiments/review-packets/ch05-manual-continuity-atlas-r1/ch05-continuity-atlas-selected-14-r1.png", "Full-panel selected sequence in narrative order."),
    ("lettering", "Transparent lettering · phone comparison", "IMAGE", "experiments/review-packets/ch05-transparent-lettering-rehearsal-r1/ch05-transparent-lettering-phone-comparison-r1.png", "Opacity arms; c014 semantic collision and 13px limitations remain explicit."),
    ("scale", "50-plan scale/cadence map", "IMAGE", "experiments/review-packets/ch05-panel-scale-cadence-policy-r1/ch05-panel-scale-cadence-map-r1.png", "Conditional 520–1200px roles, not accepted layouts."),
    ("repair", "Targeted repair paths", "IMAGE", "experiments/review-packets/ch05-failure-class-repair-matrix-r1/ch05-targeted-repair-paths-r1.png", "Six exact intervention links; broad rerolls remain disallowed."),
    ("preflight", "P010–P013 zero-prompt storyboard", "IMAGE", "experiments/review-packets/ch05-p010-p013-preflight-contract-r1/ch05-p010-p013-preflight-storyboard-r1.png", "Recommended next microsequence remains prompt-null and nonexecutable."),
    ("envelope", "Chapter-scale production envelope", "IMAGE", "experiments/review-packets/ch05-chapter-scale-production-envelope-r1/ch05-chapter-scale-production-envelope-r1.png", "36/49/72 candidate planning scenarios from measured timing."),
    ("renderrecords", "All-29 RenderRecord field matrix", "IMAGE", "experiments/review-packets/ch05-renderrecord-completeness-audit-r1/ch05-renderrecord-field-matrix-r1.png", "Exact fields and explicit null service metadata across all candidates."),
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path: Path) -> str:
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
            "id": item_id,
            "title": title,
            "kind": kind,
            "path": path_text,
            "sha256": sha(source),
            "href": relative(source),
            "summary": summary,
            "thumbnail_path": None,
            "thumbnail_sha256": None,
        }
        if kind == "IMAGE":
            with Image.open(source) as opened:
                thumb = ImageOps.contain(opened.convert("RGB"), (600, 350), Image.Resampling.LANCZOS)
            canvas = Image.new("RGB", (620, 370), (26, 32, 40))
            canvas.paste(thumb, ((620 - thumb.width) // 2, (370 - thumb.height) // 2))
            target = thumbs / f"{item_id}.png"
            canvas.save(target, optimize=False)
            row["thumbnail_path"] = target.relative_to(ROOT).as_posix()
            row["thumbnail_sha256"] = sha(target)
            row["thumbnail_href"] = relative(target)
        items.append(row)
    cards = []
    for row in items:
        visual = (
            f'<img src="{html.escape(row.get("thumbnail_href", ""))}" alt="{html.escape(row["title"])}">'
            if row["kind"] == "IMAGE"
            else '<div class="html-card">LOCAL HTML</div>'
        )
        cards.append(
            f'<article><a href="{html.escape(row["href"])}">{visual}<h2>{html.escape(row["title"])}</h2></a>'
            f'<p>{html.escape(row["summary"])}</p><code>{row["sha256"]}</code></article>'
        )
    page = '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>CH05 owner review index r3</title><style>body{margin:0;background:#10151c;color:#edf1f5;font:15px/1.45 system-ui,sans-serif}header,main,footer{max-width:1440px;margin:auto;padding:26px}header{background:#18202a;border-bottom:1px solid #33404f}h1{margin:0 0 10px}.boundary{color:#ffd18a}.stats{display:flex;gap:12px;flex-wrap:wrap}.stats span{background:#253140;border-radius:8px;padding:8px 12px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(360px,1fr));gap:18px}article{background:#19222d;border:1px solid #33404f;border-radius:12px;padding:14px;overflow:hidden}article img,.html-card{width:100%;height:220px;object-fit:contain;background:#0e1319;border-radius:8px}.html-card{display:grid;place-items:center;color:#8ecbff;font-size:28px;font-weight:800}a{color:#91ceff;text-decoration:none}code{display:block;color:#8794a3;font-size:10px;overflow-wrap:anywhere}footer{color:#97a2af}</style></head><body><header><h1>North Garden CH05 · owner review index r3</h1><p class="boundary">Local-only review surface. All art remains unaccepted, commercially uncleared, ignored by Git, and nonexecutable.</p><div class="stats"><span>29 candidates</span><span>14 selected</span><span>39 pending decisions</span><span>50 ComicPanelPlans</span><span>33 release checks</span><span>0 accepted</span></div></header><main><div class="grid">''' + "".join(cards) + '''</div></main><footer>R3 extends immutable r2 · no remote assets · no network code · no upload · no recorded owner decision</footer></body></html>'''
    INDEX.write_text(page, encoding="utf-8", newline="\n")
    r2 = json.loads(R2_PACKET.read_text(encoding="utf-8"))
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    artifacts = [{"path": INDEX.relative_to(ROOT).as_posix(), "sha256": sha(INDEX), "bytes": INDEX.stat().st_size}]
    artifacts.extend(
        {"path": row["thumbnail_path"], "sha256": row["thumbnail_sha256"], "bytes": (ROOT / row["thumbnail_path"]).stat().st_size}
        for row in items
        if row["thumbnail_path"]
    )
    packet = {
        "record_type": "CH05OwnerReviewIndexPacket",
        "schema_version": "3.0",
        "record_id": "ng-ch05-owner-review-index-r3",
        "state": "LOCAL_REVIEW_HUB_EXTENDS_R2_OWNER_PENDING",
        "extends": {"path": R2_PACKET.relative_to(ROOT).as_posix(), "sha256": sha(R2_PACKET), "link_count": r2["link_count"]},
        "contract": {"path": CONTRACT.relative_to(ROOT).as_posix(), "sha256": sha(CONTRACT), "completed_decisions": contract["summary"]["completed_decisions"], "events": contract["summary"]["events"], "human_review_minutes": contract["summary"]["human_review_minutes"]},
        "link_count": len(items),
        "image_link_count": sum(row["kind"] == "IMAGE" for row in items),
        "html_link_count": sum(row["kind"] == "HTML" for row in items),
        "links": items,
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
        "index": {"path": INDEX.relative_to(ROOT).as_posix(), "sha256": sha(INDEX), "bytes": INDEX.stat().st_size},
        "owner_decisions": 0,
        "accepted_candidates": 0,
        "provider_calls": 0,
        "uploads": 0,
        "cost_usd": 0,
        "boundary": "Append-only local review hub; r2 and the empty decision contract remain unchanged.",
    }
    PACKET.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"CH05 owner review index r3: {len(items)} links / {len(artifacts)} artifacts / 29 candidates / 39 pending decisions")
    print(f"index {sha(INDEX)} packet {sha(PACKET)}; decisions/accepted/calls/uploads/cost 0/0/0/0/$0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
