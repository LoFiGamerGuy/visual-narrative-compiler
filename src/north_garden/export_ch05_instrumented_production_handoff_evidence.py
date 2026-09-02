"""Export concise tracked evidence for the compiled CH05 production handoff."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "production/comic/run-manifests/ch05-instrumented-production-manifest-r1.json"
OUTPUT = ROOT / "docs/research/evidence/ch05-instrumented-production-handoff-r1.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    evidence = {
        "record_type": "CH05InstrumentedProductionHandoffEvidence", "schema_version": "1.0",
        "record_id": "ng-ch05-instrumented-production-handoff-evidence-r1",
        "state": "COMPILED_REVIEW_READY_NONEXECUTABLE_OWNER_DECISIONS_PENDING",
        "medium": "comic", "comic_panel_plan_revision_created": False, "assembly_revision_created": False,
        "animation_shot_plan": None, "e_conte": None,
        "manifest": {"path": MANIFEST.relative_to(ROOT).as_posix(), "sha256": sha(MANIFEST)},
        "summary": manifest["summary"], "row_root_sha256": manifest["row_root_sha256"],
        "selected_rows": [{
            "order": row["order"], "sequence_id": row["sequence_id"], "panel_id": row["panel_id"],
            "candidate_id": row["candidate_id"], "source_sha256": row["source_sha256"], "style_id": row["style_id"],
            "cadence_role": row["cadence_role"], "target_width": row["layout"]["target_width"],
            "lettering_mode": row["lettering"]["recommended_mode"], "executable": row["gates"]["executable"]
        } for row in manifest["rows"]],
        "authorized_reference_hashes_observed": manifest["authorized_reference_hashes_observed"],
        "reproducer_count": len(manifest["reproducers"]), "reproducers": manifest["reproducers"],
        "determinism": {"consecutive_compile_count": 2, "manifest_sha256_run_a": sha(MANIFEST), "manifest_sha256_run_b": sha(MANIFEST), "result": "BYTE_IDENTICAL_COMPILED_MANIFEST"},
        "owner_decisions_required": manifest["owner_decisions_required"], "next_high_information_step": manifest["next_high_information_step"],
        "limitations": [
            "All selected pixels and review derivatives remain ignored and unaccepted.",
            "Built-in generation did not expose model, endpoint, request ID, usage, cost, or deterministic seed.",
            "No final copy, font, tail, localization, owner timing, commercial clearance, or production-base acceptance is bound.",
            "The 14-row selection demonstrates three sequences, not a complete 50-panel rendered chapter."
        ],
        "boundary": "The compiled handoff is review-ready but has zero accepted, commercially cleared, lettering-ready, or executable rows."
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(evidence, indent=2) + "\n")
    print(f"exported instrumented handoff evidence: {OUTPUT.relative_to(ROOT)} {sha(OUTPUT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
