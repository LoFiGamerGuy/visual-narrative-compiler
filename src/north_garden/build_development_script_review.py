"""Build a readable review sheet for a non-canon narrative development script."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "research/development/clean-ch05-mill-signal-r1.json"
OUTPUT = ROOT / "research/development/review-packets/clean-ch05-mill-signal-r1.md"


def main() -> None:
    script = json.loads(SOURCE.read_text(encoding="utf-8"))
    continuity = script["continuity_proposal"]
    lines = [
        f"# {script['title']} — narrative review sheet",
        "",
        f"Status: **{script['state']}**",
        "",
        script["approval_boundary"],
        "",
        "## Proposed continuity",
        "",
        f"- Fictional adult cast: {', '.join(continuity['fictional_adult_cast'])}",
        f"- Time: {continuity['time']}",
        f"- Proposed spatial mode: `{continuity['spatial_mode_proposal']}`",
        "- Animation-shot plan: absent by design.",
        "",
        "## Panel review",
        "",
        "| # | Beat | Composition intent | Visible adult cast |",
        "| --- | --- | --- | --- |",
    ]
    for panel in script["panels"]:
        cast = ", ".join(panel["visible_adult_cast"]) or "environment/object only"
        lines.append(f"| {panel['display_order']:02d} | {panel['beat']} | {panel['composition']} | {cast} |")
    lines.extend([
        "",
        "## Review outcome",
        "",
        "Record one of: `approve for canon/panel-plan development`, `approve with changes`, or `reject`. Approval still does not authorize a renderer, external upload, or use of likeness material. Any promotion must create new current StoryState, AssetRegistry, SceneBeat, ComicPanelPlan, assertion-manifest, and provenance records rather than mutating this draft.",
    ])
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
