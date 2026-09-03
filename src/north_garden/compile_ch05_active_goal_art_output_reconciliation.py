"""Compile deterministic active-goal CH05 art/output reconciliation evidence."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_JSON = (
    ROOT / "docs/research/evidence/ch05-active-goal-art-output-reconciliation-r1.json"
)
OUTPUT_MARKDOWN = (
    ROOT / "docs/research/ch05-active-goal-art-output-reconciliation-r1.md"
)

BASE_RELEASE = "docs/research/evidence/ch05-complete-chapter-release-r6.json"
BASE_MANIFEST = (
    "production/comic/run-manifests/ch05-complete-chapter-production-manifest-r6.json"
)
ARMS = [
    ("alternate_graphic", "alt-graphic"),
    ("clear_line_watercolor", "clear-line-watercolor"),
    ("premium_cel", "premium-cel"),
    ("flat_graphic_gouache", "flat-graphic-gouache"),
    ("reduced_palette_text_control", "reduced-palette-text-control"),
]
TRIO = "production/comic/run-manifests/ch05-premium-cel-targeted-repair-trio-execution-r1.json"
ABLATIONS = [
    "production/comic/run-manifests/ch05-s01-flat-gouache-reference-ablation-execution-r1.json",
    "production/comic/run-manifests/ch05-s11-flat-gouache-reference-ablation-execution-r1.json",
]


def read_json(relative: str) -> dict[str, Any]:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def git_text(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()


def bind(relative: str) -> dict[str, Any]:
    path = ROOT / relative
    content = path.read_bytes()
    index_line = git_text("ls-files", "-s", "--", relative)
    if not index_line:
        raise ValueError(f"source is not tracked: {relative}")
    metadata, listed_path = index_line.split("\t", 1)
    mode, oid, stage = metadata.split(" ", 2)
    if listed_path != relative or stage != "0":
        raise ValueError(f"unexpected index binding for {relative}: {index_line}")
    if git_text("hash-object", "--", relative) != oid:
        raise ValueError(f"working bytes differ from index for {relative}")
    return {
        "path": relative,
        "sha256": hashlib.sha256(content).hexdigest(),
        "git_blob_oid": oid,
        "git_mode": mode,
        "bytes": len(content),
    }


def references(record: dict[str, Any]) -> list[Any]:
    value = record.get("input_references")
    if value is not None:
        return list(value)
    count = int(record.get("input_reference_count", 0))
    return [None] * count


def arm_record(arm_id: str, stem: str) -> dict[str, Any]:
    execution_path = f"production/comic/run-manifests/ch05-complete-chapter-{stem}-execution-manifest-r1.json"
    crop_path = (
        f"production/comic/run-manifests/ch05-complete-chapter-{stem}-crops-r1.json"
    )
    execution = read_json(execution_path)
    crops = read_json(crop_path)
    records = execution["records"]
    summary = execution["summary"]
    zero_reference = sum(1 for record in records if len(references(record)) == 0)
    reference_uses = sum(len(references(record)) for record in records)
    timing: dict[str, Any]
    if arm_id in {"alternate_graphic", "clear_line_watercolor", "premium_cel"}:
        timing = {
            "scope_class": "OVERLAP_ADJUSTED_TOOL_CALL_BATCH_WALL",
            "seconds": summary["overlap_adjusted_tool_call_wall_seconds"],
            "unique_timing_batches": summary["unique_timing_batches"],
            "actual_end_to_end_seconds": None,
            "note": summary["timing_scope"],
        }
    elif arm_id == "flat_graphic_gouache":
        timing = {
            "scope_class": "NON_OVERLAP_OBSERVED_ARITHMETIC",
            "seconds": summary["non_overlap_adjusted_observed_total_seconds"],
            "known_individual_seconds": summary[
                "known_per_output_tool_wall_seconds_sum"
            ],
            "concurrent_batch_seconds": summary["concurrent_pair_batch_wall_seconds"],
            "actual_end_to_end_seconds": summary["actual_end_to_end_wall_seconds"],
            "note": "Nine individual walls plus one S10/S11 concurrent-pair wall; no shared end-to-end stopwatch.",
        }
    else:
        timing = {
            "scope_class": "NON_OVERLAP_OBSERVED_ARITHMETIC",
            "seconds": summary["non_overlap_observed_arithmetic_seconds"],
            "known_individual_seconds": summary[
                "known_individual_tool_wall_seconds_sum"
            ],
            "concurrent_batch_seconds": round(
                summary["non_overlap_observed_arithmetic_seconds"]
                - summary["known_individual_tool_wall_seconds_sum"],
                3,
            ),
            "actual_end_to_end_seconds": summary["actual_end_to_end_wall_seconds"],
            "note": "Six individual walls plus two concurrent-batch walls; no shared end-to-end stopwatch.",
        }
    return {
        "component": arm_id,
        "source_manifests": [bind(execution_path), bind(crop_path)],
        "service_raster_outputs": summary["sequence_outputs"],
        "panel_level_candidates_or_crops": crops["summary"]["planned_crops"],
        "authorized_reference_uses": reference_uses,
        "zero_reference_outputs": zero_reference,
        "unsplit_ablation_diagnostics": 0,
        "timing": timing,
    }


def build_record() -> dict[str, Any]:
    release = read_json(BASE_RELEASE)
    base_manifest = read_json(BASE_MANIFEST)
    base_summary = release["measured_summary"]
    execution_groups: dict[str, dict[str, Any]] = {}
    for panel in base_manifest["panels"]:
        execution_groups.setdefault(panel["source_service_execution_id"], panel)
    base_reference_uses = sum(
        len(references(panel)) for panel in execution_groups.values()
    )
    base_zero_reference = sum(
        1 for panel in execution_groups.values() if len(references(panel)) == 0
    )
    base = {
        "component": "base_ch05_r6",
        "source_manifests": [bind(BASE_RELEASE), bind(BASE_MANIFEST)],
        "service_raster_outputs": base_summary["built_in_raster_outputs"],
        "panel_level_candidates_or_crops": base_summary["panel_level_candidates"],
        "selected_chapter_panels": base_summary["selected_chapter_panels"],
        "additional_superseded_or_diagnostic_candidates": (
            base_summary["panel_level_candidates"]
            - base_summary["selected_chapter_panels"]
        ),
        "authorized_reference_uses": base_reference_uses,
        "zero_reference_outputs": base_zero_reference,
        "unsplit_ablation_diagnostics": 0,
        "timing": {
            "scope_class": "TWO_REPORTED_NON_EQUIVALENT_SCOPES",
            "unique_execution_observation_sum_seconds": base_summary[
                "unique_execution_elapsed_sum_seconds"
            ],
            "approximate_overlap_adjusted_client_wall_seconds": base_summary[
                "approximate_unique_client_generation_wall_seconds"
            ],
            "actual_end_to_end_seconds": None,
            "note": "Do not equate or add the summed per-execution observations and approximate overlap-adjusted client wall.",
        },
    }

    arms = [arm_record(arm_id, stem) for arm_id, stem in ARMS]
    trio_json = read_json(TRIO)
    trio_summary = trio_json["summary"]
    trio = {
        "component": "premium_targeted_repair_trio",
        "source_manifests": [bind(TRIO)],
        "service_raster_outputs": trio_summary["standalone_outputs"],
        "panel_level_candidates_or_crops": trio_summary["comic_panel_plans"],
        "authorized_reference_uses": trio_summary["authorized_reference_uses"],
        "zero_reference_outputs": sum(
            1 for record in trio_json["records"] if len(references(record)) == 0
        ),
        "unsplit_ablation_diagnostics": 0,
        "timing": {
            "scope_class": "ONE_CONCURRENT_BATCH_WALL",
            "seconds": trio_summary["overlap_adjusted_tool_call_wall_seconds"],
            "individual_output_seconds": None,
            "actual_end_to_end_seconds": None,
            "note": trio_summary["timing_scope"],
        },
    }

    ablations = []
    for path in ABLATIONS:
        payload = read_json(path)
        summary = payload["summary"]
        ablations.append(
            {
                "component": payload["record_id"],
                "source_manifests": [bind(path)],
                "service_raster_outputs": summary["sequence_outputs"],
                "comic_panel_plans_covered": summary["comic_panel_plans"],
                "panel_level_candidates_or_crops": 0,
                "authorized_reference_uses": summary["authorized_reference_uses"],
                "zero_reference_outputs": summary["sequence_outputs"],
                "unsplit_ablation_diagnostics": summary["sequence_outputs"],
                "timing": {
                    "scope_class": "INDIVIDUAL_TOOL_CALL_WALL",
                    "seconds": summary["known_tool_wall_seconds"],
                    "actual_end_to_end_seconds": None,
                    "note": "One sequence-strip tool-call observation; output was not split into panel candidates.",
                },
            }
        )

    components = [base, *arms, trio, *ablations]
    totals = {
        key: sum(int(component[key]) for component in components)
        for key in (
            "service_raster_outputs",
            "panel_level_candidates_or_crops",
            "authorized_reference_uses",
            "zero_reference_outputs",
            "unsplit_ablation_diagnostics",
        )
    }
    five_arm_crops = sum(int(arm["panel_level_candidates_or_crops"]) for arm in arms)
    six_route_subset = {
        "aligned_review_candidates": base["selected_chapter_panels"] + five_arm_crops,
        "base_r6_selected_panels": base["selected_chapter_panels"],
        "five_full_arm_crops": five_arm_crops,
        "excluded_base_additional_candidates": base[
            "additional_superseded_or_diagnostic_candidates"
        ],
        "excluded_premium_targeted_repair_candidates": trio[
            "panel_level_candidates_or_crops"
        ],
        "relationship": "300 = 50 selected r6 + 250 five-arm crops; 312 = 300 + 9 additional r6 candidates + 3 premium targeted-repair candidates.",
    }
    return {
        "record_type": "CH05ActiveGoalArtOutputReconciliation",
        "schema_version": "1.0",
        "record_id": "ng-ch05-active-goal-art-output-reconciliation-r1",
        "state": "RECONCILED_NO_DOUBLE_COUNTING",
        "medium": "comic",
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "components": components,
        "totals": totals,
        "six_route_subset": six_route_subset,
        "timing_boundary": {
            "aggregate_end_to_end_seconds": None,
            "aggregation_permitted": False,
            "reason": "Base r6 reports two non-equivalent scopes; three arms report overlap-adjusted batch walls; flat and reduced report non-overlap arithmetic; the trio reports one concurrent batch; ablations report individual calls. Adding them would fabricate an E2E duration.",
            "mixed_scope_mechanical_sum_reportable_as_elapsed": False,
        },
        "double_count_controls": [
            "Service rasters and panel crops/candidates are different denominators and are never added.",
            "The six-route 300 count is an aligned subset, not the full 312 panel-candidate pool.",
            "Each ablation comparison reuses reference-backed flat and reduced-text columns; only its one new no-reference strip is counted.",
            "The two ablation outputs cover eight ComicPanelPlans but remain unsplit sequence diagnostics and contribute zero panel crops.",
            "Cadence, hybrid, comparison, contact-sheet, lettering, and phone artifacts are local derivatives and contribute zero service rasters.",
        ],
        "package_activity": {
            "new_pixels": 0,
            "provider_calls": 0,
            "uploads": 0,
            "spend_usd": 0,
            "acceptance_or_rights_changes": 0,
        },
        "boundary": "Deterministic accounting evidence only. No pixels, provider call, upload, spend, acceptance, rights, or production state is created by this package.",
    }


def render_markdown(record: dict[str, Any]) -> str:
    totals = record["totals"]
    lines = [
        "# CH05 active-goal art/output reconciliation r1",
        "",
        "This package reconciles non-overlapping output denominators from tracked manifests. ComicPanelPlan is the only planning structure; no pixel, provider, upload, spend, acceptance, or rights action occurs here.",
        "",
        "## Reconciled totals",
        "",
        "| Metric | Count |",
        "| --- | ---: |",
        f"| Service raster outputs | {totals['service_raster_outputs']} |",
        f"| Panel-level candidates/crops | {totals['panel_level_candidates_or_crops']} |",
        f"| Authorized reference uses | {totals['authorized_reference_uses']} |",
        f"| Zero-reference outputs | {totals['zero_reference_outputs']} |",
        f"| Unsplit ablation diagnostics | {totals['unsplit_ablation_diagnostics']} |",
        "",
        "## Components",
        "",
        "| Component | Service rasters | Panel candidates/crops | Reference uses | Zero-reference | Timing scope |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for component in record["components"]:
        timing = component["timing"]
        seconds = timing.get("seconds")
        if seconds is None:
            timing_text = (
                f"{timing['scope_class']}: {timing['unique_execution_observation_sum_seconds']} s summed observations; "
                f"~{timing['approximate_overlap_adjusted_client_wall_seconds']} s overlap-adjusted"
            )
        else:
            timing_text = f"{timing['scope_class']}: {seconds} s"
        lines.append(
            f"| `{component['component']}` | {component['service_raster_outputs']} | "
            f"{component['panel_level_candidates_or_crops']} | {component['authorized_reference_uses']} | "
            f"{component['zero_reference_outputs']} | {timing_text} |"
        )
    subset = record["six_route_subset"]
    lines.extend(
        [
            "",
            "## Six-route subset relationship",
            "",
            subset["relationship"],
            "",
            "The two no-reference ablation strips are service outputs but were never split into panel candidates. Their five-plus-three plan coverage must not be counted as eight crops.",
            "",
            "## Timing boundary",
            "",
            "Aggregate end-to-end time is deliberately `null`. The source records mix summed per-execution observations, approximate overlap-adjusted client wall, overlap-adjusted batch wall, non-overlap arithmetic, one concurrent-batch wall, and individual call walls. A mechanical sum is prohibited because it would not represent elapsed production time.",
            "",
            "## Exact source bindings",
            "",
            "| Path | SHA-256 | Git blob OID | Bytes |",
            "| --- | --- | --- | ---: |",
        ]
    )
    seen: set[str] = set()
    for component in record["components"]:
        for source in component["source_manifests"]:
            if source["path"] in seen:
                continue
            seen.add(source["path"])
            lines.append(
                f"| `{source['path']}` | `{source['sha256']}` | `{source['git_blob_oid']}` | {source['bytes']} |"
            )
    lines.extend(["", "## Boundary", "", record["boundary"], ""])
    return "\n".join(lines)


def main() -> int:
    record = build_record()
    OUTPUT_JSON.write_text(
        json.dumps(record, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    OUTPUT_MARKDOWN.write_text(render_markdown(record), encoding="utf-8", newline="\n")
    print(
        "CH05 active-goal output reconciliation: "
        f"rasters={record['totals']['service_raster_outputs']}; "
        f"panels={record['totals']['panel_level_candidates_or_crops']}; "
        f"refs={record['totals']['authorized_reference_uses']}; "
        f"zero-ref={record['totals']['zero_reference_outputs']}; "
        f"unsplit={record['totals']['unsplit_ablation_diagnostics']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
