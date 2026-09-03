"""Compile the CH05 chapter-scale production decision matrix from tracked evidence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
HANDOFF = ROOT / "docs/research/ch05-complete-chapter-review-handoff-r7.md"
SIX_ROUTE = ROOT / "docs/research/evidence/ch05-six-route-comparison-r1.json"
CADENCE_TRIAGE = (
    ROOT / "docs/research/evidence/ch05-sequence-cadence-review-triage-r1.json"
)
ADRS = [
    ROOT / "docs/adr/ADR-0188-use-measured-sequence-level-cadence.md",
    ROOT
    / "docs/adr/ADR-0189-treat-paired-reference-ablations-as-directional-evidence.md",
    ROOT / "docs/adr/ADR-0190-treat-p005-p006-as-a-finish-continuity-risk.md",
    ROOT / "docs/adr/ADR-0191-do-not-rerender-p005-p006-from-nonisolating-proxies.md",
]
JSON_OUT = (
    ROOT
    / "docs/research/evidence/ch05-chapter-scale-production-decision-matrix-r1.json"
)
MARKDOWN_OUT = (
    ROOT / "docs/research/ch05-chapter-scale-production-decision-matrix-r1.md"
)

ROUTE_LABELS = {
    "r6": "R6",
    "alt_graphic": "Alternate graphic",
    "clear_line_watercolor": "Clear-line watercolor",
    "premium_cel": "Premium cel",
    "flat_graphic_gouache": "Flat graphic-gouache",
    "reduced_palette_text_control": "Reduced-palette text control",
}
RANKING = (
    (1, "r6", "chapter backbone"),
    (2, "premium_cel", "late-block cadence specialist"),
    (3, "clear_line_watercolor", "strongest unselected single-route fallback"),
    (
        4,
        "reduced_palette_text_control",
        "opening-block and lower-density specialist with finish constraints",
    ),
    (5, "alt_graphic", "comparison route; not current production lead"),
    (6, "flat_graphic_gouache", "diagnostic style arm; not current production lead"),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def counts_text(counts: dict[str, int]) -> str:
    base = f"{counts.get('pass', 0)}/{counts.get('warn', 0)}/{counts.get('fail', 0)}"
    return (
        base
        if not counts.get("not_assessed")
        else f"{base} (+{counts['not_assessed']} not assessed)"
    )


def build_documents() -> tuple[dict[str, Any], str]:
    six = json.loads(SIX_ROUTE.read_text(encoding="utf-8"))
    cadence = json.loads(CADENCE_TRIAGE.read_text(encoding="utf-8"))
    evaluation = six["evaluation_counts"]
    complexity = six["visual_complexity"]["aggregate_equal_panel_weight"]
    sequence_rows = six["sequence_cadence_recommendation"]["sequences"]
    selected = {route: {"sequences": [], "panels": 0} for route in ROUTE_LABELS}
    for row in sequence_rows:
        route = row["selected_route"]
        selected[route]["sequences"].append(row["sequence_id"])
        selected[route]["panels"] += row["panel_count"]

    route_rows: list[dict[str, Any]] = []
    for route, label in ROUTE_LABELS.items():
        route_rows.append(
            {
                "route": route,
                "label": label,
                "semantic_pass_warn_fail": evaluation[route]["semantic"],
                "overall_pass_warn_fail": evaluation[route]["overall"],
                "continuity_identity_hair_wardrobe_pass_warn_fail_not_assessed": evaluation[
                    route
                ]["identity_hair_wardrobe"],
                "continuity_scope_limitation": "Identity/hair/wardrobe is the only standardized route-wide continuity-adjacent count in this comparison; it is not biometric identity and does not measure finish continuity.",
                "lettering_pass_warn_fail_not_assessed": evaluation[route]["lettering"],
                "style_density_pass_warn_fail_not_assessed": evaluation[route][
                    "style_density"
                ],
                "complexity_proxies_non_quality": complexity[route],
                "cadence_selected_sequence_ids": selected[route]["sequences"],
                "cadence_selected_sequence_count": len(selected[route]["sequences"]),
                "cadence_selected_panel_count": selected[route]["panels"],
            }
        )

    basis_by_route = {
        "r6": "Largest selected share (S02-S08, 34 panels); highest semantic PASS count; 50/50 lettering and continuity-adjacent identity checks. Two supplemental semantic failures prevent wholesale promotion.",
        "premium_cel": "Selected for S09-S11 (11 panels) with zero selected semantic failures; wholesale route still has 5 semantic failures, so this is a block-specific inference.",
        "clear_line_watercolor": "Best unselected wholesale semantic/overall profile after R6 (45/2/3) with 50/50 lettering and identity checks, but selected for no cadence block by the frozen objective.",
        "reduced_palette_text_control": "Selected only for S01 and is the only material lower-density separator; wholesale 38 overall failures, 27 lettering failures, and 31 style-density failures limit chapter-scale readiness.",
        "alt_graphic": "50/50 lettering and identity checks, but 7 semantic and 7 overall failures and no selected cadence block.",
        "flat_graphic_gouache": "Semantic 41/6/3 is outweighed for production review by 27 overall failures, 25 lettering failures, and 50 style-density failures; no selected cadence block.",
    }
    rankings = [
        {
            "rank": rank,
            "route": route,
            "label": ROUTE_LABELS[route],
            "inferred_role": role,
            "basis": basis_by_route[route],
            "not_a_quality_score": True,
        }
        for rank, route, role in RANKING
    ]
    inputs = [HANDOFF, SIX_ROUTE, CADENCE_TRIAGE, *ADRS]
    document: dict[str, Any] = {
        "record_type": "CH05ChapterScaleProductionDecisionMatrix",
        "schema_version": "1.0",
        "record_id": "ng-ch05-chapter-scale-production-decision-matrix-r1",
        "state": "EVIDENCE_SYNTHESIS_PENDING_OWNER_REVIEW",
        "medium": "comic",
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "inputs": [
            {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path)}
            for path in inputs
        ],
        "measured_fact": {
            "route_matrix": route_rows,
            "selected_review_cadence": {
                "assignment": {
                    "S01": "reduced_palette_text_control",
                    "S02-S08": "r6",
                    "S09-S11": "premium_cel",
                },
                "panels_by_route": {
                    "reduced_palette_text_control": 5,
                    "r6": 34,
                    "premium_cel": 11,
                },
                "semantic_pass_warn_fail": {
                    "pass": cadence["summary"]["pass"],
                    "warn": cadence["summary"]["warn"],
                    "fail": cadence["summary"]["fail"],
                },
                "warning_panel_ids": cadence["summary"]["warning_panels"],
                "route_transitions": cadence["summary"]["route_transitions"],
                "human_reviewed": cadence["summary"]["human_reviewed"],
                "accepted": cadence["summary"]["accepted"],
            },
            "finish_continuity": {
                "P005_to_P006": "Manual visual risk remains, but the matched three-arm proxy control isolated route-switch contribution on 0/2 histogram proxies; ADR-0191 prohibits rerendering from that non-isolating evidence.",
                "P039_to_P040": "Lower observed risk than P005-to-P006 in the boundary audit; no intervention is supported by current evidence.",
            },
            "accounting": {
                "direct_paid_api_cloud_usd": 0.0,
                "human_reviewed_candidates": 0,
                "accepted_candidates": 0,
                "rights_cleared_candidates": 0,
                "exact_production_bases": 0,
            },
        },
        "engineering_inference": {
            "ranking_scope": "Readiness for the next CH05 chapter-scale review workflow, not artistic merit, commercial clearance, or final production-base selection.",
            "ranking_policy": "Prioritize demonstrated cadence contribution and semantic failure avoidance, then lettering/overall burden and finish-risk evidence. Treat unassessed style-density fields as unknown, never as PASS. No numeric quality score is invented.",
            "ranked_routes": rankings,
            "cadence_recommendation": "Retain the three-block cadence as the strongest current review mechanism: reduced-palette S01, R6 S02-S08, premium cel S09-S11. Do not promote it to accepted production while owner review remains unrecorded.",
        },
        "owner_review_question": [
            "Does the assembled three-block cadence read as one coherent chapter at phone size, especially the two route boundaries?",
            "Is the visually abrupt P005-to-P006 cut acceptable as intentional beat contrast despite the route-switch proxy test being non-isolating?",
            "Are the three retained warnings acceptable or revision-worthy: P003 track overlap, P032 heel/toe direction, and P045 extra uphill building?",
            "Does provisional lettering preserve faces, hands, silhouettes, story objects, and phone readability across the full scroll?",
        ],
        "future_noncanon_litrpg_exploration": {
            "status": "IDEATION_ONLY_NONCANON_NOT_AUTHORIZED_FOR_GENERATION_OR_PRODUCTION",
            "separation_rule": "Do not merge these ideas into CH05 ComicPanelPlans, canon, provider requests, or production selection without a later explicit revision and provenance review.",
            "ideas": [
                "Fictional-adult practical armor and upgraded clothing silhouettes that preserve role and hair readability.",
                "Weapons/tools designed around causal grip, leverage, carry continuity, and readable action rather than decorative posing.",
                "Monster/ecology encounter beats and restrained LitRPG system feedback that create tactical story consequences instead of generic spectacle.",
            ],
        },
        "next_high_information_experiment": {
            "count": 1,
            "experiment_id": "ch05-cadence-objective-sensitivity-audit-r1",
            "scope": "Use only the existing six-route per-panel evaluation table. Re-run the 11-sequence cadence optimizer under leave-one-secondary-objective-out variants while preserving hard zero semantic/identity-failure constraints; report whether the current three-block assignment remains invariant or expose the Pareto alternatives.",
            "why": "This tests whether the recommended cadence is robust evidence or an artifact of lexicographic tie-breaking before more art or repair effort is spent.",
            "new_provider_needed": False,
            "new_upload_needed": False,
            "new_pixels_needed": False,
            "paid_spend_usd": 0.0,
        },
        "disposition": {
            "owner_acceptance": None,
            "rights_clearance": None,
            "commercially_cleared": None,
            "canon_change": None,
            "exact_production_base": None,
        },
        "limitations": [
            "All visual and semantic reviews remain non-gating agent evidence; human review is recorded as zero.",
            "Route-wide continuity is not directly measured beyond identity/hair/wardrobe checks and issue-specific audits.",
            "Entropy, edge density, and PNG bytes per pixel are non-quality proxies sensitive to content, crop, resize, and codec.",
            "The rank is an explicit engineering inference over current evidence, not a measured scalar score.",
        ],
        "boundary": "Decision aid only; no art acceptance, route promotion, rights or commercial clearance, canon replacement, provider authority, or exact production-base selection.",
    }

    lines = [
        "# CH05 chapter-scale production decision matrix r1",
        "",
        "This is a review decision aid, not art acceptance, commercial clearance, canon replacement, or an exact production-base selection. The active structure remains ComicPanelPlan; AnimationShotPlan and E-Conte remain null.",
        "",
        "## Measured facts",
        "",
        "| Engineering rank* | Route | Semantics P/W/F | Overall P/W/F | Continuity-adjacent identity P/W/F | Lettering P/W/F | Style-density P/W/F | Cadence use |",
        "| ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    rank_map = {route: rank for rank, route, _ in RANKING}
    for row in sorted(route_rows, key=lambda value: rank_map[value["route"]]):
        sequence_text = (
            ", ".join(row["cadence_selected_sequence_ids"])
            if row["cadence_selected_sequence_ids"]
            else "none"
        )
        lines.append(
            f"| {rank_map[row['route']]} | {row['label']} | {counts_text(row['semantic_pass_warn_fail'])} | {counts_text(row['overall_pass_warn_fail'])} | {counts_text(row['continuity_identity_hair_wardrobe_pass_warn_fail_not_assessed'])} | {counts_text(row['lettering_pass_warn_fail_not_assessed'])} | {counts_text(row['style_density_pass_warn_fail_not_assessed'])} | {row['cadence_selected_panel_count']} panels: {sequence_text} |"
        )
    lines.extend(
        [
            "",
            "*The rank is an engineering inference for the next chapter-scale review workflow, not a measured quality score. Style-density was not assessed for R6, alternate graphic, clear-line watercolor, or premium cel; unknown is not PASS. The continuity column is limited to identity/hair/wardrobe checks and does not establish finish continuity.",
            "",
            "The selected review cadence is reduced-palette S01 (5 panels), R6 S02-S08 (34), and premium cel S09-S11 (11): 47 PASS / 3 WARN / 0 FAIL with two route transitions. Warnings remain at P003, P032, and P045. Human-reviewed and accepted counts remain zero.",
            "",
            "P005-to-P006 remains a visual owner-review risk, but its matched three-arm attribution control supported a route-switch contribution on 0/2 histogram proxies. P039-to-P040 remains the lower observed boundary risk. Neither result grades art or supports a rerender.",
            "",
            "## Engineering inference",
            "",
        ]
    )
    for row in rankings:
        lines.append(
            f"{row['rank']}. **{row['label']} — {row['inferred_role']}.** {row['basis']}"
        )
    lines.extend(
        [
            "",
            "Recommendation: retain the three-block cadence for owner review without promoting it to accepted production.",
            "",
            "## Owner-review questions",
            "",
        ]
    )
    for question in document["owner_review_question"]:
        lines.append(f"- {question}")
    lines.extend(
        [
            "",
            "## Future noncanon LitRPG exploration",
            "",
            "These are ideation only and are not authorized for generation, canon, or production:",
            "",
        ]
    )
    for idea in document["future_noncanon_litrpg_exploration"]["ideas"]:
        lines.append(f"- {idea}")
    experiment = document["next_high_information_experiment"]
    lines.extend(
        [
            "",
            "## Exactly one next experiment",
            "",
            f"**{experiment['experiment_id']}:** {experiment['scope']}",
            "",
            f"Why: {experiment['why']} It requires no provider, upload, new pixels, or paid spend.",
            "",
            "## Bound inputs",
            "",
        ]
    )
    for item in document["inputs"]:
        lines.append(f"- `{item['path']}` — SHA-256 `{item['sha256']}`")
    lines.extend(
        [
            "",
            "The machine-readable record is `docs/research/evidence/ch05-chapter-scale-production-decision-matrix-r1.json`.",
            "",
        ]
    )
    return document, "\n".join(lines)


def main() -> int:
    document, markdown = build_documents()
    JSON_OUT.parent.mkdir(parents=True, exist_ok=True)
    JSON_OUT.write_text(
        json.dumps(document, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN_OUT.write_text(markdown, encoding="utf-8", newline="\n")
    print(
        json.dumps(
            {
                "json": JSON_OUT.relative_to(ROOT).as_posix(),
                "json_sha256": sha256(JSON_OUT),
                "markdown": MARKDOWN_OUT.relative_to(ROOT).as_posix(),
                "markdown_sha256": sha256(MARKDOWN_OUT),
                "ranked_routes": [
                    row["route"]
                    for row in document["engineering_inference"]["ranked_routes"]
                ],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
