"""Validate CH05 local lettering evidence and fail-closed semantic boundaries."""
from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "production/comic/lettering/ch05-transparent-lettering-rehearsal-r1.json"
REVIEW = ROOT / "production/comic/review/ch05-transparent-lettering-rehearsal-review-r1.json"
EVIDENCE = ROOT / "docs/research/evidence/ch05-transparent-lettering-rehearsal-r1.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def semantic_errors(data: dict) -> list[str]:
    failures = []
    summary = data.get("summary", {})
    if summary.get("subject_count") != 4 or summary.get("treatment_count") != 12 or summary.get("artifact_count") != 25:
        failures.append("denominator invalid")
    if summary.get("subjects_meeting_13px_target") != 0 or summary.get("phone_font_max_px", 99) >= 13:
        failures.append("phone-size failure hidden")
    if summary.get("protected_content_clearance_fail_subjects") != 1:
        failures.append("semantic clearance failure hidden")
    if summary.get("accepted_treatments") != 0 or summary.get("human_review_minutes") is not None:
        failures.append("acceptance or review fabricated")
    if summary.get("provider_calls") != 0 or summary.get("uploads") != 0 or summary.get("cost_usd") != 0:
        failures.append("external activity fabricated")
    if data.get("comic_panel_plan_revision_created") is not False or data.get("animation_shot_plan") is not None or data.get("e_conte") is not None:
        failures.append("planning boundary invalid")
    records = data.get("records", [])
    if len(records) != 12 or len({(item.get("candidate_id"), item.get("treatment_id")) for item in records}) != 12:
        failures.append("record coverage invalid")
    return sorted(set(failures))


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    review = json.loads(REVIEW.read_text(encoding="utf-8"))
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    failures = semantic_errors(evidence)
    if sha(MANIFEST) != evidence["manifest"]["sha256"] or sha(REVIEW) != evidence["engineering_review"]["sha256"]:
        failures.append("tracked binding mismatch")
    font = Path(manifest["font"]["local_path"])
    if not font.is_file() or sha(font) != manifest["font"]["sha256"]:
        failures.append("font hash mismatch")
    if manifest["review_copy_is_canon"] is not False or review["accepted_treatments"]:
        failures.append("copy or treatment promotion")
    if not review["visual_reviews"][1]["protected_content_clearance"].startswith("FAIL:"):
        failures.append("c014 visual failure missing")
    for item in evidence["records"]:
        if item["metrics"]["black_type_contrast_ratio_p05"] < 11:
            failures.append(f"unexpected contrast regression: {item['candidate_id']}/{item['treatment_id']}")
        for field in ("composite", "phone_preview"):
            path = ROOT / item[field]["path"]
            if not path.is_file() or sha(path) != item[field]["sha256"]:
                failures.append(f"artifact mismatch: {item[field]['path']}")
            elif subprocess.run(["git", "check-ignore", "-q", str(path)], cwd=ROOT, check=False).returncode:
                failures.append(f"artifact not ignored: {item[field]['path']}")
    mutations = [
        lambda d: d["summary"].update(subject_count=3), lambda d: d["summary"].update(treatment_count=11),
        lambda d: d["summary"].update(artifact_count=24), lambda d: d["summary"].update(subjects_meeting_13px_target=4),
        lambda d: d["summary"].update(phone_font_max_px=13.1), lambda d: d["summary"].update(protected_content_clearance_fail_subjects=0),
        lambda d: d["summary"].update(accepted_treatments=1), lambda d: d["summary"].update(human_review_minutes=1),
        lambda d: d["summary"].update(provider_calls=1), lambda d: d.update(comic_panel_plan_revision_created=True),
        lambda d: d["records"].pop(), lambda d: d["records"][1].update(candidate_id=d["records"][0]["candidate_id"], treatment_id=d["records"][0]["treatment_id"])
    ]
    rejected = 0
    for mutation in mutations:
        changed = copy.deepcopy(evidence); mutation(changed); rejected += bool(semantic_errors(changed))
    if rejected != len(mutations): failures.append(f"only {rejected}/{len(mutations)} mutations rejected")
    print(f"CH05 transparent lettering: {len(failures)} failures; 4 subjects/12 treatments/25 artifacts; {rejected}/{len(mutations)} mutations rejected")
    print("phone type 6.513-11.366px (0/4 at 13px); p05 backing contrast >=11.942:1; c014 semantic clearance fails; 0 calls/uploads/$0")
    for failure in failures: print(f"FAIL: {failure}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
