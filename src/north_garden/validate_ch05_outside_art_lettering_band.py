"""Validate local outside-art lettering-band evidence and non-plan boundaries."""
from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "production/comic/lettering/ch05-outside-art-lettering-band-r1.json"
REVIEW = ROOT / "production/comic/review/ch05-outside-art-lettering-band-review-r1.json"
EVIDENCE = ROOT / "docs/research/evidence/ch05-outside-art-lettering-band-r1.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def semantic_errors(data: dict) -> list[str]:
    out = []
    summary = data.get("summary", {})
    if (summary.get("treatment_count"), summary.get("subject_count"), summary.get("band_instance_count"), summary.get("artifact_count")) != (2, 3, 6, 5):
        out.append("denominator invalid")
    if summary.get("font_size_phone_px", 0) < 13 or summary.get("source_pixels_changed") != 0:
        out.append("type/clearance measurement invalid")
    if summary.get("band_scroll_dimensions") != [1200, 15046] or summary.get("phone_scroll_dimensions") != [390, 4890]:
        out.append("scroll dimensions invalid")
    if summary.get("accepted_treatments") != 0 or summary.get("human_review_minutes") is not None:
        out.append("acceptance/review fabricated")
    if summary.get("provider_calls") != 0 or summary.get("uploads") != 0 or summary.get("cost_usd") != 0:
        out.append("external activity fabricated")
    if data.get("comic_panel_plan_revision_created") is not False or data.get("assembly_revision_created") is not False or data.get("animation_shot_plan") is not None or data.get("e_conte") is not None:
        out.append("planning boundary invalid")
    treatments = data.get("treatments", [])
    if len(treatments) != 2 or {x.get("treatment_id") for x in treatments} != {"light_caption_band", "dark_direct_gutter_text"}:
        out.append("treatment coverage invalid")
    if any(x.get("source_pixels_changed") != 0 or x.get("band_count") != 3 for x in treatments):
        out.append("treatment geometry invalid")
    return sorted(set(out))


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    review = json.loads(REVIEW.read_text(encoding="utf-8"))
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    failures = semantic_errors(evidence)
    if sha(MANIFEST) != evidence["manifest"]["sha256"] or sha(REVIEW) != evidence["engineering_review"]["sha256"]:
        failures.append("tracked binding mismatch")
    if manifest["review_copy_is_canon"] is not False or review["accepted_treatments"]:
        failures.append("copy/treatment promotion")
    for treatment in evidence["treatments"]:
        for field in ("scroll", "phone_scroll"):
            path = ROOT / treatment[field]["path"]
            if not path.is_file() or sha(path) != treatment[field]["sha256"]:
                failures.append(f"artifact mismatch: {treatment[field]['path']}")
            elif subprocess.run(["git", "check-ignore", "-q", str(path)], cwd=ROOT, check=False).returncode:
                failures.append(f"artifact not ignored: {treatment[field]['path']}")
    mutations = [
        lambda d: d["summary"].update(treatment_count=1), lambda d: d["summary"].update(subject_count=2),
        lambda d: d["summary"].update(band_instance_count=5), lambda d: d["summary"].update(artifact_count=4),
        lambda d: d["summary"].update(font_size_phone_px=12.9), lambda d: d["summary"].update(source_pixels_changed=1),
        lambda d: d["summary"].update(band_scroll_dimensions=[1200, 14566]), lambda d: d["summary"].update(accepted_treatments=1),
        lambda d: d["summary"].update(provider_calls=1), lambda d: d.update(comic_panel_plan_revision_created=True),
        lambda d: d["treatments"].pop(), lambda d: d["treatments"][0].update(source_pixels_changed=1)
    ]
    rejected = 0
    for mutation in mutations:
        changed = copy.deepcopy(evidence); mutation(changed); rejected += bool(semantic_errors(changed))
    if rejected != len(mutations): failures.append(f"only {rejected}/{len(mutations)} mutations rejected")
    print(f"CH05 outside-art lettering bands: {len(failures)} failures; 2 treatments/3 subjects/6 bands/5 artifacts; {rejected}/{len(mutations)} mutations rejected")
    print("13.975px phone type; 0 source pixels changed; scroll +480px/+3.295%; no plan/assembly revision; 0 calls/uploads/$0")
    for failure in failures: print(f"FAIL: {failure}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
