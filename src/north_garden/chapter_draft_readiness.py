"""Report deterministic readiness gaps for a draft comic sequence.

This is deliberately distinct from ``chapter_lint``.  It answers whether a
sequence has the basic records and measured status required to *enter* a
chapter-scale production cycle, without treating a small art sample, a passed
hash lint, or an agent triage as production acceptance.
"""
from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REGISTRY = ROOT / "production/comic/narrative-sequence-registry-r1.json"
DEFAULT_OUTPUT = ROOT / "experiments/results/chapter_draft_readiness_20260901.json"


def load(relative_path: str) -> dict[str, object]:
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


def report(registry_path: Path) -> dict[str, object]:
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    target = registry["chapter_scale_target_panels"]
    items: list[dict[str, object]] = []
    for entry in registry["entries"]:
        edition = load(entry["edition"])
        review = load(entry["review"])
        lint = load(entry["lint"])
        panels = int(entry["panel_count"])
        panel_gap = max(0, int(target["minimum"]) - panels)
        checks = {
            "draft_edition_exists": edition["publication_state"] == "DRAFT_REVIEW_PENDING_NOT_PUBLISHED",
            "lint_has_no_failures": lint["summary"]["fail"] == 0,
            "human_review_is_pending": review["state"] == "PENDING_AUTHORIZED_HUMAN_REVIEW",
            "no_unearned_acceptance": review["summary"]["research_accepted"] == 0,
            "chapter_scale_minimum_met": panels >= int(target["minimum"]),
            "chapter_scale_maximum_not_exceeded": panels <= int(target["maximum"]),
        }
        items.append({
            "sequence_id": entry["sequence_id"],
            "chapter_label": entry["chapter_label"],
            "edition_id": edition["edition_id"],
            "panel_count": panels,
            "panel_gap_to_target_minimum": panel_gap,
            "review_state": review["state"],
            "research_accepted": review["summary"]["research_accepted"],
            "renderer_boundary": entry["renderer_boundary"],
            "checks": checks,
            "readiness": "NOT_READY_CHAPTER_SCALE" if panel_gap else "REQUIRES_HUMAN_REVIEW_AND_PRODUCTION_ACCEPTANCE",
        })
    return {
        "record_type": "ChapterDraftReadinessReport",
        "schema_version": "1.0",
        "registry": str(registry_path.relative_to(ROOT)).replace("\\", "/"),
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "target": target,
        "entries": items,
        "summary": {
            "sequence_count": len(items),
            "chapter_scale_ready_count": sum(item["readiness"] != "NOT_READY_CHAPTER_SCALE" for item in items),
            "research_accepted_panel_count": sum(int(item["research_accepted"]) for item in items),
            "limitation": "This report does not evaluate art quality, assertions, model licensing, commercial eligibility, reproducibility, or human time. It must not be used as a publication decision.",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = report(args.registry.resolve())
    args.output.resolve().parent.mkdir(parents=True, exist_ok=True)
    args.output.resolve().write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"{result['summary']['chapter_scale_ready_count']} chapter-scale-ready sequences; wrote {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
