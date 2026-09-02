"""Build append-only local CH05 owner review hub r8 over r7."""
from __future__ import annotations

import hashlib
import html
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
R7 = ROOT / "experiments/review-packets/ch05-owner-review-index-r7/owner-review-index-r7-packet.json"
OUT = ROOT / "experiments/review-packets/ch05-owner-review-index-r8"
INDEX, PACKET = OUT / "index.html", OUT / "owner-review-index-r8-packet.json"
LINKS = [
    ("index_r7", "Complete owner hub r7", "HTML", "experiments/review-packets/ch05-owner-review-index-r7/index.html", "All prior art, sequence, cadence, lettering, continuity, capacity, and evidence links."),
    ("review_starter", "Final review-session starter", "TEXT", "docs/research/ch05-final-review-session-starter-r1.md", "Eight dependency-ordered steps from visual review through blocked future ingestion."),
    ("response_guide", "Six-root response guide", "TEXT", "docs/research/ch05-owner-response-guide-r1.md", "Exact allowed values, local response file, and strict validation command."),
    ("ingestion_preflight", "Owner-input ingestion preflight", "TEXT", "docs/research/ch05-owner-ingestion-preflight-contract-r1.md", "Cross-file root, decision, reviewer, minute, lifecycle, and hash parity without ingestion."),
    ("model_license_audit", "Final model/license/provenance audit", "TEXT", "docs/research/ch05-final-model-license-provenance-audit-r1.md", "Explicit unavailable service fields, authorized reference hashes, and open commercial status."),
    ("closeout_r2", "Current overnight closeout r2", "TEXT", "docs/research/ch05-overnight-closeout-r2.md", "Final release, safe-source, counts, recommendations, limits, and remaining review decisions."),
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path: Path) -> str:
    return Path(os.path.relpath(path, OUT)).as_posix()


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    items = []
    for item_id, title, kind, path_text, summary in LINKS:
        source = ROOT / path_text
        if not source.is_file():
            raise SystemExit(f"missing review link: {source}")
        items.append({"id": item_id, "title": title, "kind": kind, "path": path_text, "sha256": sha(source), "href": relative(source), "summary": summary})
    cards = [f'<article><a href="{html.escape(item["href"])}"><div class="type">LOCAL {item["kind"]}</div><h2>{html.escape(item["title"])}</h2></a><p>{html.escape(item["summary"])}</p><code>{item["sha256"]}</code></article>' for item in items]
    page = '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>CH05 owner review index r8</title><style>body{margin:0;background:#10151c;color:#edf1f5;font:15px/1.45 system-ui,sans-serif}header,main,footer{max-width:1480px;margin:auto;padding:26px}header{background:#18202a;border-bottom:1px solid #33404f}h1{margin:0 0 10px}.boundary{color:#ffd18a}.stats{display:flex;gap:12px;flex-wrap:wrap}.stats span{background:#253140;border-radius:8px;padding:8px 12px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(360px,1fr));gap:18px}article{background:#19222d;border:1px solid #33404f;border-radius:12px;padding:14px;overflow:hidden}.type{width:100%;height:230px;display:grid;place-items:center;background:#0e1319;border-radius:8px;color:#8ecbff;font-size:26px;font-weight:800}a{color:#91ceff;text-decoration:none}code{display:block;color:#8794a3;font-size:10px;overflow-wrap:anywhere}footer{color:#97a2af}</style></head><body><header><h1>North Garden CH05 · owner review index r8</h1><p class="boundary">Local-only review entry. No owner response, ingestion, acceptance, rights clearance, or production execution is inferred.</p><div class="stats"><span>29 candidates</span><span>50 plans</span><span>122 prior links</span><span>67 priority links</span><span>6 pilot roots</span><span>0 ingested</span></div></header><main><div class="grid">''' + "".join(cards) + '''</div></main><footer>R8 extends immutable r7 · local files only · no network code · no upload · no recorded owner decision</footer></body></html>'''
    INDEX.write_text(page, encoding="utf-8", newline="\n")
    prior = json.loads(R7.read_text(encoding="utf-8"))
    packet = {"record_type": "CH05OwnerReviewIndexPacket", "schema_version": "8.0", "record_id": "ng-ch05-owner-review-index-r8", "state": "LOCAL_FINAL_REVIEW_SESSION_HUB_OWNER_INPUTS_ABSENT", "extends": {"path": R7.relative_to(ROOT).as_posix(), "sha256": sha(R7), "prior_effective_link_count": 122}, "link_count": 6, "image_link_count": 0, "html_link_count": 1, "text_link_count": 5, "links": items, "artifact_count": 1, "artifacts": [{"path": INDEX.relative_to(ROOT).as_posix(), "sha256": sha(INDEX), "bytes": INDEX.stat().st_size}], "index": {"path": INDEX.relative_to(ROOT).as_posix(), "sha256": sha(INDEX), "bytes": INDEX.stat().st_size}, "summary": {"candidate_count": 29, "plan_count": 50, "prior_review_links": 122, "priority_review_links": 67, "pilot_roots": 6, "response_files": 0, "event_logs": 0, "owner_decisions_ingested": 0, "human_review_minutes": None, "accepted_candidates": 0, "commercially_cleared": 0, "executable_panels": 0, "provider_calls": 0, "uploads": 0, "cost_usd": 0}, "animation_shot_plan": None, "e_conte": None, "boundary": "Append-only local hub; r7, generated pixels, absent owner inputs, and production state remain unchanged."}
    if prior.get("record_id") != "ng-ch05-owner-review-index-r7":
        raise SystemExit("unexpected r7 lineage")
    PACKET.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"CH05 owner review index r8: 6 links / 1 artifact; index {sha(INDEX)} packet {sha(PACKET)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
