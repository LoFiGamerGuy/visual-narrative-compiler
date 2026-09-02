"""Fail-closed validator for a complete CH05 comic production/review bundle.

The validator is intentionally local. It verifies provenance and review-state
claims but performs no provider request, upload, acceptance, or rights decision.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = ROOT / "production/comic/run-manifests/ch05-complete-chapter-production-manifest-r1.json"
PLAN_PATH = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"
CATALOG_PATH = ROOT / "docs/research/evidence/fixtures/ch05-complete-chapter-validator-r1/mutation-catalog.json"
HEX = set("0123456789abcdef")
REQUIRED_ARTIFACT_KINDS = {
    "chapter_scroll",
    "contact_sheet",
    "phone_preview",
    "lettering_overlay",
    "continuity_sheet",
}
REQUIRED_SERVICE_FIELDS = {
    "tool",
    "model",
    "endpoint",
    "request_id",
    "provider_usage",
    "provider_cost_usd",
    "seed",
    "unavailable_fields",
}
ALLOWLIST = {
    "experiments/review-packets/ch05-style-density-scale-exploration-r1/P050-wide-action-clean-graphic-r1.png": "cb1e7b496397ff0f37c07c241b7a4b5beec137d3d26c48c3cbfad60734b8c83d",
    "experiments/review-packets/ch05-style-density-scale-exploration-r1/P040-medium-close-cel-painted-r1.png": "c0a2be11cc9a51ecfbb490d490135df88e7b575b794240b002b1427ba64b6b4a",
    "experiments/review-packets/ch05-style-density-scale-exploration-r1/P036-tall-lever-clear-line-corrected-r1.png": "50f6413eeab39f35da00524a79c6e71d821f6b84da939487575324c4ad7743eb",
}
HAIR = {
    "soren": "light-brown to dark-blond; consistent cut and silhouette",
    "sigrid": "dark-brown to near-black; consistent cut and silhouette",
}
WARDROBE = {
    "soren": "pale oatmeal work coat",
    "sigrid": "practical plaid wrap",
}


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def is_sha(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and set(value) <= HEX


def rel_path(value: Any) -> Path | None:
    if not isinstance(value, str) or not value or Path(value).is_absolute():
        return None
    path = (ROOT / value).resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError:
        return None
    return path


def git_ok(args: list[str]) -> bool:
    return subprocess.run(
        ["git", *args], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False
    ).returncode == 0


def png_dimensions(path: Path) -> tuple[int, int] | None:
    header = path.read_bytes()[:24]
    if len(header) < 24 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        return None
    return int.from_bytes(header[16:20], "big"), int.from_bytes(header[20:24], "big")


def validate_generated_art(path_value: Any, expected_sha: Any, where: str, errors: list[str]) -> Path | None:
    path = rel_path(path_value)
    if path is None:
        errors.append(f"{where}: path must be repository-relative and contained")
        return None
    if not path.is_file():
        errors.append(f"{where}: artifact does not exist: {path_value}")
        return None
    if not is_sha(expected_sha) or sha_file(path) != expected_sha:
        errors.append(f"{where}: artifact SHA-256 mismatch")
    relative = path.relative_to(ROOT).as_posix()
    if git_ok(["ls-files", "--error-unmatch", "--", relative]):
        errors.append(f"{where}: generated-art path is tracked")
    if not git_ok(["check-ignore", "-q", "--", relative]):
        errors.append(f"{where}: generated-art path is not ignored")
    return path


def canonical_plans() -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    source = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    rows = sorted(source["plans"], key=lambda x: x["display_order"])
    return rows, {row["panel_id"]: row for row in rows}


def expected_zones(plan: dict[str, Any]) -> list[dict[str, Any]]:
    return plan["comic_direction"]["lettering"]["safe_zones"]


def validate_manifest(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["manifest root must be an object"]
    if data.get("record_type") != "CH05CompleteChapterProductionManifest":
        errors.append("record_type must be CH05CompleteChapterProductionManifest")
    if data.get("schema_version") != "1.0":
        errors.append("schema_version must be 1.0")
    state = data.get("state")
    if not isinstance(state, str) or any(token in state.upper() for token in ("ACCEPTED", "COMMERCIALLY_CLEARED", "EXACT_PRODUCTION_BASE")):
        errors.append("state is missing or overclaims acceptance/clearance/exact-base status")
    if data.get("medium") != "comic" or data.get("planning_structure") != "ComicPanelPlan":
        errors.append("production planning must be comic/ComicPanelPlan only")
    if data.get("animation_shot_plan") is not None:
        errors.append("animation_shot_plan must be null or absent")
    if data.get("e_conte") is not None:
        errors.append("e_conte must be null or absent")

    source = data.get("comic_panel_plan_source")
    expected_plan_path = PLAN_PATH.relative_to(ROOT).as_posix()
    if not isinstance(source, dict) or source.get("path") != expected_plan_path or source.get("sha256") != sha_file(PLAN_PATH):
        errors.append("comic_panel_plan_source path/hash mismatch")

    policy = data.get("provider_policy")
    if not isinstance(policy, dict):
        errors.append("provider_policy must be an object")
    else:
        if policy.get("permitted_product") != "openai_builtin_imagegen":
            errors.append("only OpenAI built-in ImageGen is permitted")
        if policy.get("external_provider_uploads") != 0:
            errors.append("external_provider_uploads must be zero")
        if policy.get("direct_paid_provider_api_calls") != 0:
            errors.append("direct_paid_provider_api_calls must be zero")
        uploaded = policy.get("uploaded_reference_hashes")
        if not isinstance(uploaded, list) or any(item not in ALLOWLIST.values() for item in uploaded):
            errors.append("uploaded_reference_hashes must be an allowlist-only array")

    allowlist = data.get("reference_allowlist")
    observed_allowlist: dict[str, str] = {}
    if not isinstance(allowlist, list):
        errors.append("reference_allowlist must be an array")
    else:
        for i, item in enumerate(allowlist):
            if not isinstance(item, dict):
                errors.append(f"reference_allowlist[{i}] must be an object")
                continue
            path, digest = item.get("path"), item.get("sha256")
            if item.get("provider_product") != "openai_builtin_imagegen" or item.get("data_class") != "fictional_adults":
                errors.append(f"reference_allowlist[{i}] has invalid product/data class")
            if isinstance(path, str) and isinstance(digest, str):
                observed_allowlist[path] = digest
        if observed_allowlist != ALLOWLIST:
            errors.append("reference_allowlist must equal the three hash-pinned fictional-adult references")
    for path_value, expected_hash in ALLOWLIST.items():
        path = ROOT / path_value
        if not path.is_file() or sha_file(path) != expected_hash:
            errors.append(f"authorized reference bytes missing or changed: {path_value}")

    plans, plan_by_id = canonical_plans()
    rows = data.get("panels")
    if not isinstance(rows, list):
        return errors + ["panels must be an array"]
    expected_ids = [item["panel_id"] for item in plans]
    ids = [item.get("panel_id") if isinstance(item, dict) else None for item in rows]
    orders = [item.get("display_order") if isinstance(item, dict) else None for item in rows]
    if ids != expected_ids:
        errors.append("panels must cover every approved ComicPanelPlan exactly once in canonical order")
    if orders != list(range(1, len(plans) + 1)):
        errors.append("panel display_order must be contiguous and canonical")
    if len(set(ids)) != len(ids):
        errors.append("panel_id values must be unique")

    for i, row in enumerate(rows):
        where = f"panels[{i}]"
        if not isinstance(row, dict):
            errors.append(f"{where} must be an object")
            continue
        panel_id = row.get("panel_id")
        plan = plan_by_id.get(panel_id)
        if plan is None:
            errors.append(f"{where}: unknown panel_id")
            continue
        if row.get("plan_revision_id") != plan["plan_revision_id"]:
            errors.append(f"{where}: plan_revision_id mismatch")
        status = row.get("status")
        if status not in {"RENDERED", "DIAGNOSTIC"}:
            errors.append(f"{where}: status must be RENDERED or DIAGNOSTIC")
        if status == "RENDERED":
            prompt = row.get("prompt_text")
            if not isinstance(prompt, str) or not prompt.strip():
                errors.append(f"{where}: rendered row requires exact prompt_text")
            elif row.get("prompt_sha256") != sha_bytes(prompt.encode("utf-8")):
                errors.append(f"{where}: prompt_sha256 mismatch")
            refs = row.get("input_references")
            if not isinstance(refs, list):
                errors.append(f"{where}: input_references must be an array")
            else:
                for j, ref in enumerate(refs):
                    if not isinstance(ref, dict):
                        errors.append(f"{where}.input_references[{j}] must be an object")
                        continue
                    path, digest = ref.get("path"), ref.get("sha256")
                    if ALLOWLIST.get(path) != digest:
                        errors.append(f"{where}.input_references[{j}]: reference path/hash is not allowed")
                    if ref.get("upload_target") != "openai_builtin_imagegen":
                        errors.append(f"{where}.input_references[{j}]: external upload target forbidden")
            candidate = row.get("candidate")
            if not isinstance(candidate, dict):
                errors.append(f"{where}: rendered row requires candidate object")
            else:
                artifact_path = validate_generated_art(candidate.get("path"), candidate.get("sha256"), f"{where}.candidate", errors)
                if not isinstance(candidate.get("width_px"), int) or candidate.get("width_px", 0) <= 0:
                    errors.append(f"{where}.candidate: invalid width_px")
                if not isinstance(candidate.get("height_px"), int) or candidate.get("height_px", 0) <= 0:
                    errors.append(f"{where}.candidate: invalid height_px")
                if artifact_path is not None:
                    dimensions = png_dimensions(artifact_path)
                    if dimensions is None:
                        errors.append(f"{where}.candidate: artifact must be a decodable PNG")
                    elif dimensions != (candidate.get("width_px"), candidate.get("height_px")):
                        errors.append(f"{where}.candidate: recorded dimensions do not match PNG IHDR")
                elapsed = candidate.get("elapsed_seconds")
                if isinstance(elapsed, bool) or not isinstance(elapsed, (int, float)) or elapsed < 0:
                    errors.append(f"{where}.candidate: invalid elapsed_seconds")
                service = candidate.get("service")
                if not isinstance(service, dict):
                    errors.append(f"{where}.candidate: service must be an object")
                else:
                    missing = REQUIRED_SERVICE_FIELDS - set(service)
                    if missing:
                        errors.append(f"{where}.candidate: missing service fields {sorted(missing)}")
                    unavailable = service.get("unavailable_fields")
                    if not isinstance(unavailable, list):
                        errors.append(f"{where}.candidate: unavailable_fields must be an array")
                    else:
                        for name in unavailable:
                            if name not in REQUIRED_SERVICE_FIELDS - {"tool", "unavailable_fields"}:
                                errors.append(f"{where}.candidate: unknown unavailable field {name}")
                            elif service.get(name) is not None:
                                errors.append(f"{where}.candidate: unavailable field {name} must be null")
                    if not isinstance(service.get("tool"), str) or not service.get("tool"):
                        errors.append(f"{where}.candidate: tool metadata is required")
            if row.get("diagnosis") is not None:
                errors.append(f"{where}: rendered row diagnosis must be null")
        elif status == "DIAGNOSTIC":
            if row.get("candidate") is not None:
                errors.append(f"{where}: diagnostic row candidate must be null")
            diagnosis = row.get("diagnosis")
            if not isinstance(diagnosis, dict) or any(not isinstance(diagnosis.get(k), str) or not diagnosis[k].strip() for k in ("code", "note", "next_action")):
                errors.append(f"{where}: diagnostic row requires code, note, and next_action")

        lettering = row.get("lettering_safe")
        if not isinstance(lettering, dict):
            errors.append(f"{where}: lettering_safe must be an object")
        else:
            if lettering.get("zones") != expected_zones(plan):
                errors.append(f"{where}: lettering-safe zones drift from ComicPanelPlan")
            protects = lettering.get("protects")
            required = {"faces", "people", "important_hands", "story_objects"}
            if not isinstance(protects, list) or not required <= set(protects):
                errors.append(f"{where}: lettering protection classes incomplete")
            if lettering.get("transparency_overlap_allowed_only_if_readable") is not True:
                errors.append(f"{where}: transparent overlap readability rule missing")
            if lettering.get("review_state") not in {"PENDING", "PASS", "WARN", "FAIL"}:
                errors.append(f"{where}: invalid lettering review_state")

        continuity = row.get("continuity")
        if not isinstance(continuity, dict):
            errors.append(f"{where}: continuity must be an object")
        else:
            if continuity.get("hair") != HAIR:
                errors.append(f"{where}: hair continuity contract mismatch")
            if continuity.get("wardrobe") != WARDROBE:
                errors.append(f"{where}: wardrobe continuity contract mismatch")
            if continuity.get("review_state") not in {"PENDING", "PASS", "WARN", "FAIL"}:
                errors.append(f"{where}: invalid continuity review_state")

        review = row.get("review")
        if not isinstance(review, dict):
            errors.append(f"{where}: review must be an object")
        else:
            if review.get("human_state") not in {"PENDING", "COMPLETE"}:
                errors.append(f"{where}: invalid human_state")
            minutes = review.get("human_review_minutes")
            if minutes is not None and (isinstance(minutes, bool) or not isinstance(minutes, (int, float)) or minutes < 0):
                errors.append(f"{where}: invalid human_review_minutes")
            if review.get("decision") not in {"PENDING_OWNER_REVIEW", "REJECTED_DIAGNOSTIC"}:
                errors.append(f"{where}: decision overclaims or is invalid")
            for claim in ("accepted", "commercially_cleared", "exact_production_base"):
                if review.get(claim) is not False:
                    errors.append(f"{where}: {claim} must be false")

    bundle = data.get("review_bundle")
    if not isinstance(bundle, dict) or not isinstance(bundle.get("artifacts"), list):
        errors.append("review_bundle.artifacts must be an array")
    else:
        kinds: set[str] = set()
        paths: set[str] = set()
        for i, artifact in enumerate(bundle["artifacts"]):
            where = f"review_bundle.artifacts[{i}]"
            if not isinstance(artifact, dict):
                errors.append(f"{where} must be an object")
                continue
            kind = artifact.get("kind")
            if isinstance(kind, str):
                kinds.add(kind)
            path_value = artifact.get("path")
            if path_value in paths:
                errors.append(f"{where}: artifact path must be unique")
            elif isinstance(path_value, str):
                paths.add(path_value)
            artifact_path = validate_generated_art(path_value, artifact.get("sha256"), where, errors)
            if not isinstance(artifact.get("width_px"), int) or artifact.get("width_px", 0) <= 0:
                errors.append(f"{where}: invalid width_px")
            if not isinstance(artifact.get("height_px"), int) or artifact.get("height_px", 0) <= 0:
                errors.append(f"{where}: invalid height_px")
            if artifact_path is not None:
                dimensions = png_dimensions(artifact_path)
                if dimensions is None:
                    errors.append(f"{where}: artifact must be a decodable PNG")
                elif dimensions != (artifact.get("width_px"), artifact.get("height_px")):
                    errors.append(f"{where}: recorded dimensions do not match PNG IHDR")
        missing_kinds = REQUIRED_ARTIFACT_KINDS - kinds
        if missing_kinds:
            errors.append(f"review bundle missing artifact kinds {sorted(missing_kinds)}")

    limitations = data.get("limitations")
    if not isinstance(limitations, list) or not limitations or not all(isinstance(x, str) and x.strip() for x in limitations):
        errors.append("limitations must be a non-empty string array")
    return errors


def fixture_artifacts() -> list[Path]:
    candidates = [
        ROOT / "experiments/review-packets/ch05-cadence-hardening-r1/review/contact-sheet-hardening-candidates.png",
        ROOT / "experiments/review-packets/ch05-cadence-hardening-r1/review/contact-sheet-hardening-phone-previews.png",
        ROOT / "experiments/review-packets/ch05-cadence-hardening-r1/review/contact-sheet-hardening-lettering-overlays.png",
        ROOT / "experiments/review-packets/ch05-manual-continuity-atlas-r1/ch05-continuity-atlas-all-26-r1.png",
        ROOT / "experiments/review-packets/ch05-variable-cadence-assembly-r1/ch05-variable-cadence-scroll-clean-r1.png",
    ]
    missing = [str(path) for path in candidates if not path.is_file()]
    if missing:
        raise FileNotFoundError("fixture artifacts missing: " + ", ".join(missing))
    return candidates


def build_positive_fixture() -> dict[str, Any]:
    plans, _ = canonical_plans()
    candidate = ROOT / next(iter(ALLOWLIST))
    candidate_dimensions = png_dimensions(candidate)
    if candidate_dimensions is None:
        raise ValueError(f"fixture candidate is not a PNG: {candidate}")
    prompt = "Synthetic validator fixture: fictional adults only; no provider execution."
    panels: list[dict[str, Any]] = []
    for index, plan in enumerate(plans):
        rendered = index == 0
        panels.append({
            "panel_id": plan["panel_id"],
            "plan_revision_id": plan["plan_revision_id"],
            "display_order": plan["display_order"],
            "status": "RENDERED" if rendered else "DIAGNOSTIC",
            "prompt_text": prompt if rendered else None,
            "prompt_sha256": sha_bytes(prompt.encode("utf-8")) if rendered else None,
            "input_references": [{
                "path": next(iter(ALLOWLIST)),
                "sha256": ALLOWLIST[next(iter(ALLOWLIST))],
                "upload_target": "openai_builtin_imagegen",
            }] if rendered else [],
            "candidate": {
                "path": candidate.relative_to(ROOT).as_posix(),
                "sha256": sha_file(candidate),
                "width_px": candidate_dimensions[0],
                "height_px": candidate_dimensions[1],
                "elapsed_seconds": 0.0,
                "service": {
                    "tool": "fixture_only_no_execution",
                    "model": None,
                    "endpoint": None,
                    "request_id": None,
                    "provider_usage": None,
                    "provider_cost_usd": None,
                    "seed": None,
                    "unavailable_fields": ["model", "endpoint", "request_id", "provider_usage", "provider_cost_usd", "seed"],
                },
            } if rendered else None,
            "diagnosis": None if rendered else {
                "code": "FIXTURE_NOT_RENDERED",
                "note": "Synthetic positive fixture covers this approved plan through an explicit diagnosis.",
                "next_action": "Render through the authorized chapter pipeline.",
            },
            "lettering_safe": {
                "zones": expected_zones(plan),
                "protects": ["faces", "people", "important_hands", "story_objects"],
                "transparency_overlap_allowed_only_if_readable": True,
                "review_state": "PENDING",
            },
            "continuity": {"hair": copy.deepcopy(HAIR), "wardrobe": copy.deepcopy(WARDROBE), "review_state": "PENDING"},
            "review": {
                "human_state": "PENDING",
                "human_review_minutes": None,
                "decision": "PENDING_OWNER_REVIEW",
                "accepted": False,
                "commercially_cleared": False,
                "exact_production_base": False,
            },
        })
    kinds = ["chapter_scroll", "contact_sheet", "phone_preview", "lettering_overlay", "continuity_sheet"]
    artifacts = []
    for kind, path in zip(kinds, fixture_artifacts()):
        dimensions = png_dimensions(path)
        if dimensions is None:
            raise ValueError(f"fixture review artifact is not a PNG: {path}")
        artifacts.append({"kind": kind, "path": path.relative_to(ROOT).as_posix(), "sha256": sha_file(path), "width_px": dimensions[0], "height_px": dimensions[1]})
    return {
        "record_type": "CH05CompleteChapterProductionManifest",
        "schema_version": "1.0",
        "record_id": "ng-ch05-complete-chapter-validator-positive-fixture-r1",
        "state": "SYNTHETIC_VALIDATOR_FIXTURE_NOT_PRODUCTION_EVIDENCE",
        "medium": "comic",
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "comic_panel_plan_source": {"path": PLAN_PATH.relative_to(ROOT).as_posix(), "sha256": sha_file(PLAN_PATH)},
        "provider_policy": {
            "permitted_product": "openai_builtin_imagegen",
            "external_provider_uploads": 0,
            "direct_paid_provider_api_calls": 0,
            "uploaded_reference_hashes": [ALLOWLIST[next(iter(ALLOWLIST))]],
        },
        "reference_allowlist": [
            {"path": path, "sha256": digest, "provider_product": "openai_builtin_imagegen", "data_class": "fictional_adults"}
            for path, digest in ALLOWLIST.items()
        ],
        "panels": panels,
        "review_bundle": {"artifacts": artifacts},
        "limitations": ["Synthetic validator fixture only; not generation, acceptance, commercial clearance, or exact-production-base evidence."],
    }


def mutations() -> dict[str, Callable[[dict[str, Any]], None]]:
    def pop_service(x: dict[str, Any]) -> None: x["panels"][0]["candidate"]["service"].pop("model")
    def nonnull_unavailable(x: dict[str, Any]) -> None: x["panels"][0]["candidate"]["service"]["model"] = "invented-model"
    def tracked_path(x: dict[str, Any]) -> None:
        path = "production/comic/ch05-sc01-panel-plans-v1.json"
        x["panels"][0]["candidate"].update(path=path, sha256=sha_file(ROOT / path))
    return {
        "missing_panel": lambda x: x["panels"].pop(),
        "duplicate_panel_id": lambda x: x["panels"][1].update(panel_id=x["panels"][0]["panel_id"]),
        "noncontiguous_order": lambda x: x["panels"][1].update(display_order=50),
        "unknown_panel_id": lambda x: x["panels"][0].update(panel_id="ng-ch05-sc01-p999"),
        "wrong_plan_revision": lambda x: x["panels"][0].update(plan_revision_id="wrong"),
        "prompt_hash_mismatch": lambda x: x["panels"][0].update(prompt_sha256="0" * 64),
        "missing_service_field": pop_service,
        "unavailable_service_field_not_null": nonnull_unavailable,
        "output_hash_mismatch": lambda x: x["panels"][0]["candidate"].update(sha256="0" * 64),
        "invalid_dimensions": lambda x: x["panels"][0]["candidate"].update(width_px=0),
        "invalid_elapsed_time": lambda x: x["panels"][0]["candidate"].update(elapsed_seconds=-1),
        "unauthorized_reference_hash": lambda x: x["panels"][0]["input_references"][0].update(sha256="0" * 64),
        "external_reference_upload_target": lambda x: x["panels"][0]["input_references"][0].update(upload_target="bfl_api"),
        "external_provider_upload_count": lambda x: x["provider_policy"].update(external_provider_uploads=1),
        "tracked_generated_art_path": tracked_path,
        "animation_shot_plan_present": lambda x: x.update(animation_shot_plan={}),
        "e_conte_present": lambda x: x.update(e_conte={}),
        "lettering_zone_drift": lambda x: x["panels"][0]["lettering_safe"].update(zones=[]),
        "lettering_protection_missing": lambda x: x["panels"][0]["lettering_safe"].update(protects=["faces"]),
        "soren_hair_drift": lambda x: x["panels"][0]["continuity"]["hair"].update(soren="black"),
        "sigrid_wardrobe_drift": lambda x: x["panels"][0]["continuity"]["wardrobe"].update(sigrid="armor"),
        "diagnostic_without_reason": lambda x: x["panels"][1].update(diagnosis=None),
        "automatic_acceptance": lambda x: x["panels"][0]["review"].update(accepted=True),
        "commercial_clearance_overclaim": lambda x: x["panels"][0]["review"].update(commercially_cleared=True),
        "exact_production_base_overclaim": lambda x: x["panels"][0]["review"].update(exact_production_base=True),
        "review_bundle_kind_missing": lambda x: x["review_bundle"]["artifacts"].pop(),
        "review_bundle_hash_mismatch": lambda x: x["review_bundle"]["artifacts"][0].update(sha256="0" * 64),
    }


def run_self_test() -> int:
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    names = catalog.get("mutations")
    mutation_map = mutations()
    failures: list[str] = []
    if names != list(mutation_map):
        failures.append("mutation catalog/order differs from validator")
    base = build_positive_fixture()
    positive_errors = validate_manifest(base)
    if positive_errors:
        failures.append("positive fixture rejected: " + "; ".join(positive_errors))
    rejected = 0
    for name in names or []:
        value = copy.deepcopy(base)
        mutation_map[name](value)
        errors = validate_manifest(value)
        if errors:
            rejected += 1
        else:
            failures.append(f"adversarial fixture accepted: {name}")
    print(f"CH05 complete-chapter validator self-test: positive={int(not positive_errors)}/1; adversarial={rejected}/{len(names or [])}")
    for failure in failures:
        print(f"FAIL: {failure}")
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    path = args.manifest if args.manifest.is_absolute() else ROOT / args.manifest
    if not path.is_file():
        print(f"FAIL: manifest not found: {path}")
        return 1
    errors = validate_manifest(json.loads(path.read_text(encoding="utf-8")))
    print(f"CH05 complete-chapter manifest validation: {len(errors)} failure(s)")
    for error in errors:
        print(f"FAIL: {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
