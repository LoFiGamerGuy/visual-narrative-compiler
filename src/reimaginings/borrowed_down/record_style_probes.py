"""Pin text-only style probes and create the first eligible reference-registry entry."""

from __future__ import annotations

from pathlib import Path
from PIL import Image

from .pipeline import ART, PROD, ROOT, dump, sha_file, sha_text


BASE = """Use case: illustration-story
Asset type: text-only visual style probe for an adult science-fantasy comic
Primary request: Create a text-free six-cell comic contact sheet showing the same two fictional adults beside a vertical ocean: a tall broad-shouldered 41-year-old Black woman municipal ropewright with one blunt black wedge braid, ochre work coat, teal harness and heavy boots; and a lean 38-year-old copper-brown man with a silver-black asymmetrical curl crest, narrow moustache, coral half-cape, charcoal wraps and yellow barometer gauntlet. Show: quiet conversation, hauling a taut rope, bracing under sideways gravity, a close emotional disagreement, the wall-sea city, and a non-hostile translucent diamond-shaped sea creature.
Composition/framing: clean 3 by 2 grid, one readable moment per cell, strong gutters, varied distances, phone-readable silhouettes.
Constraints: all humans explicitly fictional adults with mature proportions; practical non-sexualized clothing; coherent anatomy; visible rope tension and grounded footing; no text, letters, numbers, logos, signatures, captions, speech balloons, UI, watermarks, children, child-coded features, sexual content, gore, real-person likeness, or imitation of any named or living artist."""

PROMPTS = {
    "pressure-print": """Use case: illustration-story
Asset type: text-only visual style probe for an adult science-fantasy comic
Primary request: Create a text-free six-cell comic contact sheet showing the same two fictional adults beside a vertical ocean: a tall broad-shouldered 41-year-old Black woman municipal ropewright with one blunt black wedge braid, ochre work coat, teal harness and heavy boots; and a lean 38-year-old copper-brown man with a silver-black asymmetrical curl crest, narrow moustache, coral half-cape, charcoal wraps and yellow barometer gauntlet. Show: quiet conversation, hauling a taut rope, bracing under sideways gravity, a close emotional disagreement, the wall-sea city, and a non-hostile translucent diamond-shaped sea creature.
Style/medium: pressure-print hybrid of bold woodcut edges and three-color risograph; chunky dry-brush black keylines; imperfect off-register oxidized teal, warning coral, and acid-yellow spot ink on warm fibrous paper; angular adult proportions; large readable hands; graphic negative-space force paths.
Composition/framing: clean 3 by 2 grid, one readable moment per cell, strong gutters, varied distances, phone-readable silhouettes.
Lighting/mood: urgent civic broadside, tactile, adventurous, emotionally mature.
Constraints: all humans explicitly fictional adults with mature proportions; practical non-sexualized clothing; coherent anatomy; visible rope tension and grounded footing; no text, letters, numbers, logos, signatures, captions, speech balloons, UI, watermarks, children, child-coded features, sexual content, gore, real-person likeness, or imitation of any named or living artist.""",
    "luminous": BASE + "\nStyle/medium: luminous soft-painted science fantasy with simplified environments, velvety edges, glowing cyan water, warm coral rim light, elegant adult proportions, restrained detail.\nLighting/mood: dreamlike wonder with grounded physical action.",
    "brush": BASE + "\nStyle/medium: high-contrast monochrome brush manga with one selective cyan spot color, explosive ink shapes, white paper, economical faces, large black shadows, hand-brushed motion arcs.\nLighting/mood: kinetic, stark, intimate.",
    "cutpaper": BASE + "\nStyle/medium: layered cut-paper collage storybook for adults, torn fibrous edges, flat geometric shapes, visible paper shadows, ochre teal coral palette, simplified but mature faces.\nLighting/mood: witty, tactile, adventurous.",
}

ELAPSED = {"pressure-print": 119.176, "luminous": 45.306, "brush": 173.134, "cutpaper": 220.152}
SCORES = {
    "pressure-print": {"distinctiveness":5,"identity_stability":5,"hands_action":5,"emotion":4,"environment":5,"phone_legibility":5,"lettering_clearance":4,"sustainable_density":4,"total":37},
    "luminous": {"distinctiveness":3,"identity_stability":5,"hands_action":5,"emotion":5,"environment":5,"phone_legibility":4,"lettering_clearance":3,"sustainable_density":2,"total":32},
    "brush": {"distinctiveness":4,"identity_stability":5,"hands_action":5,"emotion":4,"environment":4,"phone_legibility":4,"lettering_clearance":4,"sustainable_density":3,"total":33},
    "cutpaper": {"distinctiveness":5,"identity_stability":4,"hands_action":4,"emotion":3,"environment":5,"phone_legibility":5,"lettering_clearance":4,"sustainable_density":4,"total":34}
}


def main() -> None:
    records = []
    folder = ART / "style-probes"
    for name, prompt in PROMPTS.items():
        path = folder / f"{name}.png"
        with Image.open(path) as im:
            dims = list(im.size)
        records.append({
            "record_type":"RenderRecord", "schema_version":"BorrowedDownRenderRecord/1.0",
            "product":"OpenAI built-in ImageGen in Codex", "tool":"image_gen", "target_chapter":None,
            "sequence":f"STYLE-{name.upper()}", "target_panel_ids":[], "exact_prompt":prompt,
            "prompt_sha256":sha_text(prompt), "input_references":[],
            "output_file":path.relative_to(ROOT).as_posix(), "output_sha256":sha_file(path),
            "dimensions":dims, "elapsed_seconds":ELAPSED[name], "model":None, "model_snapshot":None,
            "endpoint":None, "provider_request_id":None, "usage":None, "monetary_cost_usd":None,
            "deterministic_seed":None, "crop_method":None, "crop_coordinates":None,
            "candidate_files":[{"file":path.relative_to(ROOT).as_posix(),"sha256":sha_file(path)}],
            "agent_review_status":"PASS", "failure_classes":[], "human_review_state":"owner_review_pending",
            "human_review_minutes":None, "acceptance_state":"unaccepted",
            "commercial_clearance_state":"commercially_uncleared",
            "exact_production_base_state":"not_an_exact_production_base",
            "reproducibility_state":"non_reproducible_unless_proven", "score":SCORES[name],
        })
    dump(PROD / "style-probe-render-records.json", {"records": records, "selected":"pressure-print", "selection_reason":"highest measured aggregate plus best causal action and phone silhouette; selection does not imply owner acceptance or commercial clearance"})
    selected = folder / "pressure-print.png"
    dump(PROD / "reference-registry.json", {"record_type":"IsolatedFictionalAssetReferenceRegistry","schema_version":"1.0","references":[{
        "id":"pressure_print_style_anchor", "file":selected.relative_to(ROOT).as_posix(), "sha256":sha_file(selected),
        "depicts":"fictional adults, invented wall-sea city, invented creature, invented costumes and tools",
        "inspection":"locally inspected at original resolution by agent on 2026-09-03",
        "eligibility":"eligible for reuse only in Borrowed Down through OpenAI built-in ImageGen",
        "real_person_likeness":False, "children":False, "private_data":False, "third_party_art":False,
        "active":True, "owner_review_state":"pending", "commercial_clearance":"uncleared"
    }]})
    print("recorded 4 style probes; registered 1 active isolated-project reference")


if __name__ == "__main__":
    main()
