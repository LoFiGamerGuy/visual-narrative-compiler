"""Build deterministic six-route CH05 comparison and sequence-cadence evidence."""
from __future__ import annotations

import hashlib
import json
from itertools import pairwise
from pathlib import Path
from typing import Any

from build_ch05_r6_alt_graphic_comparison import metric
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[2]
ROUTES = (
    "r6",
    "alt_graphic",
    "clear_line_watercolor",
    "premium_cel",
    "flat_graphic_gouache",
    "reduced_palette_text_control",
)
ROUTE_LABELS = {
    "r6": "R6 BASE",
    "alt_graphic": "ALT GRAPHIC CONTROL",
    "clear_line_watercolor": "CLEAR-LINE",
    "premium_cel": "PREMIUM CEL",
    "flat_graphic_gouache": "FLAT-GOUACHE",
    "reduced_palette_text_control": "REDUCED-PALETTE TEXT-ONLY",
}
ASSEMBLIES = {
    "r6": ROOT / "production/comic/run-manifests/ch05-complete-chapter-assembly-manifest-r6.json",
    "alt_graphic": ROOT / "production/comic/run-manifests/ch05-complete-chapter-alt-graphic-assembly-r1.json",
    "clear_line_watercolor": ROOT / "production/comic/run-manifests/ch05-complete-chapter-clear-line-watercolor-assembly-r1.json",
    "premium_cel": ROOT / "production/comic/run-manifests/ch05-complete-chapter-premium-cel-assembly-r1.json",
    "flat_graphic_gouache": ROOT / "production/comic/run-manifests/ch05-complete-chapter-flat-graphic-gouache-assembly-r1.json",
    "reduced_palette_text_control": ROOT / "production/comic/run-manifests/ch05-complete-chapter-reduced-palette-text-control-assembly-r1.json",
}
TRIAGES = {
    "r6": ROOT / "docs/research/evidence/ch05-complete-chapter-agent-triage-r6.json",
    "alt_graphic": ROOT / "docs/research/evidence/ch05-complete-chapter-alt-graphic-agent-triage-r1.json",
    "clear_line_watercolor": ROOT / "docs/research/evidence/ch05-complete-chapter-clear-line-watercolor-agent-triage-r1.json",
    "premium_cel": ROOT / "docs/research/evidence/ch05-complete-chapter-premium-cel-agent-triage-r1.json",
    "flat_graphic_gouache": ROOT / "docs/research/evidence/ch05-complete-chapter-flat-graphic-gouache-agent-triage-r1.json",
    "reduced_palette_text_control": ROOT / "docs/research/evidence/ch05-complete-chapter-reduced-palette-text-control-agent-triage-r1.json",
}
PHONES = {
    "r6": ROOT / "experiments/review-packets/ch05-complete-chapter-draft-r6/lettered/ch05-complete-chapter-lettered-phone-390px-r1.png",
    "alt_graphic": ROOT / "experiments/review-packets/ch05-complete-chapter-alt-graphic-r1/lettered/ch05-complete-chapter-alt-graphic-lettered-r1-phone-390px.png",
    "clear_line_watercolor": ROOT / "experiments/review-packets/ch05-complete-chapter-clear-line-watercolor-r1/lettered/ch05-complete-chapter-clear-line-watercolor-lettered-r1-phone-390px.png",
    "premium_cel": ROOT / "experiments/review-packets/ch05-complete-chapter-premium-cel-r1/lettered/ch05-complete-chapter-premium-cel-lettered-r1-phone-390px.png",
    "flat_graphic_gouache": ROOT / "experiments/review-packets/ch05-complete-chapter-flat-graphic-gouache-r1/lettered/ch05-complete-chapter-flat-graphic-gouache-lettered-r1-phone-390px.png",
    "reduced_palette_text_control": ROOT / "experiments/review-packets/ch05-complete-chapter-reduced-palette-text-control-r1/lettered/ch05-complete-chapter-reduced-palette-text-control-lettered-r1-phone-390px.png",
}
REDUCED_PROMPTS = ROOT / "production/comic/run-manifests/ch05-complete-chapter-reduced-palette-text-control-prompt-manifest-r1.json"
REDUCED_EXECUTIONS = ROOT / "production/comic/run-manifests/ch05-complete-chapter-reduced-palette-text-control-execution-manifest-r1.json"
FIVE_ROUTE = ROOT / "docs/research/evidence/ch05-five-route-comparison-r1.json"
HYBRID = ROOT / "production/comic/run-manifests/ch05-semantic-pass-hybrid-assembly-r1.json"
OUT = ROOT / "experiments/review-packets/ch05-six-route-comparison-r1"
EVIDENCE = ROOT / "docs/research/evidence/ch05-six-route-comparison-r1.json"
ANCHORS = (1, 13, 29, 32, 36, 39, 41, 43, 48, 50)
R6_SUPPLEMENTAL = {1: "FAIL", 32: "WARN", 41: "FAIL"}
STATUS_RANK = {"PASS": 0, "WARN": 1, "FAIL": 2}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf", size)
    except OSError:
        return ImageFont.load_default(size=size)


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


def load_panel(entry: dict[str, Any]) -> Image.Image:
    source = ROOT / entry["source"]["path"]
    if not source.is_file() or sha256(source) != entry["source"]["sha256"]:
        raise ValueError(f"source binding failed: {entry['panel_id']}")
    with Image.open(source) as opened:
        image = opened.convert("RGB")
    if [image.width, image.height] != [entry["source"]["width"], entry["source"]["height"]]:
        raise ValueError(f"source dimensions failed: {entry['panel_id']}")
    return image


def color(status: str) -> str:
    return {"PASS": "#2d8a57", "WARN": "#c47a16", "FAIL": "#b83b3b"}.get(status, "#67717b")


def normalize_density(value: Any) -> str:
    if value == "FAIL_STRICT":
        return "FAIL"
    return value if value in STATUS_RANK else "NOT_ASSESSED"


def counts(values: list[str], not_assessed: bool = False) -> dict[str, int]:
    result = {key.lower(): values.count(key) for key in STATUS_RANK}
    if not_assessed:
        result["not_assessed"] = values.count("NOT_ASSESSED")
    return result


def build_all_50(entries: dict[str, list[dict[str, Any]]], semantic: dict[str, dict[str, str]], path: Path) -> None:
    cell_w, row_h, gap, margin, header = 360, 194, 10, 18, 104
    canvas = Image.new("RGB", (margin * 2 + 6 * cell_w + 5 * gap, header + 50 * row_h + 49 * gap + margin), "#e8e4da")
    draw = ImageDraw.Draw(canvas)
    draw.text((margin, 14), "CH05 SIX COMPLETE-CHAPTER ROUTES - ALL 50", fill="#20252a", font=font(30, True))
    draw.text((margin, 53), "Semantic status precedes appearance; all routes remain unaccepted research evidence", fill="#3d464e", font=font(16))
    for route_index, route in enumerate(ROUTES):
        draw.text((margin + route_index * (cell_w + gap) + 6, 80), ROUTE_LABELS[route], fill="#303940", font=font(12, True))
    for panel_index in range(50):
        y = header + panel_index * (row_h + gap)
        for route_index, route in enumerate(ROUTES):
            entry = entries[route][panel_index]
            status = semantic[route][entry["panel_id"]]
            x = margin + route_index * (cell_w + gap)
            draw.rectangle((x, y, x + cell_w, y + row_h), fill="#faf8f2", outline=color(status), width=3)
            draw.text((x + 7, y + 5), f"P{panel_index + 1:03d}  {status}", fill=color(status), font=font(13, True))
            image = ImageOps.contain(load_panel(entry), (cell_w - 14, row_h - 34), Image.Resampling.LANCZOS)
            canvas.paste(image, (x + 7 + (cell_w - 14 - image.width) // 2, y + 27 + (row_h - 34 - image.height) // 2))
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path, "PNG", compress_level=6, optimize=False)


def build_anchors(entries: dict[str, list[dict[str, Any]]], semantic: dict[str, dict[str, str]], path: Path) -> None:
    cell_w, row_h, gap, margin, header = 360, 316, 10, 18, 104
    canvas = Image.new("RGB", (margin * 2 + 6 * cell_w + 5 * gap, header + len(ANCHORS) * row_h + (len(ANCHORS) - 1) * gap + margin), "#e8e4da")
    draw = ImageDraw.Draw(canvas)
    draw.text((margin, 14), "CH05 SIX-ROUTE SEMANTIC ANCHORS", fill="#20252a", font=font(30, True))
    draw.text((margin, 53), "P001/P013/P029/P032/P036/P039/P041/P043/P048/P050; compare causal story behavior first", fill="#3d464e", font=font(16))
    for route_index, route in enumerate(ROUTES):
        draw.text((margin + route_index * (cell_w + gap) + 6, 80), ROUTE_LABELS[route], fill="#303940", font=font(12, True))
    for row_index, panel_number in enumerate(ANCHORS):
        y = header + row_index * (row_h + gap)
        for route_index, route in enumerate(ROUTES):
            entry = entries[route][panel_number - 1]
            status = semantic[route][entry["panel_id"]]
            x = margin + route_index * (cell_w + gap)
            draw.rectangle((x, y, x + cell_w, y + row_h), fill="#faf8f2", outline=color(status), width=4)
            draw.text((x + 7, y + 7), f"P{panel_number:03d}  {status}", fill=color(status), font=font(14, True))
            image = ImageOps.contain(load_panel(entry), (cell_w - 18, row_h - 45), Image.Resampling.LANCZOS)
            canvas.paste(image, (x + 9 + (cell_w - 18 - image.width) // 2, y + 35 + (row_h - 45 - image.height) // 2))
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path, "PNG", compress_level=6, optimize=False)


def build_phone(path: Path) -> None:
    images: dict[str, Image.Image] = {}
    for route, source in PHONES.items():
        with Image.open(source) as opened:
            image = opened.convert("RGB")
        if image.width != 390:
            raise ValueError(f"phone source must be exactly 390px wide: {route}")
        images[route] = image
    margin, gap, header = 18, 14, 76
    canvas = Image.new("RGB", (margin * 2 + 6 * 390 + 5 * gap, header + max(image.height for image in images.values()) + margin), "#11151a")
    draw = ImageDraw.Draw(canvas)
    for route_index, route in enumerate(ROUTES):
        x = margin + route_index * (390 + gap)
        draw.text((x, 14), ROUTE_LABELS[route], fill="#f4f1e8", font=font(13, True))
        canvas.paste(images[route], (x, header))
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path, "PNG", compress_level=6, optimize=False)


def build_density(
    entries: dict[str, list[dict[str, Any]]],
    density: dict[str, dict[str, str]],
    measured: dict[str, list[dict[str, float]]],
    path: Path,
) -> None:
    cell_w, row_h, gap, margin, header = 360, 328, 10, 18, 104
    canvas = Image.new("RGB", (margin * 2 + 6 * cell_w + 5 * gap, header + len(ANCHORS) * row_h + (len(ANCHORS) - 1) * gap + margin), "#e8e4da")
    draw = ImageDraw.Draw(canvas)
    draw.text((margin, 14), "CH05 SIX-ROUTE STYLE / DENSITY COMPARISON", fill="#20252a", font=font(30, True))
    draw.text((margin, 53), "Manual strict-density status where assessed; E=edge density, H=grayscale entropy. Proxies do not score quality.", fill="#3d464e", font=font(15))
    for route_index, route in enumerate(ROUTES):
        draw.text((margin + route_index * (cell_w + gap) + 6, 80), ROUTE_LABELS[route], fill="#303940", font=font(12, True))
    for row_index, panel_number in enumerate(ANCHORS):
        y = header + row_index * (row_h + gap)
        for route_index, route in enumerate(ROUTES):
            entry = entries[route][panel_number - 1]
            status = density[route][entry["panel_id"]]
            values = measured[route][panel_number - 1]
            x = margin + route_index * (cell_w + gap)
            draw.rectangle((x, y, x + cell_w, y + row_h), fill="#faf8f2", outline=color(status), width=3)
            draw.text((x + 7, y + 5), f"P{panel_number:03d} D:{status}", fill=color(status), font=font(13, True))
            image = ImageOps.contain(load_panel(entry), (cell_w - 18, row_h - 67), Image.Resampling.LANCZOS)
            canvas.paste(image, (x + 9 + (cell_w - 18 - image.width) // 2, y + 29 + (row_h - 67 - image.height) // 2))
            draw.text((x + 8, y + row_h - 29), f"E {values['edge_density_ge_32']:.4f} | H {values['grayscale_entropy_bits']:.4f}", fill="#39434b", font=font(12))
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path, "PNG", compress_level=6, optimize=False)


def sequence_cost(
    route: str,
    start: int,
    end: int,
    semantic_rows: dict[str, list[str]],
    identity_rows: dict[str, list[str]],
    overall_rows: dict[str, list[str]],
    lettering_rows: dict[str, list[str]],
) -> tuple[int, ...]:
    sl = slice(start - 1, end)
    semantic = semantic_rows[route][sl]
    identity = identity_rows[route][sl]
    overall = overall_rows[route][sl]
    lettering = lettering_rows[route][sl]
    return (
        semantic.count("FAIL") + identity.count("FAIL"),
        semantic.count("FAIL"),
        identity.count("FAIL"),
        semantic.count("WARN") + identity.count("WARN"),
        semantic.count("WARN"),
        identity.count("WARN"),
        overall.count("FAIL"),
        lettering.count("FAIL"),
        overall.count("WARN") + lettering.count("WARN"),
        ROUTES.index(route),
    )


def add_cost(left: tuple[int, ...], right: tuple[int, ...], transition: int) -> tuple[int, ...]:
    # Critical semantic/identity failures dominate. Among equally safe paths,
    # adjacent route transitions precede warnings and secondary review burden.
    return (
        left[0] + right[0],
        left[1] + right[1],
        left[2] + right[2],
        left[3] + transition,
        left[4] + right[3],
        left[5] + right[4],
        left[6] + right[5],
        left[7] + right[6],
        left[8] + right[7],
        left[9] + right[8],
        left[10] + right[9],
    )


def choose_cadence(
    sequences: list[dict[str, Any]],
    semantic_rows: dict[str, list[str]],
    identity_rows: dict[str, list[str]],
    overall_rows: dict[str, list[str]],
    lettering_rows: dict[str, list[str]],
) -> tuple[list[str], tuple[int, ...]]:
    # Cost tuple: critical failures, semantic failures, identity failures,
    # transitions, combined critical warnings, semantic warnings, identity
    # warnings, overall failures, lettering failures, secondary warnings,
    # stable route-preference sum.
    states: dict[str, tuple[tuple[int, ...], list[str]]] = {}
    first = sequences[0]
    for route in ROUTES:
        local = sequence_cost(route, first["panel_range"][0], first["panel_range"][1], semantic_rows, identity_rows, overall_rows, lettering_rows)
        states[route] = ((local[0], local[1], local[2], 0, *local[3:]), [route])
    for sequence in sequences[1:]:
        next_states: dict[str, tuple[tuple[int, ...], list[str]]] = {}
        for route in ROUTES:
            local = sequence_cost(route, sequence["panel_range"][0], sequence["panel_range"][1], semantic_rows, identity_rows, overall_rows, lettering_rows)
            options = [
                (add_cost(score, local, int(previous != route)), path + [route])
                for previous, (score, path) in states.items()
            ]
            next_states[route] = min(options, key=lambda item: (item[0], item[1]))
        states = next_states
    score, routes = min(states.values(), key=lambda item: (item[0], item[1]))
    return routes, score


def build_cadence_sheet(entries: dict[str, list[dict[str, Any]]], cadence: list[dict[str, Any]], path: Path) -> None:
    margin, header, row_h, gap, thumb_w = 24, 112, 230, 12, 250
    canvas = Image.new("RGB", (1760, header + len(cadence) * row_h + (len(cadence) - 1) * gap + margin), "#e8e4da")
    draw = ImageDraw.Draw(canvas)
    draw.text((margin, 14), "CH05 MEASURED SEQUENCE-LEVEL CADENCE", fill="#20252a", font=font(30, True))
    draw.text((margin, 52), "One route per narrative block; no within-sequence style cuts; repair only recorded failure panels", fill="#3d464e", font=font(16))
    draw.text((margin, 78), "This minimizes adjacent style transitions relative to the 33-transition review-only panel hybrid", fill="#695848", font=font(14))
    for row_index, sequence in enumerate(cadence):
        y = header + row_index * (row_h + gap)
        route = sequence["selected_route"]
        draw.rectangle((margin, y, canvas.width - margin, y + row_h), fill="#faf8f2", outline="#66727c", width=2)
        draw.text((margin + 10, y + 9), f"{sequence['sequence_id']}  P{sequence['panel_range'][0]:03d}-P{sequence['panel_range'][1]:03d}", fill="#283038", font=font(15, True))
        draw.text((margin + 10, y + 35), ROUTE_LABELS[route], fill="#485965", font=font(13, True))
        semantic = sequence["semantic_counts"]
        identity = sequence["identity_counts"]
        draw.text((margin + 10, y + 59), f"SEM P/W/F {semantic['pass']}/{semantic['warn']}/{semantic['fail']}", fill="#59636b", font=font(12))
        draw.text((margin + 10, y + 78), f"ID P/W/F {identity['pass']}/{identity['warn']}/{identity['fail']}", fill="#59636b", font=font(12))
        overall = sequence["overall_counts"]
        lettering = sequence["lettering_counts"]
        density = sequence["style_density_counts"]
        draw.text((margin + 10, y + 97), f"OVERALL {overall['pass']}/{overall['warn']}/{overall['fail']}", fill="#59636b", font=font(12))
        draw.text((margin + 10, y + 116), f"LETTER {lettering['pass']}/{lettering['warn']}/{lettering['fail']}", fill="#59636b", font=font(12))
        draw.text((margin + 10, y + 135), f"STYLE {density['pass']}/{density['warn']}/{density['fail']} NA {density['not_assessed']}", fill="#59636b", font=font(12))
        for offset, panel_number in enumerate(range(sequence["panel_range"][0], sequence["panel_range"][1] + 1)):
            image = ImageOps.contain(load_panel(entries[route][panel_number - 1]), (thumb_w - 10, 150), Image.Resampling.LANCZOS)
            x = 360 + offset * (thumb_w + 14)
            canvas.paste(image, (x + (thumb_w - image.width) // 2, y + 50 + (150 - image.height) // 2))
            draw.text((x + 6, y + 204), f"P{panel_number:03d}", fill="#39434b", font=font(12, True))
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path, "PNG", compress_level=6, optimize=False)


def main() -> int:
    required = [*ASSEMBLIES.values(), *TRIAGES.values(), *PHONES.values(), REDUCED_PROMPTS, REDUCED_EXECUTIONS, FIVE_ROUTE, HYBRID]
    missing = [path.relative_to(ROOT).as_posix() for path in required if not path.is_file()]
    if missing:
        raise ValueError("required six-route input missing: " + ", ".join(missing))
    assemblies = {route: json.loads(path.read_text(encoding="utf-8")) for route, path in ASSEMBLIES.items()}
    entries = {route: sorted(document["entries"], key=lambda row: row["order"]) for route, document in assemblies.items()}
    canonical_ids = [entry["panel_id"] for entry in entries["r6"]]
    if len(canonical_ids) != 50 or any([entry["panel_id"] for entry in entries[route]] != canonical_ids for route in ROUTES):
        raise ValueError("all six assemblies must share the exact 50 ordered ComicPanelPlan ids")
    triages = {route: json.loads(path.read_text(encoding="utf-8")) for route, path in TRIAGES.items()}
    rows = {route: sorted(document["rows"], key=lambda row: row["display_order"]) for route, document in triages.items()}
    if any([row["panel_id"] for row in rows[route]] != canonical_ids for route in ROUTES):
        raise ValueError("all six triages must cover the exact 50 ordered ComicPanelPlan ids")

    semantic_rows: dict[str, list[str]] = {}
    overall_rows: dict[str, list[str]] = {}
    lettering_rows: dict[str, list[str]] = {}
    density_rows: dict[str, list[str]] = {}
    identity_rows: dict[str, list[str]] = {}
    evaluation_counts: dict[str, Any] = {}
    for route in ROUTES:
        semantic_values = [row.get("semantic_status", row["status"]) for row in rows[route]]
        if route == "r6":
            semantic_values = [R6_SUPPLEMENTAL.get(index + 1, value) for index, value in enumerate(semantic_values)]
        overall_values = [row["status"] for row in rows[route]]
        lettering_values = [row.get("checks", {}).get("lettering_clearance", "NOT_ASSESSED") for row in rows[route]]
        density_values = [normalize_density(row.get("style_density_compliance", row.get("style_status"))) for row in rows[route]]
        identity_values = [row.get("checks", {}).get("hair_and_wardrobe", "NOT_ASSESSED") for row in rows[route]]
        semantic_rows[route], overall_rows[route] = semantic_values, overall_values
        lettering_rows[route], density_rows[route], identity_rows[route] = lettering_values, density_values, identity_values
        evaluation_counts[route] = {
            "semantic": counts(semantic_values),
            "overall": counts(overall_values),
            "lettering": counts(lettering_values, True),
            "style_density": counts(density_values, True),
            "identity_hair_wardrobe": counts(identity_values, True),
        }

    measured: dict[str, list[dict[str, float]]] = {route: [] for route in ROUTES}
    per_panel: list[dict[str, Any]] = []
    for index, panel_id in enumerate(canonical_ids):
        result: dict[str, Any] = {"panel_id": panel_id}
        for route in ROUTES:
            source = ROOT / entries[route][index]["source"]["path"]
            values = metric(load_panel(entries[route][index]), source.stat().st_size)
            measured[route].append(values)
            result[route] = {
                **values,
                "semantic_status": semantic_rows[route][index],
                "overall_status": overall_rows[route][index],
                "lettering_status": lettering_rows[route][index],
                "style_density_status": density_rows[route][index],
                "identity_status": identity_rows[route][index],
            }
        per_panel.append(result)
    aggregate = {
        route: {key: round(sum(row[key] for row in measured[route]) / 50, 6) for key in measured[route][0]}
        for route in ROUTES
    }

    prompt_document = json.loads(REDUCED_PROMPTS.read_text(encoding="utf-8"))
    execution_document = json.loads(REDUCED_EXECUTIONS.read_text(encoding="utf-8"))
    sequences = prompt_document["sequences"]
    prompt_reference_bindings = sum(len(row.get("input_references", [])) for row in sequences)
    execution_reference_bindings = sum(len(row.get("input_references", [])) for row in execution_document["records"])
    execution_summary = execution_document["summary"]
    if prompt_reference_bindings or execution_reference_bindings or execution_summary["authorized_reference_uses"] or execution_summary["reference_uploads"]:
        raise ValueError("reduced-palette route is not a zero-upload text-only control")

    selected_routes, cadence_score = choose_cadence(sequences, semantic_rows, identity_rows, overall_rows, lettering_rows)
    cadence: list[dict[str, Any]] = []
    selected_panel_routes: list[str] = []
    targeted_repairs: list[dict[str, Any]] = []
    for sequence, route in zip(sequences, selected_routes, strict=True):
        start, end = sequence["panel_range"]
        semantic_values = semantic_rows[route][start - 1:end]
        identity_values = identity_rows[route][start - 1:end]
        overall_values = overall_rows[route][start - 1:end]
        lettering_values = lettering_rows[route][start - 1:end]
        density_values = density_rows[route][start - 1:end]
        failures = [canonical_ids[index] for index in range(start - 1, end) if semantic_rows[route][index] == "FAIL"]
        for panel_id in failures:
            targeted_repairs.append({"panel_id": panel_id, "sequence_id": sequence["source_sequence_id"], "style_to_preserve": route, "reason": "explicit semantic FAIL in selected sequence route", "action": "smallest targeted same-style repair; do not substitute a differently styled panel"})
        selected_panel_routes.extend([route] * (end - start + 1))
        cadence.append({
            "sequence_id": sequence["source_sequence_id"],
            "panel_range": [start, end],
            "panel_count": end - start + 1,
            "selected_route": route,
            "semantic_counts": counts(semantic_values),
            "identity_counts": counts(identity_values, True),
            "overall_counts": counts(overall_values),
            "lettering_counts": counts(lettering_values, True),
            "style_density_counts": counts(density_values, True),
            "explicit_semantic_failure_panel_ids": failures,
            "within_sequence_style_transitions": 0,
        })
    transitions = sum(left != right for left, right in pairwise(selected_panel_routes))
    sequence_transitions = sum(left != right for left, right in pairwise(selected_routes))
    if transitions != sequence_transitions or transitions > 10:
        raise ValueError("sequence cadence transition invariant failed")

    all_50 = OUT / "ch05-six-route-all-50-contact-sheet.png"
    anchors = OUT / "ch05-six-route-semantic-anchors.png"
    phone = OUT / "ch05-six-route-lettered-phone-comparison.png"
    density = OUT / "ch05-six-route-style-density-comparison.png"
    cadence_sheet = OUT / "ch05-six-route-sequence-cadence.png"
    semantic_maps = {route: dict(zip(canonical_ids, semantic_rows[route], strict=True)) for route in ROUTES}
    density_maps = {route: dict(zip(canonical_ids, density_rows[route], strict=True)) for route in ROUTES}
    build_all_50(entries, semantic_maps, all_50)
    build_anchors(entries, semantic_maps, anchors)
    build_phone(phone)
    build_density(entries, density_maps, measured, density)
    build_cadence_sheet(entries, cadence, cadence_sheet)

    reduced_summary = triages["reduced_palette_text_control"]["summary"]
    document = {
        "record_type": "CH05CompleteChapterSixRouteComparison",
        "schema_version": "1.0",
        "record_id": "ng-ch05-six-route-comparison-r1",
        "state": "ENGINEERING_COMPARISON_AND_SEQUENCE_CADENCE_PENDING_OWNER_REVIEW",
        "medium": "comic",
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "inputs": [{"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path)} for path in required],
        "coverage": {"routes": 6, "comic_panel_plans_per_route": 50, "paired_panel_ids": 50, "total_panel_candidates_compared": 300},
        "semantic_anchor_panel_ids": [f"ng-ch05-sc01-p{number:03d}" for number in ANCHORS],
        "evaluation_counts": evaluation_counts,
        "reduced_palette_text_control": {
            "summary_as_recorded": reduced_summary,
            "zero_upload_result": {
                "result": "PASS_ZERO_UPLOAD_TEXT_ONLY_CONTROL",
                "prompt_sequences": len(sequences),
                "prompt_input_reference_bindings": prompt_reference_bindings,
                "execution_records": len(execution_document["records"]),
                "execution_input_reference_bindings": execution_reference_bindings,
                "authorized_reference_uses": execution_summary["authorized_reference_uses"],
                "reference_uploads": execution_summary["reference_uploads"],
                "direct_paid_provider_api_calls": execution_summary["direct_paid_provider_api_calls"],
            },
            "identity_drift": {
                "result": "NO_OBSERVED_ROLE_HAIR_WARDROBE_DRIFT_IN_VISIBLE_CAST_PANELS",
                "visible_adult_cast_panels": reduced_summary.get("visible_adult_cast_panels"),
                "visible_cast_identity_pass": reduced_summary.get("mature_identity_hair_wardrobe_pass"),
                "planned_zero_cast_panels": reduced_summary.get("zero_cast_panels_without_people"),
                "counts": evaluation_counts["reduced_palette_text_control"]["identity_hair_wardrobe"],
                "continuity_result": triages["reduced_palette_text_control"].get("continuity_result"),
                "basis": "Manual fictional-character hair/wardrobe continuity observations only; not biometric identification.",
                "scope_limitation": "The pass covers mature role binding, approved hair-color family, and wardrobe. It does not establish exact facial identity, hair shape, or panel-to-panel micro-continuity.",
            },
        },
        "visual_complexity": {
            "method": "Equal-panel grayscale entropy, FIND_EDGES>=32 density, and native PNG bytes/pixel; proxies compare density only and do not score quality.",
            "aggregate_equal_panel_weight": aggregate,
            "per_panel": per_panel,
        },
        "sequence_cadence_recommendation": {
            "method": "Dynamic programming over the 11 canonical generation sequences. Lexicographic objective minimizes combined semantic/identity failures, semantic failures, identity failures, adjacent sequence-route transitions, critical warnings, then overall/lettering burden and a stable route-order tie-break. Each sequence uses exactly one route.",
            "objective_score_fields": ["combined_semantic_identity_failures", "semantic_failures", "identity_failures", "adjacent_route_transitions", "combined_semantic_identity_warnings", "semantic_warnings", "identity_warnings", "overall_failures", "lettering_failures", "combined_overall_lettering_warnings", "stable_route_preference_sum"],
            "objective_score": list(cadence_score),
            "sequences": cadence,
            "sequence_route_transitions": sequence_transitions,
            "adjacent_panel_route_transitions": transitions,
            "review_only_panel_hybrid_transitions": 33,
            "transition_reduction_from_hybrid": 33 - transitions,
            "targeted_same_style_repairs": targeted_repairs,
            "policy": "Preserve one style per narrative sequence. Do not cherry-pick a different route inside a sequence; repair only an explicit semantic failure with the smallest same-style correction.",
            "production_manifest_created": False,
        },
        "recommendation": {
            "production_mechanism": "sequence-strip generation, deterministic crop extraction, one selected style per narrative block, variable panel-size cadence, phone/lettering review, and same-style targeted semantic repair",
            "wholesale_route_selection": None,
            "appearance_only_selection": False,
            "next_high_information_step": "Owner reviews the six-route anchors, lettered phone columns, density comparison, and sequence-cadence sheet; then explicitly approves or revises sequence assignments before any production manifest is created.",
        },
        "owner_disposition": {"accepted_route": None, "accepted_sequence_assignments": None, "accepted_panel_ids": None, "commercial_rights_clearance": None, "exact_production_base": None},
        "artifacts": {
            "all_50_six_columns": artifact(all_50),
            "semantic_anchors": artifact(anchors),
            "lettered_phone_comparison": artifact(phone),
            "style_density_comparison": artifact(density),
            "sequence_cadence": artifact(cadence_sheet),
        },
        "spend": {"direct_paid_api_cloud_usd": 0.0, "built_in_product_monetary_cost_usd": None},
        "limitations": [
            "Agent triage and the derived cadence are non-gating recommendations.",
            "R6 uses the preserved 47/1/2 supplemental semantic audit without rewriting frozen evidence.",
            "Style-density status is explicitly NOT_ASSESSED where a triage did not perform that strict manual test.",
            "Complexity proxies do not measure artistic quality, identity, narrative value, commercial suitability, or acceptance.",
            "Identity drift findings are manual fictional-character observations, not biometric recognition.",
            "The cadence optimizer does not prove cross-sequence palette, lighting, line-weight, or environment continuity.",
            "Built-in product model, endpoint, request ID, seed, usage, and monetary cost remain unavailable where source records say so.",
            "No route, sequence assignment, panel, or generated pixel is accepted, commercially cleared, or selected as an exact production base.",
        ],
        "boundary": "Measured comparison and provisional engineering recommendation only; owner acceptance, production-manifest creation, commercial clearance, and exact production-base selection remain null.",
    }
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"artifacts": document["artifacts"], "cadence": document["sequence_cadence_recommendation"], "evaluation_counts": evaluation_counts, "metrics": aggregate, "output": EVIDENCE.relative_to(ROOT).as_posix(), "sha256": sha256(EVIDENCE)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
