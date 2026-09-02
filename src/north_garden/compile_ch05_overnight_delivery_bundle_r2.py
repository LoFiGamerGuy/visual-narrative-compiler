"""Compile the append-only CH05 overnight delivery bundle r2."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
START_COMMIT = "e011cac"
PATHS = {
    "r1": "production/comic/handoff/ch05-overnight-delivery-bundle-r1.json",
    "render": "production/comic/run-manifests/ch05-built-in-renderrecord-index-r1.json",
    "route": "production/comic/recommendations/ch05-pipeline-route-recommendation-r1.json",
    "decisions": "production/comic/review/ch05-route-review-decision-matrix-r1.json",
    "links": "production/comic/review/ch05-review-artifact-link-manifest-r3.json",
    "release": "docs/research/evidence/ch05-overnight-integrated-release-gate-r9.json",
    "capacity": "production/comic/run-manifests/ch05-chapter-production-duration-capacity-r1.json",
    "playbook": "production/comic/handoff/ch05-chapter-production-operating-playbook-r1.json",
    "lifecycle": "production/comic/run-manifests/ch05-chapter-batch-lifecycle-application-r1.json",
    "unlock": "production/comic/review/ch05-p010-p013-owner-unlock-contract-r1.json",
    "cost": "docs/research/evidence/ch05-production-cost-ledger-r26.json",
    "safe_source": "docs/research/evidence/ch05-overnight-safe-source-parity-r1.json",
    "frozen": "docs/research/evidence/frozen-gauntlet-baseline-integrity-r1.json",
}
OUTPUT = ROOT / "production/comic/handoff/ch05-overnight-delivery-bundle-r2.json"
EVIDENCE = ROOT / "docs/research/evidence/ch05-overnight-delivery-bundle-r2.json"
SUMMARY = ROOT / "docs/research/ch05-overnight-delivery-summary-r2.md"
CHANGED = ROOT / "docs/research/ch05-overnight-changed-files-through-playbook-r1.md"
HUB = ROOT / "experiments/review-packets/ch05-owner-review-index-r5/index.html"
LINK_DOC = ROOT / "docs/research/ch05-review-links-r3.md"
UNLOCK_DOC = ROOT / "docs/research/ch05-p010-p013-owner-unlock-checklist-r1.md"
CAPACITY_CHART = ROOT / "experiments/review-packets/ch05-chapter-production-duration-capacity-r1/ch05-chapter-duration-capacity-map-r1.png"
PLAYBOOK_DOC = ROOT / "docs/research/ch05-chapter-production-operating-playbook-r1.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def binding(path: Path, *, absolute: bool = False) -> dict:
    out = {"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path)}
    if absolute:
        out["absolute_path"] = path.resolve().as_posix()
    return out


def load(key: str) -> dict:
    return json.loads((ROOT / PATHS[key]).read_text(encoding="utf-8"))


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", check=True
    ).stdout.strip()


def main() -> int:
    render, route, decisions, links = (load(k) for k in ("render", "route", "decisions", "links"))
    release, capacity, playbook, lifecycle = (load(k) for k in ("release", "capacity", "playbook", "lifecycle"))
    unlock, cost, frozen = (load(k) for k in ("unlock", "cost", "frozen"))
    head, origin = git("rev-parse", "HEAD"), git("rev-parse", "origin/main")
    commits = git("rev-list", "--reverse", f"{START_COMMIT}^..{head}").splitlines()
    changed = git("diff", "--name-only", f"{START_COMMIT}^", head).splitlines()
    strongest = [x for x in links["artifacts"] if "strongest_candidates" in x["categories"]]
    dimensions = sorted({(r["output"]["width"], r["output"]["height"]) for r in render["records"]})
    key_links = [
        {"id": "owner_hub_r5", **binding(HUB, absolute=True)},
        {"id": "exhaustive_review_links_r3", **binding(LINK_DOC, absolute=True)},
        {"id": "owner_unlock_checklist", **binding(UNLOCK_DOC, absolute=True)},
        {"id": "duration_capacity_chart", **binding(CAPACITY_CHART, absolute=True)},
        {"id": "operating_playbook", **binding(PLAYBOOK_DOC, absolute=True)},
    ]
    limitations = [
        "All 29 candidates remain unaccepted and commercially uncleared; shortlist membership is engineering triage only.",
        "Built-in model, endpoint, request ID, provider usage, monetary cost, and seed are unavailable for every candidate.",
        "Generation reproducibility is unproven and no deterministic seed is available.",
        "Style/task samples are unbalanced, so run-specific pass rates do not estimate general provider quality.",
        "Hair, wardrobe, role order, hands, causality, density, and lettering clearance still require human visual review.",
        "Human review minutes remain null because prior review was not captured through the timer contract.",
        "Final copy, fonts, tails, localization, accessibility, lettering acceptance, and commercial rights remain open.",
        "The three non-canon LitRPG concepts do not revise CH05 canon, wardrobe, equipment, class, weapons, or monsters.",
        "The 49/68-candidate capacity figures are measured generation-only planning envelopes, not schedules or commitments.",
        "Absolute review links are valid only for the recorded C:/AgentWorkspaces/anime-pipeline workspace root.",
    ]
    bundle = {
        "record_type": "ComicOvernightDeliveryBundle",
        "schema_version": "2.0",
        "record_id": "ng-ch05-overnight-delivery-bundle-r2",
        "state": "ENGINEERING_HANDOFF_READY_OWNER_DECISIONS_PENDING",
        "medium": "comic",
        "supersedes": binding(ROOT / PATHS["r1"]),
        "source_lineage": {
            "start_commit": START_COMMIT,
            "base_commit": head,
            "origin_main_at_compile": origin,
            "base_remote_parity": head == origin,
            "commit_count": len(commits),
            "changed_path_count": len(changed),
        },
        "inputs": [binding(ROOT / p) for p in PATHS.values()],
        "key_links": key_links,
        "measured_art": {
            "candidates": 29,
            "ch05_candidates": 26,
            "noncanon_concepts": 3,
            "distinct_ch05_plans": 14,
            "generated_sequences": 3,
            "selected_candidates": 14,
            "engineering_pass_warn_fail": {"pass": 17, "warn": 3, "fail": 6},
            "observed_seconds": render["summary"]["total_elapsed_seconds"],
            "reference_uses": render["summary"]["input_reference_uses"],
            "dimension_sets": [list(x) for x in dimensions],
            "strongest_candidates": [
                {"path": x["path"], "absolute_path": x["absolute_path"], "sha256": x["sha256"]}
                for x in strongest
            ],
            "accepted": 0,
            "commercially_cleared": 0,
        },
        "ranked_engineering_recommendations": route["role_allocation"],
        "recommended_route": route["recommended_route"],
        "chapter_pipeline": {
            "comic_panel_plans": 50,
            "sequence_batches": 12,
            "review_artifacts_planned": lifecycle["summary"]["planned_review_artifacts"],
            "batches_entered": lifecycle["summary"]["batches_entered"],
            "batches_not_entered": lifecycle["summary"]["batches_not_entered"],
            "lifecycle_states": release["effective_state"]["lifecycle_states"],
            "legal_transitions": release["effective_state"]["lifecycle_legal_edges"],
            "illegal_transition_pairs": release["effective_state"]["lifecycle_illegal_pairs"],
            "pilot_prompt_blueprints": release["effective_state"]["prompt_blueprint_rows"],
            "production_prompts": release["effective_state"]["production_prompts"],
            "prerender_artifacts_planned": release["effective_state"]["prerender_artifacts_planned"],
            "prerender_artifacts_built": release["effective_state"]["prerender_artifacts_built"],
            "review_links": links["effective_unique_artifact_count"],
            "integrated_checks": release["summary"]["effective_command_count"],
            "operating_steps": playbook["summary"]["steps"],
            "shell_validation_commands": playbook["summary"]["shell_commands"],
        },
        "capacity": {
            "remaining_planning_candidates": capacity["remaining_plan_envelope"]["planning_candidates"],
            "remaining_p10_seconds": round(capacity["observed_basis"]["p10_seconds"] * 49, 3),
            "remaining_median_seconds": round(capacity["observed_basis"]["median_seconds"] * 49, 3),
            "remaining_p90_seconds": round(capacity["observed_basis"]["p90_seconds"] * 49, 3),
            "fresh_arm_candidates": capacity["fresh_chapter_consistency_arm"]["planning_candidates"],
            "fresh_arm_median_seconds": round(capacity["observed_basis"]["median_seconds"] * 68, 3),
            "forecast": False,
        },
        "owner_frontier": {
            "required_root_decisions": unlock["required_decision_count"],
            "resolved_root_decisions": unlock["resolved_required_decisions"],
            "route_decisions": decisions["decision_count"],
            "candidate_reviews": len(unlock["existing_candidate_reviews"]),
            "rows": decisions["decisions"],
        },
        "limitations": limitations,
        "integrity": {
            "frozen_paths": frozen["summary"]["frozen_paths_compared"],
            "frozen_changed": frozen["summary"]["frozen_paths_changed"],
            "baseline_paths": frozen["summary"]["baseline_tracked_paths_compared"],
            "baseline_changed": frozen["summary"]["baseline_tracked_paths_changed"],
            "baseline_generations": frozen["summary"]["baseline_generations"],
            "baseline_accepted": frozen["summary"]["baseline_accepted_outputs"],
            "safe_source_capture_paths": load("safe_source")["summary"]["tracked_paths"],
            "zero_cost_milestones": cost["revision_summary"]["total_local_milestones"],
        },
        "activity": {
            "paid_api_calls": 0,
            "external_uploads": 0,
            "cloud_gpu_uses": 0,
            "purchases": 0,
            "paid_spend_usd": 0,
            "built_in_monetary_cost_usd": None,
            "human_review_minutes": None,
            "owner_decisions": 0,
            "accepted_candidates": 0,
            "commercially_cleared_candidates": 0,
            "executable_panels": 0,
            "comic_panel_plan_revisions": 0,
        },
        "animation_shot_plan": None,
        "e_conte": None,
        "boundary": "Append-only engineering handoff. No candidate, route, right, prompt, or production panel is promoted by this record.",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(bundle, indent=2) + "\n", encoding="utf-8", newline="\n")
    changed_lines = [
        "# CH05 changed files through operating playbook r1",
        "",
        f"Commit range: `{START_COMMIT}^..{head}`. This immutable inventory ends at the pushed playbook base; r2 bundle files follow it.",
        "",
        *[f"- `{p}`" for p in changed],
    ]
    CHANGED.write_text("\n".join(changed_lines) + "\n", encoding="utf-8", newline="\n")
    summary = [
        "# CH05 overnight delivery summary r2",
        "",
        f"Review hub: [owner hub r5]({HUB.resolve().as_posix()})",
        f"Exhaustive 112-link inventory: [review links r3]({LINK_DOC.resolve().as_posix()})",
        f"Six-root unlock checklist: [owner unlock r1]({UNLOCK_DOC.resolve().as_posix()})",
        f"Duration/capacity map: [capacity map r1]({CAPACITY_CHART.resolve().as_posix()})",
        f"Operating playbook: [playbook r1]({PLAYBOOK_DOC.resolve().as_posix()})",
        "",
        "## Measured result",
        "",
        "- 29 candidates: 26 CH05 + 3 non-canon concepts; 14 distinct plans; 17 pass, 3 warn, 6 fail across CH05 engineering review.",
        "- 1,385.036 observed seconds, 39 authorized reference uses, $0 paid API/cloud spend; built-in monetary cost unavailable.",
        "- 50 ComicPanelPlans form 12 coherent 3–5-panel batches; 112 exact review links; 58 integrated checks.",
        "- Remaining-plan envelope: 49 candidates, median 2,510.123 seconds; fresh consistency arm: 68 candidates, median 3,483.436 seconds.",
        "",
        "## Ranked engineering route",
        "",
        *[f"{r['priority']}. `{r['mechanism']}` — {', '.join(r['roles'])}. {r['evidence']}" for r in route["role_allocation"]],
        "",
        f"Recommended hybrid: {route['recommended_route']}. This remains an engineering recommendation, not owner acceptance.",
        "",
        "## Exact owner frontier",
        "",
        "Six pilot roots remain unresolved; the ten route/candidate/rights questions remain un-ingested.",
        *[f"- `{row['decision_id']}` — {row['question']}" for row in decisions["decisions"]],
        "",
        "## Limitations",
        "",
        *[f"- {item}" for item in limitations],
    ]
    SUMMARY.write_text("\n".join(summary) + "\n", encoding="utf-8", newline="\n")
    evidence = {
        "record_type": "ComicOvernightDeliveryBundleEvidence",
        "schema_version": "2.0",
        "record_id": "ng-ch05-overnight-delivery-bundle-evidence-r2",
        "state": "PASS_OWNER_PENDING",
        "bundle": binding(OUTPUT),
        "summary_document": binding(SUMMARY),
        "changed_files_document": binding(CHANGED),
        "inputs": bundle["inputs"],
        "summary": {
            "candidates": 29, "ch05_candidates": 26, "noncanon_concepts": 3,
            "distinct_ch05_plans": 14, "selected": 14, "chapter_plans": 50,
            "sequence_batches": 12, "review_links": 112, "strongest_candidates": 14,
            "remaining_decisions": 10, "required_root_decisions": 6, "resolved_root_decisions": 0,
            "integrated_checks": 58, "operating_steps": 12, "planning_candidates": 49,
            "fresh_arm_candidates": 68, "observed_seconds": 1385.036, "reference_uses": 39,
            "paid_spend_usd": 0, "owner_decisions": 0, "accepted_candidates": 0,
            "executable_panels": 0, "human_review_minutes": None,
        },
        "base_remote_parity": head == origin,
        "animation_shot_plan": None,
        "e_conte": None,
    }
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8", newline="\n")
    print("CH05 delivery r2: 29 candidates/50 plans/12 batches/112 links/14 strongest/10 decisions/58 checks")
    print(f"base parity {head == origin}; activity calls/uploads/spend/accepted/executable 0/0/$0/0/0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
