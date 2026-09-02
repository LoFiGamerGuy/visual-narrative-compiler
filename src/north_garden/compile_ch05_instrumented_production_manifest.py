"""Compile the selected CH05 evidence into one fail-closed, non-promotional production handoff."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "production/comic/run-manifests/ch05-instrumented-production-manifest-r1.json"
PLANS = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"
ASSEMBLY = ROOT / "production/comic/assembly/ch05-variable-cadence-assembly-r1.json"
INITIAL = ROOT / "docs/research/evidence/ch05-overnight-production-r1.json"
HARDENING = ROOT / "docs/research/evidence/ch05-cadence-hardening-r1.json"
STYLE = ROOT / "production/comic/style-direction/ch05-mill-signal-r8.json"
MODEL_REGISTRY = ROOT / "docs/research/model-license-registry.md"

INPUT_PATHS = [
    "production/comic/ch05-sc01-panel-plans-v1.json",
    "production/comic/assembly/ch05-variable-cadence-assembly-r1.json",
    "production/comic/style-direction/ch05-mill-signal-r8.json",
    "docs/research/evidence/ch05-overnight-production-r1.json",
    "docs/research/evidence/ch05-cadence-hardening-r1.json",
    "docs/research/evidence/ch05-variable-cadence-assembly-r1.json",
    "docs/research/evidence/ch05-transparent-lettering-rehearsal-r1.json",
    "docs/research/evidence/ch05-lettering-width-copy-sensitivity-r1.json",
    "docs/research/evidence/ch05-outside-art-lettering-band-r1.json",
    "docs/research/model-license-registry.md",
]

REPRODUCERS = [
    ("build cadence assembly", "src/north_garden/build_ch05_variable_cadence_assembly.py"),
    ("export cadence evidence", "src/north_garden/export_ch05_variable_cadence_assembly_evidence.py"),
    ("validate cadence evidence", "src/north_garden/validate_ch05_variable_cadence_assembly.py"),
    ("build opacity rehearsal", "src/north_garden/build_ch05_transparent_lettering_rehearsal.py"),
    ("export opacity evidence", "src/north_garden/export_ch05_transparent_lettering_evidence.py"),
    ("validate opacity evidence", "src/north_garden/validate_ch05_transparent_lettering_rehearsal.py"),
    ("build width/copy sweep", "src/north_garden/build_ch05_lettering_width_copy_sensitivity.py"),
    ("export width/copy evidence", "src/north_garden/export_ch05_lettering_width_copy_evidence.py"),
    ("validate width/copy evidence", "src/north_garden/validate_ch05_lettering_width_copy_sensitivity.py"),
    ("build outside-art alternatives", "src/north_garden/build_ch05_outside_art_lettering_band.py"),
    ("export outside-art evidence", "src/north_garden/export_ch05_outside_art_lettering_band_evidence.py"),
    ("validate outside-art evidence", "src/north_garden/validate_ch05_outside_art_lettering_band.py"),
    ("compile production handoff", "src/north_garden/compile_ch05_instrumented_production_manifest.py"),
    ("validate production handoff", "src/north_garden/validate_ch05_instrumented_production_manifest.py"),
]

LETTERING = {
    "c005": {"recommended_mode": "SILENT_TRANSITION_AT_CURRENT_WIDTH", "reason": "Current 720px footprint misses tested 13px type; full-width art or outside-art caption requires a plan/assembly revision."},
    "c013": {"recommended_mode": "LIGHT_OUTSIDE_ART_CAPTION_OPTION_REQUIRES_PLAN_REVISION", "reason": "Deduction beat can retain 760px portrait art with 13.975px caption geometry; attributed speech remains untested."},
    "c014": {"recommended_mode": "SILENT_OBJECT_INSERT_REQUIRED_CURRENT_PLAN", "reason": "Current safe zone overlaps a person; outside-art geometry is only a non-plan demonstration."},
    "h001": {"recommended_mode": "WIDE_LETTERED_ANCHOR_OPTION_REQUIRES_WIDTH_AND_FINAL_COPY", "reason": "One tested line needs 1120px and two need 1200px; current assembly width is 1040px."},
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()


def main() -> int:
    plans = json.loads(PLANS.read_text(encoding="utf-8"))
    assembly = json.loads(ASSEMBLY.read_text(encoding="utf-8"))
    initial = json.loads(INITIAL.read_text(encoding="utf-8"))
    hardening = json.loads(HARDENING.read_text(encoding="utf-8"))
    plan_map = {item["panel_id"]: item for item in plans["plans"]}
    candidate_map = {item["candidate_id"]: item for item in initial["candidates"] + hardening["candidates"]}
    compile_inputs = {path: sha(ROOT / path) for path in INPUT_PATHS}
    reproducer_records = []
    for label, path in REPRODUCERS:
        full = ROOT / path
        if not full.is_file():
            raise SystemExit(f"missing reproducer: {path}")
        reproducer_records.append({"label": label, "path": path, "sha256": sha(full), "command": f"python {path}"})
    rows = []
    for entry in assembly["entries"]:
        plan = plan_map[entry["panel_id"]]
        candidate = candidate_map[entry["candidate_id"]]
        if candidate["panel_id"] != entry["panel_id"] or candidate["output"]["sha256"] != entry["source_sha256"]:
            raise SystemExit(f"candidate/assembly binding mismatch: {entry['candidate_id']}")
        lettering = LETTERING.get(entry["candidate_id"], {
            "recommended_mode": "PENDING_FINAL_SCRIPT_NO_LETTERING_EXECUTION",
            "reason": "Final copy, copy length, speaker semantics, and exact panel treatment are not bound."
        })
        rows.append({
            "order": entry["order"], "sequence_id": entry["sequence_id"], "panel_id": entry["panel_id"],
            "plan_revision_id": plan["plan_revision_id"], "plan_canonical_sha256": canonical_sha(plan),
            "development_panel_id": plan["development_panel_id"], "narrative_beat": plan["narrative_beat"],
            "visible_adult_cast": plan["visible_adult_cast"], "spatial_mode": plan["spatial_mode"],
            "candidate_id": entry["candidate_id"], "style_id": candidate["style_id"], "cadence_role": entry["cadence_role"],
            "source_path": entry["source_path"], "source_sha256": entry["source_sha256"], "source_dimensions": entry["source_dimensions"],
            "prompt_sha256": candidate["prompt_sha256"], "input_references": candidate["input_references"],
            "generation": {
                "tool_mode": candidate["execution"]["tool_mode"], "elapsed_seconds": candidate["execution"]["elapsed_seconds"],
                "model": candidate["execution"]["model"], "endpoint": candidate["execution"]["endpoint"],
                "provider_request_id": candidate["execution"]["provider_request_id"], "usage": candidate["execution"]["usage"],
                "cost_usd": candidate["execution"]["cost_usd"], "deterministic_seed": None
            },
            "engineering_review": candidate["engineering_review"], "selection_state": entry["selection_state"],
            "layout": {"target_width": entry["target_width"], "alignment": entry["alignment"], "gutter_after": entry["gutter_after"]},
            "lettering": {**lettering, "final_copy": None, "speaker_binding": None, "tail_geometry": None, "phone_type_validated_for_final_copy": False},
            "gates": {
                "owner_candidate_acceptance": False, "commercial_clearance": False, "generation_reproducible": False,
                "final_copy_bound": False, "lettering_plan_validated": False, "sequence_acceptance": False,
                "production_base_eligible": False, "executable": False
            }
        })
    row_root = canonical_sha(rows)
    reference_hashes = sorted({ref["sha256"] for row in rows for ref in row["input_references"]})
    manifest = {
        "record_type": "ComicInstrumentedProductionHandoffManifest", "schema_version": "1.0",
        "record_id": "ng-ch05-instrumented-production-handoff-r1",
        "state": "REVIEW_READY_NONEXECUTABLE_OWNER_DECISIONS_PENDING",
        "medium": "comic", "comic_panel_plan_collection": PLANS.relative_to(ROOT).as_posix(),
        "comic_panel_plan_revision_created": False, "assembly_revision_created": False,
        "animation_shot_plan": None, "e_conte": None,
        "compile_inputs": compile_inputs, "reproducers": reproducer_records,
        "style_direction": {"path": STYLE.relative_to(ROOT).as_posix(), "sha256": sha(STYLE), "record_id": json.loads(STYLE.read_text(encoding="utf-8"))["record_id"]},
        "model_license_registry": {"path": MODEL_REGISTRY.relative_to(ROOT).as_posix(), "sha256": sha(MODEL_REGISTRY), "built_in_status": "FICTIONAL_FRONTIER_ART_RESEARCH_ONLY_PROVENANCE_LIMITED"},
        "authorized_reference_hashes_observed": reference_hashes,
        "summary": {
            "selected_panel_count": len(rows), "sequence_count": len({row["sequence_id"] for row in rows}),
            "distinct_comic_panel_plans": len({row["panel_id"] for row in rows}), "distinct_styles": len({row["style_id"] for row in rows}),
            "engineering_selected_sources": len(rows), "owner_accepted_sources": 0, "commercially_cleared_sources": 0,
            "lettering_ready_panels": 0, "executable_panels": 0, "accepted_sequences": 0,
            "provider_calls_for_compilation": 0, "uploads_for_compilation": 0, "cost_usd_for_compilation": 0,
            "human_review_minutes": None
        },
        "rows": rows, "row_root_sha256": row_root,
        "owner_decisions_required": [
            "Accept/reject/reroll each exact selected candidate; engineering selection is not owner acceptance.",
            "Accept/revise the variable width/alignment/gutter cadence and mixed finish-density rhythm.",
            "Bind final CH05 copy and choose balloon, caption, direct-text, or silent semantics in ComicPanelPlan revisions where needed.",
            "Resolve production/commercial eligibility for the provenance-limited built-in outputs before exact-base promotion.",
            "Record review minutes and sequence-level acceptance decisions."
        ],
        "next_high_information_step": "Build a deterministic local reviewer index over every packet and strongest candidate, then collect exact owner decisions before any production-plan promotion.",
        "boundaries": [
            "All 14 rows are nonexecutable because owner acceptance, commercial clearance, final copy, and lettering-plan validation are absent.",
            "No generated pixel is tracked; source art and derived review artifacts remain ignored.",
            "Compilation performs no provider call, upload, budget reservation, purchase, model download, or external action.",
            "ComicPanelPlan is the only active production-planning structure; AnimationShotPlan and E-Conte remain null.",
            "Frozen v2.1.1 and baseline_legacy are outside this compiler and must remain unchanged."
        ]
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(manifest, indent=2) + "\n")
    print(f"compiled CH05 instrumented handoff: {len(rows)} rows / root {row_root}; 0 executable/accepted; {OUTPUT.relative_to(ROOT)} {sha(OUTPUT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
