"""Compile deterministic non-gating triage for the full CH05 premium-cel arm."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[2]
PLAN = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"
ASSEMBLY = ROOT / "production/comic/run-manifests/ch05-complete-chapter-premium-cel-assembly-r1.json"
OUTPUT = ROOT / "docs/research/evidence/ch05-complete-chapter-premium-cel-agent-triage-r1.json"
MARKDOWN = ROOT / "docs/research/ch05-complete-chapter-premium-cel-agent-triage-r1.md"
SHEET = ROOT / "experiments/review-packets/ch05-complete-chapter-premium-cel-r1/review/ch05-complete-chapter-premium-cel-triage-sheet-r1.png"

ISSUES: dict[int, tuple[str, str, str]] = {
    1: ("FAIL", "departure_vector", "The farmhouse is cold and dark, but both adults travel uphill toward it rather than unmistakably downhill away with it physically behind them."),
    3: ("WARN", "track_overlap", "The boot and fresh prints read, but overlap with older trail traffic remains subtle at phone width."),
    8: ("WARN", "map_fold_state", "The folded-map action reads, but one frame does not prove that the fold hides the farmhouse section while exposing the creek line."),
    12: ("WARN", "twine_direction", "The taut diagonal twine reads, but downhill direction lacks enough terrain context for phone-width certainty."),
    13: ("FAIL", "role_order", "Soren leads while Sigrid follows; the ComicPanelPlan requires Sigrid to lead downhill and Soren to follow."),
    29: ("FAIL", "independent_exterior_watch", "Sigrid enters correctly, but Soren looks toward her rather than independently watching the exterior in a different gaze direction."),
    32: ("WARN", "far_bank_footprint_orientation", "Prints begin on far dry ground, but oversized asymmetric heel/toe shapes pointing back toward Soren remain ambiguous."),
    36: ("FAIL", "continuous_leverage_force_path", "Both adults and one plank are visible, but the high tin/contact endpoint is outside the panel, so the single-panel force path is incomplete."),
    39: ("FAIL", "simultaneous_three_mark_count", "A torn-edge X fragment is visible, but one uninterrupted map view does not simultaneously expose the square, circle, and distinct third upstream mark."),
    45: ("WARN", "farmhouse_geography", "An extra uphill building near the mill can be mistaken for the farmhouse and weakens return geography."),
}
STRONGEST_ORDERS = [4, 6, 17, 19, 20, 22, 26, 30, 33, 41, 43, 44, 46, 48, 49, 50]
CHECK_KEYS = (
    "role_binding",
    "role_order",
    "visible_adult_count",
    "shared_set_and_blocking",
    "target_change_behavior",
    "causal_action_or_clue",
    "hair_and_wardrobe",
    "lettering_clearance",
    "phone_readability",
    "cross_panel_canon",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = ["DejaVuSans-Bold.ttf", "Arial Bold.ttf"] if bold else ["DejaVuSans.ttf", "Arial.ttf"]
    for name in candidates:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default(size=size)


def wrap(draw: ImageDraw.ImageDraw, text: str, selected: ImageFont.ImageFont, width: int, max_lines: int = 2) -> list[str]:
    lines: list[str] = []
    current = ""
    for word in text.split():
        candidate = word if not current else f"{current} {word}"
        if draw.textbbox((0, 0), candidate, font=selected)[2] <= width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
            if len(lines) == max_lines:
                break
    if current and len(lines) < max_lines:
        lines.append(current)
    return lines


def build_sheet(entries: list[dict[str, Any]], rows: list[dict[str, Any]], summary: dict[str, Any]) -> dict[str, Any]:
    status = {row["panel_id"]: row for row in rows}
    columns = 5
    grid_rows = math.ceil(len(entries) / columns)
    tile_w, tile_h, gap, margin, header = 300, 254, 14, 24, 112
    canvas = Image.new(
        "RGB",
        (margin * 2 + columns * tile_w + 4 * gap, header + margin + grid_rows * tile_h + (grid_rows - 1) * gap),
        "#e7e3da",
    )
    draw = ImageDraw.Draw(canvas)
    draw.text((margin, 16), "CH05 PREMIUM-CEL R1 - AGENT TRIAGE", fill="#20252a", font=font(28, True))
    draw.text(
        (margin, 54),
        f"{summary['pass']} PASS | {summary['warn']} WARN | {summary['fail']} FAIL | hair/wardrobe 50/50 | owner review pending",
        fill="#3b454d",
        font=font(18),
    )
    draw.text(
        (margin, 80),
        "Non-gating visual evidence: green is not acceptance or commercial clearance.",
        fill="#695848",
        font=font(14),
    )
    for index, entry in enumerate(entries):
        row = status[entry["panel_id"]]
        source = ROOT / entry["source"]["path"]
        if not source.is_file() or sha256(source) != entry["source"]["sha256"]:
            raise ValueError(f"source mismatch: {entry['panel_id']}")
        with Image.open(source) as opened:
            image = opened.convert("RGB")
        col, grid_row = index % columns, index // columns
        x = margin + col * (tile_w + gap)
        y = header + grid_row * (tile_h + gap)
        color = "#2d8a57" if row["status"] == "PASS" else "#c47a16" if row["status"] == "WARN" else "#b83b3b"
        draw.rectangle((x, y, x + tile_w, y + tile_h), fill="#faf8f2", outline=color, width=4)
        draw.text(
            (x + 10, y + 8),
            f"{entry['order']:02d}  {entry['panel_id'].split('-')[-1].upper()}  {row['status']}",
            fill=color,
            font=font(16, True),
        )
        framed = ImageOps.contain(image, (tile_w - 18, 165), Image.Resampling.LANCZOS)
        canvas.paste(framed, (x + (tile_w - framed.width) // 2, y + 38 + (165 - framed.height) // 2))
        label = (row["primary_issue_class"] or "no blocking issue").replace("_", " ")
        for line_no, line in enumerate(wrap(draw, label, font(13), tile_w - 20)):
            draw.text((x + 10, y + 212 + line_no * 16), line, fill="#343b41", font=font(13))
    SHEET.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(SHEET, format="PNG", compress_level=6, optimize=False)
    return {
        "path": SHEET.relative_to(ROOT).as_posix(),
        "sha256": sha256(SHEET),
        "width": canvas.width,
        "height": canvas.height,
        "bytes": SHEET.stat().st_size,
        "tracked": False,
    }


def main() -> int:
    plans = sorted(json.loads(PLAN.read_text(encoding="utf-8"))["plans"], key=lambda row: row["display_order"])
    assembly = json.loads(ASSEMBLY.read_text(encoding="utf-8"))
    entries = sorted(assembly["entries"], key=lambda row: row["order"])
    if len(entries) != 50 or [row["panel_id"] for row in plans] != [row["panel_id"] for row in entries]:
        raise ValueError("assembly differs from canonical 50-panel ComicPanelPlan order")

    rows: list[dict[str, Any]] = []
    for plan, entry in zip(plans, entries, strict=True):
        order = plan["display_order"]
        status, issue, note = ISSUES.get(
            order,
            ("PASS", None, "No blocking panel-local or cross-panel issue found in non-gating agent triage."),
        )
        checks = {key: "PASS" for key in CHECK_KEYS}
        if status != "PASS":
            target_key = {
                "role_order": "role_order",
                "independent_exterior_watch": "role_binding",
                "map_fold_state": "target_change_behavior",
                "farmhouse_geography": "shared_set_and_blocking",
                "departure_vector": "cross_panel_canon",
                "far_bank_footprint_orientation": "cross_panel_canon",
                "simultaneous_three_mark_count": "cross_panel_canon",
            }.get(issue, "causal_action_or_clue")
            checks[target_key] = status
            if status == "WARN" or issue in {
                "continuous_leverage_force_path",
                "simultaneous_three_mark_count",
            }:
                checks["phone_readability"] = status
        rows.append(
            {
                "display_order": order,
                "panel_id": plan["panel_id"],
                "plan_revision_id": plan["plan_revision_id"],
                "candidate_id": entry["candidate_id"],
                "candidate_sha256": entry["source"]["sha256"],
                "status": status,
                "primary_issue_class": issue,
                "note": note,
                "checks": checks,
                "human_review_state": "PENDING",
                "human_review_minutes": None,
                "accepted": False,
                "commercially_cleared": False,
                "exact_production_base": False,
            }
        )

    counts = {status: sum(row["status"] == status for row in rows) for status in ("PASS", "WARN", "FAIL")}
    summary = {
        "chapter_panels": 50,
        "pass": counts["PASS"],
        "warn": counts["WARN"],
        "fail": counts["FAIL"],
        "hair_and_wardrobe_pass": 50,
        "role_correct_hair_and_wardrobe_pass": 50,
        "cross_panel_gates_pass": 3,
        "cross_panel_gates_warn": 1,
        "cross_panel_gates_fail": 4,
        "strongest_shortlist": len(STRONGEST_ORDERS),
        "human_reviewed": 0,
        "accepted": 0,
    }
    sheet = build_sheet(entries, rows, summary)
    strongest = [
        {
            "display_order": order,
            "panel_id": rows[order - 1]["panel_id"],
            "candidate_id": rows[order - 1]["candidate_id"],
            "candidate_sha256": rows[order - 1]["candidate_sha256"],
            "status": "PASS",
        }
        for order in STRONGEST_ORDERS
    ]
    document = {
        "record_type": "CH05CompleteChapterAgentTriage",
        "schema_version": "1.0",
        "record_id": "ng-ch05-complete-chapter-premium-cel-agent-triage-r1",
        "display_title": "CH05 PREMIUM-CEL R1 - AGENT TRIAGE",
        "state": "NON_GATING_AGENT_TRIAGE_PENDING_OWNER_REVIEW",
        "medium": "comic",
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "inputs": [
            {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path)} for path in (PLAN, ASSEMBLY)
        ],
        "summary": summary,
        "role_continuity": {
            "result": "PASS_50_OF_50",
            "SOREN": "light-brown/dark-blond hair and pale oatmeal work coat",
            "SIGRID": "dark-brown/near-black tied hair and dark blue-brown plaid wrap",
            "note": "No obvious role-color swap or wardrobe loss was observed; this remains manual visual triage, not biometric recognition.",
        },
        "gate_transfer": {
            "cold_farmhouse_until_reversal": "PASS",
            "departure_vector": "FAIL",
            "independent_entry_roles": "FAIL",
            "impossible_far_bank_prints": "WARN",
            "continuous_leverage_force_path": "FAIL",
            "third_upstream_mark": "FAIL_STRICT_SIMULTANEOUS_COUNT",
            "drum_fully_out": "PASS",
            "map_possession": "PASS",
        },
        "style_hypothesis_result": {
            "result": "WEAKLY_SEPARATING",
            "note": "Cel-shaped character modeling is present, but high terrain, cloth, and material texture keeps the route close to the painterly clear-line arms rather than establishing a clean premium-cel separation.",
            "largest_discontinuity": "Sequence s08 / P035-P039 shifts to bright sunlight, green foliage, and a high-key cinematic finish against the preceding cold, wet, dim mill continuity.",
        },
        "strongest_shortlist": strongest,
        "rows": rows,
        "triage_sheet": sheet,
        "recommendation": (
            "Do not promote the premium-cel arm wholesale. Preserve P041, P043, the P048-P050 climax, and the other shortlisted passes "
            "for hybrid owner comparison; retain stronger existing repaired P029/P036 evidence and limit any next correction to exact "
            "P001/P013/P032/P039 semantics."
        ),
        "limitations": [
            "Agent triage is non-gating and owner review remains pending.",
            "Hair, wardrobe, role, action, style, and canon judgments are manual visual observations.",
            "Prompt compliance and a PASS label do not establish acceptance, rights, or exact production-base status.",
            "Built-in product model, endpoint, request ID, seed, usage, and monetary cost are unavailable.",
            "No identical request was repeated; stochastic reproducibility remains unmeasured.",
        ],
        "boundary": "Review evidence only; no acceptance, commercial clearance, canon replacement, or exact production-base decision.",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")

    issue_rows = "\n".join(
        f"| {row['display_order']:03d} | `{row['panel_id']}` | {row['status']} | `{row['primary_issue_class']}` | {row['note']} |"
        for row in rows
        if row["status"] != "PASS"
    )
    strongest_text = ", ".join(f"P{order:03d}" for order in STRONGEST_ORDERS)
    MARKDOWN.write_text(
        "# CH05 premium-cel r1 agent triage\n\n"
        f"The complete 50-panel arm measures **{counts['PASS']} PASS / {counts['WARN']} WARN / {counts['FAIL']} FAIL** in non-gating agent triage. Owner review is pending.\n\n"
        "Hair and wardrobe hold in their correct roles across 50/50 panels: Soren retains light-brown/dark-blond hair and the pale oatmeal coat; Sigrid retains dark-brown/near-black tied hair and the plaid wrap. This is manual continuity review, not biometric recognition.\n\n"
        "## Non-pass panels\n\n"
        "| Order | Panel | Status | Issue | Evidence |\n|---:|---|---|---|---|\n"
        + issue_rows
        + "\n\n## Cross-panel gates\n\n"
        "Cold-house reversal, fully extinguished drum, and map possession pass. Far-bank footprint orientation remains a warning. Departure vector, independent entry roles, visible leverage endpoint, and simultaneous three-mark count fail.\n\n"
        "## Style and continuity\n\n"
        "Style separation is weak: cel-shaped character modeling is visible, but terrain, cloth, and material microtexture remain high. Sequence s08 (P035-P039) is the largest discontinuity, shifting to bright sunlight, green foliage, and a high-key cinematic finish against the cold, wet, dim mill.\n\n"
        f"Strongest shortlist: **{strongest_text}**. P041 fully extinguishes the drum; P043 preserves the map while leaving the open tin; P048-P050 provide the strongest urgent climax.\n\n"
        "Do not promote this arm wholesale. Preserve its strongest panels for hybrid owner comparison and apply only exact semantic repairs. No panel is accepted, commercially cleared, or declared an exact production base.\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                **summary,
                "output": OUTPUT.relative_to(ROOT).as_posix(),
                "sha256": sha256(OUTPUT),
                "markdown": MARKDOWN.relative_to(ROOT).as_posix(),
                "sheet": sheet,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
