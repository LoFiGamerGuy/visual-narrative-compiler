"""Build a deterministic local HTML review index for all overnight CH05 evidence."""
from __future__ import annotations

import hashlib
import html
import json
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "experiments/review-packets/ch05-owner-review-index-r1"
INDEX = OUT / "index.html"
PACKET = OUT / "owner-review-index-packet.json"
PRODUCTION = ROOT / "production/comic/run-manifests/ch05-instrumented-production-manifest-r1.json"
INITIAL = ROOT / "docs/research/evidence/ch05-overnight-production-r1.json"
HARDENING = ROOT / "docs/research/evidence/ch05-cadence-hardening-r1.json"
CONCEPTS = ROOT / "docs/research/evidence/future-litrpg-visual-concepts-r1.json"

REVIEW_LINKS = [
    ("Variable-cadence clean scroll", "experiments/review-packets/ch05-variable-cadence-assembly-r1/ch05-variable-cadence-scroll-clean-r1.png", "Fourteen selected beats at chapter cadence."),
    ("Variable-cadence phone scroll", "experiments/review-packets/ch05-variable-cadence-assembly-r1/ch05-variable-cadence-phone-scroll-390px-r1.png", "Actual 390px chapter footprint."),
    ("Exact lettering-safe zones", "experiments/review-packets/ch05-variable-cadence-assembly-r1/ch05-variable-cadence-scroll-safe-zones-r1.png", "Canonical normalized safe-zone overlay."),
    ("Departure and clue sequence", "experiments/review-packets/ch05-variable-cadence-assembly-r1/sequence-selected-departure_and_clue.png", "P001/P002/P003/P009 selected order."),
    ("Bridge to mill sequence", "experiments/review-packets/ch05-variable-cadence-assembly-r1/sequence-selected-bridge_to_mill.png", "P019/P026/P029/P035/P036 selected order."),
    ("Signal and return sequence", "experiments/review-packets/ch05-variable-cadence-assembly-r1/sequence-selected-signal_and_return.png", "P040/P044/P046/P049/P050 selected order."),
    ("Opacity comparison", "experiments/review-packets/ch05-transparent-lettering-rehearsal-r1/ch05-transparent-lettering-phone-comparison-r1.png", "96%/88%/76%; c014 fails person clearance."),
    ("Width × copy comparison", "experiments/review-packets/ch05-lettering-width-copy-sensitivity-r1/ch05-lettering-width-copy-sensitivity-r1.png", "Current-to-full-width phone-type sweep."),
    ("Outside-art lettering comparison", "experiments/review-packets/ch05-outside-art-lettering-band-r1/ch05-outside-art-lettering-band-comparison-r1.png", "Light band versus dark direct gutter text."),
    ("Main batch overview", "experiments/review-packets/ch05-overnight-production-r1/review/contact-sheet-all-candidates.png", "Twenty CH05 candidates across four style families."),
    ("Cadence hardening overview", "experiments/review-packets/ch05-cadence-hardening-r1/review/contact-sheet-hardening-candidates.png", "Six targeted style/lettering/causal checks."),
    ("Future LitRPG concepts", "experiments/review-packets/future-litrpg-visual-concepts-r1/review/contact-sheet-future-litrpg-concepts.png", "Three separate non-canon equipment/monster concepts."),
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def href(path: Path) -> str:
    return Path(os.path.relpath(path, OUT)).as_posix()


def thumbnail(source: Path, destination: Path, box: tuple[int, int] = (360, 500)) -> None:
    with Image.open(source) as opened:
        image = opened.convert("RGB")
    image.thumbnail(box, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", box, (20, 24, 30))
    x, y = (box[0] - image.width) // 2, (box[1] - image.height) // 2
    canvas.paste(image, (x, y))
    canvas.save(destination, optimize=False)


def review_state(candidate: dict) -> str:
    results = candidate.get("engineering_review", {}).get("results", {})
    values = list(results.values())
    if any(str(value).startswith("FAIL") for value in values):
        return "engineering-fail"
    if any(str(value).startswith("WARN") for value in values):
        return "engineering-warn"
    return "engineering-pass"


def candidate_card(item: dict, selected: bool, thumb_path: Path) -> str:
    output = item["output"]
    note = item.get("engineering_review", {}).get("note", "")
    panel = item.get("panel_id", item.get("concept_id", "non-canon concept"))
    style = item.get("style_id", item.get("format_role", "concept"))
    elapsed = item.get("execution", {}).get("elapsed_seconds")
    source = ROOT / output["path"]
    selected_badge = '<span class="badge selected">selected sequence</span>' if selected else ""
    canon_badge = '<span class="badge concept">non-canon concept</span>' if item["candidate_id"].startswith("l") else ""
    return f'''<article class="card">
      <a href="{html.escape(href(source))}"><img loading="lazy" src="{html.escape(href(thumb_path))}" alt="{html.escape(item['candidate_id'])}"></a>
      <div class="card-body"><div>{selected_badge}{canon_badge}<span class="badge {review_state(item)}">{review_state(item).replace('-', ' ')}</span></div>
      <h3>{html.escape(item['candidate_id'])} · {html.escape(str(panel))}</h3>
      <p class="meta">{html.escape(str(style))} · {output['width']}×{output['height']} · {elapsed:.3f}s · <code>{output['sha256'][:12]}…</code></p>
      <p>{html.escape(note)}</p>
      <p><a href="{html.escape(href(source))}">open full candidate</a></p></div></article>'''


def main() -> int:
    production = json.loads(PRODUCTION.read_text(encoding="utf-8"))
    initial = json.loads(INITIAL.read_text(encoding="utf-8"))
    hardening = json.loads(HARDENING.read_text(encoding="utf-8"))
    concepts = json.loads(CONCEPTS.read_text(encoding="utf-8"))
    selected_ids = {row["candidate_id"] for row in production["rows"]}
    chapter_candidates = initial["candidates"] + hardening["candidates"]
    concept_candidates = concepts["candidates"]
    all_candidates = chapter_candidates + concept_candidates
    OUT.mkdir(parents=True, exist_ok=True)
    thumbs = OUT / "thumbnails"
    thumbs.mkdir(exist_ok=True)
    candidate_records, candidate_html = [], []
    for item in all_candidates:
        source = ROOT / item["output"]["path"]
        if not source.is_file() or sha(source) != item["output"]["sha256"]:
            raise SystemExit(f"candidate source mismatch: {item['candidate_id']}")
        thumb_path = thumbs / f"candidate-{item['candidate_id']}.png"
        thumbnail(source, thumb_path)
        candidate_records.append({
            "candidate_id": item["candidate_id"], "selected": item["candidate_id"] in selected_ids,
            "source_path": item["output"]["path"], "source_sha256": item["output"]["sha256"],
            "thumbnail_path": thumb_path.relative_to(ROOT).as_posix(), "thumbnail_sha256": sha(thumb_path),
            "engineering_state": review_state(item), "accepted": False
        })
        candidate_html.append(candidate_card(item, item["candidate_id"] in selected_ids, thumb_path))
    review_records, review_html = [], []
    review_thumbs = OUT / "review-thumbnails"
    review_thumbs.mkdir(exist_ok=True)
    for index, (title, relative, note) in enumerate(REVIEW_LINKS, start=1):
        source = ROOT / relative
        if not source.is_file():
            raise SystemExit(f"missing review artifact: {relative}")
        thumb_path = review_thumbs / f"review-{index:02d}.png"
        thumbnail(source, thumb_path, (360, 420))
        review_records.append({"title": title, "path": relative, "sha256": sha(source), "thumbnail_path": thumb_path.relative_to(ROOT).as_posix(), "thumbnail_sha256": sha(thumb_path), "note": note})
        review_html.append(f'''<article class="card review-card"><a href="{html.escape(href(source))}"><img loading="lazy" src="{html.escape(href(thumb_path))}" alt="{html.escape(title)}"></a><div class="card-body"><h3>{html.escape(title)}</h3><p>{html.escape(note)}</p><p><a href="{html.escape(href(source))}">open review artifact</a></p></div></article>''')
    selected_cards = [card for card, item in zip(candidate_html, all_candidates) if item["candidate_id"] in selected_ids]
    other_cards = [card for card, item in zip(candidate_html, all_candidates) if item["candidate_id"] not in selected_ids and not item["candidate_id"].startswith("l")]
    concept_cards = [card for card, item in zip(candidate_html, all_candidates) if item["candidate_id"].startswith("l")]
    css = '''body{margin:0;background:#10141a;color:#e7e8ea;font:16px/1.45 system-ui,sans-serif}header,main{max-width:1500px;margin:auto;padding:24px}header{background:#171d25;border-bottom:1px solid #303844}h1,h2,h3{line-height:1.15}h2{margin-top:48px}.lede,.meta{color:#adb5bf}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(310px,1fr));gap:18px}.card{background:#19212b;border:1px solid #303a47;border-radius:12px;overflow:hidden}.card img{display:block;width:100%;height:360px;object-fit:contain;background:#12171e}.review-card img{height:300px}.card-body{padding:16px}.badge{display:inline-block;margin:0 6px 8px 0;padding:3px 8px;border-radius:999px;background:#394352;font-size:12px}.selected{background:#245f48}.concept{background:#694c25}.engineering-pass{background:#225b49}.engineering-warn{background:#755e20}.engineering-fail{background:#762f37}a{color:#89c8ff}code{font-size:12px}nav a{margin-right:16px}footer{padding:40px;color:#89939e;text-align:center}'''
    evidence_links = [INITIAL, HARDENING, CONCEPTS, PRODUCTION]
    evidence_html = " · ".join(f'<a href="{html.escape(href(path))}">{html.escape(path.name)}</a>' for path in evidence_links)
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>North Garden CH05 owner review index r1</title><style>{css}</style></head><body>
    <header><h1>North Garden CH05 · owner review index r1</h1><p class="lede">29 new candidates · 26 CH05 production-research candidates · 3 non-canon LitRPG concepts · 14 provisional sequence selections · 0 accepted</p>
    <nav><a href="#start">start here</a><a href="#selected">selected 14</a><a href="#alternates">alternates & diagnostics</a><a href="#concepts">future LitRPG concepts</a></nav>
    <p><strong>Boundary:</strong> all art remains unaccepted, commercially uncleared, and nondeterministic at generation. Review copy is non-canon. {evidence_html}</p></header>
    <main><section id="start"><h2>Start here: sequences, cadence, and lettering</h2><div class="grid">{''.join(review_html)}</div></section>
    <section id="selected"><h2>Provisional selected 14</h2><p class="lede">Engineering selections for sequence/cadence review; owner acceptance is still zero.</p><div class="grid">{''.join(selected_cards)}</div></section>
    <section id="alternates"><h2>Alternates and preserved diagnostics</h2><div class="grid">{''.join(other_cards)}</div></section>
    <section id="concepts"><h2>Separate non-canon future LitRPG concepts</h2><p class="lede">Equipment, armor, weapons, and Mireback direction only; these do not revise CH05.</p><div class="grid">{''.join(concept_cards)}</div></section></main>
    <footer>Built deterministically from hash-pinned local evidence. No provider call, upload, cost, acceptance, or plan revision.</footer></body></html>'''
    with INDEX.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(page)
    artifact_paths = [INDEX] + sorted(thumbs.glob("*.png")) + sorted(review_thumbs.glob("*.png"))
    artifacts = [{"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path), "bytes": path.stat().st_size} for path in artifact_paths]
    root = hashlib.sha256("".join(item["path"] + ":" + item["sha256"] + "\n" for item in artifacts).encode()).hexdigest()
    packet = {
        "record_type": "CH05OwnerReviewIndexPacket", "schema_version": "1.0", "record_id": "ng-ch05-owner-review-index-packet-r1",
        "state": "READY_FOR_OWNER_REVIEW_UNACCEPTED", "index": {"path": INDEX.relative_to(ROOT).as_posix(), "sha256": sha(INDEX)},
        "production_manifest": {"path": PRODUCTION.relative_to(ROOT).as_posix(), "sha256": sha(PRODUCTION)},
        "evidence_sources": [
            {"path": INITIAL.relative_to(ROOT).as_posix(), "sha256": sha(INITIAL)},
            {"path": HARDENING.relative_to(ROOT).as_posix(), "sha256": sha(HARDENING)},
            {"path": CONCEPTS.relative_to(ROOT).as_posix(), "sha256": sha(CONCEPTS)}
        ],
        "candidate_count": len(candidate_records), "chapter_candidate_count": len(chapter_candidates), "concept_candidate_count": len(concept_candidates),
        "selected_candidate_count": len(selected_ids), "review_link_count": len(review_records),
        "candidates": candidate_records, "review_links": review_records, "artifact_count": len(artifacts), "artifact_inventory_root_sha256": root,
        "artifacts": artifacts, "human_review_minutes": None, "accepted_candidates": 0,
        "provider_calls": 0, "uploads": 0, "cost_usd": 0,
        "boundary": "Browsable local review index only; no candidate, concept, sequence, lettering treatment, plan, or production base is accepted."
    }
    with PACKET.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(packet, indent=2) + "\n")
    print(f"built owner review index: 29 candidates / 14 selected / 12 review links / {len(artifacts)} artifacts; root {root}; index {sha(INDEX)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
