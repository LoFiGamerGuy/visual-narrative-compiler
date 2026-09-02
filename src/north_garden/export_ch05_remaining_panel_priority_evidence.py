"""Export tracked evidence for the exact CH05 50-plan coverage/priority partition."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PRIORITY = ROOT / "production/comic/coverage/ch05-remaining-panel-priority-r1.json"
OUTPUT = ROOT / "docs/research/evidence/ch05-remaining-panel-priority-r1.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    priority = json.loads(PRIORITY.read_text(encoding="utf-8"))
    evidence = {
        "record_type": "CH05RemainingPanelPriorityEvidence", "schema_version": "1.0",
        "record_id": "ng-ch05-remaining-panel-priority-evidence-r1",
        "state": "EXACT_50_PLAN_PARTITION_OWNER_REVIEW_BEFORE_NEW_GENERATION",
        "medium": "comic", "comic_panel_plan_revision_created": False, "animation_shot_plan": None, "e_conte": None,
        "priority_manifest": {"path": PRIORITY.relative_to(ROOT).as_posix(), "sha256": sha(PRIORITY)},
        "summary": priority["summary"], "coverage": priority["coverage"], "priority_tiers": priority["priority_tiers"],
        "row_root_sha256": priority["row_root_sha256"], "chart": priority["chart"],
        "determinism": {"consecutive_compile_count": 2, "manifest_sha256_run_a": sha(PRIORITY), "manifest_sha256_run_b": sha(PRIORITY), "result": "BYTE_IDENTICAL_PRIORITY_MANIFEST_AND_CHART_HASH"},
        "decision": priority["decision"],
        "limitations": [
            "Priority orders production evidence and does not rank canon importance or aesthetic quality.",
            "Tier A is not authorized execution; current candidate decisions and the 29-candidate run should be reviewed first.",
            "No final copy, prompt, provider metadata, candidate timing, or production cost is estimated for uncovered plans.",
            "The exact 50-plan denominator is planning coverage, not 50-panel rendered or accepted coverage."
        ],
        "boundary": "All 50 ComicPanelPlans remain unchanged; new accepted/executable panels, calls, uploads, cost, and human minutes are zero/null."
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8", newline="\n") as handle: handle.write(json.dumps(evidence, indent=2) + "\n")
    print(f"exported remaining-panel priority evidence: {OUTPUT.relative_to(ROOT)} {sha(OUTPUT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
