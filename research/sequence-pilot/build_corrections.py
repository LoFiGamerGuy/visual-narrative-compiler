"""Build the offline nine-panel correction comparison using verified original bytes.

Standard library only. Reads frozen plan and reservation/registration events;
does not import review findings, infer acceptance or mutate the production log.
Copied display images live under the ignored corrections/assets directory.
"""
from pathlib import Path
import hashlib
import html
import json
import shutil

ROOT = Path(__file__).resolve().parents[2]
PILOT = ROOT / "production" / "sequence-pilot"
OUT = ROOT / "docs" / "research" / "sequence-pilot" / "corrections"


def esc(value):
    return html.escape(str(value))


def verified_source(candidate):
    relative = Path(candidate["path"])
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError("Candidate source must remain within the pilot")
    path = PILOT / relative
    if path.is_symlink() or not path.resolve().is_relative_to((PILOT / "candidates").resolve()):
        raise ValueError("Candidate source is not a regular in-pilot candidate")
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != candidate["sha256"]:
        raise ValueError(f"Candidate hash mismatch: {candidate['id']}")
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("This bounded presentation expects the registered PNG originals")
    width, height = int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")
    if (width, height) != (candidate["width"], candidate["height"]):
        raise ValueError(f"Candidate dimensions mismatch: {candidate['id']}")
    return path


def main():
    plan_bytes = (PILOT / "plan.json").read_bytes()
    plan = json.loads(plan_bytes)
    plan_hash = hashlib.sha256(plan_bytes).hexdigest()
    events_bytes = (PILOT / "events.jsonl").read_bytes()
    events = [json.loads(line) for line in events_bytes.splitlines() if line.strip()]
    # Do not read observed/final review payloads into the presentation model.
    relevant = [e for e in events if e["type"] in ("reserved", "registered")]
    if any(e["plan_sha256"] != plan_hash for e in relevant):
        raise ValueError("Reservation/registration plan does not match frozen source")
    attempts = {e["data"]["id"]: e["data"] for e in relevant if e["type"] == "reserved"}
    candidates = [e["data"] for e in relevant if e["type"] == "registered"]
    if len(candidates) != 23 or {c["id"] for c in candidates} != {f"C{n:05d}" for n in range(1, 24)}:
        raise SystemExit("Wait for exactly C00001 through C00023 to be registered before building this bounded comparison")
    by_attempt = {}
    for c in candidates:
        if c["attempt_id"] in by_attempt:
            raise ValueError("Ambiguous candidate mapping for a compared attempt")
        by_attempt[c["attempt_id"]] = c
    retry_attempts = sorted((a for a in attempts.values() if a.get("retry_of")), key=lambda a: a["panel"])
    if len(retry_attempts) != 9 or len({a["panel"] for a in retry_attempts}) != 9:
        raise ValueError("Expected exactly nine corrected panels")
    pairs = []
    for retry in retry_attempts:
        original_attempt = attempts[retry["retry_of"]]
        if original_attempt.get("retry_of") or original_attempt["panel"] != retry["panel"]:
            raise ValueError("Retries must link directly to the original same-panel attempt")
        if not retry.get("hard_failure"):
            raise ValueError("Every correction needs its recorded hard-failure reason")
        old, new = by_attempt[original_attempt["id"]], by_attempt[retry["id"]]
        pairs.append((retry, old, new, verified_source(old), verified_source(new)))
    # Verify the whole batch before making any presentation copies.
    assets = OUT / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    sections = []
    for index, (retry, old, new, old_path, new_path) in enumerate(pairs):
        panel_id = retry["panel"]
        panel = next(p for p in plan["panels"] if f"P{p['panel']:02d}" == panel_id)
        figures = []
        for label, c, path in [("Original candidate", old, old_path), ("Corrected candidate", new, new_path)]:
            destination = assets / path.name
            shutil.copyfile(path, destination)
            if hashlib.sha256(destination.read_bytes()).hexdigest() != c["sha256"]:
                raise ValueError("Copied raster hash mismatch")
            url = "assets/" + path.name
            is_original = c is old
            status = "Rejected for targeted retry" if is_original else "Draft / unaccepted"
            figures.append(f'''<figure>
<figcaption><span class="version">{label}</span><span class="status">{status}</span></figcaption>
<a class="image-link" href="{esc(url)}" aria-label="Open full-size {esc(panel_id)} {label.lower()} {esc(c['id'])}"><img src="{esc(url)}" width="{c['width']}" height="{c['height']}" alt="Actual {label.lower()} for {esc(panel_id)}. Compare it with the frozen beat and recorded retry reason; no acceptance is asserted." loading="{'eager' if index == 0 else 'lazy'}" decoding="async"></a>
<div class="image-meta"><span>{esc(c['id'])} · {esc(c['attempt_id'])}</span><span>{c['width']} × {c['height']} px</span><a href="{esc(url)}">Open original-size image ↗</a></div>
<details class="provenance"><summary>Source identity and registration status</summary><dl><dt>SHA256</dt><dd class="hash">{esc(c['sha256'])}</dd><dt>Registered status</dt><dd>{esc(c['status'])}</dd><dt>Owner review at registration</dt><dd>{esc(c['owner_review'])}</dd><dt>Commercial clearance at registration</dt><dd>{esc(c['commercial_clearance'])}</dd></dl></details>
</figure>''')
        sections.append(f'''<section class="comparison" id="{esc(panel_id)}" aria-labelledby="title-{esc(panel_id)}">
<div class="panel-heading"><span class="panel-number">{esc(panel_id)}</span><div><h2 id="title-{esc(panel_id)}">{esc(panel['function'])}</h2><p class="camera">Frozen camera: {esc(panel['camera'])}</p></div><a class="to-top" href="#top">Top ↑</a></div>
<p class="beat"><strong>Required beat.</strong> {esc(panel['beat'])}</p>
<div class="reason"><span class="reason-label">Recorded reason for the one retry</span><p>{esc(retry['hard_failure'])}</p></div>
<div class="pair">{''.join(figures)}</div>
<details class="contract"><summary>Frozen continuity contract</summary><p>{esc(panel['continuity_contract'])}</p></details>
<p class="review-note">Correction is not acceptance. These are preserved draft candidates; consult the <a href="../../../../research/sequence-pilot/corrected-visual-review.md">corrected visual review</a> for the final observations and rejection status.</p>
</section>''')
    navigation = ''.join(f'<a href="#{esc(a[0]["panel"])}">{esc(a[0]["panel"])}</a>' for a in pairs)
    document = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><meta name="description" content="Nine verified original and corrected panel pairs from the bounded sequence pilot, with recorded retry reasons and no acceptance claim."><meta name="plan-sha256" content="{plan_hash}"><meta name="ledger-sha256-at-build" content="{hashlib.sha256(events_bytes).hexdigest()}"><title>Nine correction attempts — Three Charges, One Dose</title><link rel="stylesheet" href="style.css"></head><body>
<a class="skip" href="#comparisons">Skip to comparisons</a>
<header id="top"><div class="topbar"><a href="../index.html">Anime Pipeline / Research</a><nav aria-label="Project"><a href="../reader/index.html">Pilot reader ↗</a><a href="../index.html">Research report ↗</a></nav></div>
<div class="hero"><p class="eyebrow">Three Charges, One Dose · Bounded correction record</p><h1>Nine corrections.<br>Every original preserved.</h1><p class="lead">Compare the actual first candidates with their one targeted retry. Each pair keeps its frozen story beat, recorded failure reason and source identity visible.</p><p class="notice"><strong>Draft / rejected pending final review. Correction is not acceptance.</strong> A revised image may still fail the required event, contact, geography or state. This gallery does not supply a new visual verdict.</p><p>These nine panels have used their primary generation and their one permitted hard-failure retry. <strong>No third generation is allowed under the frozen budget.</strong> A remaining defect must be reported; this presentation does not authorize another retry or a production release.</p><div class="hero-links"><a href="../../../../research/sequence-pilot/corrected-visual-review.md">Read the corrected visual review ↗</a><a href="../reader/index.html">Read the complete draft sequence ↗</a></div></div></header>
<nav class="panel-nav" aria-label="Corrected panels"><span>Jump to panel</span>{navigation}</nav>
<main id="comparisons">{''.join(sections)}</main>
<footer><h2>How this comparison was assembled</h2><p>The frozen plan and reservation/registration ledger supply the beats, retry links and reasons. All 18 displayed PNGs are byte-for-byte copies of the registered candidates, verified against their recorded SHA256 and dimensions. No image was cropped, repainted or substituted for this gallery. Display scaling preserves its aspect ratio.</p><p>Registration status is historical metadata, not a final review result. The final review remains separate. Generated display copies are ignored local assets; the preserved candidate originals remain in the pilot workspace.</p><p><a href="../../../../production/sequence-pilot/plan.json">Frozen plan</a> · <a href="../../../../production/sequence-pilot/events.jsonl">Provenance ledger</a> · <a href="../../../../research/sequence-pilot/build_corrections.py">Reproducible builder</a> · <a href="#top">Back to top ↑</a></p></footer>
</body></html>'''
    (OUT / "index.html").write_text(document, encoding="utf-8")
    print(json.dumps({"pairs": len(pairs), "verified_raster_copies": len(pairs)*2, "panels": [p[0]["panel"] for p in pairs], "output": str(OUT / "index.html"), "plan_sha256": plan_hash, "ledger_sha256_at_build": hashlib.sha256(events_bytes).hexdigest()}))


if __name__ == "__main__":
    main()
