"""Compile explicit cross-panel semantic gates discovered by complete-chapter review."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PLANS = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"
OUTPUT = ROOT / "production/comic/contracts/ch05-cross-panel-semantic-gates-r1.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    gates = [
        {"gate_id": "cold_farmhouse_until_reversal", "panel_ids": ["ng-ch05-sc01-p001", "ng-ch05-sc01-p048", "ng-ch05-sc01-p049"], "required_prompt_phrases": {"ng-ch05-sc01-p001": "farmhouse chimney completely cold: no smoke, no glow, no lit window", "ng-ch05-sc01-p048": "first new farmhouse chimney smoke of the chapter", "ng-ch05-sc01-p049": "stove was never lit before departure"}, "intent": "Preserve the final smoke reversal rather than revealing it in the opening."},
        {"gate_id": "departure_vector", "panel_ids": ["ng-ch05-sc01-p001"], "required_prompt_phrases": {"ng-ch05-sc01-p001": "travel downhill away from the farmhouse with the farmhouse clearly behind them"}, "intent": "Make departure geography causal and unambiguous."},
        {"gate_id": "independent_entry_roles", "panel_ids": ["ng-ch05-sc01-p029"], "required_prompt_phrases": {"ng-ch05-sc01-p029": "Soren independently watches the exterior while Sigrid enters; their gazes point in different directions"}, "intent": "Separate entry and watch roles."},
        {"gate_id": "impossible_far_bank_prints", "panel_ids": ["ng-ch05-sc01-p031", "ng-ch05-sc01-p032"], "required_prompt_phrases": {"ng-ch05-sc01-p031": "dry prints stop at the near water edge", "ng-ch05-sc01-p032": "far-bank prints begin on dry ground and asymmetric heel-toe shapes point back toward Soren"}, "intent": "Make the impossible footprint chain readable without labels."},
        {"gate_id": "continuous_leverage_force_path", "panel_ids": ["ng-ch05-sc01-p035", "ng-ch05-sc01-p036", "ng-ch05-sc01-p037"], "required_prompt_phrases": {"ng-ch05-sc01-p035": "tin remains high above on the beam", "ng-ch05-sc01-p036": "one continuous plank visibly connects both adult grips through the brace to contact and move the high tin", "ng-ch05-sc01-p037": "same tin now open on the stone beside the retained creek map"}, "intent": "Preserve object identity and a visible force path."},
        {"gate_id": "third_upstream_mark", "panel_ids": ["ng-ch05-sc01-p039"], "required_prompt_phrases": {"ng-ch05-sc01-p039": "three distinct upstream marks including the third mark at the torn edge"}, "intent": "Make the deduction clue count explicit."},
        {"gate_id": "drum_fully_out", "panel_ids": ["ng-ch05-sc01-p041"], "required_prompt_phrases": {"ng-ch05-sc01-p041": "drum fully cold and out: no ember, no flame, no smoke plume"}, "intent": "Allow silence and cessation to drive retreat."},
        {"gate_id": "map_possession", "panel_ids": ["ng-ch05-sc01-p037", "ng-ch05-sc01-p043", "ng-ch05-sc01-p046"], "required_prompt_phrases": {"ng-ch05-sc01-p037": "same tin now open on the stone beside the retained creek map", "ng-ch05-sc01-p043": "leave the open tin but Sigrid visibly keeps the creek map", "ng-ch05-sc01-p046": "Sigrid hides that same retained creek map under her plaid wrap"}, "intent": "Prevent the map from being abandoned then reappearing."},
    ]
    doc = {"record_type": "ComicPanelPlanCrossPanelSemanticGateContract", "schema_version": "1.0", "record_id": "ng-ch05-cross-panel-semantic-gates-r1", "state": "ACTIVE_PRE_PROMPT_FAIL_CLOSED", "medium": "comic", "planning_structure": "ComicPanelPlan", "animation_shot_plan": None, "e_conte": None, "comic_panel_plan_source": {"path": PLANS.relative_to(ROOT).as_posix(), "sha256": sha256(PLANS)}, "gates": gates, "summary": {"gates": len(gates), "unique_affected_panels": len({panel for gate in gates for panel in gate["panel_ids"]}), "required_prompt_bindings": sum(len(gate["required_prompt_phrases"]) for gate in gates)}, "boundary": "Prompt-stage semantic contract only; it does not establish visual compliance, acceptance, canon revision, or commercial clearance."}
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"output": OUTPUT.relative_to(ROOT).as_posix(), "sha256": sha256(OUTPUT), **doc["summary"]}, sort_keys=True))
    return 0


if __name__ == "__main__": raise SystemExit(main())
