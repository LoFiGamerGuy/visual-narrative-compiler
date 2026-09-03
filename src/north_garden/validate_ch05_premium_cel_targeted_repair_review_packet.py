"""Validate deterministic review evidence for the CH05 targeted-repair trio."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = (
    ROOT / "docs/research/evidence/ch05-premium-cel-targeted-repair-trio-review-r1.json"
)
EXECUTION = (
    ROOT
    / "production/comic/run-manifests/ch05-premium-cel-targeted-repair-trio-execution-r1.json"
)
PREFLIGHT = (
    ROOT
    / "production/comic/run-manifests/ch05-premium-cel-targeted-repair-trio-r1.json"
)
EXPECTED_ORDERS = [1, 32, 39]
EXPECTED_STATUSES = ["PASS", "WARN", "PASS"]
EXPECTED_HAIR_WARDROBE = [
    {"soren": "PASS", "sigrid": "PASS"},
    {"soren": "PASS", "sigrid": "NOT_APPLICABLE"},
    {"soren": "PARTIAL_PASS_VISIBLE_HEAD_AND_COAT", "sigrid": "NOT_APPLICABLE"},
]
EXPECTED_TARGET_CHECKS = [
    {
        "cold_house_no_smoke_glow_or_lit_window": "PASS",
        "farmhouse_behind_and_upslope": "PASS",
        "backs_and_downhill_away_travel": "PASS",
        "sigrid_leads_soren_follows": "PASS",
    },
    {
        "far_dry_bank_only": "PASS",
        "water_gap_and_bank_separation": "PASS",
        "no_near_bank_or_water_prints": "PASS",
        "heel_toe_orientation_at_phone_width": "WARN_OWNER_REVIEW_REQUIRED",
    },
    {
        "square_circle_and_third_mark_simultaneous": "PASS",
        "third_mark_upstream_near_torn_edge": "PASS",
        "finger_on_third_mark": "PASS",
        "single_uninterrupted_map_surface": "PASS",
    },
]
EXPECTED_SUMMARY = {
    "source_outputs": 3,
    "phone_previews": 3,
    "safe_zone_overlays": 3,
    "pass": 2,
    "warn": 1,
    "fail": 0,
    "owner_reviews": 0,
    "accepted": 0,
    "commercially_cleared": 0,
    "exact_production_base": 0,
    "provider_calls": 0,
    "uploads": 0,
    "external_cost_usd": "0.000000",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ignored_untracked(relative: str) -> bool:
    ignored = (
        subprocess.run(
            ["git", "check-ignore", "--quiet", "--", relative], cwd=ROOT, check=False
        ).returncode
        == 0
    )
    tracked = (
        subprocess.run(
            ["git", "ls-files", "--error-unmatch", "--", relative],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        ).returncode
        == 0
    )
    return ignored and not tracked


def expected_overlay(source: Image.Image, zones: list[dict[str, Any]]) -> Image.Image:
    base = source.convert("RGBA")
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    for zone in zones:
        x, y, width, height = zone["rect_norm"]
        box = (
            round(x * base.width),
            round(y * base.height),
            round((x + width) * base.width),
            round((y + height) * base.height),
        )
        draw.rectangle(
            box,
            fill=(30, 210, 220, 74),
            outline=(0, 120, 155, 245),
            width=max(3, base.width // 300),
        )
    return Image.alpha_composite(base, layer).convert("RGB")


def pixels_equal(left: Image.Image, right: Image.Image) -> bool:
    left_rgb = left.convert("RGB")
    right_rgb = right.convert("RGB")
    return (
        left_rgb.size == right_rgb.size
        and ImageChops.difference(left_rgb, right_rgb).getbbox() is None
    )


def validate_artifact(
    value: dict[str, Any],
    label: str,
    errors: list[str],
    expected_size: tuple[int, int] | None = None,
) -> Path | None:
    check = lambda condition, message: None if condition else errors.append(message)
    relative = value.get("path", "")
    path = ROOT / relative
    check(
        relative.startswith(
            "experiments/review-packets/ch05-premium-cel-targeted-repair-trio-r1/review/"
        ),
        f"{label} path scope",
    )
    check(path.is_file(), f"{label} exists")
    if not path.is_file():
        return None
    check(sha256(path) == value.get("sha256"), f"{label} hash")
    check(path.stat().st_size == value.get("bytes"), f"{label} bytes")
    with Image.open(path) as image:
        check(image.format == "PNG", f"{label} format")
        check(
            [image.width, image.height] == [value.get("width"), value.get("height")],
            f"{label} dimensions",
        )
        if expected_size is not None:
            check(image.size == expected_size, f"{label} expected dimensions")
    check(ignored_untracked(relative), f"{label} ignored/untracked")
    return path


def validate(document: dict[str, Any], verify_files: bool = True) -> list[str]:
    errors: list[str] = []
    check = lambda condition, message: None if condition else errors.append(message)
    execution = json.loads(EXECUTION.read_text(encoding="utf-8"))
    preflight = json.loads(PREFLIGHT.read_text(encoding="utf-8"))
    execution_rows = execution["records"]
    preflight_by_order = {row["display_order"]: row for row in preflight["requests"]}
    rows = document.get("triage", [])
    artifacts = document.get("review_artifacts", {})

    check(
        document.get("record_type") == "CH05PremiumCelTargetedRepairTrioReviewEvidence",
        "record_type",
    )
    check(
        document.get("schema_version") == "1.0"
        and document.get("record_id")
        == "ng-ch05-premium-cel-targeted-repair-trio-review-r1",
        "identity",
    )
    check(
        document.get("state") == "NON_GATING_AGENT_TRIAGE_OWNER_REVIEW_PENDING", "state"
    )
    check(
        document.get("medium") == "comic"
        and document.get("planning_structure") == "ComicPanelPlan",
        "comic planning",
    )
    check(
        document.get("animation_shot_plan") is None and document.get("e_conte") is None,
        "cross-medium fields",
    )
    check(
        document.get("sources")
        == [
            {
                "path": EXECUTION.relative_to(ROOT).as_posix(),
                "sha256": sha256(EXECUTION),
            },
            {
                "path": PREFLIGHT.relative_to(ROOT).as_posix(),
                "sha256": sha256(PREFLIGHT),
            },
        ],
        "source bindings",
    )
    check(document.get("summary") == EXPECTED_SUMMARY, "summary")
    check(
        [row.get("display_order") for row in rows] == EXPECTED_ORDERS,
        "triage order/denominator",
    )
    check(
        [row.get("agent_triage", {}).get("status") for row in rows]
        == EXPECTED_STATUSES,
        "triage statuses",
    )

    for index, (row, execution_row) in enumerate(zip(rows, execution_rows)):
        order = EXPECTED_ORDERS[index]
        check(
            row.get("panel_id") == execution_row.get("panel_id"),
            f"panel binding P{order:03d}",
        )
        check(
            row.get("source_output")
            == {
                key: execution_row["output"][key]
                for key in ("path", "sha256", "width", "height", "bytes")
            },
            f"source output binding P{order:03d}",
        )
        triage = row.get("agent_triage", {})
        check(
            triage.get("target_checks") == EXPECTED_TARGET_CHECKS[index],
            f"target checks P{order:03d}",
        )
        check(
            triage.get("hair_wardrobe") == EXPECTED_HAIR_WARDROBE[index],
            f"hair/wardrobe P{order:03d}",
        )
        check(
            isinstance(triage.get("summary"), str) and bool(triage.get("summary")),
            f"triage summary P{order:03d}",
        )
        check(
            row.get("owner_review_state") == "PENDING"
            and row.get("human_review_minutes") is None
            and all(
                row.get(key) is False
                for key in ("accepted", "commercially_cleared", "exact_production_base")
            ),
            f"review boundary P{order:03d}",
        )

    phone = artifacts.get("phone_previews", [])
    overlays = artifacts.get("safe_zone_overlays", [])
    check(len(phone) == 3 and len(overlays) == 3, "derived artifact counts")
    check(
        len({item.get("path") for item in phone + overlays}) == 6,
        "derived artifact uniqueness",
    )
    comparison_keys = [
        "native_comparison",
        "phone_390_comparison",
        "safe_zone_comparison",
    ]
    check(
        all(isinstance(artifacts.get(key), dict) for key in comparison_keys),
        "comparison artifacts",
    )
    check(
        len({artifacts.get(key, {}).get("path") for key in comparison_keys}) == 3,
        "comparison uniqueness",
    )

    if verify_files:
        validate_artifact(
            artifacts.get("native_comparison", {}),
            "native comparison",
            errors,
            (1680, 854),
        )
        validate_artifact(
            artifacts.get("phone_390_comparison", {}),
            "phone comparison",
            errors,
            (430, 1677),
        )
        validate_artifact(
            artifacts.get("safe_zone_comparison", {}),
            "safe-zone comparison",
            errors,
            (1680, 854),
        )
        for index, execution_row in enumerate(execution_rows):
            order = EXPECTED_ORDERS[index]
            source_path = ROOT / execution_row["output"]["path"]
            check(
                source_path.is_file()
                and sha256(source_path) == execution_row["output"]["sha256"],
                f"source file binding P{order:03d}",
            )
            if (
                not source_path.is_file()
                or index >= len(phone)
                or index >= len(overlays)
            ):
                continue
            with Image.open(source_path) as source_image:
                source = source_image.convert("RGB")
            expected_height = round(source.height * 390 / source.width)
            phone_path = validate_artifact(
                phone[index],
                f"phone preview P{order:03d}",
                errors,
                (390, expected_height),
            )
            overlay_path = validate_artifact(
                overlays[index], f"safe-zone overlay P{order:03d}", errors, source.size
            )
            if phone_path is not None:
                with Image.open(phone_path) as actual:
                    expected = source.resize(
                        (390, expected_height), Image.Resampling.LANCZOS
                    )
                    check(
                        pixels_equal(actual, expected), f"phone derivation P{order:03d}"
                    )
            if overlay_path is not None:
                with Image.open(overlay_path) as actual:
                    expected = expected_overlay(
                        source, preflight_by_order[order]["lettering_safe_zones"]
                    )
                    check(
                        pixels_equal(actual, expected),
                        f"overlay derivation P{order:03d}",
                    )
    return errors


def self_test(document: dict[str, Any]) -> tuple[int, int]:
    mutations: list[Callable[[dict[str, Any]], None]] = [
        lambda value: value.__setitem__("state", "ACCEPTED"),
        lambda value: value.__setitem__("planning_structure", "AnimationShotPlan"),
        lambda value: value.__setitem__("animation_shot_plan", {}),
        lambda value: value["sources"][0].__setitem__("sha256", "0" * 64),
        lambda value: value["triage"].pop(),
        lambda value: value["triage"][0]["agent_triage"].__setitem__("status", "FAIL"),
        lambda value: value["triage"][1]["agent_triage"].__setitem__("status", "PASS"),
        lambda value: value["triage"][1]["agent_triage"]["target_checks"].__setitem__(
            "heel_toe_orientation_at_phone_width", "PASS"
        ),
        lambda value: value["triage"][2]["agent_triage"]["hair_wardrobe"].__setitem__(
            "soren", "PASS"
        ),
        lambda value: value["triage"][0].__setitem__("accepted", True),
        lambda value: value["triage"][0]["source_output"].__setitem__(
            "sha256", "0" * 64
        ),
        lambda value: value["summary"].__setitem__("owner_reviews", 1),
        lambda value: value["summary"].__setitem__("provider_calls", 1),
        lambda value: value["summary"].__setitem__("commercially_cleared", 1),
        lambda value: value["review_artifacts"]["phone_previews"][0].__setitem__(
            "path", value["review_artifacts"]["phone_previews"][1]["path"]
        ),
        lambda value: value["review_artifacts"].pop("safe_zone_comparison"),
    ]
    caught = 0
    for mutation in mutations:
        candidate = copy.deepcopy(document)
        mutation(candidate)
        caught += bool(validate(candidate, verify_files=False))
    return caught, len(mutations)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    document = json.loads(EVIDENCE.read_text(encoding="utf-8"))
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
                "records": len(document.get("triage", [])),
                "self_test": f"{caught}/{total}" if args.self_test else None,
            },
            sort_keys=True,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
