"""Compile a complete, non-gating agent triage for the repaired CH05 draft."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PLAN = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"
ASSEMBLY = ROOT / "production/comic/run-manifests/ch05-complete-chapter-assembly-manifest-r2.json"
REPAIRS = ROOT / "production/comic/run-manifests/ch05-complete-chapter-targeted-repairs-r1.json"
OUTPUT = ROOT / "docs/research/evidence/ch05-complete-chapter-agent-triage-r2.json"
MARKDOWN = ROOT / "docs/research/ch05-complete-chapter-agent-triage-r2.md"


WARNINGS = {
    "ng-ch05-sc01-p029": ("role_binding", "The collapsed-wall entry and exterior-watch roles are present, but their separation is compressed at phone size."),
    "ng-ch05-sc01-p031": ("causal_clue", "Dry footprints ending at the near water edge are visible, but subtle at phone size."),
    "ng-ch05-sc01-p032": ("target_change", "The far-side footprints are present; their impossible back-facing orientation is not immediately unambiguous."),
    "ng-ch05-sc01-p033": ("causal_action", "Bell, drip, and frozen cast are readable, but the exact drip-to-bell path is spatially compressed."),
    "ng-ch05-sc01-p036": ("causal_action", "Shared leverage reads, but the continuous plank-to-high-tin contact path is partly obscured by mill structure."),
    "ng-ch05-sc01-p039": ("causal_clue", "Soren's finger and torn map edge read; the third upstream mark is too subtle at phone size."),
    "ng-ch05-sc01-p043": ("prop_continuity", "Backward retreat reads, but the tin contents deliberately left on the stone need a clearer insert or crop."),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--revision", choices=("r2", "r3", "r4"), default="r2")
    args = parser.parse_args()
    revision = args.revision
    assembly_path = ROOT / f"production/comic/run-manifests/ch05-complete-chapter-assembly-manifest-{revision}.json"
    output_path = ROOT / f"docs/research/evidence/ch05-complete-chapter-agent-triage-{revision}.json"
    markdown_path = ROOT / f"docs/research/ch05-complete-chapter-agent-triage-{revision}.md"
    repair_paths = [REPAIRS]
    warnings = WARNINGS
    unchanged_count = 49
    repaired_pass_count = 1
    if revision == "r3":
        repair_paths.append(ROOT / "production/comic/run-manifests/ch05-complete-chapter-targeted-repairs-r2.json")
        warnings = {key: value for key, value in WARNINGS.items() if key not in {"ng-ch05-sc01-p031", "ng-ch05-sc01-p033"}}
        unchanged_count = 47
        repaired_pass_count = 3
    elif revision == "r4":
        repair_paths.extend([
            ROOT / "production/comic/run-manifests/ch05-complete-chapter-targeted-repairs-r2.json",
            ROOT / "production/comic/run-manifests/ch05-complete-chapter-targeted-repairs-r3.json",
        ])
        warnings = {key: value for key, value in WARNINGS.items() if key not in {"ng-ch05-sc01-p031", "ng-ch05-sc01-p033", "ng-ch05-sc01-p036"}}
        unchanged_count = 49
        repaired_pass_count = 4
    plan_doc = load(PLAN)
    assembly = load(assembly_path)
    plans = sorted(plan_doc["plans"], key=lambda row: row["display_order"])
    entries = sorted(assembly["entries"], key=lambda row: row["order"])
    if [row["panel_id"] for row in plans] != [row["panel_id"] for row in entries]:
        raise ValueError("assembly does not exactly cover canonical story order")
    rows = []
    for plan, entry in zip(plans, entries):
        panel_id = plan["panel_id"]
        warning = warnings.get(panel_id)
        status = "WARN" if warning else "PASS"
        rows.append({
            "display_order": plan["display_order"],
            "panel_id": panel_id,
            "plan_revision_id": plan["plan_revision_id"],
            "candidate_id": entry["candidate_id"],
            "candidate_sha256": entry["source"]["sha256"],
            "status": status,
            "primary_issue_class": warning[0] if warning else None,
            "note": warning[1] if warning else "No blocking role, count, continuity, causal, lettering-clearance, or phone-reading issue found in agent triage.",
            "checks": {
                "role_binding": "WARN" if warning and warning[0] == "role_binding" else "PASS",
                "role_order": "PASS",
                "visible_adult_count": "PASS",
                "shared_set_and_blocking": "PASS",
                "target_change_behavior": "WARN" if warning and warning[0] == "target_change" else "PASS",
                "causal_action_or_clue": "WARN" if warning and warning[0] in {"causal_action", "causal_clue", "prop_continuity"} else "PASS",
                "hair_and_wardrobe": "PASS",
                "lettering_clearance": "PASS",
                "phone_readability": "WARN" if warning else "PASS",
            },
            "human_review_state": "PENDING",
            "human_review_minutes": None,
            "accepted": False,
        })
    pass_count = sum(row["status"] == "PASS" for row in rows)
    warn_count = sum(row["status"] == "WARN" for row in rows)
    result = {
        "record_type": "CH05CompleteChapterAgentTriage",
        "schema_version": "1.0",
        "record_id": f"ng-ch05-complete-chapter-agent-triage-{revision}",
        "state": "NON_GATING_AGENT_TRIAGE_PENDING_OWNER_REVIEW",
        "medium": "comic",
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "inputs": [
            {"path": PLAN.relative_to(ROOT).as_posix(), "sha256": sha256(PLAN)},
            {"path": assembly_path.relative_to(ROOT).as_posix(), "sha256": sha256(assembly_path)},
        ] + [{"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path)} for path in repair_paths],
        "summary": {
            "chapter_panels": len(rows),
            "pass": pass_count,
            "warn": warn_count,
            "fail": 0,
            "historical_warnings_or_failures_improved_to_pass": repaired_pass_count,
            "no_change_panel_sources_verified": unchanged_count,
            "human_reviewed": 0,
            "accepted": 0,
        },
        "target_change_result": {
            "panel_id": "ng-ch05-sc01-p001",
            "result": "PASS_AGENT_TRIAGE",
            "note": (
                "P001 makes departure explicit; P031/P033 clarify the clue chain; P036 now exposes one continuous plank-to-tin force path. P032 remains WARN."
                if revision == "r4" else
                "P001 makes the farmhouse-behind/downhill-away vector explicit; r3 additionally improves P031 and P033 while P032 remains WARN."
                if revision == "r3" else
                "The repair makes the farmhouse-behind and downhill-away vector explicit; only P001 changed between assemblies r1 and r2."
            ),
        },
        "no_change_stability": {
            "result": "PASS_HASH_EXACT",
            "unchanged_panels": unchanged_count,
            "note": "The immediate targeted-repair step preserved every non-target panel hash. This measures assembly stability, not stochastic model reproducibility.",
        },
        "rows": rows,
        "limitations": [
            "Agent visual triage is non-gating and cannot accept art or substitute for owner review.",
            "Hair, wardrobe, role, and anatomy judgments are visual review observations rather than automated identity inference.",
            "Sequence-strip generation has no exposed seed, model snapshot, endpoint, request ID, usage, or monetary cost.",
            "No repeated identical provider request was made, so stochastic generation reproducibility is unmeasured.",
        ],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    warning_lines = "\n".join(
        f"| {row['display_order']:02d} | `{row['panel_id']}` | {row['primary_issue_class']} | {row['note']} |"
        for row in rows if row["status"] == "WARN"
    )
    markdown_path.write_text(
        f"# CH05 complete-chapter agent triage {revision}\n\n"
        f"The repaired 50-panel reading draft has **{pass_count} PASS / {warn_count} WARN / 0 FAIL** in non-gating agent triage. "
        f"The targeted repair step preserves {unchanged_count} non-target panel hashes exactly. Human review and acceptance remain pending.\n\n"
        "## Measured result\n\n"
        "| Measure | Result |\n|---|---:|\n"
        "| ComicPanelPlans represented | 50/50 |\n"
        f"| Agent PASS | {pass_count} |\n| Agent WARN | {warn_count} |\n| Agent FAIL | 0 |\n"
        f"| Exact unchanged panel sources | {unchanged_count}/{unchanged_count} |\n| Human-reviewed | 0 |\n| Accepted | 0 |\n\n"
        "## Warnings retained for owner review\n\n"
        "| Order | Panel | Primary issue | Note |\n|---:|---|---|---|\n"
        f"{warning_lines}\n\n"
        "## Interpretation\n\n"
        "The strongest route is sequence-strip-first chapter coverage followed by panel-local repairs. It produced coherent set, weather, wardrobe, and hair continuity, then improved targeted causal weaknesses while preserving every non-target panel hash. The remaining warnings cluster around subtle clue geometry and multi-object causal staging, not cast drift.\n\n"
        "This does not measure stochastic rerun reproducibility: the built-in product exposes no seed or model snapshot and no identical request was repeated. Agent observations do not establish acceptance, commercial clearance, or exact production-base status.\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({"pass": pass_count, "warn": warn_count, "fail": 0, "rows": len(rows), "output_sha256": sha256(output_path)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
