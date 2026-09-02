"""Partition all 50 CH05 ComicPanelPlans into coherent 3-5 panel production batches."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
READINESS = ROOT / "production/comic/run-manifests/ch05-chapter-production-readiness-matrix-r1.json"
REFERENCE = ROOT / "production/comic/continuity/ch05-reference-use-and-continuity-risk-plan-r1.json"
ROUTE = ROOT / "production/comic/recommendations/ch05-pipeline-route-recommendation-r1.json"
OUTPUT = ROOT / "production/comic/run-manifests/ch05-chapter-sequence-production-batches-r1.json"
EVIDENCE = ROOT / "docs/research/evidence/ch05-chapter-sequence-production-batches-r1.json"
CHART = ROOT / "experiments/review-packets/ch05-chapter-sequence-production-batches-r1/ch05-sequence-batch-map-r1.png"

SPECS = [
    ("seq01", "Departure and changed trail", 1, 4, 4),
    ("seq02", "Runnel, marker, and narrowing path", 5, 9, 4),
    ("seq03", "Water, soot twine, and creek redirection", 10, 13, 1),
    ("seq04", "Lost smoke and first mill reveal", 14, 18, 2),
    ("seq05", "Bridge warning and covert approach", 19, 23, 2),
    ("seq06", "Hidden drum and wall-line clue", 24, 27, 3),
    ("seq07", "Bell trap and alternate entry", 28, 31, 3),
    ("seq08", "False tracks, bell, tin, and plank", 32, 36, 3),
    ("seq09", "Tin map deduction and signal conclusion", 37, 40, 3),
    ("seq10", "Signal collapse, retreat, and twine cut", 41, 44, 3),
    ("seq11", "Silence after cut and uphill return", 45, 47, 4),
    ("seq12", "Farmhouse smoke and urgent final run", 48, 50, 4),
]


def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()
def binding(path: Path) -> dict: return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path)}


def cadence_class(scale_role: str) -> str:
    if scale_role.startswith("WIDE") or scale_role == "TALL_OR_WIDE_DUAL_CAUSAL": return "ANCHOR_OR_ACTION"
    if scale_role.startswith("SMALL"): return "INSERT_OR_PAUSE"
    return "CHARACTER_OR_REACTION"


def build_chart(sequences: list[dict]) -> None:
    CHART.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", (1800, 1220), "#10151c"); draw = ImageDraw.Draw(image); font = ImageFont.load_default()
    draw.text((38, 24), "CH05 · 12 coherent production batches / 50 ComicPanelPlans", fill="#eef3f8", font=font)
    draw.text((38, 45), "Narrative order is fixed; production wave is evidence readiness, not story order", fill="#ffcf88", font=font)
    colors = {"ANCHOR_OR_ACTION": "#477ca2", "CHARACTER_OR_REACTION": "#4b805e", "INSERT_OR_PAUSE": "#6d647d"}
    x = 38
    for label, color in colors.items():
        draw.rectangle((x, 70, x + 18, 88), fill=color); draw.text((x + 24, 72), label.replace("_", " "), fill="#dce4ec", font=font); x += 245
    row_h = 88
    for index, sequence in enumerate(sequences):
        top = 110 + index * row_h
        draw.text((38, top + 6), f"{sequence['sequence_id']} · wave {sequence['production_wave']} · {sequence['title']}", fill="#eef3f8", font=font)
        draw.text((38, top + 28), f"{sequence['panel_count']} panels · readiness S/D/A/B {sequence['readiness_counts']['selected']}/{sequence['readiness_counts']['dry_run']}/{sequence['readiness_counts']['tier_a']}/{sequence['readiness_counts']['backlog']} · prompts 0", fill="#aeb9c5", font=font)
        left = 720
        for panel in sequence["panels"]:
            color = colors[panel["cadence_class"]]
            draw.rounded_rectangle((left, top, left + 190, top + 66), radius=7, fill=color, outline="#9eabb8")
            draw.text((left + 8, top + 7), panel["panel_id"].split("-")[-1].upper(), fill="white", font=font)
            draw.text((left + 8, top + 27), panel["scale_role"].replace("_", " ")[:25], fill="#e8edf2", font=font)
            draw.text((left + 8, top + 47), f"{panel['width_range_px'][0]}–{panel['width_range_px'][1]} px", fill="#e8edf2", font=font)
            left += 202
    image.save(CHART, optimize=False)


def main() -> int:
    readiness = json.loads(READINESS.read_text(encoding="utf-8")); refs = {row["panel_id"]: row for row in json.loads(REFERENCE.read_text(encoding="utf-8"))["rows"]}; by_order = {row["display_order"]: row for row in readiness["rows"]}
    sequences = []
    for sequence_id, title, start, end, wave in SPECS:
        source_rows = [by_order[index] for index in range(start, end + 1)]
        panels = []
        for row in source_rows:
            panels.append({"display_order": row["display_order"], "panel_id": row["panel_id"], "plan_revision_id": row["plan_revision_id"], "narrative_beat": row["narrative_beat"], "narrative_function": row["narrative_function"], "visible_adult_cast": row["visible_adult_cast"], "scale_role": row["scale_role"], "width_range_px": row["width_range_px"], "cadence_class": cadence_class(row["scale_role"]), "recommended_mechanisms": row["recommended_mechanisms"], "readiness_class": row["readiness_class"], "continuity_risk": refs[row["panel_id"]]["continuity_risk"], "reference_hypotheses": refs[row["panel_id"]]["reference_hypotheses"], "prompt": None, "output": None, "owner_accepted": False, "execution_ready": False})
        readiness_counts = {"selected": sum(row["readiness_class"] == "EVIDENCE_SELECTED_OWNER_PENDING" for row in source_rows), "dry_run": sum(row["readiness_class"] == "DRY_RUN_OWNER_GATES_PENDING" for row in source_rows), "tier_a": sum(row["readiness_class"] == "PRIORITIZED_NO_DRY_RUN" for row in source_rows), "backlog": sum(row["readiness_class"] == "BACKLOG_PLAN_ONLY" for row in source_rows)}
        cadence_counts = {key: sum(panel["cadence_class"] == key for panel in panels) for key in ("ANCHOR_OR_ACTION", "CHARACTER_OR_REACTION", "INSERT_OR_PAUSE")}
        sequences.append({"sequence_id": sequence_id, "narrative_order": len(sequences) + 1, "production_wave": wave, "title": title, "panel_range": [start, end], "panel_count": len(panels), "narrative_functions": list(dict.fromkeys(panel["narrative_function"] for panel in panels)), "readiness_counts": readiness_counts, "cadence_counts": cadence_counts, "panels": panels, "planned_review_artifacts": [f"{sequence_id}-contact-sheet.png", f"{sequence_id}-phone-390px.png", f"{sequence_id}-continuity-strip.png", f"{sequence_id}-lettering-safe-zone-strip.png"], "prompt_count": 0, "rendered_candidates": 0, "accepted_candidates": 0, "execution_ready": False})
    build_chart(sequences)
    wave_counts = {str(wave): sum(sequence["production_wave"] == wave for sequence in sequences) for wave in (1,2,3,4)}
    record = {"record_type": "ComicChapterSequenceProductionBatches", "schema_version": "1.0", "record_id": "ng-ch05-chapter-sequence-production-batches-r1", "state": "TWELVE_COHERENT_BATCHES_ZERO_PROMPT_OWNER_PENDING", "medium": "comic", "inputs": [binding(path) for path in (READINESS, REFERENCE, ROUTE)], "summary": {"plan_count": 50, "sequence_count": 12, "minimum_panels_per_sequence": min(sequence["panel_count"] for sequence in sequences), "maximum_panels_per_sequence": max(sequence["panel_count"] for sequence in sequences), "wave_1_sequences": wave_counts["1"], "wave_2_sequences": wave_counts["2"], "wave_3_sequences": wave_counts["3"], "wave_4_sequences": wave_counts["4"], "planned_review_artifacts": sum(len(sequence["planned_review_artifacts"]) for sequence in sequences), "prompt_count": 0, "rendered_candidates": 0, "accepted_candidates": 0, "execution_ready_sequences": 0, "provider_calls": 0, "uploads": 0, "cost_usd": 0, "human_review_minutes": None}, "production_wave_rationale": {"1": "P010–P013 is the only four-row dry-run contract and highest-information continuity pilot.", "2": "P014–P023 concentrates eight Tier A rows around bridge warning, reveal, and covert approach.", "3": "P024–P044 extends mill approach/interior/deduction/retreat mechanics after pilot evidence.", "4": "Departure context and final-return batches retain selected anchors but wait for chapter-wide route/copy decisions."}, "sequences": sequences, "chart": {"path": CHART.relative_to(ROOT).as_posix(), "sha256": sha(CHART), "dimensions": [1800, 1220]}, "comic_panel_plan_revision_created": False, "animation_shot_plan": None, "e_conte": None, "boundary": "ComicPanelPlan-only sequence partition. No prompt, output, upload, review, acceptance, execution, or plan revision."}
    OUTPUT.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8", newline="\n")
    evidence = {"record_type": "ComicChapterSequenceProductionBatchesEvidence", "schema_version": "1.0", "record_id": "ng-ch05-chapter-sequence-production-batches-evidence-r1", "state": "PASS_ZERO_PROMPT", "manifest": binding(OUTPUT), "inputs": record["inputs"], "summary": record["summary"], "chart": record["chart"], "animation_shot_plan": None, "e_conte": None}
    EVIDENCE.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"CH05 sequence batches: 50 plans / 12 sequences / sizes {record['summary']['minimum_panels_per_sequence']}–{record['summary']['maximum_panels_per_sequence']} / waves {wave_counts}")
    print("prompts/renders/accepted/executable/calls/uploads/cost 0/0/0/0/0/0/$0")
    return 0


if __name__ == "__main__": raise SystemExit(main())
