"""Build exact built-in ImageGen prompts for the bounded non-canon LitRPG concepts."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PLAN = ROOT / "production/comic/concepts/future-litrpg-visual-concepts-r1.json"
PROFILE = ROOT / "production/comic/continuity/ch05-fictional-adult-visual-profile-r1.json"
OUT = ROOT / "experiments/review-packets/future-litrpg-visual-concepts-r1/prompt-manifest.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit-manifest", action="store_true")
    parser.add_argument("--candidate")
    args = parser.parse_args()
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    refs = {item["reference_id"]: item for item in profile["authorized_references"]}
    entries = []
    for candidate in plan["candidates"]:
        selected = [refs[ref_id] for ref_id in candidate["reference_ids"]]
        input_line = " ".join(f"Image {index}: {item['role']}; exact fictional-adult project reference only." for index, item in enumerate(selected, 1))
        prompt = "\n".join([
            "Use case: illustration-story",
            f"Asset type: explicitly NON-CANON North Garden future LitRPG concept {candidate['candidate_id']}; not CH05 production art and not a ComicPanelPlan.",
            f"Primary request: {candidate['request']}",
            f"Input images: {input_line}",
            f"Style/medium: {plan['style']}.",
            "Identity invariant: Soren always has wavy light-brown to dark-blond hair, never black; Sigrid always has dark-brown to near-black tied-back hair, never blond. P050/P040 control identity; never copy P036 hair colors.",
            "Adult boundary: every visible person is an unmistakably mature fictional adult with practical, non-sexualized proportions and clothing; no real-person likeness.",
            "Equipment boundary: practical fantasy armor and weapons only, readable grip and load, no gore, injury, fetish treatment, giant decorative weapon, logo, watermark, caption, speech balloon, interface, or readable text.",
            "Continuity boundary: these wardrobe, armor, weapon, monster, and class ideas are separate non-canon exploration and do not revise CH05 wardrobe or story state.",
        ])
        exact_refs = [{"reference_id": item["reference_id"], "path": str((ROOT / item["path"]).resolve()), "sha256": item["sha256"], "role": item["role"]} for item in selected]
        output_path = ROOT / plan["output_root"] / "candidates" / f"{candidate['candidate_id']}-{candidate['concept_id']}-r1.png"
        entries.append({
            **candidate,
            "prompt": prompt,
            "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
            "references": exact_refs,
            "output_path": str(output_path.resolve()),
        })
    manifest = {
        "record_type": "FutureLitRPGConceptPromptManifest",
        "schema_version": "1.0",
        "record_id": "ng-future-litrpg-concept-prompt-manifest-r1",
        "state": "EXACT_NONCANON_PROMPTS_READY",
        "plan": {"path": PLAN.relative_to(ROOT).as_posix(), "sha256": sha256(PLAN)},
        "profile": {"path": PROFILE.relative_to(ROOT).as_posix(), "sha256": sha256(PROFILE)},
        "entries": entries,
        "boundary": "Built-in ImageGen only; exact fictional references only; ignored non-canon concepts; no production or commercial status."
    }
    if args.emit_manifest:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"wrote {len(entries)} exact non-canon prompts to {OUT}")
    if args.candidate:
        entry = next((item for item in entries if item["candidate_id"] == args.candidate), None)
        if entry is None:
            raise SystemExit("unknown candidate")
        print(json.dumps(entry, separators=(",", ":")))
    if not args.emit_manifest and not args.candidate:
        print(f"{len(entries)} exact non-canon prompts ready")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
