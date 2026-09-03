"""Compile non-gating panel and cross-panel triage for CH05 alternate graphic r1."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PLAN = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"
ASSEMBLY = ROOT / "production/comic/run-manifests/ch05-complete-chapter-alt-graphic-assembly-r1.json"
EXECUTION = ROOT / "production/comic/run-manifests/ch05-complete-chapter-alt-graphic-execution-manifest-r1.json"
OUTPUT = ROOT / "docs/research/evidence/ch05-complete-chapter-alt-graphic-agent-triage-r1.json"
MARKDOWN = ROOT / "docs/research/ch05-complete-chapter-alt-graphic-agent-triage-r1.md"

ISSUES: dict[int, tuple[str, str, str]] = {
    1: ("FAIL", "departure_geography_and_reversal", "Travel reads uphill toward the farmhouse area and the farmhouse-behind/downhill-away relation is absent; opening smoke also risks preempting P048/P049."),
    3: ("WARN", "causal_clue", "Fresh track overlap exists but the overlap relation is marginal at phone size."),
    8: ("WARN", "map_fold_state", "Map handling reads, but hiding the farmhouse section while exposing the creek line is not explicit."),
    12: ("WARN", "twine_direction", "Taut twine reads, but the downhill direction lacks enough terrain context."),
    22: ("WARN", "stop_gap_action", "Sigrid's stop gap reads, but the staging approaches a shared reach rather than a clean one-hand stop."),
    29: ("FAIL", "role_binding", "At the collapsed-wall entry Soren's gaze follows Sigrid instead of independently watching the exterior."),
    30: ("WARN", "clue_order", "Footprint-like marks leak into the establishing panel before their formal discovery."),
    32: ("FAIL", "footprint_orientation", "Prints appear to traverse the water and do not expose a readable heel/toe orientation pointing back toward Soren."),
    36: ("FAIL", "force_path", "The cooperative leverage action is energetic, but the high tin/contact endpoint is not visible in the same panel, breaking single-panel causality."),
    39: ("FAIL", "third_mark", "The torn-edge comparison reads, but the distinct third upstream mark is absent or too ambiguous."),
    41: ("FAIL", "drum_extinguish_state", "The drum retains a visible ember/plume after the plan requires it to finally go out."),
    43: ("FAIL", "map_possession_continuity", "The retreat leaves tin contents and map-like paper behind, conflicting with P046 where the map is carried."),
    45: ("WARN", "farmhouse_geography", "An extra hillside structure can be mistaken for the farmhouse and weakens return geography."),
    46: ("WARN", "map_possession_continuity", "The carried map reads in isolation but exposes the P043 possession discontinuity."),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    plans = sorted(json.loads(PLAN.read_text(encoding="utf-8"))["plans"], key=lambda row: row["display_order"])
    assembly = json.loads(ASSEMBLY.read_text(encoding="utf-8"))
    entries = sorted(assembly["entries"], key=lambda row: row["order"])
    if [row["panel_id"] for row in plans] != [row["panel_id"] for row in entries]:
        raise ValueError("assembly differs from canonical ComicPanelPlan order")
    rows: list[dict[str, Any]] = []
    for plan, entry in zip(plans, entries, strict=True):
        order = plan["display_order"]
        status, issue, note = ISSUES.get(order, ("PASS", "", "No blocking panel-local or cross-panel issue found in non-gating agent triage."))
        check_value = "FAIL" if status == "FAIL" else "WARN"
        checks = {key: "PASS" for key in ("role_binding", "role_order", "visible_adult_count", "shared_set_and_blocking", "target_change_behavior", "causal_action_or_clue", "hair_and_wardrobe", "lettering_clearance", "phone_readability", "cross_panel_canon")}
        target_key = "role_binding" if issue == "role_binding" else "cross_panel_canon" if issue in {"departure_geography_and_reversal", "clue_order", "map_possession_continuity", "farmhouse_geography"} else "causal_action_or_clue"
        if status != "PASS":
            checks[target_key] = check_value
            checks["phone_readability"] = check_value if issue in {"causal_clue", "map_fold_state", "twine_direction", "third_mark", "footprint_orientation"} else checks["phone_readability"]
        rows.append({
            "display_order": order,
            "panel_id": plan["panel_id"],
            "plan_revision_id": plan["plan_revision_id"],
            "candidate_id": entry["candidate_id"],
            "candidate_sha256": entry["source"]["sha256"],
            "status": status,
            "primary_issue_class": issue or None,
            "note": note,
            "checks": checks,
            "human_review_state": "PENDING",
            "human_review_minutes": None,
            "accepted": False,
            "commercially_cleared": False,
            "exact_production_base": False,
        })
    counts = {status: sum(row["status"] == status for row in rows) for status in ("PASS", "WARN", "FAIL")}
    result = {
        "record_type": "CH05CompleteChapterAgentTriage",
        "schema_version": "1.0",
        "record_id": "ng-ch05-complete-chapter-alt-graphic-agent-triage-r1",
        "display_title": "CH05 ALT GRAPHIC R1 - AGENT TRIAGE",
        "state": "NON_GATING_AGENT_TRIAGE_PENDING_OWNER_REVIEW",
        "medium": "comic",
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "inputs": [{"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path)} for path in (PLAN, ASSEMBLY, EXECUTION)],
        "summary": {"chapter_panels": 50, "pass": counts["PASS"], "warn": counts["WARN"], "fail": counts["FAIL"], "hair_and_wardrobe_pass": 50, "human_reviewed": 0, "accepted": 0},
        "style_hypothesis_result": {"result": "NON_SEPARATING", "note": "The requested lower-density route remains texture-heavy and painterly in terrain, cloth, and hatching; it does not establish a density advantage over r6."},
        "cross_panel_findings": [
            {"gate": "opening_chimney_smoke_false_until_p048", "result": "FAIL", "affected_panels": ["ng-ch05-sc01-p001", "ng-ch05-sc01-p048", "ng-ch05-sc01-p049"]},
            {"gate": "map_possession_p037_p043_p046", "result": "FAIL", "affected_panels": ["ng-ch05-sc01-p037", "ng-ch05-sc01-p043", "ng-ch05-sc01-p046"]},
            {"gate": "drum_extinguished_at_p041", "result": "FAIL", "affected_panels": ["ng-ch05-sc01-p041"]},
            {"gate": "hair_and_wardrobe_contract", "result": "PASS", "affected_panels": [row["panel_id"] for row in rows]},
        ],
        "recommendation": "Retain r6 as the stronger engineering base; use alternate P002/P004/P006/P010/P017/P019/P020/P023/P028/P033/P037/P038/P040/P042/P044/P047/P048/P049/P050 as style/story evidence, not wholesale replacements. Repair cross-panel canon deterministically before any further stochastic render.",
        "rows": rows,
        "limitations": ["Agent triage is non-gating and cannot accept art.", "Hair, wardrobe, action, and canon judgments are visual observations.", "The built-in product exposes no seed, model, endpoint, request ID, usage, or monetary cost.", "No identical request was repeated; stochastic reproducibility remains unmeasured."],
        "boundary": "No acceptance, commercial clearance, or exact production-base decision is created.",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    issue_rows = "\n".join(f"| {row['display_order']:02d} | `{row['panel_id']}` | {row['status']} | {row['primary_issue_class']} | {row['note']} |" for row in rows if row["status"] != "PASS")
    MARKDOWN.write_text(
        "# CH05 alternate graphic r1 agent triage\n\n"
        f"The complete 50-panel alternate draft measures **{counts['PASS']} PASS / {counts['WARN']} WARN / {counts['FAIL']} FAIL** in non-gating agent triage. Hair and wardrobe remain stable across all 50 crops; the requested lower-density hypothesis is non-separating because the output remains texture-heavy.\n\n"
        "| Order | Panel | Status | Issue | Evidence |\n|---:|---|---|---|---|\n" + issue_rows + "\n\n"
        "Retain r6 as the stronger engineering base. The alternate ending, bridge warning, and several clue inserts are valuable style/story evidence, but P001, P029, P032, P036, P039, P041, and P043 block wholesale promotion. Human review, commercial clearance, acceptance, and exact-base status remain open.\n",
        encoding="utf-8", newline="\n"
    )
    print(json.dumps({**result["summary"], "output": OUTPUT.relative_to(ROOT).as_posix(), "sha256": sha256(OUTPUT)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
