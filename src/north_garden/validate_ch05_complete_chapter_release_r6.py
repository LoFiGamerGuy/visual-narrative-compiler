"""Validate the frozen CH05 r6 release and its ignored local review artifacts."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
RELEASE = ROOT / "docs/research/evidence/ch05-complete-chapter-release-r6.json"
ALLOWED_REFERENCE_HASHES = {
    "cb1e7b496397ff0f37c07c241b7a4b5beec137d3d26c48c3cbfad60734b8c83d",
    "c0a2be11cc9a51ecfbb490d490135df88e7b575b794240b002b1427ba64b6b4a",
    "50f6413eeab39f35da00524a79c6e71d821f6b84da939487575324c4ad7743eb",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(document: dict[str, Any], *, verify_files: bool = True) -> list[str]:
    errors: list[str] = []
    expect = lambda condition, message: None if condition else errors.append(message)
    expect(document.get("record_type") == "CH05CompleteChapterReviewRelease", "record_type")
    expect(document.get("state") == "FROZEN_REVIEW_CANDIDATE_UNACCEPTED", "state")
    expect(document.get("planning_structure") == "ComicPanelPlan", "planning_structure")
    expect(document.get("animation_shot_plan") is None, "animation_shot_plan")
    expect(document.get("e_conte") is None, "e_conte")
    measured = document.get("measured_summary", {})
    expected_counts = {
        "comic_panel_plans": 50, "selected_chapter_panels": 50,
        "built_in_raster_outputs": 16, "panel_level_candidates": 59,
        "authorized_reference_uses": 34, "unique_authorized_reference_hashes": 3,
        "human_reviewed": 0, "accepted": 0, "commercially_cleared": 0,
        "exact_production_base": 0, "direct_paid_api_cloud_spend_usd": 0,
    }
    for key, value in expected_counts.items():
        expect(measured.get(key) == value, f"measured_summary.{key}")
    expect(measured.get("human_review_minutes") is None, "human_review_minutes")
    expect(measured.get("built_in_product_monetary_cost_usd") is None, "built_in cost")
    expect(measured.get("agent_triage") == {"pass": 49, "warn": 1, "fail": 0, "gating": False}, "agent_triage")
    expect(measured.get("remaining_warning_panel_ids") == ["ng-ch05-sc01-p032"], "remaining warning")
    expect(measured.get("unique_execution_elapsed_sum_seconds") == 1592.908, "execution elapsed sum")
    expect(measured.get("approximate_unique_client_generation_wall_seconds") == 1200.7, "wall seconds")
    provider = document.get("provider_disclosure", {})
    expect(provider.get("product") == "openai_builtin_imagegen", "provider product")
    for key in ("model", "endpoint", "provider_request_ids", "provider_usage", "provider_cost_usd", "seed"):
        expect(provider.get(key) is None, f"provider_disclosure.{key}")
    expect(provider.get("direct_paid_provider_api_calls") == 0, "direct API calls")
    expect(provider.get("external_uploads_beyond_authorized_hashes") == 0, "external uploads")
    owner = document.get("owner_review_state", {})
    expect(owner.get("human_reviewed") is False, "owner human_reviewed")
    expect(owner.get("accepted_candidate_ids") == [], "accepted candidate ids")
    bindings = document.get("source_bindings", [])
    expect(len(bindings) == 17, "source binding count")
    artifacts = document.get("review_artifacts", [])
    expect(len(artifacts) == 8, "review artifact count")
    expect(len({row.get("kind") for row in artifacts}) == 8, "unique artifact kinds")
    if verify_files:
        for row in bindings:
            path = ROOT / row.get("path", "")
            expect(path.is_file(), f"binding missing: {row.get('path')}")
            if path.is_file():
                expect(sha256(path) == row.get("sha256"), f"binding hash: {row.get('path')}")
        for row in artifacts:
            path = ROOT / row.get("path", "")
            expect(path.is_file(), f"artifact missing: {row.get('path')}")
            if not path.is_file():
                continue
            expect(sha256(path) == row.get("sha256"), f"artifact hash: {row.get('path')}")
            with Image.open(path) as image:
                expect(list(image.size) == [row.get("width_px"), row.get("height_px")], f"artifact dimensions: {row.get('path')}")
            expect(path.stat().st_size == row.get("bytes"), f"artifact bytes: {row.get('path')}")
            rel = row["path"]
            ignored = subprocess.run(["git", "check-ignore", "-q", "--", rel], cwd=ROOT).returncode == 0
            tracked = subprocess.run(["git", "ls-files", "--error-unmatch", "--", rel], cwd=ROOT, capture_output=True).returncode == 0
            expect(ignored, f"artifact not ignored: {rel}")
            expect(not tracked, f"artifact tracked: {rel}")
        production = json.loads((ROOT / "production/comic/run-manifests/ch05-complete-chapter-production-manifest-r6.json").read_text(encoding="utf-8"))
        expect(set(production["provider_policy"]["uploaded_reference_hashes"]) == ALLOWED_REFERENCE_HASHES, "reference allowlist")
    return errors


def self_test(document: dict[str, Any]) -> tuple[int, int]:
    mutations = [
        ("state", lambda d: d.__setitem__("state", "ACCEPTED")),
        ("planning", lambda d: d.__setitem__("planning_structure", "AnimationShotPlan")),
        ("animation", lambda d: d.__setitem__("animation_shot_plan", {})),
        ("count", lambda d: d["measured_summary"].__setitem__("selected_chapter_panels", 49)),
        ("triage", lambda d: d["measured_summary"].__setitem__("agent_triage", {"pass": 50, "warn": 0, "fail": 0, "gating": False})),
        ("accept", lambda d: d["measured_summary"].__setitem__("accepted", 1)),
        ("cost", lambda d: d["measured_summary"].__setitem__("built_in_product_monetary_cost_usd", 0)),
        ("model", lambda d: d["provider_disclosure"].__setitem__("model", "invented")),
        ("owner", lambda d: d["owner_review_state"].__setitem__("human_reviewed", True)),
        ("artifact", lambda d: d["review_artifacts"].pop()),
    ]
    caught = 0
    for _, mutate in mutations:
        candidate = copy.deepcopy(document)
        mutate(candidate)
        caught += bool(validate(candidate, verify_files=False))
    return caught, len(mutations)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    document = json.loads(RELEASE.read_text(encoding="utf-8"))
    errors = validate(document)
    caught = total = 0
    if args.self_test:
        caught, total = self_test(document)
        if caught != total:
            errors.append(f"self-test caught {caught}/{total}")
    print(json.dumps({"status": "PASS" if not errors else "FAIL", "errors": errors, "bindings": len(document.get("source_bindings", [])), "artifacts": len(document.get("review_artifacts", [])), "self_test": f"{caught}/{total}" if args.self_test else None}, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
