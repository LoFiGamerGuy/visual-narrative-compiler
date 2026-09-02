"""Build exact prompts for the authorized CH05 overnight ImageGen plan."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PLAN_PATH = ROOT / "production/comic/overnight/ch05-overnight-production-plan-r1.json"
PROFILE_PATH = ROOT / "production/comic/continuity/ch05-fictional-adult-visual-profile-r1.json"
PANELS_PATH = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def prompt_for(candidate: dict, plan: dict, profile: dict, references: dict[str, dict], style: str) -> tuple[str, list[dict]]:
    selected_refs = [references[item] for item in candidate["reference_ids"]]
    reference_lines = []
    for index, reference in enumerate(selected_refs, 1):
        reference_lines.append(f"Image {index}: {reference['role']}; exact fictional reference only.")
    visible = plan["visible_adult_cast"]
    if visible == ["SOREN", "SIGRID"]:
        cast = "exactly two clearly adult fictional characters: Soren and Sigrid"
    elif visible == ["SOREN"]:
        cast = "only Soren is visible; do not copy Sigrid or any extra person from a reference"
    elif visible == ["SIGRID"]:
        cast = "only Sigrid is visible; do not copy Soren or any extra person from a reference"
    else:
        cast = "no people are visible; this is an environment or story-object panel"
    safe = plan["comic_direction"]["lettering"]["safe_zones"][0]
    s = profile["roles"]["SOREN"]
    g = profile["roles"]["SIGRID"]
    input_line = "Input images: none; text-only control." if not reference_lines else "Input images: " + " ".join(reference_lines)
    prompt = "\n".join([
        "Use case: illustration-story",
        f"Asset type: North Garden CH05 ComicPanelPlan candidate {candidate['candidate_id']} for {candidate['format_role']}",
        f"Primary request: {plan['narrative_beat']} Composition requirement: {plan['composition_intent']}. {candidate['special_instruction']}",
        input_line,
        "Scene/backdrop: wet northern rural dark-fantasy setting at cold overcast dawn; use only environment and story objects implied by the beat.",
        f"Style/medium: {style}.",
        f"Composition/framing: {candidate['format_role']}; {plan['comic_direction']['direction_note']}",
        f"Lettering: preserve the canonical {safe['anchor']} normalized safe zone {safe['rect_norm']} as a quiet low-detail field. No text or balloon. Do not place any face, person, important hand, causal prop, or essential silhouette inside it.",
        f"Continuity - Soren: {s['hair']}; {s['face']}; {s['wardrobe']}; {s['silhouette']}.",
        f"Continuity - Sigrid: {g['hair']}; {g['face']}; {g['wardrobe']}; {g['silhouette']}.",
        f"Cast constraint: {cast}.",
        "Reference invariant: P050 is the dual identity anchor and P040 is the Sigrid face anchor. If P036 is present, use it only for composition and lever staging; never copy its dark-haired Soren or blond Sigrid.",
        "Constraints: all visible characters are clearly adults with mature proportions and practical non-sexualized clothing; expressive unobstructed faces; readable anatomy and hands; causal action and story objects; strong phone-size silhouette; no real-person likeness.",
        "Avoid: child-coded appearance, blond Sigrid, black-haired Soren, swapped wardrobes, extra people, merged limbs, illegible hands, face occlusion, opaque lettering, decorative text, labels, captions, speech balloons, logos, watermark, generic speed-line wallpaper, magic or undeclared weapons/monsters.",
    ])
    refs = [{"reference_id": item["reference_id"], "path": str((ROOT / item["path"]).resolve()), "sha256": item["sha256"], "role": item["role"]} for item in selected_refs]
    return prompt, refs


def build(plan_path: Path = PLAN_PATH) -> dict:
    plan, profile, panels = load(plan_path), load(PROFILE_PATH), load(PANELS_PATH)
    references = {item["reference_id"]: item for item in profile["authorized_references"]}
    panel_by_id = {item["panel_id"]: item for item in panels["plans"]}
    entries = []
    for candidate in plan["candidates"]:
        panel = panel_by_id[candidate["panel_id"]]
        prompt, refs = prompt_for(candidate, panel, profile, references, plan["style_families"][candidate["style_id"]])
        filename = f"{candidate['candidate_id']}-{candidate['panel_id'].split('-')[-1]}-{candidate['style_id']}-r1.png"
        entries.append({
            **candidate,
            "plan_revision_id": panel["plan_revision_id"],
            "prompt": prompt,
            "prompt_sha256": sha256_bytes(prompt.encode("utf-8")),
            "references": refs,
            "output_path": str((ROOT / plan["output_root"] / "candidates" / filename).resolve()),
        })
    return {
        "record_type": "CH05AuthorizedImageGenPromptManifest",
        "schema_version": "1.0",
        "record_id": f"{plan['record_id']}-prompt-manifest",
        "state": "EXACT_PROMPTS_READY",
        "plan": {"path": plan_path.relative_to(ROOT).as_posix(), "sha256": sha256(plan_path)},
        "profile": {"path": PROFILE_PATH.relative_to(ROOT).as_posix(), "sha256": sha256(PROFILE_PATH)},
        "panels": {"path": PANELS_PATH.relative_to(ROOT).as_posix(), "sha256": sha256(PANELS_PATH)},
        "candidate_count": len(entries),
        "entries": entries,
        "boundary": "Exact built-in ImageGen prompts. Only listed hash-pinned fictional references are permitted; outputs remain ignored and unaccepted.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, default=PLAN_PATH)
    parser.add_argument("--emit-manifest", action="store_true")
    parser.add_argument("--candidate")
    args = parser.parse_args()
    plan_path = args.plan.resolve()
    try:
        plan_path.relative_to(ROOT.resolve())
    except ValueError as error:
        raise SystemExit("plan escapes workspace") from error
    manifest = build(plan_path)
    out = ROOT / load(plan_path)["output_root"] / "prompt-manifest.json"
    if args.emit_manifest:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"wrote {len(manifest['entries'])} exact prompts to {out}")
    if args.candidate:
        entry = next((item for item in manifest["entries"] if item["candidate_id"] == args.candidate), None)
        if entry is None:
            raise SystemExit(f"unknown candidate: {args.candidate}")
        print(json.dumps(entry, separators=(",", ":")))
    if not args.emit_manifest and not args.candidate:
        print(f"{len(manifest['entries'])} exact prompts ready")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
