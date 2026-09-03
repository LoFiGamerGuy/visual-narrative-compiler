"""Compile the final CH05 owner-facing start-here page and bound evidence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
MARKDOWN_OUT = ROOT / "docs/research/ch05-final-owner-start-here-r1.md"
JSON_OUT = ROOT / "docs/research/evidence/ch05-final-owner-start-here-r1.json"
GIT_COMMIT = "fa8d1edbb3076ef7c0a7ad8a797abc9a09a5c0ec"
GIT_URL = (
    f"https://github.com/LoFiGamerGuy/visual-narrative-compiler/commit/{GIT_COMMIT}"
)

VISUALS = (
    (
        "assembled_lettered_chapter",
        "Full assembled lettered chapter",
        "experiments/review-packets/ch05-sequence-cadence-review-r1/lettered/ch05-sequence-cadence-lettered-r1.png",
        "d73c1703431c4c5c8181918ea51d3e66f37aa9cefa6ac6aa8c619a2e035b39c8",
        1200,
        26776,
    ),
    (
        "clean_phone_chapter",
        "Clean 390px phone chapter",
        "experiments/review-packets/ch05-sequence-cadence-review-r1/clean/ch05-complete-chapter-phone-390px.png",
        "0ccd4c0d5d8116791421e137e6d3620ec95d041e062595f20160afc6e8bd5f13",
        390,
        8702,
    ),
    (
        "six_routes_all_50",
        "All 50 panels across six routes",
        "experiments/review-packets/ch05-six-route-comparison-r1/ch05-six-route-all-50-contact-sheet.png",
        "733b0b79786b78d4c0bdb4033b3a90da0d08be4d9f8d1703d438636debfd0122",
        2246,
        10312,
    ),
    (
        "six_route_style_density",
        "Six-route style-density comparison",
        "experiments/review-packets/ch05-six-route-comparison-r1/ch05-six-route-style-density-comparison.png",
        "e466d52e7d86bc32094f24ffa97e37c0d3b2225a947b0ef9226ea6170bb68ed7",
        2246,
        3492,
    ),
    (
        "sequence_cadence",
        "Sequence-cadence recommendation",
        "experiments/review-packets/ch05-six-route-comparison-r1/ch05-six-route-sequence-cadence.png",
        "fefe4d5d1a43f415ebe92c681f7c08cb2b573689948970095883296e64666c4f",
        1760,
        2786,
    ),
    (
        "cadence_triage",
        "Cadence triage and exact warning panels",
        "experiments/review-packets/ch05-sequence-cadence-review-r1/review/ch05-sequence-cadence-triage-sheet-r1.png",
        "cbe37fd8aba674f9ac4e493df04168b5b5f5f39662a7f17c885acd92528e968b",
        1604,
        2790,
    ),
    (
        "boundary_continuity",
        "P005/P006 and P039/P040 boundary continuity",
        "experiments/review-packets/ch05-sequence-cadence-review-r1/review/ch05-sequence-cadence-boundary-continuity-sheet-r1.png",
        "32305d7b1d1b23d061fe9f83702ace268cc7afc0f913cf6f9fef36fc9d05730b",
        1200,
        1040,
    ),
    (
        "lettering_safe_zones",
        "All-50 lettering-safe-zone overlay",
        "experiments/review-packets/ch05-sequence-cadence-review-r1/clean/ch05-complete-chapter-contact-sheet-lettering-overlay.png",
        "7e99f7b6b558a56cade8f503ee5f70c613455f1aba157eee39455d3b3a61d123",
        1612,
        4158,
    ),
    (
        "strongest_14",
        "Strongest 14 CH05 candidates in narrative order",
        "experiments/review-packets/ch05-manual-continuity-atlas-r1/ch05-continuity-atlas-selected-14-r1.png",
        "ff379a13f9be5c0100cdaca2de6a6847a4f86024f397fc03293ad2778c2130eb",
        1500,
        8106,
    ),
    (
        "noncanon_litrpg",
        "Noncanon LitRPG armor, weapon, and monster concepts",
        "experiments/review-packets/future-litrpg-visual-concepts-r1/review/contact-sheet-future-litrpg-concepts.png",
        "2f858c7f9a16300b7259fb94bb6e6dd1ce6c23f69804c8e2b08262e0b0c80f9a",
        2260,
        870,
    ),
)

DOCUMENTS = (
    (
        "review_handoff_r7",
        "Complete chapter review handoff r7",
        "docs/research/ch05-complete-chapter-review-handoff-r7.md",
        "739cf2766edf816f24b0296253245d13ad7298cddf1b61286c43af999e065686",
    ),
    (
        "decision_matrix",
        "Chapter-scale production decision matrix",
        "docs/research/ch05-chapter-scale-production-decision-matrix-r1.md",
        "deee902a9c3d43bd1715f85df28c67574047267db4927967ee433e9bfabe8ce1",
    ),
    (
        "cadence_sensitivity",
        "Cadence objective-sensitivity audit",
        "docs/research/ch05-cadence-objective-sensitivity-audit-r1.md",
        "2d19612f4933fcda03674a402ca175b67d751acbeef8109fbe68a423d5fa0217",
    ),
    (
        "art_output_reconciliation",
        "Art/output count reconciliation",
        "docs/research/ch05-active-goal-art-output-reconciliation-r1.md",
        "753b68ab47572efd55a37c391aa4312cd36a4d0dfb254abcc9f32ec9537d943c",
    ),
    (
        "safe_source_inventory_r2",
        "Safe-source change inventory r2",
        "docs/research/ch05-overnight-safe-source-change-inventory-r2.md",
        "d9860743eb907931f9b824cf48f9584f9729934d8117ddbf0c050ce7e2ea5b3e",
    ),
    (
        "final_closeout_release",
        "Final overnight closeout release",
        "docs/research/evidence/ch05-overnight-closeout-release-r1.json",
        "90c6bb2455febe1622048d35eef4ec341e436ff7feb9efc4455174c8951dbc66",
    ),
    (
        "adr_0194",
        "ADR-0194 final engineering recommendation",
        "docs/adr/ADR-0194-close-ch05-overnight-with-measured-three-block-review-route.md",
        "6598ed5e7c641349c6d4a831a07b3f6d093d307896ea0e6e2a8a0fced23cdb8f",
    ),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def absolute(path: Path) -> str:
    return path.resolve().as_posix()


def bind_visuals() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for (
        artifact_id,
        title,
        relative,
        expected_hash,
        expected_width,
        expected_height,
    ) in VISUALS:
        path = ROOT / relative
        if not path.is_file():
            raise ValueError(f"missing visual artifact: {relative}")
        observed_hash = sha256(path)
        with Image.open(path) as image:
            width, height = image.size
        if observed_hash != expected_hash or [width, height] != [
            expected_width,
            expected_height,
        ]:
            raise ValueError(f"visual binding mismatch: {artifact_id}")
        rows.append(
            {
                "id": artifact_id,
                "title": title,
                "path": relative,
                "absolute_path": absolute(path),
                "sha256": observed_hash,
                "width": width,
                "height": height,
                "bytes": path.stat().st_size,
                "repository_state": "IGNORED_LOCAL_REVIEW_ARTIFACT",
            }
        )
    return rows


def bind_documents() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for document_id, title, relative, expected_hash in DOCUMENTS:
        path = ROOT / relative
        if not path.is_file() or sha256(path) != expected_hash:
            raise ValueError(f"supporting document binding mismatch: {document_id}")
        rows.append(
            {
                "id": document_id,
                "title": title,
                "path": relative,
                "absolute_path": absolute(path),
                "sha256": expected_hash,
                "bytes": path.stat().st_size,
            }
        )
    return rows


def build_documents() -> tuple[dict[str, Any], str]:
    visuals = bind_visuals()
    supporting = bind_documents()
    document: dict[str, Any] = {
        "record_type": "CH05FinalOwnerStartHere",
        "schema_version": "1.0",
        "record_id": "ng-ch05-final-owner-start-here-r1",
        "state": "LOCAL_OWNER_REVIEW_START_READY_DECISIONS_PENDING",
        "medium": "comic",
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "visual_review_set": visuals,
        "supporting_documents": supporting,
        "git_checkpoint": {
            "commit": GIT_COMMIT,
            "short_commit": "fa8d1ed",
            "subject": "Close CH05 overnight production study",
            "url": GIT_URL,
        },
        "measured_counts": {
            "service_raster_outputs": 76,
            "panel_level_candidates_or_crops": 312,
            "authorized_reference_uses": 132,
            "zero_reference_outputs": 13,
            "unsplit_ablation_diagnostics": 2,
        },
        "selected_cadence": {
            "assignment": {
                "S01": "reduced_palette_text_control",
                "S02-S08": "r6",
                "S09-S11": "premium_cel",
            },
            "semantic_pass": 47,
            "semantic_warn": 3,
            "semantic_fail": 0,
            "route_transitions": 2,
            "warning_panel_ids": ["P003", "P032", "P045"],
            "finish_review_question": "P005-to-P006",
        },
        "ranked_recommendation": [
            {"rank": 1, "route": "r6", "role": "semantic chapter backbone"},
            {
                "rank": 2,
                "route": "premium_cel",
                "role": "policy-sensitive late-block specialist",
            },
            {
                "rank": 3,
                "route": "clear_line_watercolor",
                "role": "leading unselected style-development fallback",
            },
            {
                "rank": 4,
                "route": "reduced_palette_text_control",
                "role": "opening/lower-density specialist with wholesale finish constraints",
            },
            {
                "rank": 5,
                "route": "alt_graphic",
                "role": "comparison route, not current lead",
            },
            {
                "rank": 6,
                "route": "flat_graphic_gouache",
                "role": "diagnostic style arm, not current lead",
            },
        ],
        "decision_separation": {
            "visual_decisions_now": [
                "Retain or revise the three-block cadence after reading the lettered and clean phone chapters.",
                "Record dispositions for P003, P032, P045, P005-to-P006, lettering clearance, and the strongest 14 candidates.",
                "Treat the LitRPG equipment/monster sheet as noncanon taste feedback only.",
            ],
            "rights_and_exact_base_decisions_later": [
                "Commercial rights clearance remains null and must be decided separately from visual approval.",
                "Exact-production-base eligibility remains null for every candidate and route.",
                "A positive visual disposition does not imply rights clearance, canon promotion, or exact-base selection.",
            ],
        },
        "timing_and_spend": {
            "aggregate_end_to_end_art_production_seconds": None,
            "reason": "Source records mix summed observations, overlap-adjusted walls, non-overlap arithmetic, concurrent-batch walls, and individual call walls; adding them would not yield defensible elapsed production time.",
            "closeout_validation_observed_seconds": 42.965392,
            "closeout_validation_is_not_art_production_time": True,
            "direct_paid_api_cloud_usd": 0.0,
            "built_in_product_monetary_cost_usd": None,
            "service_metadata_unavailable": [
                "model",
                "endpoint",
                "provider_request_id",
                "usage",
                "deterministic_seed",
            ],
        },
        "disposition": {
            "owner_visual_decisions_recorded": 0,
            "accepted": 0,
            "rights_cleared": 0,
            "commercially_cleared": 0,
            "canon_promoted": 0,
            "exact_production_base": 0,
        },
        "activity_boundary": {
            "new_pixels": 0,
            "provider_calls": 0,
            "uploads": 0,
            "paid_spend_usd": 0.0,
        },
        "limitations": [
            "The ten visual artifacts are ignored local evidence; their exact hashes and dimensions are checked, but that does not accept their content.",
            "The six-route metrics and reviews remain non-gating; automated proxies are not quality scores.",
            "The Git checkpoint is a source/evidence checkpoint, not a commercial-use or pixel-rights conclusion.",
        ],
        "boundary": "Owner navigation and evidence binding only; no pixel creation or edit, provider call, upload, spend, acceptance, rights clearance, canon promotion, or exact-production-base selection.",
    }

    visual_lines = [
        f"{index}. [{row['title']}]({row['absolute_path']}) — {row['width']} × {row['height']}, SHA-256 `{row['sha256']}`."
        for index, row in enumerate(visuals, start=1)
    ]
    support_lines = [
        f"- [{row['title']}]({row['absolute_path']}) — SHA-256 `{row['sha256']}`."
        for row in supporting
    ]
    ranking_lines = [
        f"{row['rank']}. **{row['route']}** — {row['role']}."
        for row in document["ranked_recommendation"]
    ]
    markdown = "\n".join(
        [
            "# North Garden CH05 — final owner start here",
            "",
            "Start with the ten visual links below. Everything remains review evidence: no art is accepted, commercially cleared, canon-promoted, or selected as an exact production base.",
            "",
            "## Minimum visual review set",
            "",
            *visual_lines,
            "",
            "Review order: full lettered chapter; clean phone chapter; exhaustive six-route and density comparisons; cadence, warning, boundary, and lettering diagnostics; strongest-candidate atlas; then optional noncanon LitRPG concepts.",
            "",
            "## Recommended direction",
            "",
            "Retain the measured three-block route for owner review: reduced-palette S01, R6 S02-S08, and premium cel S09-S11. It measures 47 semantic PASS / 3 WARN / 0 FAIL with two route transitions. Review P003, P032, P045, and P005-to-P006 explicitly.",
            "",
            *ranking_lines,
            "",
            "This ranking is an engineering recommendation for the next review workflow, not a visual-quality score, acceptance, or wholesale-route promotion.",
            "",
            "## Measured art/output scope",
            "",
            "| Service raster outputs | Panel candidates/crops | Authorized reference uses | Zero-reference outputs | Unsplit ablation diagnostics |",
            "| ---: | ---: | ---: | ---: | ---: |",
            "| 76 | 312 | 132 | 13 | 2 |",
            "",
            "The aligned six-route comparison is a 300-candidate subset. Aggregate end-to-end art-production time is unavailable because source records use incompatible timing scopes. The closeout validation run took 42.965392 seconds; that is validation time, not art-production time. Direct paid API/cloud spend is $0. Built-in monetary cost and model, endpoint, request ID, usage, and deterministic seed remain unavailable.",
            "",
            "## Keep these decisions separate",
            "",
            "### Visual review now",
            "",
            "- Retain or revise the three-block cadence.",
            "- Resolve P003, P032, P045, P005-to-P006, lettering clearance, and strongest-candidate dispositions.",
            "- Give noncanon taste feedback on the LitRPG armor, weapons, and Mireback concepts without changing CH05 canon.",
            "",
            "### Rights and exact-base authority later",
            "",
            "- Commercial-rights clearance remains null and separate from visual approval.",
            "- Exact-production-base eligibility remains null for every candidate and route.",
            "- Visual approval does not imply rights clearance, canon promotion, or exact-base selection.",
            "",
            "## Supporting evidence",
            "",
            *support_lines,
            f"- [Git commit `fa8d1ed`]({GIT_URL}) — `{GIT_COMMIT}`, Close CH05 overnight production study.",
            "",
            "The machine-readable binding is `docs/research/evidence/ch05-final-owner-start-here-r1.json`.",
            "",
        ]
    )
    return document, markdown


def main() -> int:
    document, markdown = build_documents()
    MARKDOWN_OUT.parent.mkdir(parents=True, exist_ok=True)
    MARKDOWN_OUT.write_text(markdown, encoding="utf-8", newline="\n")
    JSON_OUT.write_text(
        json.dumps(document, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "markdown": MARKDOWN_OUT.relative_to(ROOT).as_posix(),
                "markdown_sha256": sha256(MARKDOWN_OUT),
                "json": JSON_OUT.relative_to(ROOT).as_posix(),
                "json_sha256": sha256(JSON_OUT),
                "visuals": len(document["visual_review_set"]),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
