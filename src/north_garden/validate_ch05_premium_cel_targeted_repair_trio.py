"""Validate the CH05 P001/P032/P039 targeted-repair preflight manifest."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "production/comic/run-manifests/ch05-premium-cel-targeted-repair-trio-r1.json"
PLANS = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"
GATES = ROOT / "production/comic/contracts/ch05-cross-panel-semantic-gates-r1.json"
PROFILE = ROOT / "production/comic/continuity/ch05-fictional-adult-visual-profile-r1.json"
PREMIUM_ARM = ROOT / "production/comic/run-manifests/ch05-complete-chapter-premium-cel-prompt-manifest-r1.json"
EXPECTED_ORDERS = [1, 32, 39]
EXPECTED_REFERENCE_IDS = ["p050_dual_identity_action", "p040_sigrid_face"]
EXPECTED_REFERENCE_HASHES = [
    "cb1e7b496397ff0f37c07c241b7a4b5beec137d3d26c48c3cbfad60734b8c83d",
    "c0a2be11cc9a51ecfbb490d490135df88e7b575b794240b002b1427ba64b6b4a",
]
EXPECTED_GATE_IDS = {
    1: ["cold_farmhouse_until_reversal", "departure_vector"],
    32: ["impossible_far_bank_prints"],
    39: ["third_upstream_mark"],
}
REQUIRED_REPAIR_TERMS = {
    1: (
        "left-to-right downhill-away",
        "physically behind both adults and upslope",
        "backs, gazes, torsos, and leading feet point downhill",
        "no smoke, glow, firelight, or lit panes",
    ),
    32: (
        "near bank",
        "far dry bank",
        "asymmetric heel and toe shape pointing back toward Soren and camera",
        "No footprints or footprint-like marks appear on the near bank",
    ),
    39: (
        "simultaneously shows exactly one square farmhouse symbol, one circle mill symbol, and one distinct third upstream mark",
        "one uninterrupted paper surface",
        "fingertip stops exactly on the third torn-edge mark",
        "no written words, labels, legend",
    ),
}
STYLE_TERMS = (
    "Premium cel-painted / clean graphic hybrid",
    "broad clean shapes",
    "low microtexture",
    "phone-width clarity",
    "Fictional mature adults only",
    "No child-coded features",
    "No text:",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def validate(document: dict[str, Any], verify_files: bool = True) -> list[str]:
    errors: list[str] = []

    def check(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    check(document.get("record_type") == "CH05PremiumCelTargetedRepairTrioPreflightManifest", "record_type")
    check(document.get("schema_version") == "1.0", "schema_version")
    check(document.get("record_id") == "ng-ch05-premium-cel-targeted-repair-trio-r1", "record_id")
    check(document.get("state") == "EXACT_PROMPTS_COMPILED_NOT_EXECUTED", "state")
    check(document.get("medium") == "comic", "medium")
    check(
        document.get("planning_structure") == "ComicPanelPlan"
        and document.get("animation_shot_plan") is None
        and document.get("e_conte") is None,
        "planning boundary",
    )

    coverage = document.get("coverage", {})
    check(
        coverage
        == {
            "comic_panel_plans": 3,
            "panel_orders": EXPECTED_ORDERS,
            "standalone_requests": 3,
            "planned_outputs": 3,
            "outputs_per_request": 1,
            "references_per_request": 2,
            "planned_reference_uses": 6,
            "cross_panel_gates": 4,
            "gate_phrase_bindings": 4,
        },
        "coverage",
    )
    check(document.get("authorized_reference_ids") == EXPECTED_REFERENCE_IDS, "reference id allowlist")
    check(document.get("authorized_reference_hashes") == EXPECTED_REFERENCE_HASHES, "reference hash allowlist")

    plan_doc = json.loads(PLANS.read_text(encoding="utf-8"))
    gate_doc = json.loads(GATES.read_text(encoding="utf-8"))
    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    plan_by_order = {row["display_order"]: row for row in plan_doc["plans"]}
    gate_by_id = {row["gate_id"]: row for row in gate_doc["gates"]}
    profile_refs = {row["reference_id"]: row for row in profile["authorized_references"]}

    requests = document.get("requests", [])
    check([row.get("display_order") for row in requests] == EXPECTED_ORDERS, "request order and denominator")
    check(canonical_sha256(requests) == document.get("request_root_sha256"), "request root")
    check(sum(row.get("reference_use_count", 0) for row in requests) == 6, "reference use total")
    check(sum(len(row.get("cross_panel_gate_bindings", [])) for row in requests) == 4, "gate binding total")
    check(len({row.get("planned_output") for row in requests}) == 3, "one unique output per request")

    for row in requests:
        order = row.get("display_order")
        if order not in EXPECTED_ORDERS:
            continue
        plan = plan_by_order[order]
        prompt = row.get("prompt_text", "")
        check(row.get("panel_id") == plan["panel_id"], f"panel id P{order:03d}")
        check(row.get("comic_panel_plan_revision_id") == plan["plan_revision_id"], f"plan revision P{order:03d}")
        check(row.get("comic_panel_plan_canonical_sha256") == canonical_sha256(plan), f"plan hash P{order:03d}")
        check(row.get("comic_panel_plan_revision_created") is False, f"no plan revision P{order:03d}")
        check(row.get("narrative_beat") == plan["narrative_beat"], f"narrative beat P{order:03d}")
        check(row.get("composition_intent") == plan["composition_intent"], f"composition P{order:03d}")
        check(row.get("visible_adult_cast") == plan["visible_adult_cast"], f"cast P{order:03d}")
        check(row.get("lettering_safe_zones") == plan["comic_direction"]["lettering"]["safe_zones"], f"safe zone P{order:03d}")
        check(
            prompt == "\n".join(row.get("prompt_lines", []))
            and hashlib.sha256(prompt.encode("utf-8")).hexdigest() == row.get("prompt_sha256"),
            f"prompt binding P{order:03d}",
        )
        for term in STYLE_TERMS + REQUIRED_REPAIR_TERMS[order]:
            check(term in prompt, f"required prompt term P{order:03d}:{term}")

        references = row.get("input_references", [])
        check([item.get("reference_id") for item in references] == EXPECTED_REFERENCE_IDS, f"reference order P{order:03d}")
        check(row.get("reference_use_count") == 2 and len(references) == 2, f"two references P{order:03d}")
        for reference in references:
            reference_id = reference.get("reference_id")
            expected = profile_refs.get(reference_id)
            check(reference == expected, f"profile reference binding P{order:03d}:{reference_id}")
            if verify_files and expected is not None:
                path = ROOT / expected["path"]
                check(path.is_file() and sha256(path) == expected["sha256"], f"reference file P{order:03d}:{reference_id}")

        bindings = row.get("cross_panel_gate_bindings", [])
        check([item.get("gate_id") for item in bindings] == EXPECTED_GATE_IDS[order], f"gate ids P{order:03d}")
        for binding in bindings:
            gate = gate_by_id.get(binding.get("gate_id"), {})
            expected_phrase = gate.get("required_prompt_phrases", {}).get(plan["panel_id"])
            check(
                binding.get("panel_id") == plan["panel_id"]
                and binding.get("required_prompt_phrase") == expected_phrase
                and isinstance(expected_phrase, str)
                and expected_phrase in prompt,
                f"gate phrase P{order:03d}:{binding.get('gate_id')}",
            )

        expected_output = (
            "experiments/review-packets/ch05-premium-cel-targeted-repair-trio-r1/source-panels/"
            f"P{order:03d}-premium-cel-clean-graphic-hybrid-r1.png"
        )
        check(row.get("planned_output") == expected_output, f"planned output P{order:03d}")
        if verify_files:
            ignored = subprocess.run(
                ["git", "check-ignore", "-q", expected_output], cwd=ROOT, check=False
            ).returncode == 0
            check(ignored, f"planned output is not ignored P{order:03d}")
        check(
            all(
                row.get(key) is None
                for key in (
                    "execution",
                    "output",
                    "render_record",
                    "provider_model",
                    "provider_endpoint",
                    "provider_request_id",
                    "provider_usage",
                    "provider_cost_usd",
                    "elapsed_seconds",
                    "human_review_minutes",
                )
            ),
            f"null execution/provider fields P{order:03d}",
        )
        check(
            row.get("human_review_state") == "PENDING_NOT_RENDERED"
            and row.get("accepted") is False
            and row.get("commercially_cleared") is False
            and row.get("exact_production_base") is False,
            f"review/promotion boundary P{order:03d}",
        )

    preflight = document.get("execution_preflight", {})
    check(
        preflight
        == {
            "compiler_complete": True,
            "validator_required_before_generation": True,
            "generation_started": False,
            "current_reference_uploads": 0,
            "current_provider_calls": 0,
            "current_outputs": 0,
            "current_spend_usd": 0,
        },
        "execution preflight boundary",
    )
    boundary = document.get("boundary", {})
    check(boundary.get("permitted_product") == "openai_builtin_imagegen", "permitted product")
    check(
        boundary.get("permitted_upload_class")
        == "two_exact_hash_pinned_project_generated_fictional_adult_references_only",
        "permitted upload class",
    )
    for key in (
        "direct_paid_provider_api_calls",
        "bfl_calls",
        "gemini_calls",
        "xai_calls",
        "new_upload_classes",
        "real_person_or_child_material",
        "training_or_publication_authority",
        "current_executions",
        "current_outputs",
        "accepted",
        "commercially_cleared",
        "exact_production_base",
    ):
        check(boundary.get(key) == 0, f"boundary:{key}")

    expected_sources = [
        {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path)}
        for path in (PLANS, GATES, PROFILE, PREMIUM_ARM)
    ]
    check(document.get("sources") == expected_sources, "source list")
    if verify_files:
        for source in document.get("sources", []):
            path = ROOT / source.get("path", "")
            check(path.is_file() and sha256(path) == source.get("sha256"), f"source binding:{source.get('path')}")
    return errors


def self_test(document: dict[str, Any]) -> tuple[int, int]:
    mutations: list[Callable[[dict[str, Any]], None]] = [
        lambda value: value.__setitem__("state", "EXECUTED"),
        lambda value: value.__setitem__("planning_structure", "AnimationShotPlan"),
        lambda value: value.__setitem__("e_conte", {}),
        lambda value: value["coverage"].__setitem__("planned_reference_uses", 5),
        lambda value: value["requests"].pop(),
        lambda value: value["requests"][0].__setitem__("comic_panel_plan_revision_id", "tampered"),
        lambda value: value["requests"][0].__setitem__("comic_panel_plan_canonical_sha256", "0" * 64),
        lambda value: value["requests"][0].__setitem__("prompt_text", "tampered"),
        lambda value: value["requests"][0]["prompt_lines"].pop(),
        lambda value: value["requests"][0]["input_references"][0].__setitem__("sha256", "0" * 64),
        lambda value: value["requests"][1]["input_references"].pop(),
        lambda value: value["requests"][1]["cross_panel_gate_bindings"].pop(),
        lambda value: value["requests"][2]["cross_panel_gate_bindings"][0].__setitem__("required_prompt_phrase", "tampered"),
        lambda value: value["requests"][2].__setitem__("planned_output", "experiments/wrong.png"),
        lambda value: value["requests"][0].__setitem__("execution", {}),
        lambda value: value["requests"][0].__setitem__("accepted", True),
        lambda value: value["execution_preflight"].__setitem__("generation_started", True),
        lambda value: value["boundary"].__setitem__("direct_paid_provider_api_calls", 1),
        lambda value: value["boundary"].__setitem__("new_upload_classes", 1),
        lambda value: value["boundary"].__setitem__("real_person_or_child_material", 1),
    ]
    caught = 0
    for mutation in mutations:
        candidate = copy.deepcopy(document)
        mutation(candidate)
        caught += bool(validate(candidate, verify_files=False))
    return caught, len(mutations)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    document = json.loads(MANIFEST.read_text(encoding="utf-8"))
    errors = validate(document)
    caught = total = 0
    if args.self_test:
        caught, total = self_test(document)
        if caught != total:
            errors.append(f"self-test {caught}/{total}")
    print(
        json.dumps(
            {
                "status": "PASS" if not errors else "FAIL",
                "errors": errors,
                "plans": document.get("coverage", {}).get("comic_panel_plans"),
                "requests": len(document.get("requests", [])),
                "planned_outputs": document.get("coverage", {}).get("planned_outputs"),
                "reference_uses": sum(row.get("reference_use_count", 0) for row in document.get("requests", [])),
                "gate_bindings": sum(
                    len(row.get("cross_panel_gate_bindings", [])) for row in document.get("requests", [])
                ),
                "provider_calls": document.get("execution_preflight", {}).get("current_provider_calls"),
                "self_test": f"{caught}/{total}" if args.self_test else None,
            },
            sort_keys=True,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
