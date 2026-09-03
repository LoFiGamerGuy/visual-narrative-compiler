"""Build deterministic local review artifacts and non-gating triage for the repair trio."""

from __future__ import annotations

import hashlib
import json
import textwrap
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[2]
EXECUTION = (
    ROOT
    / "production/comic/run-manifests/ch05-premium-cel-targeted-repair-trio-execution-r1.json"
)
PREFLIGHT = (
    ROOT
    / "production/comic/run-manifests/ch05-premium-cel-targeted-repair-trio-r1.json"
)
OUT = (
    ROOT / "experiments/review-packets/ch05-premium-cel-targeted-repair-trio-r1/review"
)
EVIDENCE = (
    ROOT / "docs/research/evidence/ch05-premium-cel-targeted-repair-trio-review-r1.json"
)
FONT = ImageFont.load_default()
TRIAGE = {
    1: {
        "status": "PASS",
        "summary": "Cold farmhouse is behind and upslope; both adults show backs/three-quarter backs and travel downhill away.",
        "target_checks": {
            "cold_house_no_smoke_glow_or_lit_window": "PASS",
            "farmhouse_behind_and_upslope": "PASS",
            "backs_and_downhill_away_travel": "PASS",
            "sigrid_leads_soren_follows": "PASS",
        },
        "hair_wardrobe": {"soren": "PASS", "sigrid": "PASS"},
    },
    32: {
        "status": "WARN",
        "summary": "Far dry bank and water separation pass; exact heel/toe facing remains pending owner confirmation at 390px.",
        "target_checks": {
            "far_dry_bank_only": "PASS",
            "water_gap_and_bank_separation": "PASS",
            "no_near_bank_or_water_prints": "PASS",
            "heel_toe_orientation_at_phone_width": "WARN_OWNER_REVIEW_REQUIRED",
        },
        "hair_wardrobe": {"soren": "PASS", "sigrid": "NOT_APPLICABLE"},
    },
    39: {
        "status": "PASS",
        "summary": "Square farmhouse, circular mill, and third upstream mark appear simultaneously; Soren's finger rests on the third mark.",
        "target_checks": {
            "square_circle_and_third_mark_simultaneous": "PASS",
            "third_mark_upstream_near_torn_edge": "PASS",
            "finger_on_third_mark": "PASS",
            "single_uninterrupted_map_surface": "PASS",
        },
        "hair_wardrobe": {
            "soren": "PARTIAL_PASS_VISIBLE_HEAD_AND_COAT",
            "sigrid": "NOT_APPLICABLE",
        },
    },
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def artifact(path: Path) -> dict[str, Any]:
    with Image.open(path) as image:
        width, height = image.size
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "sha256": sha256(path),
        "width": width,
        "height": height,
        "bytes": path.stat().st_size,
    }


def save_exact(image: Image.Image, path: Path) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    rgb = image.convert("RGB")
    if path.exists():
        with Image.open(path) as current:
            if (
                current.convert("RGB").size != rgb.size
                or current.convert("RGB").tobytes() != rgb.tobytes()
            ):
                raise ValueError(
                    f"refusing to overwrite non-identical review artifact: {path}"
                )
    else:
        rgb.save(path, format="PNG", compress_level=9, optimize=False)
    return artifact(path)


def fit(image: Image.Image, width: int, height: int) -> Image.Image:
    return ImageOps.contain(
        image.convert("RGB"), (width, height), Image.Resampling.LANCZOS
    )


def label(
    canvas: Image.Image, text: str, xy: tuple[int, int], fill=(238, 242, 246)
) -> None:
    ImageDraw.Draw(canvas).text(xy, text, font=FONT, fill=fill)


def safe_overlay(source: Image.Image, zones: list[dict[str, Any]]) -> Image.Image:
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


def contact_sheet(entries: list[dict[str, Any]], mode: str) -> Image.Image:
    cell_width, cell_height = 560, 780
    canvas = Image.new("RGB", (cell_width * 3, cell_height + 74), (20, 25, 31))
    label(
        canvas, "CH05 premium-cel targeted repair trio | owner review pending", (18, 12)
    )
    label(
        canvas,
        "Native source is hash-pinned; displayed fit-to-cell. Cyan marks exact ComicPanelPlan lettering-safe zone."
        if mode == "safe"
        else "Native hash-pinned output preview; agent triage is non-gating.",
        (18, 34),
    )
    for index, entry in enumerate(entries):
        source = Image.open(ROOT / entry["output"]["path"]).convert("RGB")
        view = (
            safe_overlay(source, entry["lettering_safe_zones"])
            if mode == "safe"
            else source
        )
        fitted = fit(view, cell_width - 28, cell_height - 115)
        x = index * cell_width + (cell_width - fitted.width) // 2
        y = 74 + (cell_height - 115 - fitted.height) // 2
        canvas.paste(fitted, (x, y))
        order = entry["display_order"]
        triage = TRIAGE[order]
        label(
            canvas,
            f"P{order:03d} | {triage['status']} | {entry['output']['width']}x{entry['output']['height']}",
            (index * cell_width + 14, cell_height - 28),
        )
    return canvas


def phone_sheet(
    entries: list[dict[str, Any]],
) -> tuple[Image.Image, list[dict[str, Any]]]:
    previews = []
    blocks = []
    for entry in entries:
        source = Image.open(ROOT / entry["output"]["path"]).convert("RGB")
        height = round(source.height * 390 / source.width)
        preview = source.resize((390, height), Image.Resampling.LANCZOS)
        path = OUT / "phone-390" / f"P{entry['display_order']:03d}-phone-390-r1.png"
        previews.append(save_exact(preview, path))
        blocks.append((entry, preview))
    total_height = 54 + sum(preview.height + 64 for _, preview in blocks)
    canvas = Image.new("RGB", (430, total_height), (20, 25, 31))
    label(canvas, "Exact 390px phone-width previews", (20, 15))
    y = 50
    for entry, preview in blocks:
        canvas.paste(preview, (20, y))
        y += preview.height + 8
        triage = TRIAGE[entry["display_order"]]
        for line in textwrap.wrap(
            f"P{entry['display_order']:03d} {triage['status']}: {triage['summary']}",
            width=62,
        )[:3]:
            label(canvas, line, (20, y))
            y += 13
        y += 17
    return canvas, previews


def main() -> int:
    execution = json.loads(EXECUTION.read_text(encoding="utf-8"))
    entries = execution["records"]
    overlays = []
    for entry in entries:
        source = Image.open(ROOT / entry["output"]["path"]).convert("RGB")
        output = (
            OUT
            / "safe-zone-overlays"
            / f"P{entry['display_order']:03d}-safe-zone-overlay-r1.png"
        )
        overlays.append(
            save_exact(safe_overlay(source, entry["lettering_safe_zones"]), output)
        )
    native_sheet = save_exact(
        contact_sheet(entries, "native"),
        OUT / "targeted-repair-native-comparison-r1.png",
    )
    safe_sheet = save_exact(
        contact_sheet(entries, "safe"),
        OUT / "targeted-repair-safe-zone-comparison-r1.png",
    )
    phone_canvas, phone_previews = phone_sheet(entries)
    phone_sheet_artifact = save_exact(
        phone_canvas, OUT / "targeted-repair-phone-390-comparison-r1.png"
    )
    source_artifacts = [artifact(ROOT / entry["output"]["path"]) for entry in entries]
    triage_rows = []
    for entry in entries:
        order = entry["display_order"]
        triage_rows.append(
            {
                "panel_id": entry["panel_id"],
                "display_order": order,
                "source_output": source_artifacts[len(triage_rows)],
                "agent_triage": TRIAGE[order],
                "owner_review_state": "PENDING",
                "human_review_minutes": None,
                "accepted": False,
                "commercially_cleared": False,
                "exact_production_base": False,
            }
        )
    evidence = {
        "record_type": "CH05PremiumCelTargetedRepairTrioReviewEvidence",
        "schema_version": "1.0",
        "record_id": "ng-ch05-premium-cel-targeted-repair-trio-review-r1",
        "state": "NON_GATING_AGENT_TRIAGE_OWNER_REVIEW_PENDING",
        "medium": "comic",
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "sources": [
            {
                "path": EXECUTION.relative_to(ROOT).as_posix(),
                "sha256": sha256(EXECUTION),
            },
            {
                "path": PREFLIGHT.relative_to(ROOT).as_posix(),
                "sha256": sha256(PREFLIGHT),
            },
        ],
        "summary": {
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
        },
        "triage": triage_rows,
        "review_artifacts": {
            "native_comparison": native_sheet,
            "phone_390_comparison": phone_sheet_artifact,
            "safe_zone_comparison": safe_sheet,
            "phone_previews": phone_previews,
            "safe_zone_overlays": overlays,
        },
        "limitations": [
            "Agent visual triage is non-gating and does not replace owner review.",
            "P032 remains WARN because exact heel/toe orientation requires owner confirmation at 390px.",
            "P039 Soren continuity is a partial pass because only the visible head/coat portion can be reviewed.",
            "The safe-zone overlays visualize declared rectangles; they do not prove semantic clearance automatically.",
            "No output is accepted, commercially cleared, or selected as an exact production base.",
        ],
    }
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text(
        json.dumps(evidence, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "evidence": EVIDENCE.relative_to(ROOT).as_posix(),
                "sha256": sha256(EVIDENCE),
                **evidence["summary"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
