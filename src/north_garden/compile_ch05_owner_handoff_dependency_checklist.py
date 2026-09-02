"""Compile dependency-ordered owner review checklist with exact local links."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MATRIX = ROOT / "production/comic/review/ch05-route-review-decision-matrix-r1.json"
OWNER = ROOT / "production/comic/review/ch05-owner-decision-contract-r1.json"
LINKS = ROOT / "production/comic/review/ch05-review-artifact-link-manifest-r1.json"
READINESS = ROOT / "production/comic/run-manifests/ch05-chapter-production-readiness-matrix-r1.json"
OUTPUT = ROOT / "production/comic/review/ch05-owner-handoff-dependency-checklist-r1.json"
MARKDOWN = ROOT / "docs/research/ch05-owner-handoff-checklist-r1.md"
EVIDENCE = ROOT / "docs/research/evidence/ch05-owner-handoff-dependency-checklist-r1.json"

ROUTE_ARTIFACTS = {
    "route_role_aware_hybrid": "experiments/review-packets/ch05-continuity-style-density-r1/style-engineering-results-r1.png",
    "c005_transition_density": "experiments/review-packets/ch05-continuity-style-density-r1/selected-phone-density-montage-r1.png",
    "c014_action_punctuation": "experiments/review-packets/ch05-continuity-style-density-r1/sequence-appearance-jumps-r1.png",
    "lettering_semantics": "experiments/review-packets/ch05-transparent-lettering-rehearsal-r1/ch05-transparent-lettering-phone-comparison-r1.png",
    "lettering_visual_arm": "experiments/review-packets/ch05-outside-art-lettering-band-r1/ch05-outside-art-lettering-band-comparison-r1.png",
    "p010_p013_finish_rhythm": "experiments/review-packets/ch05-p010-p013-preflight-contract-r1/ch05-p010-p013-preflight-storyboard-r1.png",
    "p010_p013_copy": "experiments/review-packets/ch05-p010-p013-preflight-contract-r1/ch05-p010-p013-preflight-storyboard-r1.png",
    "strongest_candidate_shortlist": "experiments/review-packets/ch05-owner-review-index-r3/index.html",
    "noncanon_litrpg_direction": "experiments/review-packets/future-litrpg-visual-concepts-r1/review/contact-sheet-future-litrpg-concepts.png",
    "commercial_and_exact_base": "production/comic/recommendations/ch05-pipeline-route-recommendation-r1.json",
}
DEPENDENCIES = {
    "route_role_aware_hybrid": [],
    "c005_transition_density": [],
    "c014_action_punctuation": [],
    "lettering_semantics": [],
    "lettering_visual_arm": ["route:lettering_semantics"],
    "p010_p013_finish_rhythm": ["route:route_role_aware_hybrid", "route:c005_transition_density", "route:c014_action_punctuation"],
    "p010_p013_copy": ["route:lettering_semantics"],
    "strongest_candidate_shortlist": [],
    "noncanon_litrpg_direction": [],
    "commercial_and_exact_base": ["route:route_role_aware_hybrid", "route:strongest_candidate_shortlist"],
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def binding(path: Path) -> dict:
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path)}


def artifact(path_text: str) -> dict:
    path = ROOT / path_text
    return {"path": path_text, "absolute_path": path.resolve().as_posix(), "sha256": sha(path)}


def main() -> int:
    matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
    owner = json.loads(OWNER.read_text(encoding="utf-8"))
    links = json.loads(LINKS.read_text(encoding="utf-8"))
    owner_by_id = {row["subject_id"]: row for row in owner["subjects"]}
    strongest = [item for item in links["artifacts"] if "strongest_candidates" in item["categories"]]
    candidate_tasks = []
    for item in strongest:
        filename = Path(item["path"]).name
        candidate_id = filename.split("-")[0]
        subject = owner_by_id[candidate_id]
        candidate_tasks.append({"task_id": f"candidate:{candidate_id}", "task_type": "CANDIDATE_REVIEW", "stage": 1, "subject_id": candidate_id, "question": f"Disposition {candidate_id} for further production evaluation.", "allowed_decisions": subject["allowed_decisions"], "dependencies": [], "optional_for_ch05_next_microsequence": False, "artifact": {"path": item["path"], "absolute_path": item["absolute_path"], "sha256": item["sha256"]}, "decision": None, "reviewer": None, "human_review_minutes": None})
    candidate_tasks.sort(key=lambda row: row["subject_id"])
    route_tasks = []
    for row in matrix["decisions"]:
        decision_id = row["decision_id"]
        stage = 3 if decision_id == "commercial_and_exact_base" else 2 if DEPENDENCIES[decision_id] else 1
        optional = decision_id == "noncanon_litrpg_direction"
        dependencies = list(DEPENDENCIES[decision_id])
        if decision_id == "strongest_candidate_shortlist":
            dependencies = [task["task_id"] for task in candidate_tasks]
            stage = 2
        route_tasks.append({"task_id": f"route:{decision_id}", "task_type": "ROUTE_DECISION", "stage": stage, "subject_id": decision_id, "question": row["question"], "engineering_default": row["engineering_default"], "consequence": row["consequence"], "dependencies": dependencies, "optional_for_ch05_next_microsequence": optional, "artifact": artifact(ROUTE_ARTIFACTS[decision_id]), "decision": None, "reviewer": None, "human_review_minutes": None})
    tasks = sorted(candidate_tasks + route_tasks, key=lambda row: (row["stage"], row["task_type"], row["task_id"]))
    stage_counts = {str(stage): sum(row["stage"] == stage for row in tasks) for stage in (1, 2, 3)}
    record = {"record_type": "ComicOwnerHandoffDependencyChecklist", "schema_version": "1.0", "record_id": "ng-ch05-owner-handoff-dependency-checklist-r1", "state": "DEPENDENCY_ORDERED_ALL_DECISIONS_EMPTY", "medium": "comic", "inputs": [binding(path) for path in (MATRIX, OWNER, LINKS, READINESS)], "summary": {"task_count": len(tasks), "candidate_review_tasks": len(candidate_tasks), "route_decision_tasks": len(route_tasks), "stage_1_tasks": stage_counts["1"], "stage_2_tasks": stage_counts["2"], "stage_3_tasks": stage_counts["3"], "optional_parallel_tasks": sum(row["optional_for_ch05_next_microsequence"] for row in tasks), "completed_tasks": 0, "owner_decisions": 0, "accepted_candidates": 0, "human_review_minutes": None, "provider_calls": 0, "uploads": 0, "cost_usd": 0}, "stage_definitions": {"1": "Foundational route/density/lettering semantics, individual candidate reviews, and optional non-canon taste review can proceed in parallel.", "2": "Dependent lettering/P010 rhythm/copy and shortlist rollup after their prerequisites.", "3": "Commercial-clearance and exact-production-base authority only after route and candidate dispositions."}, "tasks": tasks, "next_microsequence_gate_note": "P010–P013 remains blocked by route, cadence, copy-or-silence, exact-reference selection, commercial, and candidate/style review gates in its production manifest.", "comic_panel_plan_revision_created": False, "animation_shot_plan": None, "e_conte": None, "boundary": "Read-only dependency aid. Does not ingest a decision, start a timer, authorize a prompt/upload, accept art, or establish commercial clearance."}
    OUTPUT.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8", newline="\n")
    lines = ["# CH05 owner handoff dependency checklist r1", "", "All decisions are empty. Order is based only on prerequisites, not on a preference score. The non-canon LitRPG task is optional and does not block CH05.", ""]
    for stage in (1, 2, 3):
        lines.extend([f"## Stage {stage}", "", record["stage_definitions"][str(stage)], ""])
        for task in [item for item in tasks if item["stage"] == stage]:
            optional = " (optional parallel)" if task["optional_for_ch05_next_microsequence"] else ""
            deps = ", ".join(task["dependencies"]) or "none"
            lines.append(f"- [ ] [{task['task_id']}]({task['artifact']['absolute_path']}){optional} — {task['question']} Dependencies: {deps}.")
        lines.append("")
    MARKDOWN.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    evidence = {"record_type": "ComicOwnerHandoffDependencyChecklistEvidence", "schema_version": "1.0", "record_id": "ng-ch05-owner-handoff-dependency-checklist-evidence-r1", "state": "PASS_ALL_EMPTY", "checklist": binding(OUTPUT), "markdown": binding(MARKDOWN), "inputs": record["inputs"], "summary": record["summary"], "animation_shot_plan": None, "e_conte": None}
    EVIDENCE.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"CH05 owner checklist: {len(tasks)} tasks = {len(candidate_tasks)} candidates + {len(route_tasks)} route; stages {stage_counts['1']}/{stage_counts['2']}/{stage_counts['3']}")
    print("completed/decisions/accepted/minutes/calls/uploads/cost 0/0/0/null/0/0/$0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
