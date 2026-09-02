"""Validate the compiled CH05 production handoff and fail closed on promotion or boundary drift."""
from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "production/comic/run-manifests/ch05-instrumented-production-manifest-r1.json"
PLANS = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"

AUTHORIZED = {
    "cb1e7b496397ff0f37c07c241b7a4b5beec137d3d26c48c3cbfad60734b8c83d",
    "c0a2be11cc9a51ecfbb490d490135df88e7b575b794240b002b1427ba64b6b4a",
    "50f6413eeab39f35da00524a79c6e71d821f6b84da939487575324c4ad7743eb",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()


def semantic_errors(data: dict) -> list[str]:
    out = []
    summary = data.get("summary", {})
    if (summary.get("selected_panel_count"), summary.get("sequence_count"), summary.get("distinct_comic_panel_plans")) != (14, 3, 14):
        out.append("denominator invalid")
    zero_fields = ["owner_accepted_sources", "commercially_cleared_sources", "lettering_ready_panels", "executable_panels", "accepted_sequences", "provider_calls_for_compilation", "uploads_for_compilation", "cost_usd_for_compilation"]
    if any(summary.get(field) != 0 for field in zero_fields) or summary.get("human_review_minutes") is not None:
        out.append("promotion/activity/review fabricated")
    if data.get("comic_panel_plan_revision_created") is not False or data.get("assembly_revision_created") is not False or data.get("animation_shot_plan") is not None or data.get("e_conte") is not None:
        out.append("planning boundary invalid")
    rows = data.get("rows", [])
    if len(rows) != 14 or [row.get("order") for row in rows] != list(range(1, 15)):
        out.append("row/order coverage invalid")
    if len({row.get("candidate_id") for row in rows}) != 14 or len({row.get("panel_id") for row in rows}) != 14:
        out.append("row uniqueness invalid")
    if data.get("row_root_sha256") != canonical_sha(rows):
        out.append("row root invalid")
    if any(any(value is not False for value in row.get("gates", {}).values()) for row in rows):
        out.append("row gate promoted")
    if any(row.get("lettering", {}).get("final_copy") is not None or row.get("lettering", {}).get("phone_type_validated_for_final_copy") is not False for row in rows):
        out.append("final lettering fabricated")
    return sorted(set(out))


def main() -> int:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    plans = json.loads(PLANS.read_text(encoding="utf-8"))
    plan_map = {item["panel_id"]: item for item in plans["plans"]}
    failures = semantic_errors(data)
    for path, expected in data["compile_inputs"].items():
        full = ROOT / path
        if not full.is_file() or sha(full) != expected:
            failures.append(f"compile input mismatch: {path}")
    for item in data["reproducers"]:
        path = ROOT / item["path"]
        if not path.is_file() or sha(path) != item["sha256"] or item["command"] != f"python {item['path']}":
            failures.append(f"reproducer mismatch: {item['path']}")
    if set(data["authorized_reference_hashes_observed"]) - AUTHORIZED:
        failures.append("unauthorized reference hash observed")
    for row in data["rows"]:
        plan = plan_map.get(row["panel_id"])
        if plan is None or canonical_sha(plan) != row["plan_canonical_sha256"] or plan["plan_revision_id"] != row["plan_revision_id"]:
            failures.append(f"plan mismatch: {row['panel_id']}")
        path = ROOT / row["source_path"]
        if not path.is_file() or sha(path) != row["source_sha256"]:
            failures.append(f"source mismatch: {row['candidate_id']}")
        elif subprocess.run(["git", "check-ignore", "-q", str(path)], cwd=ROOT, check=False).returncode:
            failures.append(f"source pixel not ignored: {row['candidate_id']}")
        generation = row["generation"]
        if any(generation[field] is not None for field in ("model", "endpoint", "provider_request_id", "usage", "cost_usd", "deterministic_seed")):
            failures.append(f"unavailable generation metadata fabricated: {row['candidate_id']}")
    if data["model_license_registry"]["built_in_status"] != "FICTIONAL_FRONTIER_ART_RESEARCH_ONLY_PROVENANCE_LIMITED":
        failures.append("commercial/provenance status changed")
    mutations = [
        lambda d: d["summary"].update(selected_panel_count=13), lambda d: d["summary"].update(sequence_count=2),
        lambda d: d["summary"].update(owner_accepted_sources=1), lambda d: d["summary"].update(commercially_cleared_sources=1),
        lambda d: d["summary"].update(lettering_ready_panels=1), lambda d: d["summary"].update(executable_panels=1),
        lambda d: d["summary"].update(provider_calls_for_compilation=1), lambda d: d["summary"].update(human_review_minutes=1),
        lambda d: d.update(comic_panel_plan_revision_created=True), lambda d: d["rows"].pop(),
        lambda d: d["rows"][1].update(candidate_id=d["rows"][0]["candidate_id"]),
        lambda d: d["rows"][0]["gates"].update(owner_candidate_acceptance=True),
        lambda d: d["rows"][0]["lettering"].update(final_copy="fabricated"),
        lambda d: d.update(row_root_sha256="0" * 64), lambda d: d.update(animation_shot_plan={})
    ]
    rejected = 0
    for mutation in mutations:
        changed = copy.deepcopy(data); mutation(changed); rejected += bool(semantic_errors(changed))
    if rejected != len(mutations): failures.append(f"only {rejected}/{len(mutations)} mutations rejected")
    print(f"CH05 instrumented production handoff: {len(failures)} failures; 14 rows/3 sequences/14 plans; {rejected}/{len(mutations)} mutations rejected")
    print("0 accepted/commercial/lettering-ready/executable; exact prompts/sources/refs/cadence/lettering gates bound; 0 calls/uploads/$0")
    for failure in failures: print(f"FAIL: {failure}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
