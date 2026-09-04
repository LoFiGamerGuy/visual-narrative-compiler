#!/usr/bin/env python3
"""Record bounded style/topology ImageGen requests without inventing provider metadata."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from PIL import Image

from .pipeline import ART, PROD, density_metrics, dump, sha_file, sha_text, utc_now


STYLE_PROBE_TEMPLATE = """Use case: illustration-story
Asset type: Candidate {label} clean fantasy-webtoon style-system probe, owner-review-pending
Primary request: Create one portrait canvas divided into exactly three clean stacked comic frames with narrow gutters, top to bottom: (1) expressive close-up of Sola Merrow, a fictional adult woman age 38 with warm brown skin, long dark auburn segmented low braid and one silver forelock, listening to a tiny cyan-gold road pulse on her copper bracer; (2) quiet two-person waist-up exchange between Sola and Tarin Kest, fictional adult man age 45 with deep umber skin and short tight black curls silver at the temples, both in practical civic work clothes; (3) wide vertical-scale view of those two adults on a pearl-stone crescent road over a deep blue cloud sea.
Style/medium: {style}
Color palette: {palette}
Composition: one focal subject per frame, mature adult anatomy, large readable faces/hands/silhouettes, simple backgrounds in frames 1–2, controlled depth in frame 3, generous natural negative space.
Constraints: source art only; no text, letters, numbers, captions, balloons, blank rectangles, placards, logos, signatures, watermarks; no children or young-looking adults; no sexualization; no real-person likeness; no third-party characters; no named-artist or named-title imitation.
Avoid: woodcut, dry brush, risograph, paper grain, hatching, crosshatching, grunge, muddy palette, equal detail everywhere, multiple competing effects, generic glossy 3D."""

STYLE_VARIANTS = {
    "a": (
        "original clean cinematic fantasy-webtoon illustration; crisp controlled dark-navy contours; limited internal linework; polished smooth cel shading with very restrained painterly gradients.",
        "midnight blue dominant, pearl and cool gray support, selective cyan-gold luminous accent.",
        "candidate-a.png", None,
    ),
    "b": (
        "original luminous restrained painterly fantasy-webtoon illustration; clean confident outer contours, soft simplified interior modeling, elegant broad color planes, edges selectively softened away from the focal subject.",
        "violet-midnight dominant, pale stone support, selective amber-cyan luminous accent.",
        "candidate-b.png", None,
    ),
    "c": (
        "original flat graphic fantasy-webtoon illustration; strong clean navy silhouettes, large uncluttered shapes, minimal interior linework, two-step cel shading, sparing geometric gradients.",
        "inky navy dominant, pale mint and pearl support, selective coral-gold luminous accent.",
        "candidate-c.png", None,
    ),
}

COMMON = """Use case: illustration-story
Asset type: controlled clean fantasy-webtoon topology pilot, owner-review-pending
Input images: Image 1 is the registered clean-cinematic style-system anchor created in this experiment; use it only for original Sola/Tarin identity, palette, contour, and rendering continuity.
World: original Caelune pearl-stone skyroad over a deep blue cloud sea.
Style: preserve the reference's crisp controlled dark-navy contours, limited internal lines, smooth restrained cel shading, midnight/pearl palette, and one cyan-gold oathlight accent.
Characters: Sola Merrow, fictional adult woman age 38, warm brown skin, dark auburn segmented low braid, one silver forelock, navy practical coat, ochre scarf, copper bracer; Tarin Kest, fictional adult man age 45, deep umber skin, short tight black curls silver at temples, pearl-gray practical coat, ivory spear-key.
Constraints: mature adult proportions; non-sexualized practical clothing; one dominant focal action per frame; clear faces, hands, silhouettes and causal contact at 390-pixel width; simple supporting background; no text, letters, numbers, captions, balloons, blank rectangles, placards, logos, signatures or watermarks; no children, young-looking adults, real-person likeness, third-party character, named-artist or named-title imitation.
Avoid: woodcut, dry brush, risograph, paper grain, hatching, crosshatching, grunge, equal detail everywhere, muddy contrast, multiple effects, crowded machinery, glossy 3D."""

TOPOLOGY = {
    "individual-01": ("Topology: one individual portrait comic panel, no internal gutters.\nSingle beat: expressive close-up of Sola hearing a tiny cyan-gold oath pulse lift from her bracer; her adult face and open hand carry wary recognition; quiet midnight background.", 51.532),
    "individual-02": ("Topology: one individual portrait comic panel, no internal gutters.\nSingle beat: quiet waist-up two-person interaction; Sola shows Tarin the pulse while Tarin studies it without touching; restrained concern and new trust; ample empty background.", 98.179),
    "individual-03": ("Topology: one individual portrait comic panel, no internal gutters.\nSingle beat: physical action on a broken skyroad with dramatic vertical scale; Tarin anchors his spear-key while Sola pulls one thin oathlight line across a gap; clear force direction and readable feet/hands; one effect only.", 152.564),
    "two-strip-01": ("Topology: one portrait canvas divided into exactly two stacked chronological comic frames with one clean narrow gutter.\nFrame 1: expressive close-up of Sola hearing a tiny cyan-gold oath pulse lift from her bracer; wary recognition.\nFrame 2: quiet waist-up two-person interaction; Sola shows Tarin the pulse while he studies it without touching; restrained concern and new trust.\nEach frame is distinct, spacious, and independently crop-safe.", 206.699),
    "two-strip-02": ("Topology: one individual portrait comic panel, no internal gutters.\nSingle beat: physical action on a broken skyroad with dramatic vertical scale; Tarin anchors his spear-key while Sola pulls one thin oathlight line across a gap; clear force direction and readable feet/hands; one effect only.", 261.650),
    "three-strip-01": ("Topology: one portrait canvas divided into exactly three stacked chronological comic frames with clean narrow gutters.\nFrame 1: expressive close-up of Sola hearing a tiny cyan-gold oath pulse lift from her bracer; wary recognition.\nFrame 2: quiet waist-up two-person interaction; Sola shows Tarin the pulse while he studies it without touching; restrained concern and new trust.\nFrame 3: physical action on a broken skyroad with vertical scale; Tarin anchors his spear-key while Sola pulls one thin oathlight line across a gap; clear force direction.\nEach frame is distinct, spacious, and independently crop-safe.", 316.883),
}


def base_record(request_id: str, prompt: str, path: Path, elapsed: float | None, refs: list[dict[str, Any]]) -> dict[str, Any]:
    image = Image.open(path).convert("RGB")
    return {
        "record_type": "RenderRecord", "schema_version": "CityKeepsOathsRenderRecord/1.0", "request_id": request_id,
        "exact_prompt": prompt, "prompt_sha256": sha_text(prompt), "target_chapter": None, "target_sequence": "bounded-pilot",
        "target_panel_ids": [], "input_references": refs, "output_path": path.relative_to(ART.parents[2]).as_posix(),
        "output_sha256": sha_file(path), "dimensions": list(image.size), "measured_elapsed_seconds": elapsed,
        "product": "OpenAI built-in ImageGen in Codex", "tool": "image_gen", "model": None, "endpoint": None,
        "provider_request_id": None, "usage": None, "monetary_cost_usd": None, "deterministic_seed": None,
        "extraction_method": None, "crop_coordinates": None,
        "candidate_paths_and_hashes": [{"file": path.relative_to(ART.parents[2]).as_posix(), "sha256": sha_file(path)}],
        "review_status": "PASS", "failure_classes": [], "human_review_state": "owner_review_pending",
        "acceptance_state": "unaccepted", "commercial_clearance_state": "commercially_uncleared",
        "production_base_state": "not_an_exact_production_base", "reproducibility_state": "non_reproducible_unless_proven",
        "recorded_utc": utc_now(),
    }


def main() -> None:
    records = []
    for label, (style, palette, filename, elapsed) in STYLE_VARIANTS.items():
        prompt = STYLE_PROBE_TEMPLATE.format(label=label.upper(), style=style, palette=palette)
        path = ART / "style-probes" / filename
        record = base_record(f"STYLE-{label.upper()}", prompt, path, elapsed, [])
        record["timing_note"] = "Individual elapsed was not captured in the first concurrent probe batch; the observed concurrent batch wall time was 200.3 seconds. Null is retained rather than invented."
        record["metrics_390px"] = density_metrics(Image.open(path))
        records.append(record)
    anchor = records[0]["candidate_paths_and_hashes"][0]
    for name, (suffix, elapsed) in TOPOLOGY.items():
        prompt = COMMON + "\n" + suffix
        path = ART / "pilot" / f"{name}.png"
        record = base_record(f"PILOT-{name.upper()}", prompt, path, elapsed, [{"id":"clean-cinematic-style-anchor-v1", **anchor}])
        record["metrics_390px"] = density_metrics(Image.open(path))
        records.append(record)
    dump(PROD / "pilot" / "render-records.json", {"requests": records})
    print(f"recorded {len(records)} bounded requests")


if __name__ == "__main__":
    main()
