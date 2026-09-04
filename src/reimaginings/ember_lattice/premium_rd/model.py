from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from .core import PremiumRDError, duplicate_values, median, read_json, resolve_under, sha256_bytes, sha256_file, slug


REQUIRED_SCENARIOS = (
    "hero_close_up",
    "supporting_close_up",
    "two_character_emotional_acting",
    "full_body_costume_continuity",
    "hands_equipment_interaction",
    "recurring_multi_character",
    "establishing_environment",
    "depth_architecture",
    "monster_or_boss",
    "fast_melee_action",
    "causal_action_sequence",
    "injury_equipment_continuity",
    "quiet_dialogue",
    "status_ui",
    "xp_level_ui",
    "skill_quest_ui",
    "inventory_enemy_cultivation_ui",
    "low_lettering_density",
    "moderate_lettering_density",
    "high_lettering_density",
)

REQUIRED_CRITERIA = (
    "character_identity",
    "age_body_consistency",
    "costume_equipment_continuity",
    "anatomy_hands_feet",
    "facial_acting",
    "pose_specificity",
    "camera_perspective_control",
    "environment_continuity",
    "action_geography",
    "contact_consequence",
    "monster_readability",
    "lighting_palette_continuity",
    "style_stability",
    "lettering_safe_composition",
    "editability",
    "reproducibility",
    "correction_success_rate",
    "time_cost",
    "monetary_cost",
    "failure_rate",
    "sustained_sequential_quality",
)

HARD_FAILURES = {
    "IDENTITY_FAILURE",
    "SEVERE_ANATOMY",
    "SEVERE_PERSPECTIVE",
    "COSTUME_CONTINUITY",
    "EQUIPMENT_CONTINUITY",
    "ACTION_GEOGRAPHY",
    "CONTACT_CONSEQUENCE",
    "LETTERING_COLLISION",
    "UNSAFE_OBSTRUCTION",
    "SYSTEM_ARITHMETIC",
    "PROGRESSION_CONTRADICTION",
    "MISSING_ASSET",
    "HASH_MISMATCH",
}


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _check_box(value: Any, name: str, errors: list[str]) -> None:
    if not isinstance(value, list) or len(value) != 4 or not all(_is_number(v) for v in value):
        errors.append(f"{name} must be normalized [left, top, right, bottom]")
        return
    left, top, right, bottom = value
    if not (0 <= left < right <= 1 and 0 <= top < bottom <= 1):
        errors.append(f"{name} must satisfy 0 <= left < right <= 1 and 0 <= top < bottom <= 1")


def _required_string(row: dict[str, Any], field: str, prefix: str, errors: list[str]) -> None:
    if not isinstance(row.get(field), str) or not row[field].strip():
        errors.append(f"{prefix}.{field} must be a non-empty string")


def validate_manifest(manifest: Any, content_root: Path, verify_assets: bool = True) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(manifest, dict):
        return {"status": "FAIL", "errors": ["manifest root must be an object"], "warnings": []}
    if manifest.get("schema") != "PremiumBenchmarkManifest/1.0":
        errors.append("manifest.schema must be PremiumBenchmarkManifest/1.0")
    project = manifest.get("project")
    if not isinstance(project, dict):
        errors.append("project must be an object")
        project = {}
    for field in ("title", "story_slug", "chapter", "build_id"):
        _required_string(project, field, "project", errors)
    try:
        if project.get("story_slug"):
            slug(project["story_slug"], "project.story_slug")
        if project.get("build_id"):
            slug(project["build_id"], "project.build_id")
    except PremiumRDError as exc:
        errors.append(str(exc))
    canvas = project.get("canvas")
    if not isinstance(canvas, dict) or not all(isinstance(canvas.get(k), int) and canvas[k] > 0 for k in ("width", "height")):
        errors.append("project.canvas needs positive integer width and height")
    if project.get("deliverable") not in {"benchmark", "premium_ch01"}:
        errors.append("project.deliverable must be benchmark or premium_ch01")

    workflows = manifest.get("workflows")
    if not isinstance(workflows, list) or len(workflows) < 2:
        errors.append("workflows must contain at least baseline and one premium workflow")
        workflows = []
    workflow_ids: list[str] = []
    for index, row in enumerate(workflows):
        prefix = f"workflows[{index}]"
        if not isinstance(row, dict):
            errors.append(f"{prefix} must be an object")
            continue
        for field in ("workflow_id", "label", "architecture"):
            _required_string(row, field, prefix, errors)
        if row.get("workflow_id"):
            try:
                workflow_ids.append(slug(row["workflow_id"], f"{prefix}.workflow_id"))
            except PremiumRDError as exc:
                errors.append(str(exc))
    for value in duplicate_values(workflow_ids):
        errors.append(f"duplicate workflow_id {value}")
    if workflows and sum(bool(row.get("is_baseline")) for row in workflows if isinstance(row, dict)) != 1:
        errors.append("exactly one workflow must set is_baseline=true")

    assets = manifest.get("assets")
    if not isinstance(assets, list) or not assets:
        errors.append("assets must be a non-empty array")
        assets = []
    asset_ids: list[str] = []
    asset_map: dict[str, dict[str, Any]] = {}
    asset_failures = 0
    for index, row in enumerate(assets):
        prefix = f"assets[{index}]"
        if not isinstance(row, dict):
            errors.append(f"{prefix} must be an object")
            continue
        for field in ("asset_id", "path", "sha256", "media_type", "workflow_id"):
            _required_string(row, field, prefix, errors)
        asset_id = row.get("asset_id")
        if isinstance(asset_id, str):
            try:
                slug(asset_id, f"{prefix}.asset_id")
                asset_ids.append(asset_id)
                asset_map[asset_id] = row
            except PremiumRDError as exc:
                errors.append(str(exc))
        if row.get("workflow_id") not in workflow_ids:
            errors.append(f"{prefix}.workflow_id is not registered")
        digest = row.get("sha256")
        if not isinstance(digest, str) or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            errors.append(f"{prefix}.sha256 must be lowercase SHA-256")
        try:
            path = resolve_under(content_root, row.get("path"), f"{prefix}.path")
            if verify_assets:
                if not path.is_file():
                    errors.append(f"missing asset {row.get('asset_id')}: {path}")
                    asset_failures += 1
                elif isinstance(digest, str) and sha256_file(path) != digest:
                    errors.append(f"asset hash mismatch {row.get('asset_id')}")
                    asset_failures += 1
        except (PremiumRDError, TypeError) as exc:
            errors.append(str(exc))
    for value in duplicate_values(asset_ids):
        errors.append(f"duplicate asset_id {value}")

    records = manifest.get("render_records")
    if not isinstance(records, list):
        errors.append("render_records must be an array")
        records = []
    rendered_assets: list[str] = []
    for index, record in enumerate(records):
        prefix = f"render_records[{index}]"
        if not isinstance(record, dict):
            errors.append(f"{prefix} must be an object")
            continue
        for field in ("record_id", "workflow_id", "panel_id", "output_asset_id", "output_hash", "review_status"):
            _required_string(record, field, prefix, errors)
        output_asset_id = record.get("output_asset_id")
        if output_asset_id not in asset_map:
            errors.append(f"{prefix}.output_asset_id is not registered")
        else:
            rendered_assets.append(output_asset_id)
            if record.get("output_hash") != asset_map[output_asset_id].get("sha256"):
                errors.append(f"{prefix}.output_hash does not reconcile to asset hash")
            if record.get("workflow_id") != asset_map[output_asset_id].get("workflow_id"):
                errors.append(f"{prefix}.workflow_id does not match output asset")
        exact_prompt = record.get("exact_prompt")
        prompt_hash = record.get("prompt_hash")
        if not isinstance(exact_prompt, str) or not exact_prompt:
            errors.append(f"{prefix}.exact_prompt must be a non-empty string")
        elif prompt_hash != sha256_bytes(exact_prompt.encode("utf-8")):
            errors.append(f"{prefix}.prompt_hash does not match exact_prompt")
        if record.get("workflow_id") not in workflow_ids:
            errors.append(f"{prefix}.workflow_id is not registered")
        if not isinstance(record.get("input_references"), list):
            errors.append(f"{prefix}.input_references must be an array")
        if not _is_number(record.get("measured_elapsed_seconds")) or record["measured_elapsed_seconds"] < 0:
            errors.append(f"{prefix}.measured_elapsed_seconds must be non-negative")
        cost = record.get("monetary_cost")
        if cost is not None and (not _is_number(cost) or cost < 0):
            errors.append(f"{prefix}.monetary_cost must be null or non-negative")
        for nullable in ("model", "endpoint", "provider_request_id", "usage", "deterministic_seed"):
            if nullable not in record:
                errors.append(f"{prefix}.{nullable} must be present (null when unavailable)")
        if not isinstance(record.get("failure_classes"), list):
            errors.append(f"{prefix}.failure_classes must be an array")
    for value in duplicate_values(rendered_assets):
        errors.append(f"multiple render_records target asset {value}")
    missing_records = sorted(set(asset_ids) - set(rendered_assets))
    if missing_records:
        errors.append(f"missing render_records for {len(missing_records)} assets")

    evidence_documents = manifest.get("evidence_documents", [])
    if not isinstance(evidence_documents, list):
        errors.append("evidence_documents must be an array")
        evidence_documents = []
    document_ids: list[str] = []
    for index, document in enumerate(evidence_documents):
        prefix = f"evidence_documents[{index}]"
        if not isinstance(document, dict):
            errors.append(f"{prefix} must be an object")
            continue
        for field in ("document_id", "title", "category", "path", "sha256"):
            _required_string(document, field, prefix, errors)
        if isinstance(document.get("document_id"), str):
            document_ids.append(document["document_id"])
        try:
            path = resolve_under(content_root, document.get("path"), f"{prefix}.path")
            if verify_assets:
                if not path.is_file():
                    errors.append(f"missing evidence document {document.get('document_id')}: {path}")
                elif sha256_file(path) != document.get("sha256"):
                    errors.append(f"evidence document hash mismatch {document.get('document_id')}")
                elif path.suffix.lower() == ".json":
                    try:
                        read_json(path)
                    except PremiumRDError as exc:
                        errors.append(str(exc))
        except (PremiumRDError, TypeError) as exc:
            errors.append(str(exc))
    for value in duplicate_values(document_ids):
        errors.append(f"duplicate evidence document_id {value}")

    panels = manifest.get("panels")
    if not isinstance(panels, list) or len(panels) < 24:
        errors.append("panels must contain at least 24 representative benchmark panels")
        panels = panels if isinstance(panels, list) else []
    if project.get("deliverable") == "premium_ch01" and isinstance(panels, list) and not 40 <= len(panels) <= 60 and not project.get("panel_count_rationale"):
        errors.append("premium_ch01 requires 40–60 panels or a non-empty panel_count_rationale")
    panel_ids: list[str] = []
    scenario_counts: Counter[str] = Counter()
    action_sequence_counts: Counter[str] = Counter()
    for index, panel in enumerate(panels):
        prefix = f"panels[{index}]"
        if not isinstance(panel, dict):
            errors.append(f"{prefix} must be an object")
            continue
        for field in ("schema", "panel_id", "sequence_id", "beat", "density"):
            _required_string(panel, field, prefix, errors)
        if panel.get("schema") != "ComicPanelPlan/1.0":
            errors.append(f"{prefix}.schema must reuse ComicPanelPlan/1.0")
        panel_id = panel.get("panel_id")
        if isinstance(panel_id, str):
            try:
                slug(panel_id, f"{prefix}.panel_id")
                panel_ids.append(panel_id)
            except PremiumRDError as exc:
                errors.append(str(exc))
        if panel.get("order") != index + 1:
            errors.append(f"{prefix}.order must equal {index + 1}")
        if panel.get("density") not in {"low", "moderate", "high"}:
            errors.append(f"{prefix}.density must be low, moderate, or high")
        if not isinstance(panel.get("action"), bool):
            errors.append(f"{prefix}.action must be boolean")
        scenarios = panel.get("scenarios")
        if not isinstance(scenarios, list) or not scenarios:
            errors.append(f"{prefix}.scenarios must be a non-empty array")
        else:
            unknown = sorted(set(scenarios) - set(REQUIRED_SCENARIOS))
            if unknown:
                errors.append(f"{prefix}.scenarios has unknown values: {', '.join(unknown)}")
            scenario_counts.update(scenarios)
        variants = panel.get("variants")
        if not isinstance(variants, dict):
            errors.append(f"{prefix}.variants must map every workflow to an asset_id")
        else:
            variant_hashes: dict[str, str] = {}
            for workflow_id in workflow_ids:
                if variants.get(workflow_id) not in asset_map:
                    errors.append(f"{prefix}.variants[{workflow_id}] is missing or unregistered")
                elif asset_map[variants[workflow_id]].get("workflow_id") != workflow_id:
                    errors.append(f"{prefix}.variants[{workflow_id}] points to the wrong workflow")
                else:
                    variant_hashes[workflow_id] = asset_map[variants[workflow_id]].get("sha256", "")
            if len(variant_hashes) > 1 and len(set(variant_hashes.values())) != len(variant_hashes):
                errors.append(f"{prefix}.variants must be hash-distinct across workflows")
        for zone_name in ("focal_exclusions", "lettering_safe_zones"):
            zones = panel.get(zone_name)
            if not isinstance(zones, list):
                errors.append(f"{prefix}.{zone_name} must be an array")
            else:
                for z_index, box in enumerate(zones):
                    _check_box(box, f"{prefix}.{zone_name}[{z_index}]", errors)
        units = panel.get("lettering_units", [])
        if not isinstance(units, list):
            errors.append(f"{prefix}.lettering_units must be an array")
        else:
            seen_order: set[int] = set()
            for u_index, unit in enumerate(units):
                u_prefix = f"{prefix}.lettering_units[{u_index}]"
                if not isinstance(unit, dict):
                    errors.append(f"{u_prefix} must be an object")
                    continue
                if unit.get("kind") not in {"dialogue", "open", "caption", "sfx", "ui"}:
                    errors.append(f"{u_prefix}.kind is unsupported")
                _required_string(unit, "text", u_prefix, errors)
                if unit.get("kind") != "sfx":
                    _check_box(unit.get("box"), f"{u_prefix}.box", errors)
                order = unit.get("reading_order")
                if not isinstance(order, int) or order < 1 or order in seen_order:
                    errors.append(f"{u_prefix}.reading_order must be a unique positive integer")
                seen_order.add(order)
        if panel.get("action"):
            sequence = panel.get("action_sequence")
            if not isinstance(sequence, str) or not sequence:
                errors.append(f"{prefix}.action_sequence required for action panel")
            else:
                action_sequence_counts[sequence] += 1
    for value in duplicate_values(panel_ids):
        errors.append(f"duplicate panel_id {value}")
    panel_map = {panel["panel_id"]: panel for panel in panels if isinstance(panel, dict) and isinstance(panel.get("panel_id"), str)}
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            continue
        panel_id = record.get("panel_id")
        if panel_id not in panel_map:
            errors.append(f"render_records[{index}].panel_id is not registered")
            continue
        output_asset_id = record.get("output_asset_id")
        workflow_id = record.get("workflow_id")
        if panel_map[panel_id].get("variants", {}).get(workflow_id) == output_asset_id and record.get("review_status") != "REVIEWED_PASS":
            errors.append(f"render_records[{index}] is an active panel variant but not REVIEWED_PASS")
    missing_scenarios = [name for name in REQUIRED_SCENARIOS if not scenario_counts[name]]
    if missing_scenarios:
        errors.append("benchmark scenario coverage missing: " + ", ".join(missing_scenarios))
    if not any(count >= 6 for count in action_sequence_counts.values()):
        errors.append("at least one causal action_sequence must contain six or more panels")

    failures = manifest.get("failures")
    if not isinstance(failures, list):
        errors.append("failures must be an array")
        failures = []
    for index, failure in enumerate(failures):
        prefix = f"failures[{index}]"
        if not isinstance(failure, dict):
            errors.append(f"{prefix} must be an object")
            continue
        for field in ("failure_id", "panel_id", "workflow_id", "failed_asset_id", "failure_class", "changed_instruction", "status"):
            _required_string(failure, field, prefix, errors)
        if failure.get("panel_id") not in panel_ids:
            errors.append(f"{prefix}.panel_id is not registered")
        if failure.get("workflow_id") not in workflow_ids:
            errors.append(f"{prefix}.workflow_id is not registered")
        if failure.get("failed_asset_id") not in asset_map:
            errors.append(f"{prefix}.failed_asset_id is not registered")
        elif asset_map[failure["failed_asset_id"]].get("workflow_id") != failure.get("workflow_id"):
            errors.append(f"{prefix}.failed_asset_id belongs to a different workflow")
        if failure.get("status") not in {"OPEN", "REPAIRED", "ACCEPTED_LIMITATION"}:
            errors.append(f"{prefix}.status is unsupported")
        if not isinstance(failure.get("frozen_variables"), list) or not failure.get("frozen_variables"):
            errors.append(f"{prefix}.frozen_variables must be non-empty")
        if failure.get("status") == "REPAIRED":
            repaired = failure.get("repaired_asset_id")
            if repaired not in asset_map:
                errors.append(f"{prefix}.repaired_asset_id is not registered")
            elif asset_map[repaired].get("workflow_id") != failure.get("workflow_id"):
                errors.append(f"{prefix}.repaired_asset_id belongs to a different workflow")
            elif panel_map.get(failure.get("panel_id"), {}).get("variants", {}).get(failure.get("workflow_id")) != repaired:
                errors.append(f"{prefix}.repaired_asset_id must be the active workflow variant")
            if failure.get("failed_asset_id") == repaired:
                errors.append(f"{prefix}.failed and repaired assets must differ")
            before = failure.get("non_target_hashes_before")
            after = failure.get("non_target_hashes_after")
            if not isinstance(before, dict) or before != after:
                errors.append(f"{prefix} must prove unchanged non-target hashes")
    unresolved_hard = sum(
        failure.get("status") == "OPEN" and failure.get("failure_class") in HARD_FAILURES
        for failure in failures if isinstance(failure, dict)
    )
    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "warnings": warnings,
        "counts": {
            "workflows": len(workflow_ids),
            "assets": len(asset_ids),
            "panels": len(panel_ids),
            "failures": len(failures),
            "render_records": len(records),
            "evidence_documents": len(evidence_documents),
            "asset_integrity_failures": asset_failures,
            "unresolved_hard_failures": unresolved_hard,
        },
        "scenario_coverage": dict(sorted(scenario_counts.items())),
    }


def validate_rubric(rubric: Any, manifest: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if not isinstance(rubric, dict):
        return {"status": "FAIL", "errors": ["rubric root must be an object"], "warnings": []}
    if rubric.get("schema") != "PremiumRubric/1.0":
        errors.append("rubric.schema must be PremiumRubric/1.0")
    criteria = rubric.get("criteria")
    if not isinstance(criteria, list):
        errors.append("criteria must be an array")
        criteria = []
    names = [row.get("criterion_id") for row in criteria if isinstance(row, dict)]
    missing = sorted(set(REQUIRED_CRITERIA) - set(names))
    extra = sorted(set(names) - set(REQUIRED_CRITERIA))
    if missing:
        errors.append("missing rubric criteria: " + ", ".join(missing))
    if extra:
        errors.append("unknown rubric criteria: " + ", ".join(extra))
    for value in duplicate_values([v for v in names if isinstance(v, str)]):
        errors.append(f"duplicate criterion_id {value}")
    weights: dict[str, float] = {}
    for index, row in enumerate(criteria):
        if not isinstance(row, dict):
            errors.append(f"criteria[{index}] must be an object")
            continue
        _required_string(row, "label", f"criteria[{index}]", errors)
        weight = row.get("weight")
        if not _is_number(weight) or weight <= 0:
            errors.append(f"criteria[{index}].weight must be positive")
        elif isinstance(row.get("criterion_id"), str):
            weights[row["criterion_id"]] = float(weight)
    if weights and abs(sum(weights.values()) - 1.0) > 1e-9:
        errors.append(f"criterion weights must sum to 1.0, got {sum(weights.values()):.12g}")

    workflow_ids = {row["workflow_id"] for row in manifest.get("workflows", []) if isinstance(row, dict) and "workflow_id" in row}
    panel_ids = {row["panel_id"] for row in manifest.get("panels", []) if isinstance(row, dict) and "panel_id" in row}
    evaluations = rubric.get("evaluations")
    if not isinstance(evaluations, list):
        errors.append("evaluations must be an array")
        evaluations = []
    keys: list[str] = []
    for index, row in enumerate(evaluations):
        prefix = f"evaluations[{index}]"
        if not isinstance(row, dict):
            errors.append(f"{prefix} must be an object")
            continue
        workflow_id, panel_id = row.get("workflow_id"), row.get("panel_id")
        if workflow_id not in workflow_ids:
            errors.append(f"{prefix}.workflow_id is not registered")
        if panel_id not in panel_ids:
            errors.append(f"{prefix}.panel_id is not registered")
        keys.append(f"{workflow_id}/{panel_id}")
        scores = row.get("scores")
        if not isinstance(scores, dict) or set(scores) != set(REQUIRED_CRITERIA):
            errors.append(f"{prefix}.scores must contain exactly all required criteria")
        else:
            for criterion, score in scores.items():
                if not _is_number(score) or not 0 <= score <= 5:
                    errors.append(f"{prefix}.scores.{criterion} must be between 0 and 5")
        hard_failures = row.get("hard_failures")
        if not isinstance(hard_failures, list) or not all(isinstance(v, str) and v for v in hard_failures):
            errors.append(f"{prefix}.hard_failures must be an array of strings")
    for value in duplicate_values(keys):
        errors.append(f"duplicate evaluation {value}")
    expected = {f"{workflow}/{panel}" for workflow in workflow_ids for panel in panel_ids}
    missing_evaluations = sorted(expected - set(keys))
    if missing_evaluations:
        errors.append(f"missing {len(missing_evaluations)} workflow/panel evaluations")
    return {"status": "PASS" if not errors else "FAIL", "errors": errors, "warnings": []}


def rubric_summary(rubric: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
    weights = {row["criterion_id"]: float(row["weight"]) for row in rubric["criteria"]}
    by_workflow: dict[str, list[float]] = defaultdict(list)
    hard: Counter[str] = Counter()
    for row in rubric["evaluations"]:
        weighted = sum(float(row["scores"][key]) * weights[key] for key in weights) * 20
        by_workflow[row["workflow_id"]].append(weighted)
        hard[row["workflow_id"]] += len(row["hard_failures"])
    rows = []
    for workflow in manifest["workflows"]:
        workflow_id = workflow["workflow_id"]
        scores = by_workflow[workflow_id]
        rows.append({
            "workflow_id": workflow_id,
            "label": workflow["label"],
            "median_score": round(median(scores), 3),
            "weakest_panel_score": round(min(scores) if scores else 0.0, 3),
            "mean_score": round(sum(scores) / len(scores) if scores else 0.0, 3),
            "hard_failure_count": hard[workflow_id],
            "eligible": hard[workflow_id] == 0,
        })
    eligible = [row for row in rows if row["eligible"]]
    winner = max(eligible, key=lambda row: (row["median_score"], row["weakest_panel_score"], row["mean_score"], row["workflow_id"]), default=None)
    return {"schema": "PremiumRubricSummary/1.0", "workflows": rows, "winner": winner}


def validate_bundle(manifest: Any, rubric: Any, content_root: Path, verify_assets: bool = True) -> dict[str, Any]:
    manifest_report = validate_manifest(manifest, content_root, verify_assets=verify_assets)
    rubric_report = validate_rubric(rubric, manifest if isinstance(manifest, dict) else {})
    quality_errors: list[str] = []
    summary = None
    if manifest_report["status"] == rubric_report["status"] == "PASS":
        summary = rubric_summary(rubric, manifest)
        selected = manifest.get("recommendation", {}).get("selected_workflow_id")
        baseline = next((row["workflow_id"] for row in manifest["workflows"] if row.get("is_baseline")), None)
        winner = (summary.get("winner") or {}).get("workflow_id")
        rows = {row["workflow_id"]: row for row in summary["workflows"]}
        if selected not in rows:
            quality_errors.append("recommendation.selected_workflow_id is not registered")
        elif selected == baseline:
            quality_errors.append("selected premium architecture cannot be the baseline")
        elif winner != selected:
            quality_errors.append(f"selected workflow {selected} does not match complete-set winner {winner}")
        elif baseline in rows:
            if rows[selected]["median_score"] <= rows[baseline]["median_score"]:
                quality_errors.append("selected workflow does not improve median score over baseline")
            if rows[selected]["weakest_panel_score"] <= rows[baseline]["weakest_panel_score"]:
                quality_errors.append("selected workflow does not improve weakest-panel score over baseline")
        if manifest_report.get("counts", {}).get("unresolved_hard_failures", 0):
            quality_errors.append("unresolved hard failures block the quality gate")
    status = "PASS" if manifest_report["status"] == rubric_report["status"] == "PASS" and not quality_errors else "FAIL"
    return {
        "schema": "PremiumBundleValidation/1.0",
        "status": status,
        "manifest": manifest_report,
        "rubric": rubric_report,
        "quality": {"status": "PASS" if not quality_errors else "FAIL", "errors": quality_errors, "summary": summary},
    }
