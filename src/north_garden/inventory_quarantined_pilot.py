"""Hash-pin and inventory the historical Garden's Anchor pilot without importing canon.

The source is intentionally treated as historical evidence.  This tool extracts
only source claims and panel-number ranges; it never maps names, copies prompts,
or turns text into current Canon/StoryState/ComicPanelPlan objects.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "garden-work/northgarden/pilot.md"
OUTPUT = ROOT / "research/historical/inventories/gardens-anchor-pilot-r1.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def panel_numbers(section: str) -> list[int]:
    return [int(match.group(1)) for match in re.finditer(r"(?m)^([0-9]{2})\s*$", section)]


def details(label: str, numbers: list[int]) -> dict[str, object]:
    expected = list(range(1, (max(numbers) if numbers else 0) + 1))
    return {
        "source_label": label,
        "observed_panel_numbers": numbers,
        "observed_count": len(numbers),
        "contiguous_from_01": numbers == expected,
    }


def main() -> None:
    text = SOURCE.read_text(encoding="utf-8")
    first = text.index("Chapter OneDay")
    second = text.index("Chapter TwoDay")
    footer = text.index("THE GARDEN’S ANCHOR · pilot chapters 01–02")
    opening_claim_text = "Two chapters, ninety-two panels"
    opening_claim = 92 if opening_claim_text in text else None
    footer_claim = re.search(r"pilot chapters 01–02 · (\d+) panels", text)
    footer_claim_value = int(footer_claim.group(1)) if footer_claim else None
    ch1 = details("Chapter One", panel_numbers(text[first:second]))
    ch2 = details("Chapter Two", panel_numbers(text[second:footer]))
    observed_total = int(ch1["observed_count"]) + int(ch2["observed_count"])
    output = {
        "record_type": "HistoricalNarrativeInventory",
        "schema_version": "1.0",
        "record_id": "ng-historical-gardens-anchor-pilot-r1",
        "source_path": "garden-work/northgarden/pilot.md",
        "source_sha256": sha256(SOURCE),
        "classification": "HISTORICAL_NARRATIVE_AND_DESIGN_EVIDENCE_NOT_IMPORTED",
        "import_prohibitions": [
            "No current canon/name mapping.",
            "No current ComicPanelPlan or AnimationShotPlan/E-Conte generation.",
            "No reuse of prompts, images, photo-derived design material, or likeness references.",
        ],
        "chapters": [ch1, ch2],
        "count_claims": {
            "opening_claim": opening_claim,
            "footer_claim": footer_claim_value,
            "observed_numbered_total": observed_total,
            "state": "INTERNALLY_INCONSISTENT" if len({opening_claim, footer_claim_value, observed_total}) > 1 else "CONSISTENT",
        },
        "decision_reference": "docs/adr/ADR-0022-quarantine-gardens-anchor-script-and-design-conflict.md",
        "limitation": "This inventory establishes source facts only; it is not approval to adapt, render, publish, or call the historical script current North Garden canon.",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"{output['count_claims']['state']}; wrote {OUTPUT}")


if __name__ == "__main__":
    main()
