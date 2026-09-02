"""Compile exact local links for every CH05 review deliverable needed at handoff."""
from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "production/comic/review/ch05-review-artifact-link-manifest-r1.json"
MARKDOWN = ROOT / "docs/research/ch05-review-links-r1.md"


def glob(pattern: str) -> list[str]:
    return sorted(path.relative_to(ROOT).as_posix() for path in ROOT.glob(pattern) if path.is_file())


CATEGORIES = {
    "review_hubs": [
        "experiments/review-packets/ch05-owner-review-index-r1/index.html",
        "experiments/review-packets/ch05-owner-review-index-r2/index.html",
        "experiments/review-packets/ch05-owner-review-index-r3/index.html",
        "experiments/review-packets/ch05-owner-decision-worksheet-r1/index.html",
    ],
    "contact_sheets": [
        "experiments/review-packets/ch05-style-density-scale-exploration-r1/contact-sheet-r1.png",
        "experiments/review-packets/ch05-mill-signal-imagegen-smoke-r1/contact-sheet-r1.png",
        *glob("experiments/review-packets/ch05-overnight-production-r1/review/contact-sheet-*.png"),
        *glob("experiments/review-packets/ch05-cadence-hardening-r1/review/contact-sheet-*.png"),
        *glob("experiments/review-packets/future-litrpg-visual-concepts-r1/review/contact-sheet-*.png"),
    ],
    "sequence_packets": [
        *glob("experiments/review-packets/ch05-overnight-production-r1/review/sequence-*.png"),
        *glob("experiments/review-packets/ch05-variable-cadence-assembly-r1/sequence-selected-*.png"),
        "experiments/review-packets/ch05-variable-cadence-assembly-r1/ch05-variable-cadence-scroll-clean-r1.png",
        "experiments/review-packets/ch05-variable-cadence-assembly-r1/ch05-variable-cadence-scroll-safe-zones-r1.png",
        "experiments/review-packets/ch05-variable-cadence-assembly-r1/ch05-variable-cadence-phone-scroll-390px-r1.png",
    ],
    "lettering_overlays": [
        "experiments/review-packets/ch05-style-density-scale-exploration-r1/lettering-clearance-overlay-r1.png",
        *glob("experiments/review-packets/ch05-mill-signal-imagegen-smoke-r1/lettering-*-overlay-r1.png"),
        "experiments/review-packets/ch05-p036-repair-readiness-r1/ch05-p036-lettering-target-conflict-overlay-r1.png",
        *glob("experiments/review-packets/ch05-overnight-production-r1/review/lettering-overlays/*.png"),
        *glob("experiments/review-packets/ch05-cadence-hardening-r1/review/lettering-overlays/*.png"),
        "experiments/review-packets/ch05-transparent-lettering-rehearsal-r1/ch05-transparent-lettering-phone-comparison-r1.png",
        "experiments/review-packets/ch05-lettering-width-copy-sensitivity-r1/ch05-lettering-width-copy-sensitivity-r1.png",
        "experiments/review-packets/ch05-outside-art-lettering-band-r1/ch05-outside-art-lettering-band-comparison-r1.png",
    ],
    "strongest_candidates": [
        "experiments/review-packets/ch05-cadence-hardening-r1/candidates/h001-p050-cel_painted-r1.png",
        "experiments/review-packets/ch05-cadence-hardening-r1/candidates/h002-p003-clear_line_watercolor-r1.png",
        "experiments/review-packets/ch05-cadence-hardening-r1/candidates/h004-p029-clean_graphic-r1.png",
        "experiments/review-packets/ch05-cadence-hardening-r1/candidates/h006-p036-clear_line_watercolor-r1.png",
        "experiments/review-packets/ch05-overnight-production-r1/candidates/c019-p001-clear_line_watercolor-r1.png",
        "experiments/review-packets/ch05-overnight-production-r1/candidates/c002-p002-cel_painted-r1.png",
        "experiments/review-packets/ch05-overnight-production-r1/candidates/c005-p009-clear_line_watercolor-r1.png",
        "experiments/review-packets/ch05-overnight-production-r1/candidates/c006-p019-clean_graphic-r1.png",
        "experiments/review-packets/ch05-overnight-production-r1/candidates/c008-p026-cel_painted-r1.png",
        "experiments/review-packets/ch05-overnight-production-r1/candidates/c010-p035-clear_line_watercolor-r1.png",
        "experiments/review-packets/ch05-overnight-production-r1/candidates/c013-p040-clear_line_watercolor-r1.png",
        "experiments/review-packets/ch05-overnight-production-r1/candidates/c014-p044-limited_ink_flat-r1.png",
        "experiments/review-packets/ch05-overnight-production-r1/candidates/c015-p046-cel_painted-r1.png",
        "experiments/review-packets/ch05-overnight-production-r1/candidates/c016-p049-clean_graphic-r1.png",
    ],
    "noncanon_litrpg_concepts": glob("experiments/review-packets/future-litrpg-visual-concepts-r1/candidates/*.png"),
    "diagnostic_and_policy_sheets": [
        *glob("experiments/review-packets/ch05-continuity-style-density-r1/*.png"),
        *glob("experiments/review-packets/ch05-manual-continuity-atlas-r1/*.png"),
        "experiments/review-packets/ch05-panel-scale-cadence-policy-r1/ch05-panel-scale-cadence-map-r1.png",
        "experiments/review-packets/ch05-failure-class-repair-matrix-r1/ch05-targeted-repair-paths-r1.png",
        "experiments/review-packets/ch05-p010-p013-preflight-contract-r1/ch05-p010-p013-preflight-storyboard-r1.png",
        "experiments/review-packets/ch05-chapter-scale-production-envelope-r1/ch05-chapter-scale-production-envelope-r1.png",
        "experiments/review-packets/ch05-renderrecord-completeness-audit-r1/ch05-renderrecord-field-matrix-r1.png",
    ],
    "packet_records": [
        "experiments/review-packets/ch05-style-density-scale-exploration-r1/review-packet.json",
        "experiments/review-packets/ch05-overnight-production-r1/review/review-packet.json",
        "experiments/review-packets/ch05-cadence-hardening-r1/review/review-packet.json",
        "experiments/review-packets/future-litrpg-visual-concepts-r1/review/review-packet.json",
        "experiments/review-packets/ch05-variable-cadence-assembly-r1/assembly-packet.json",
        "experiments/review-packets/ch05-transparent-lettering-rehearsal-r1/lettering-rehearsal-packet.json",
        "experiments/review-packets/ch05-lettering-width-copy-sensitivity-r1/width-copy-sensitivity-packet.json",
        "experiments/review-packets/ch05-outside-art-lettering-band-r1/outside-art-lettering-band-packet.json",
        "experiments/review-packets/ch05-continuity-style-density-r1/continuity-style-density-packet.json",
        "experiments/review-packets/ch05-manual-continuity-atlas-r1/manual-continuity-atlas-packet.json",
        "experiments/review-packets/ch05-owner-review-index-r1/owner-review-index-packet.json",
        "experiments/review-packets/ch05-owner-review-index-r2/owner-review-index-r2-packet.json",
        "experiments/review-packets/ch05-owner-review-index-r3/owner-review-index-r3-packet.json",
        "experiments/review-packets/ch05-owner-decision-worksheet-r1/decision-worksheet-packet.json",
    ],
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    category_by_path: dict[str, list[str]] = defaultdict(list)
    for category, paths in CATEGORIES.items():
        for path_text in paths:
            if category not in category_by_path[path_text]:
                category_by_path[path_text].append(category)
    artifacts = []
    for path_text in sorted(category_by_path):
        path = ROOT / path_text
        if not path.is_file():
            raise SystemExit(f"missing review artifact: {path_text}")
        artifacts.append(
            {
                "path": path_text,
                "absolute_path": path.resolve().as_posix(),
                "sha256": sha(path),
                "bytes": path.stat().st_size,
                "categories": sorted(category_by_path[path_text]),
            }
        )
    counts = {category: len(dict.fromkeys(paths)) for category, paths in CATEGORIES.items()}
    manifest = {
        "record_type": "CH05ReviewArtifactLinkManifest",
        "schema_version": "1.0",
        "record_id": "ng-ch05-review-artifact-link-manifest-r1",
        "workspace_root_at_compile": str(ROOT.resolve()),
        "state": "LOCAL_REVIEW_LINKS_READY_OWNER_PENDING",
        "category_counts": counts,
        "unique_artifact_count": len(artifacts),
        "artifacts": artifacts,
        "summary": {
            "candidate_count": 29,
            "selected_candidate_count": 14,
            "owner_decisions": 0,
            "accepted_candidates": 0,
            "provider_calls": 0,
            "uploads": 0,
            "cost_usd": 0,
            "human_review_minutes": None,
        },
        "limitations": [
            "Absolute paths are valid for the recorded workspace root and must be recompiled if the repository moves.",
            "Links expose ignored local artifacts only; generated pixels remain untracked and unpublished.",
            "The strongest-candidate category is a provisional engineering shortlist, not owner acceptance or commercial clearance.",
        ],
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    lines = [
        "# CH05 exact local review links r1",
        "",
        "Generated deterministically from `ch05-review-artifact-link-manifest-r1.json`. All art remains ignored, unpublished, unaccepted, and commercially uncleared.",
        "",
        f"Unique artifacts: {len(artifacts)}. Workspace root: `{ROOT.resolve().as_posix()}`.",
        "",
    ]
    by_path = {item["path"]: item for item in artifacts}
    for category, paths in CATEGORIES.items():
        lines.extend([f"## {category.replace('_', ' ').title()}", ""])
        for path_text in dict.fromkeys(paths):
            item = by_path[path_text]
            label = Path(path_text).name
            lines.append(f"- [{label}]({item['absolute_path']}) — `{item['sha256']}`")
        lines.append("")
    MARKDOWN.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print(f"CH05 review links: {len(artifacts)} unique artifacts; " + ", ".join(f"{key}={value}" for key, value in counts.items()))
    print("generated pixels tracked/published/accepted 0/0/0; provider calls/uploads/cost 0/0/$0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
