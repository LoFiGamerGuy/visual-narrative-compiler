"""Validate 12 coherent CH05 sequence production batches."""
from __future__ import annotations

import copy, hashlib, json, subprocess
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "docs/research/evidence/ch05-chapter-sequence-production-batches-r1.json"


def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()


def errors(record: dict) -> list[str]:
    summary = record.get("summary", {}); failures = []
    actual = tuple(summary.get(key) for key in ("plan_count", "sequence_count", "minimum_panels_per_sequence", "maximum_panels_per_sequence", "wave_1_sequences", "wave_2_sequences", "wave_3_sequences", "wave_4_sequences", "planned_review_artifacts"))
    if actual != (50, 12, 3, 5, 1, 2, 5, 4, 48) or record.get("state") != "PASS_ZERO_PROMPT": failures.append("sequence denominator/state invalid")
    if any(summary.get(key) != 0 for key in ("prompt_count", "rendered_candidates", "accepted_candidates", "execution_ready_sequences", "provider_calls", "uploads", "cost_usd")) or summary.get("human_review_minutes") is not None: failures.append("activity/promotion fabricated")
    if record.get("animation_shot_plan") is not None or record.get("e_conte") is not None: failures.append("planning boundary invalid")
    return failures


def main() -> int:
    record = json.loads(EVIDENCE.read_text(encoding="utf-8")); failures = errors(record)
    manifest_path = ROOT / record["manifest"]["path"]
    if not manifest_path.is_file() or sha(manifest_path) != record["manifest"]["sha256"]: failures.append("manifest binding invalid"); manifest = {}
    else: manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for item in record["inputs"]:
        path = ROOT / item["path"]
        if not path.is_file() or sha(path) != item["sha256"]: failures.append(f"input binding invalid: {item['path']}")
    chart = ROOT / record["chart"]["path"]
    if not chart.is_file() or sha(chart) != record["chart"]["sha256"] or subprocess.run(["git", "check-ignore", "-q", str(chart)], cwd=ROOT, check=False).returncode: failures.append("chart binding/ignore invalid")
    else:
        with Image.open(chart) as image:
            if list(image.size) != record["chart"]["dimensions"]: failures.append("chart dimensions invalid")
    sequences = manifest.get("sequences", []); panels = [panel for sequence in sequences for panel in sequence.get("panels", [])]
    if len(sequences) != 12 or len(panels) != 50 or [panel.get("display_order") for panel in panels] != list(range(1,51)) or len({panel.get("panel_id") for panel in panels}) != 50: failures.append("sequence/panel partition invalid")
    if any(not 3 <= sequence.get("panel_count", 0) <= 5 or sequence.get("prompt_count") != 0 or sequence.get("rendered_candidates") != 0 or sequence.get("accepted_candidates") != 0 or sequence.get("execution_ready") is not False or len(sequence.get("planned_review_artifacts", [])) != 4 for sequence in sequences): failures.append("sequence fail-closed/artifact state invalid")
    if any(panel.get("prompt") is not None or panel.get("output") is not None or panel.get("owner_accepted") is not False or panel.get("execution_ready") is not False for panel in panels): failures.append("panel fail-closed state invalid")
    mutations = [lambda x:x.update(state="FAIL"),lambda x:x["summary"].update(plan_count=49),lambda x:x["summary"].update(sequence_count=11),lambda x:x["summary"].update(minimum_panels_per_sequence=2),lambda x:x["summary"].update(maximum_panels_per_sequence=6),lambda x:x["summary"].update(wave_1_sequences=0),lambda x:x["summary"].update(wave_2_sequences=1),lambda x:x["summary"].update(wave_3_sequences=4),lambda x:x["summary"].update(wave_4_sequences=3),lambda x:x["summary"].update(planned_review_artifacts=47),lambda x:x["summary"].update(prompt_count=1),lambda x:x["summary"].update(rendered_candidates=1),lambda x:x["summary"].update(accepted_candidates=1),lambda x:x["summary"].update(execution_ready_sequences=1),lambda x:x["summary"].update(provider_calls=1),lambda x:x["summary"].update(uploads=1),lambda x:x["summary"].update(cost_usd=1),lambda x:x["summary"].update(human_review_minutes=1),lambda x:x.update(animation_shot_plan={})]
    rejected=0
    for mutation in mutations: candidate=copy.deepcopy(record);mutation(candidate);rejected+=bool(errors(candidate))
    if rejected!=len(mutations): failures.append(f"only {rejected}/{len(mutations)} mutations rejected")
    print(f"CH05 sequence batches: {len(failures)} failures; 50 plans/12 sequences/3–5 panels/48 planned artifacts; {rejected}/{len(mutations)} mutations rejected")
    print("prompts/renders/accepted/executable/calls/uploads/cost 0/0/0/0/0/0/$0")
    for failure in failures: print(f"FAIL: {failure}")
    return 1 if failures else 0


if __name__ == "__main__": raise SystemExit(main())
