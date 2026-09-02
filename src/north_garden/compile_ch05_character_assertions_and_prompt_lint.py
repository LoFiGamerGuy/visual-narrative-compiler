"""Compile exact CH05 character assertions and lint all canonical built-in prompts."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PLANS = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"
PROFILE = ROOT / "production/comic/continuity/ch05-fictional-adult-visual-profile-r1.json"
PRIORITY = ROOT / "production/comic/coverage/ch05-remaining-panel-priority-r1.json"
PROMPTS = [
    ROOT / "experiments/review-packets/ch05-overnight-production-r1/prompt-manifest.json",
    ROOT / "experiments/review-packets/ch05-cadence-hardening-r1/prompt-manifest.json",
]
MANIFEST = ROOT / "production/comic/continuity/ch05-character-assertion-manifest-r1.json"
EVIDENCE = ROOT / "docs/research/evidence/ch05-character-assertion-and-prompt-lint-r1.json"


def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()
def root_hash(rows: list[dict]) -> str:
    return hashlib.sha256("\n".join(json.dumps(row,sort_keys=True,separators=(",",":")) for row in rows).encode()).hexdigest()


def main() -> int:
    plans=json.loads(PLANS.read_text(encoding="utf-8")); profile=json.loads(PROFILE.read_text(encoding="utf-8")); priority=json.loads(PRIORITY.read_text(encoding="utf-8"))
    tier_by_panel={row["panel_id"]:row["coverage_state"] for row in priority["rows"]}
    roles=profile["roles"]
    plan_rows=[]
    for plan in plans["plans"]:
        cast=plan["visible_adult_cast"]
        assertions={role:roles[role] for role in cast}
        plan_rows.append({
            "panel_id":plan["panel_id"],"plan_revision_id":plan["plan_revision_id"],"display_order":plan["display_order"],
            "coverage_partition":tier_by_panel[plan["panel_id"]],"visible_adult_cast":cast,"visible_adult_count":len(cast),
            "role_assertions":assertions,"no_people_required":not cast,
            "composition_intent":plan["composition_intent"],
            "role_order_semantics":{
                "source":"composition_intent_and_narrative_beat_not_visible_adult_cast_array_order",
                "requires_literal_prompt_translation":len(cast)>1,
                "note":"The cast array is membership, not foreground/leader/action order; do not infer staging from SOREN,SIGRID array order.",
            },
            "comic_panel_plan_only":True,"animation_shot_plan":None,"e_conte":None,
        })
    common_required=[
        "Continuity - Soren:","short-to-medium wavy light-brown to dark-blond hair","pale oatmeal work coat",
        "Continuity - Sigrid:","dark-brown to near-black hair tied","practical plaid wrap",
        "all visible characters are clearly adults","mature proportions","practical non-sexualized clothing",
        "no real-person likeness","child-coded appearance","P036 is present, use it only for composition",
        "never copy its dark-haired Soren or blond Sigrid",
    ]
    plan_by_id={row["panel_id"]:row for row in plans["plans"]}; prompt_rows=[]
    for prompt_path in PROMPTS:
        document=json.loads(prompt_path.read_text(encoding="utf-8"))
        for entry in document["entries"]:
            prompt=entry["prompt"]; plan=plan_by_id[entry["panel_id"]]; cast=plan["visible_adult_cast"]
            if cast==["SOREN","SIGRID"]: cast_phrase="exactly two clearly adult fictional characters: Soren and Sigrid"
            elif cast==["SOREN"]: cast_phrase="only Soren is visible; do not copy Sigrid or any extra person"
            elif cast==["SIGRID"]: cast_phrase="only Sigrid is visible; do not copy Soren or any extra person"
            else: cast_phrase="no people"
            checks={
                "prompt_hash_exact":hashlib.sha256(prompt.encode()).hexdigest()==entry["prompt_sha256"],
                "plan_revision_exact":entry["plan_revision_id"]==plan["plan_revision_id"],
                "common_adult_hair_wardrobe_boundary_complete":all(token in prompt for token in common_required),
                "cast_constraint_matches_plan":cast_phrase in prompt,
                "p036_composition_only_guard":("p036_composition_only" not in entry["reference_ids"] or ("P036" in prompt and "composition" in prompt and "never copy its dark-haired Soren or blond Sigrid" in prompt)),
                "comic_panel_plan_named":"ComicPanelPlan" in prompt,
            }
            prompt_rows.append({"candidate_id":entry["candidate_id"],"panel_id":entry["panel_id"],"plan_revision_id":entry["plan_revision_id"],
                                "prompt_manifest":prompt_path.relative_to(ROOT).as_posix(),"prompt_sha256":entry["prompt_sha256"],
                                "reference_ids":entry["reference_ids"],"visible_adult_cast":cast,"checks":checks,"all_checks_pass":all(checks.values()),
                                "output_review_boundary":"Prompt compliance does not prove rendered hair, wardrobe, role, anatomy, or identity; manual visual review remains required."})
    if len(plan_rows)!=50 or len(prompt_rows)!=26 or not all(row["all_checks_pass"] for row in prompt_rows):raise SystemExit("character assertion or prompt lint failed")
    cast_counts=Counter(tuple(row["visible_adult_cast"]) for row in plan_rows)
    manifest={
        "record_type":"ComicCharacterAssertionManifest","schema_version":"1.0","record_id":"ng-ch05-character-assertion-manifest-r1",
        "state":"REVIEW_CONTROL_READY_NOT_RENDER_AUTHORITY","medium":"comic","comic_panel_plan_collection":{"path":PLANS.relative_to(ROOT).as_posix(),"sha256":sha(PLANS)},
        "continuity_profile":{"path":PROFILE.relative_to(ROOT).as_posix(),"sha256":sha(PROFILE)},"plan_count":50,
        "cast_distribution":{"NO_PEOPLE":cast_counts[()],"SOREN_ONLY":cast_counts[("SOREN",)],"SIGRID_ONLY":cast_counts[("SIGRID",)],"SOREN_AND_SIGRID":cast_counts[("SOREN","SIGRID")]},
        "plans":plan_rows,"plan_row_root_sha256":root_hash(plan_rows),"animation_shot_plan":None,"e_conte":None,
        "p036_identity_boundary":"P036 is composition-only because its hair roles conflict; P050/P040 remain identity anchors.",
        "future_design_boundary":"Armor, weapons, upgraded clothes, and monsters remain separately labeled non-canon until a future ComicPanelPlan revision and owner decision.",
        "boundary":"Assertions constrain future prompt compilation but authorize no prompt, generation, upload, acceptance, canon change, or commercial use.",
    }
    MANIFEST.parent.mkdir(parents=True,exist_ok=True)
    with MANIFEST.open("w",encoding="utf-8",newline="\n") as h:h.write(json.dumps(manifest,indent=2)+"\n")
    evidence={
        "record_type":"CH05CharacterAssertionAndPromptLintEvidence","schema_version":"1.0","record_id":"ng-ch05-character-assertion-and-prompt-lint-evidence-r1",
        "state":"FIFTY_PLAN_ASSERTIONS_AND_TWENTY_SIX_PROMPTS_PASS",
        "manifest":{"path":MANIFEST.relative_to(ROOT).as_posix(),"sha256":sha(MANIFEST),"plan_row_root_sha256":manifest["plan_row_root_sha256"]},
        "inputs":{"plan_collection":{"path":PLANS.relative_to(ROOT).as_posix(),"sha256":sha(PLANS)},"continuity_profile":{"path":PROFILE.relative_to(ROOT).as_posix(),"sha256":sha(PROFILE)},
                  "prompt_manifests":[{"path":p.relative_to(ROOT).as_posix(),"sha256":sha(p)} for p in PROMPTS]},
        "summary":{"plan_count":50,"no_people_plans":cast_counts[()],"soren_only_plans":cast_counts[("SOREN",)],"sigrid_only_plans":cast_counts[("SIGRID",)],"dual_cast_plans":cast_counts[("SOREN","SIGRID")],
                   "prompt_count":26,"prompt_pass_count":sum(row["all_checks_pass"] for row in prompt_rows),"p036_prompt_count":sum("p036_composition_only" in row["reference_ids"] for row in prompt_rows),
                   "rendered_identity_inference_count":0,"prompts_created":0,"plans_revised":0,"provider_calls":0,"uploads":0,"external_cost_usd":0},
        "prompt_rows":prompt_rows,"prompt_row_root_sha256":root_hash(prompt_rows),
        "limitations":["String lint verifies explicit constraints, not rendered appearance.","No automated face, biometric, or identity inference is performed.","Visible-adult cast arrays encode membership, not leader/foreground/action ordering.","Manual visual review remains the authority for hair, wardrobe, role, anatomy, and continuity outcomes."],
        "boundary":"No generation or project promotion occurs; this is deterministic metadata and prompt-contract evidence only.",
    }
    with EVIDENCE.open("w",encoding="utf-8",newline="\n") as h:h.write(json.dumps(evidence,indent=2)+"\n")
    no_people=cast_counts[()]; soren_only=cast_counts[("SOREN",)]; sigrid_only=cast_counts[("SIGRID",)]; dual=cast_counts[("SOREN","SIGRID")]
    print(f"CH05 character assertions: 50 plans ({no_people} empty/{soren_only} Soren/{sigrid_only} Sigrid/{dual} dual)")
    print(f"prompt lint: 26/26 pass; P036 guarded {evidence['summary']['p036_prompt_count']}; rendered identity inference 0")
    return 0


if __name__=="__main__":raise SystemExit(main())
