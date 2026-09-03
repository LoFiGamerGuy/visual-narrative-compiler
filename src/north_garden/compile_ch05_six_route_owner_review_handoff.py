"""Compile the concise CH05 six-route owner-review handoff and artifact index."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
MARKDOWN = ROOT / "docs/research/ch05-six-route-owner-review-handoff-r1.md"
EVIDENCE = ROOT / "docs/research/evidence/ch05-six-route-owner-review-handoff-r1.json"

ARTIFACT_SPECS = [
    (
        "cadence_lettered_phone",
        "Selected sequence-cadence packet",
        "1. Lettered 390px phone scroll",
        "experiments/review-packets/ch05-sequence-cadence-review-r1/lettered/ch05-sequence-cadence-lettered-r1-phone-390px.png",
    ),
    (
        "cadence_clean_phone",
        "Selected sequence-cadence packet",
        "2. Clean 390px phone scroll",
        "experiments/review-packets/ch05-sequence-cadence-review-r1/clean/ch05-complete-chapter-phone-390px.png",
    ),
    (
        "cadence_continuity",
        "Selected sequence-cadence packet",
        "3. Cast continuity sheet",
        "experiments/review-packets/ch05-sequence-cadence-review-r1/review/ch05-sequence-cadence-continuity-sheet-r1.png",
    ),
    (
        "cadence_boundary_continuity",
        "Selected sequence-cadence packet",
        "4. P005/P006 and P039/P040 boundary continuity",
        "experiments/review-packets/ch05-sequence-cadence-review-r1/review/ch05-sequence-cadence-boundary-continuity-sheet-r1.png",
    ),
    (
        "cadence_triage",
        "Selected sequence-cadence packet",
        "5. Semantic triage sheet",
        "experiments/review-packets/ch05-sequence-cadence-review-r1/review/ch05-sequence-cadence-triage-sheet-r1.png",
    ),
    (
        "cadence_safe_contact",
        "Selected sequence-cadence packet",
        "6. Canonical safe-zone contact sheet",
        "experiments/review-packets/ch05-sequence-cadence-review-r1/clean/ch05-complete-chapter-contact-sheet-lettering-overlay.png",
    ),
    (
        "cadence_clean_long",
        "Selected sequence-cadence packet",
        "7. Clean native chapter scroll",
        "experiments/review-packets/ch05-sequence-cadence-review-r1/clean/ch05-complete-chapter-long-scroll.png",
    ),
    (
        "cadence_clean_contact",
        "Selected sequence-cadence packet",
        "8. Clean all-50 contact sheet",
        "experiments/review-packets/ch05-sequence-cadence-review-r1/clean/ch05-complete-chapter-contact-sheet.png",
    ),
    (
        "cadence_safe_scroll",
        "Selected sequence-cadence packet",
        "9. Canonical safe-zone native scroll",
        "experiments/review-packets/ch05-sequence-cadence-review-r1/clean/ch05-complete-chapter-long-scroll-lettering-overlay.png",
    ),
    (
        "cadence_lettered_long",
        "Selected sequence-cadence packet",
        "10. Lettered native chapter scroll",
        "experiments/review-packets/ch05-sequence-cadence-review-r1/lettered/ch05-sequence-cadence-lettered-r1.png",
    ),
    (
        "six_all_50",
        "Six-route comparisons",
        "All 50 panels across six routes",
        "experiments/review-packets/ch05-six-route-comparison-r1/ch05-six-route-all-50-contact-sheet.png",
    ),
    (
        "six_semantic",
        "Six-route comparisons",
        "Semantic anchors",
        "experiments/review-packets/ch05-six-route-comparison-r1/ch05-six-route-semantic-anchors.png",
    ),
    (
        "six_lettered_phone",
        "Six-route comparisons",
        "Lettered phone comparison",
        "experiments/review-packets/ch05-six-route-comparison-r1/ch05-six-route-lettered-phone-comparison.png",
    ),
    (
        "six_style_density",
        "Six-route comparisons",
        "Style and density comparison",
        "experiments/review-packets/ch05-six-route-comparison-r1/ch05-six-route-style-density-comparison.png",
    ),
    (
        "six_sequence_cadence",
        "Six-route comparisons",
        "Sequence cadence recommendation",
        "experiments/review-packets/ch05-six-route-comparison-r1/ch05-six-route-sequence-cadence.png",
    ),
    (
        "rp_contact",
        "Reduced-palette text control",
        "All-50 contact sheet",
        "experiments/review-packets/ch05-complete-chapter-reduced-palette-text-control-r1/review/ch05-complete-chapter-contact-sheet.png",
    ),
    (
        "rp_contact_safe",
        "Reduced-palette text control",
        "All-50 canonical safe-zone contact sheet",
        "experiments/review-packets/ch05-complete-chapter-reduced-palette-text-control-r1/review/ch05-complete-chapter-contact-sheet-lettering-overlay.png",
    ),
    (
        "rp_long",
        "Reduced-palette text control",
        "Native chapter long scroll",
        "experiments/review-packets/ch05-complete-chapter-reduced-palette-text-control-r1/review/ch05-complete-chapter-long-scroll.png",
    ),
    (
        "rp_long_safe",
        "Reduced-palette text control",
        "Native long-scroll safe-zone overlay",
        "experiments/review-packets/ch05-complete-chapter-reduced-palette-text-control-r1/review/ch05-complete-chapter-long-scroll-lettering-overlay.png",
    ),
    (
        "rp_phone",
        "Reduced-palette text control",
        "Unlettered 390px phone scroll",
        "experiments/review-packets/ch05-complete-chapter-reduced-palette-text-control-r1/review/ch05-complete-chapter-phone-390px.png",
    ),
    (
        "rp_lettered",
        "Reduced-palette text control",
        "Lettered native scroll",
        "experiments/review-packets/ch05-complete-chapter-reduced-palette-text-control-r1/lettered/ch05-complete-chapter-reduced-palette-text-control-lettered-r1.png",
    ),
    (
        "rp_lettered_phone",
        "Reduced-palette text control",
        "Lettered 390px phone scroll",
        "experiments/review-packets/ch05-complete-chapter-reduced-palette-text-control-r1/lettered/ch05-complete-chapter-reduced-palette-text-control-lettered-r1-phone-390px.png",
    ),
    (
        "rp_continuity",
        "Reduced-palette text control",
        "Hair, wardrobe, and cast continuity",
        "experiments/review-packets/ch05-complete-chapter-reduced-palette-text-control-r1/review/ch05-complete-chapter-reduced-palette-text-control-continuity-sheet.png",
    ),
    (
        "rp_triage",
        "Reduced-palette text control",
        "Semantic, lettering, phone, and strict-style triage",
        "experiments/review-packets/ch05-complete-chapter-reduced-palette-text-control-r1/review/ch05-complete-chapter-reduced-palette-text-control-triage-sheet-r1.png",
    ),
    (
        "flat_contact",
        "Flat-gouache route packet",
        "All-50 contact sheet",
        "experiments/review-packets/ch05-complete-chapter-flat-graphic-gouache-r1/review/ch05-complete-chapter-contact-sheet.png",
    ),
    (
        "flat_contact_safe",
        "Flat-gouache route packet",
        "All-50 canonical safe-zone contact sheet",
        "experiments/review-packets/ch05-complete-chapter-flat-graphic-gouache-r1/review/ch05-complete-chapter-contact-sheet-lettering-overlay.png",
    ),
    (
        "flat_long",
        "Flat-gouache route packet",
        "Native chapter long scroll",
        "experiments/review-packets/ch05-complete-chapter-flat-graphic-gouache-r1/review/ch05-complete-chapter-long-scroll.png",
    ),
    (
        "flat_long_safe",
        "Flat-gouache route packet",
        "Native long-scroll safe-zone overlay",
        "experiments/review-packets/ch05-complete-chapter-flat-graphic-gouache-r1/review/ch05-complete-chapter-long-scroll-lettering-overlay.png",
    ),
    (
        "flat_phone",
        "Flat-gouache route packet",
        "Unlettered 390px phone scroll",
        "experiments/review-packets/ch05-complete-chapter-flat-graphic-gouache-r1/review/ch05-complete-chapter-phone-390px.png",
    ),
    (
        "flat_lettered",
        "Flat-gouache route packet",
        "Lettered native scroll",
        "experiments/review-packets/ch05-complete-chapter-flat-graphic-gouache-r1/lettered/ch05-complete-chapter-flat-graphic-gouache-lettered-r1.png",
    ),
    (
        "flat_lettered_phone",
        "Flat-gouache route packet",
        "Lettered 390px phone scroll",
        "experiments/review-packets/ch05-complete-chapter-flat-graphic-gouache-r1/lettered/ch05-complete-chapter-flat-graphic-gouache-lettered-r1-phone-390px.png",
    ),
    (
        "flat_continuity",
        "Flat-gouache route packet",
        "Hair, wardrobe, and cast continuity",
        "experiments/review-packets/ch05-complete-chapter-flat-graphic-gouache-r1/review/ch05-complete-chapter-flat-graphic-gouache-continuity-sheet.png",
    ),
    (
        "flat_triage",
        "Flat-gouache route packet",
        "Agent triage",
        "experiments/review-packets/ch05-complete-chapter-flat-graphic-gouache-r1/review/ch05-complete-chapter-flat-graphic-gouache-triage-sheet-r1.png",
    ),
    (
        "s01_ablation_native",
        "Matched reference ablations",
        "S01 three-column native comparison",
        "experiments/review-packets/ch05-s01-flat-gouache-reference-ablation-r1/review/s01-reference-ablation-three-column-native-r1.png",
    ),
    (
        "s01_ablation_phone",
        "Matched reference ablations",
        "S01 three-column 390px comparison",
        "experiments/review-packets/ch05-s01-flat-gouache-reference-ablation-r1/review/s01-reference-ablation-three-column-390px-r1.png",
    ),
    (
        "s11_ablation_native",
        "Matched reference ablations",
        "S11 three-column native comparison",
        "experiments/review-packets/ch05-s11-flat-gouache-reference-ablation-r1/review/s11-reference-ablation-three-column-native-r1.png",
    ),
    (
        "s11_ablation_phone",
        "Matched reference ablations",
        "S11 three-column 390px comparison",
        "experiments/review-packets/ch05-s11-flat-gouache-reference-ablation-r1/review/s11-reference-ablation-three-column-390px-r1.png",
    ),
    (
        "hybrid_contact",
        "Semantic-pass hybrid",
        "All-50 contact sheet",
        "experiments/review-packets/ch05-semantic-pass-hybrid-r1/review/ch05-complete-chapter-contact-sheet.png",
    ),
    (
        "hybrid_contact_safe",
        "Semantic-pass hybrid",
        "All-50 canonical safe-zone contact sheet",
        "experiments/review-packets/ch05-semantic-pass-hybrid-r1/review/ch05-complete-chapter-contact-sheet-lettering-overlay.png",
    ),
    (
        "hybrid_long",
        "Semantic-pass hybrid",
        "Native chapter long scroll",
        "experiments/review-packets/ch05-semantic-pass-hybrid-r1/review/ch05-complete-chapter-long-scroll.png",
    ),
    (
        "hybrid_phone",
        "Semantic-pass hybrid",
        "Unlettered 390px phone scroll",
        "experiments/review-packets/ch05-semantic-pass-hybrid-r1/review/ch05-complete-chapter-phone-390px.png",
    ),
    (
        "hybrid_lettered",
        "Semantic-pass hybrid",
        "Lettered native scroll",
        "experiments/review-packets/ch05-semantic-pass-hybrid-r1/lettered/ch05-semantic-pass-hybrid-lettered-r1.png",
    ),
    (
        "hybrid_lettered_phone",
        "Semantic-pass hybrid",
        "Lettered 390px phone scroll",
        "experiments/review-packets/ch05-semantic-pass-hybrid-r1/lettered/ch05-semantic-pass-hybrid-lettered-r1-phone-390px.png",
    ),
    (
        "hybrid_continuity",
        "Semantic-pass hybrid",
        "Hair, wardrobe, and cast continuity",
        "experiments/review-packets/ch05-semantic-pass-hybrid-r1/review/ch05-semantic-pass-hybrid-continuity-sheet-r1.png",
    ),
    (
        "hybrid_triage",
        "Semantic-pass hybrid",
        "Agent triage",
        "experiments/review-packets/ch05-semantic-pass-hybrid-r1/review/ch05-semantic-pass-hybrid-triage-sheet-r1.png",
    ),
    (
        "rp_p010",
        "Strongest reduced-palette candidates",
        "P010 listening profile",
        "experiments/review-packets/ch05-complete-chapter-reduced-palette-text-control-r1/panels/p010-reduced-palette-text-control-r1.png",
    ),
    (
        "rp_p014",
        "Strongest reduced-palette candidates",
        "P014 ridge occlusion",
        "experiments/review-packets/ch05-complete-chapter-reduced-palette-text-control-r1/panels/p014-reduced-palette-text-control-r1.png",
    ),
    (
        "rp_p035",
        "Strongest reduced-palette candidates",
        "P035 high tin",
        "experiments/review-packets/ch05-complete-chapter-reduced-palette-text-control-r1/panels/p035-reduced-palette-text-control-r1.png",
    ),
    (
        "rp_p040",
        "Strongest reduced-palette candidates",
        "P040 deduction profile",
        "experiments/review-packets/ch05-complete-chapter-reduced-palette-text-control-r1/panels/p040-reduced-palette-text-control-r1.png",
    ),
    (
        "rp_p041",
        "Strongest reduced-palette candidates",
        "P041 cold drum",
        "experiments/review-packets/ch05-complete-chapter-reduced-palette-text-control-r1/panels/p041-reduced-palette-text-control-r1.png",
    ),
    (
        "rp_p046",
        "Strongest reduced-palette candidates",
        "P046 retained map",
        "experiments/review-packets/ch05-complete-chapter-reduced-palette-text-control-r1/panels/p046-reduced-palette-text-control-r1.png",
    ),
]

REVIEW_QUESTIONS = [
    "Which route or sequence-level cadence should lead the next production pass after comparing semantic correctness, continuity, lettering, density, and phone readability together?",
    "Do P010, P014, P035, P040, P041, and P046 merit provisional visual approval for targeted continuity/style reference use, without implying rights or exact-base clearance?",
    "For reduced-palette P008, P036, and P050, should the next step be the logged minimal semantic repairs rather than wholesale regeneration?",
    "Should canonical lettering move into gutters/outside-art bands for collision-heavy panels, or should those compositions be regenerated around the current safe zones?",
    "Does the reduced-palette arm's lower measured density outweigh its 24% strict 3-5-mass compliance, or should the prompt enforce an even harder background/detail budget?",
    "Do the matched S01 and S11 ablations show enough continuity benefit from references to justify selective reference-conditioned production?",
    "Is the semantic-pass hybrid useful only as a story-proof assembly, or are its route transitions acceptable enough to guide sequence-level production?",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def artifact(spec: tuple[str, str, str, str]) -> dict[str, Any]:
    artifact_id, section, title, relative = spec
    path = ROOT / relative
    if not path.is_file():
        raise FileNotFoundError(relative)
    with Image.open(path) as image:
        image.verify()
    with Image.open(path) as image:
        width, height, image_format = image.width, image.height, image.format
    if image_format != "PNG":
        raise ValueError(f"not PNG: {relative}")
    return {
        "id": artifact_id,
        "section": section,
        "title": title,
        "path": relative,
        "absolute_path": path.resolve().as_posix(),
        "sha256": sha256(path),
        "width": width,
        "height": height,
        "bytes": path.stat().st_size,
        "repository_state": "IGNORED_LOCAL_REVIEW_ARTIFACT",
    }


def markdown_link(relative: str) -> str:
    return "../../" + relative


def render_markdown(artifacts: list[dict[str, Any]]) -> str:
    lines = [
        "# CH05 six-route owner review handoff",
        "",
        "Start with the selected cadence's lettered phone scroll and boundary sheet, then inspect the five six-route sheets, reduced-palette route, flat-gouache packet, matched ablations, and semantic-pass hybrid. All linked pixels are ignored local review artifacts. Nothing here is accepted, rights-cleared, commercially cleared, or selected as an exact production base.",
        "",
    ]
    sections: list[str] = []
    for item in artifacts:
        if item["section"] not in sections:
            sections.append(item["section"])
    for section in sections:
        lines.extend(
            [
                f"## {section}",
                "",
                "| Artifact | Dimensions | SHA-256 |",
                "|---|---:|---|",
            ]
        )
        for item in artifacts:
            if item["section"] != section:
                continue
            link = markdown_link(item["path"])
            lines.append(
                f"| [{item['title']}]({link}) | {item['width']}×{item['height']} | `{item['sha256']}` |"
            )
        lines.append("")
    lines.extend(["## Review questions", ""])
    lines.extend(
        f"{index}. {question}" for index, question in enumerate(REVIEW_QUESTIONS, 1)
    )
    lines.extend(
        [
            "",
            "## Evidence and boundary",
            "",
            "The machine-readable artifact list is [ch05-six-route-owner-review-handoff-r1.json](evidence/ch05-six-route-owner-review-handoff-r1.json). Hashes and dimensions are validated against local files; generated pixels remain ignored and untracked. Review answers must be recorded separately before any acceptance, rights, commercial-use, or exact-production-base state changes.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    artifacts = [artifact(spec) for spec in ARTIFACT_SPECS]
    markdown = render_markdown(artifacts)
    MARKDOWN.write_text(markdown, encoding="utf-8", newline="\n")
    sections = list(dict.fromkeys(item["section"] for item in artifacts))
    evidence = {
        "record_type": "CH05SixRouteOwnerReviewHandoff",
        "schema_version": "1.0",
        "record_id": "ng-ch05-six-route-owner-review-handoff-r1",
        "state": "LOCAL_REVIEW_INDEX_READY_OWNER_DISPOSITIONS_PENDING",
        "medium": "comic",
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "summary": {
            "artifact_count": len(artifacts),
            "section_count": len(sections),
            "six_route_comparison_sheets": 5,
            "reduced_palette_packet_artifacts": 9,
            "flat_route_packet_artifacts": 9,
            "matched_ablation_comparisons": 4,
            "semantic_pass_hybrid_artifacts": 8,
            "selected_sequence_cadence_packet_artifacts": 10,
            "strongest_reduced_palette_candidates": 6,
            "review_questions": len(REVIEW_QUESTIONS),
            "owner_dispositions": 0,
            "accepted": 0,
            "rights_cleared": 0,
            "commercially_cleared": 0,
            "exact_production_base": 0,
        },
        "handoff": {
            "path": MARKDOWN.relative_to(ROOT).as_posix(),
            "sha256": sha256(MARKDOWN),
            "bytes": MARKDOWN.stat().st_size,
        },
        "sections": sections,
        "strongest_reduced_palette_panel_ids": [
            "P010",
            "P014",
            "P035",
            "P040",
            "P041",
            "P046",
        ],
        "review_questions": REVIEW_QUESTIONS,
        "artifacts": artifacts,
        "limitations": [
            "This index proves local artifact identity and availability, not visual acceptance.",
            "Absolute paths are workspace-specific; repository-relative Markdown links remain portable with the workspace tree.",
            "Generated pixels remain ignored and are not copied into tracked documentation.",
        ],
        "boundary": "Owner-review navigation only; no acceptance, rights clearance, commercial clearance, exact production-base selection, provider call, upload, AnimationShotPlan, or E-Conte action.",
    }
    EVIDENCE.write_text(
        json.dumps(evidence, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "artifacts": len(artifacts),
                "markdown": {
                    "path": MARKDOWN.relative_to(ROOT).as_posix(),
                    "sha256": sha256(MARKDOWN),
                },
                "evidence": {
                    "path": EVIDENCE.relative_to(ROOT).as_posix(),
                    "sha256": sha256(EVIDENCE),
                },
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
