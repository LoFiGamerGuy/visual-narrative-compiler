from __future__ import annotations

from pathlib import Path
from typing import Any

from .core import sha256_bytes, write_json
from .model import REQUIRED_CRITERIA, REQUIRED_SCENARIOS


def author_template(output_dir: Path, panel_count: int = 48) -> dict[str, str]:
    """Author a deterministic, intentionally unscored benchmark starter bundle."""
    if panel_count < 24:
        raise ValueError("premium benchmark templates require at least 24 panels")
    workflows = [
        {"workflow_id": "baseline", "label": "Approved Candidate B baseline", "architecture": "existing approved source route", "is_baseline": True},
        {"workflow_id": "premium", "label": "Premium candidate", "architecture": "document exact multi-stage architecture", "is_baseline": False},
    ]
    assets = []
    render_records = []
    panels = []
    for index in range(panel_count):
        order = index + 1
        panel_id = f"el-premium-ch01-p{order:03d}"
        variants = {}
        for workflow in workflows:
            workflow_id = workflow["workflow_id"]
            asset_id = f"{workflow_id}-p{order:03d}"
            variants[workflow_id] = asset_id
            assets.append({
                "asset_id": asset_id,
                "workflow_id": workflow_id,
                "path": f"assets/{workflow_id}/p{order:03d}.svg",
                "sha256": "0" * 64,
                "media_type": "image/svg+xml",
                "dimensions": {"width": 864, "height": 1536},
            })
            prompt = f"AUTHOR REQUIRED: exact {workflow_id} prompt for {panel_id}"
            render_records.append({
                "record_id": f"render-{workflow_id}-p{order:03d}",
                "workflow_id": workflow_id,
                "panel_id": panel_id,
                "exact_prompt": prompt,
                "prompt_hash": sha256_bytes(prompt.encode("utf-8")),
                "input_references": [],
                "output_asset_id": asset_id,
                "output_hash": "0" * 64,
                "measured_elapsed_seconds": 0,
                "model": None,
                "endpoint": None,
                "provider_request_id": None,
                "usage": None,
                "monetary_cost": None,
                "deterministic_seed": None,
                "review_status": "AUTHOR_REQUIRED",
                "failure_classes": [],
                "reproducible": False,
                "commercial_clearance": False,
            })
        scenarios = [REQUIRED_SCENARIOS[index % len(REQUIRED_SCENARIOS)]]
        if index >= len(REQUIRED_SCENARIOS):
            scenarios.append(REQUIRED_SCENARIOS[(index + 7) % len(REQUIRED_SCENARIOS)])
        panels.append({
            "schema": "ComicPanelPlan/1.0",
            "panel_id": panel_id,
            "sequence_id": "el-premium-ch01-action-a" if 8 <= index < 14 else f"el-premium-ch01-s{index // 6 + 1:02d}",
            "order": order,
            "beat": f"AUTHOR REQUIRED: benchmark narrative objective {order:03d}",
            "density": ("low", "moderate", "high")[index % 3],
            "action": 8 <= index < 14,
            "action_sequence": "action-a" if 8 <= index < 14 else None,
            "scenarios": scenarios,
            "variants": variants,
            "focal_exclusions": [[0.2, 0.2, 0.8, 0.78]],
            "lettering_safe_zones": [[0.04, 0.04, 0.4, 0.18]],
            "lettering_units": [],
        })
    manifest: dict[str, Any] = {
        "schema": "PremiumBenchmarkManifest/1.0",
        "project": {"title": "Ember Lattice Premium R&D", "story_slug": "ember-lattice", "chapter": "ch01", "build_id": "premium-rd-draft", "deliverable": "premium_ch01", "canvas": {"width": 864, "height": 1536}},
        "workflows": workflows,
        "assets": assets,
        "render_records": render_records,
        "panels": panels,
        "failures": [],
        "evidence_documents": [],
        "recommendation": {
            "selected_workflow_id": "premium",
            "executive_recommendation": "AUTHOR REQUIRED after complete-set evaluation.",
            "architecture": "AUTHOR REQUIRED",
            "provider_limitations": "AUTHOR REQUIRED",
            "licensing_reproducibility": "AUTHOR REQUIRED",
            "remaining_gaps": "AUTHOR REQUIRED",
        },
    }
    equal_weight = 1.0 / len(REQUIRED_CRITERIA)
    rubric = {
        "schema": "PremiumRubric/1.0",
        "scale": {"minimum": 0, "maximum": 5, "anchors": {"0": "unusable", "3": "production-capable with repair", "5": "premium sustained quality"}},
        "criteria": [{"criterion_id": criterion, "label": criterion.replace("_", " ").title(), "weight": equal_weight} for criterion in REQUIRED_CRITERIA],
        "evaluations": [
            {"workflow_id": workflow["workflow_id"], "panel_id": panel["panel_id"], "scores": {criterion: 0 for criterion in REQUIRED_CRITERIA}, "hard_failures": [], "evidence": "AUTHOR REQUIRED"}
            for workflow in workflows for panel in panels
        ],
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / "benchmark-manifest.json"
    rubric_path = output_dir / "rubric.json"
    write_json(manifest_path, manifest)
    write_json(rubric_path, rubric)
    return {"manifest": str(manifest_path), "rubric": str(rubric_path)}
