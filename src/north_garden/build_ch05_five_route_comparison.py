"""Build deterministic five-route CH05 complete-chapter comparison evidence."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont, ImageOps

from build_ch05_r6_alt_graphic_comparison import metric


ROOT = Path(__file__).resolve().parents[2]
ROUTES = ("r6", "alt_graphic", "clear_line_watercolor", "premium_cel", "flat_graphic_gouache")
ROUTE_LABELS = {
    "r6": "R6 BASE",
    "alt_graphic": "ALT GRAPHIC CONTROL",
    "clear_line_watercolor": "CLEAR-LINE STYLE LEAD",
    "premium_cel": "PREMIUM-CEL PANEL SOURCE",
    "flat_graphic_gouache": "FLAT-GOUACHE DENSITY PROBE",
}
ASSEMBLIES = {
    "r6": ROOT / "production/comic/run-manifests/ch05-complete-chapter-assembly-manifest-r6.json",
    "alt_graphic": ROOT / "production/comic/run-manifests/ch05-complete-chapter-alt-graphic-assembly-r1.json",
    "clear_line_watercolor": ROOT / "production/comic/run-manifests/ch05-complete-chapter-clear-line-watercolor-assembly-r1.json",
    "premium_cel": ROOT / "production/comic/run-manifests/ch05-complete-chapter-premium-cel-assembly-r1.json",
    "flat_graphic_gouache": ROOT / "production/comic/run-manifests/ch05-complete-chapter-flat-graphic-gouache-assembly-r1.json",
}
TRIAGES = {
    "r6": ROOT / "docs/research/evidence/ch05-complete-chapter-agent-triage-r6.json",
    "alt_graphic": ROOT / "docs/research/evidence/ch05-complete-chapter-alt-graphic-agent-triage-r1.json",
    "clear_line_watercolor": ROOT / "docs/research/evidence/ch05-complete-chapter-clear-line-watercolor-agent-triage-r1.json",
    "premium_cel": ROOT / "docs/research/evidence/ch05-complete-chapter-premium-cel-agent-triage-r1.json",
    "flat_graphic_gouache": ROOT / "docs/research/evidence/ch05-complete-chapter-flat-graphic-gouache-agent-triage-r1.json",
}
PHONES = {
    "r6": ROOT / "experiments/review-packets/ch05-complete-chapter-draft-r6/lettered/ch05-complete-chapter-lettered-phone-390px-r1.png",
    "alt_graphic": ROOT / "experiments/review-packets/ch05-complete-chapter-alt-graphic-r1/lettered/ch05-complete-chapter-alt-graphic-lettered-r1-phone-390px.png",
    "clear_line_watercolor": ROOT / "experiments/review-packets/ch05-complete-chapter-clear-line-watercolor-r1/lettered/ch05-complete-chapter-clear-line-watercolor-lettered-r1-phone-390px.png",
    "premium_cel": ROOT / "experiments/review-packets/ch05-complete-chapter-premium-cel-r1/lettered/ch05-complete-chapter-premium-cel-lettered-r1-phone-390px.png",
    "flat_graphic_gouache": ROOT / "experiments/review-packets/ch05-complete-chapter-flat-graphic-gouache-r1/lettered/ch05-complete-chapter-flat-graphic-gouache-lettered-r1-phone-390px.png",
}
OUT = ROOT / "experiments/review-packets/ch05-five-route-comparison-r1"
EVIDENCE = ROOT / "docs/research/evidence/ch05-five-route-comparison-r1.json"
ANCHORS = (1, 13, 29, 32, 36, 39, 41, 43, 48, 50)
SEMANTIC_COUNTS = {
    "r6_supplemental": {"pass": 47, "warn": 1, "fail": 2},
    "alt_graphic": {"pass": 36, "warn": 7, "fail": 7},
    "clear_line_watercolor": {"pass": 45, "warn": 2, "fail": 3},
    "premium_cel": {"pass": 40, "warn": 5, "fail": 5},
    "flat_graphic_gouache": {"pass": 41, "warn": 6, "fail": 3},
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf", size)
    except OSError:
        return ImageFont.load_default(size=size)


def load_panel(entry: dict[str, Any]) -> Image.Image:
    path = ROOT / entry["source"]["path"]
    if sha256(path) != entry["source"]["sha256"]:
        raise ValueError(f"source hash mismatch: {entry['panel_id']}")
    with Image.open(path) as opened:
        return opened.convert("RGB")


def artifact(path: Path) -> dict[str, Any]:
    with Image.open(path) as opened:
        width, height = opened.size
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "sha256": sha256(path),
        "width": width,
        "height": height,
        "bytes": path.stat().st_size,
        "repository_state": "IGNORED_LOCAL_REVIEW_ARTIFACT",
    }


def status_color(status: str) -> str:
    if status.startswith("PASS"):
        return "#2d8a57"
    if status.startswith("WARN"):
        return "#c47a16"
    return "#b83b3b"


def build_all_50(entries: dict[str, list[dict[str, Any]]], statuses: dict[str, dict[str, str]], path: Path) -> None:
    cell_w, row_h, gap, margin, header = 390, 205, 12, 20, 102
    canvas = Image.new("RGB", (margin * 2 + 5 * cell_w + 4 * gap, header + margin + 50 * row_h + 49 * gap), "#e8e4da")
    draw = ImageDraw.Draw(canvas)
    draw.text((margin, 14), "CH05 FIVE COMPLETE-CHAPTER ROUTES - ALL 50", fill="#20252a", font=font(30, True))
    draw.text((margin, 54), "Five route columns; semantic status precedes style preference; R6 retains its supplemental cross-panel audit", fill="#3d464e", font=font(16))
    for route_index, route in enumerate(ROUTES):
        draw.text((margin + route_index * (cell_w + gap) + 8, 80), ROUTE_LABELS[route], fill="#303940", font=font(13, True))
    for panel_index in range(50):
        panel_number = panel_index + 1
        y = header + panel_index * (row_h + gap)
        for route_index, route in enumerate(ROUTES):
            entry = entries[route][panel_index]
            status = statuses[route][entry["panel_id"]]
            color = status_color(status)
            x = margin + route_index * (cell_w + gap)
            draw.rectangle((x, y, x + cell_w, y + row_h), fill="#faf8f2", outline=color, width=3)
            draw.text((x + 8, y + 5), f"P{panel_number:03d}  {status}", fill=color, font=font(14, True))
            image = ImageOps.contain(load_panel(entry), (cell_w - 16, row_h - 36), Image.Resampling.LANCZOS)
            canvas.paste(image, (x + 8 + (cell_w - 16 - image.width) // 2, y + 29 + (row_h - 36 - image.height) // 2))
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path, "PNG", compress_level=6, optimize=False)


def build_anchors(entries: dict[str, list[dict[str, Any]]], statuses: dict[str, dict[str, str]], path: Path) -> None:
    cell_w, row_h, gap, margin, header = 390, 330, 12, 20, 102
    canvas = Image.new("RGB", (margin * 2 + 5 * cell_w + 4 * gap, header + margin + len(ANCHORS) * row_h + (len(ANCHORS) - 1) * gap), "#e8e4da")
    draw = ImageDraw.Draw(canvas)
    draw.text((margin, 14), "CH05 FIVE-ROUTE SEMANTIC ANCHORS", fill="#20252a", font=font(30, True))
    draw.text((margin, 54), "P001/P013/P029/P032/P036/P039/P041/P043/P048/P050; compare story behavior before visual preference", fill="#3d464e", font=font(16))
    for route_index, route in enumerate(ROUTES):
        draw.text((margin + route_index * (cell_w + gap) + 8, 80), ROUTE_LABELS[route], fill="#303940", font=font(13, True))
    for row_index, panel_number in enumerate(ANCHORS):
        y = header + row_index * (row_h + gap)
        for route_index, route in enumerate(ROUTES):
            entry = entries[route][panel_number - 1]
            status = statuses[route][entry["panel_id"]]
            color = status_color(status)
            x = margin + route_index * (cell_w + gap)
            draw.rectangle((x, y, x + cell_w, y + row_h), fill="#faf8f2", outline=color, width=4)
            draw.text((x + 8, y + 7), f"P{panel_number:03d}  {status}", fill=color, font=font(15, True))
            image = ImageOps.contain(load_panel(entry), (cell_w - 20, row_h - 48), Image.Resampling.LANCZOS)
            canvas.paste(image, (x + 10 + (cell_w - 20 - image.width) // 2, y + 38 + (row_h - 48 - image.height) // 2))
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path, "PNG", compress_level=6, optimize=False)


def build_phone(path: Path) -> None:
    images: dict[str, Image.Image] = {}
    for route, source in PHONES.items():
        with Image.open(source) as opened:
            image = opened.convert("RGB")
        if image.width != 390:
            raise ValueError(f"phone source is not 390px wide: {route}")
        images[route] = image
    margin, gap, header = 20, 18, 76
    canvas = Image.new("RGB", (margin * 2 + 5 * 390 + 4 * gap, header + max(image.height for image in images.values()) + margin), "#11151a")
    draw = ImageDraw.Draw(canvas)
    for route_index, route in enumerate(ROUTES):
        x = margin + route_index * (390 + gap)
        draw.text((x, 14), ROUTE_LABELS[route], fill="#f4f1e8", font=font(15, True))
        canvas.paste(images[route], (x, header))
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path, "PNG", compress_level=6, optimize=False)


def count_statuses(statuses: dict[str, str]) -> dict[str, int]:
    counts = {"pass": 0, "warn": 0, "fail": 0}
    for status in statuses.values():
        counts[status.rstrip("*").lower()] += 1
    return counts


def percent_change(new: float, baseline: float) -> float:
    return round((new / baseline - 1.0) * 100.0, 3)


def main() -> int:
    assemblies = {route: json.loads(path.read_text(encoding="utf-8")) for route, path in ASSEMBLIES.items()}
    entries = {route: document["entries"] for route, document in assemblies.items()}
    canonical_ids = [entry["panel_id"] for entry in entries["r6"]]
    if len(canonical_ids) != 50 or any([entry["panel_id"] for entry in entries[route]] != canonical_ids for route in ROUTES):
        raise ValueError("all five assemblies must share the 50 canonical ordered panel ids")
    triages = {route: json.loads(path.read_text(encoding="utf-8")) for route, path in TRIAGES.items()}
    statuses: dict[str, dict[str, str]] = {}
    for route in ROUTES:
        status_key = "semantic_status" if route == "flat_graphic_gouache" else "status"
        statuses[route] = {row["panel_id"]: row[status_key] for row in triages[route]["rows"]}
    statuses["r6"]["ng-ch05-sc01-p001"] = "FAIL*"
    statuses["r6"]["ng-ch05-sc01-p032"] = "WARN*"
    statuses["r6"]["ng-ch05-sc01-p041"] = "FAIL*"
    expected_keys = {
        "r6": "r6_supplemental",
        "alt_graphic": "alt_graphic",
        "clear_line_watercolor": "clear_line_watercolor",
        "premium_cel": "premium_cel",
        "flat_graphic_gouache": "flat_graphic_gouache",
    }
    for route in ROUTES:
        if set(statuses[route]) != set(canonical_ids):
            raise ValueError(f"triage coverage mismatch: {route}")
        if count_statuses(statuses[route]) != SEMANTIC_COUNTS[expected_keys[route]]:
            raise ValueError(f"triage semantic count mismatch: {route}")

    aggregate: dict[str, dict[str, float]] = {}
    per_panel: list[dict[str, Any]] = []
    measured: dict[str, list[dict[str, float]]] = {route: [] for route in ROUTES}
    for index, panel_id in enumerate(canonical_ids):
        row: dict[str, Any] = {"panel_id": panel_id}
        for route in ROUTES:
            source = ROOT / entries[route][index]["source"]["path"]
            values = metric(load_panel(entries[route][index]), source.stat().st_size)
            measured[route].append(values)
            row[route] = values
        per_panel.append(row)
    for route in ROUTES:
        aggregate[route] = {key: round(sum(row[key] for row in measured[route]) / 50, 6) for key in measured[route][0]}
    flat_changes = {
        baseline: {key: percent_change(aggregate["flat_graphic_gouache"][key], aggregate[baseline][key]) for key in aggregate[baseline]}
        for baseline in ("r6", "clear_line_watercolor", "premium_cel")
    }

    all_50 = OUT / "ch05-five-route-all-50-contact-sheet.png"
    anchors = OUT / "ch05-five-route-semantic-anchors.png"
    phone = OUT / "ch05-five-route-lettered-phone-comparison.png"
    build_all_50(entries, statuses, all_50)
    build_anchors(entries, statuses, anchors)
    build_phone(phone)

    inputs = [*ASSEMBLIES.values(), *TRIAGES.values(), *PHONES.values()]
    flat_summary = triages["flat_graphic_gouache"]["summary"]
    document = {
        "record_type": "CH05CompleteChapterFiveRouteComparison",
        "schema_version": "1.0",
        "record_id": "ng-ch05-five-route-comparison-r1",
        "state": "ENGINEERING_SELECTION_PENDING_OWNER_REVIEW",
        "medium": "comic",
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "inputs": [{"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path)} for path in inputs],
        "coverage": {"routes": 5, "comic_panel_plans_per_route": 50, "paired_panel_ids": 50, "total_panel_candidates_compared": 250},
        "semantic_anchor_panel_ids": [f"ng-ch05-sc01-p{number:03d}" for number in ANCHORS],
        "semantic_counts": SEMANTIC_COUNTS,
        "flat_graphic_gouache_constraints": {
            "semantic_counts_used_for_route_comparison": SEMANTIC_COUNTS["flat_graphic_gouache"],
            "combined_semantic_lettering_phone_status": {"pass": flat_summary["pass"], "warn": flat_summary["warn"], "fail": flat_summary["fail"]},
            "lettering_clearance": {"pass": flat_summary["lettering_pass"], "warn": flat_summary["lettering_warn"], "fail": flat_summary["lettering_fail"]},
            "strict_requested_style_density": {"pass": flat_summary["style_density_pass"], "warn": flat_summary["style_density_warn"], "fail": flat_summary["style_density_fail_strict"]},
            "interpretation": "Flat-gouache has only three semantic failures, but its 25 lettering-clearance failures plus 6 warnings and 0/50 strict requested-style-density compliance prevent wholesale selection.",
        },
        "visual_complexity": {
            "method": "Same 390px/equal-panel entropy, FIND_EDGES>=32 density, and native PNG bytes/pixel definitions as r6-vs-alt, three-route, and four-route comparisons.",
            "aggregate_equal_panel_weight": aggregate,
            "flat_proxy_change_percent": flat_changes,
            "per_panel": per_panel,
            "interpretation": "Flat-gouache achieves a modest reduction in edge density and PNG bytes/pixel relative to R6 and larger reductions relative to clear-line watercolor, but entropy remains near R6 and manual inspection finds 0/50 panels within the strict 4-6 broad-mass texture budget. These proxies support comparison only and do not measure quality.",
        },
        "ranking": [
            {"rank": 1, "route": "r6_plus_cross_panel_gates", "role": "current_base", "reason": "Lowest measured semantic failure/warning burden (47 pass, 1 warn, 2 fail) and strongest existing causal assembly."},
            {"rank": 2, "route": "clear_line_watercolor", "role": "leading_style_direction", "reason": "Best measured style-development route while retaining a low semantic burden (45 pass, 2 warn, 3 fail)."},
            {"rank": 3, "route": "premium_cel", "role": "selected_panel_source", "reason": "Useful panel-level source, while its 40/5/5 semantic result still prevents wholesale selection."},
            {"rank": 4, "route": "flat_graphic_gouache", "role": "density_diagnostic", "reason": "Semantically competitive at 41/6/3 and modestly lower in two complexity proxies, but 0/50 strict density compliance and 25 lettering failures make it a diagnostic rather than a wholesale route."},
            {"rank": 5, "route": "alt_graphic", "role": "control", "reason": "Retained as a controlled comparison; seven warnings and seven failures remain the largest semantic burden."},
        ],
        "recommendation": {
            "production_mechanism": "sequence-strip generation plus deterministic panel extraction, variable-cadence assembly, phone/lettering review, and hash-isolated panel selection/repair",
            "current_base": "r6",
            "leading_style_direction": "clear_line_watercolor",
            "selected_panel_source": "premium_cel",
            "density_diagnostic": "flat_graphic_gouache",
            "control_route": "alt_graphic",
            "flat_graphic_gouache_wholesale_selection": False,
            "wholesale_route_selection": None,
            "next_high_information_step": "owner reviews five-route semantic anchors and full lettered phone scrolls, then advances only explicitly selected, hash-pinned panels into a hybrid assembly; any new low-density probe must enforce a measurable texture budget and safe-zone-aware composition",
            "appearance_only_selection": False,
        },
        "owner_disposition": {
            "accepted_route": None,
            "accepted_panel_ids": None,
            "commercial_rights_clearance": None,
            "exact_production_base": None,
        },
        "artifacts": {
            "all_50_five_columns": artifact(all_50),
            "semantic_anchors": artifact(anchors),
            "lettered_phone_comparison": artifact(phone),
        },
        "spend": {"direct_paid_api_cloud_usd": 0.0, "built_in_product_monetary_cost_usd": None},
        "limitations": [
            "Agent triage is non-gating.",
            "The R6 supplemental audit is preserved as 47/1/2 and does not rewrite frozen evidence.",
            "Flat-gouache comparison statuses use its semantic_status field; its heavier combined status and lettering burden remain separately disclosed.",
            "Complexity proxies do not measure artistic quality, identity, narrative value, strict style compliance, or commercial suitability.",
            "Prompt gates do not prove pixel compliance.",
            "No route or panel is accepted, commercially cleared, or selected as an exact production base.",
        ],
        "boundary": "Engineering recommendation only; owner acceptance, exact panel advancement, commercial-rights clearance, and production-base selection remain null and separate.",
    }
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"artifacts": document["artifacts"], "metrics": aggregate, "flat_proxy_change_percent": flat_changes, "output": EVIDENCE.relative_to(ROOT).as_posix(), "sha256": sha256(EVIDENCE)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
