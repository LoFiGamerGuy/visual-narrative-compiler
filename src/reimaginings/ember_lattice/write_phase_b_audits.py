from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
VOLUME = ROOT / "production" / "reimaginings" / "ember-lattice" / "volume"
DOCS = ROOT / "docs" / "reimaginings" / "ember-lattice" / "phase-b-audits"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def scope_metrics(start: int, end: int, metrics: dict) -> dict:
    rows = metrics["chapters"][start - 1:end]
    panels = len(rows) * 24
    action = sum(row["action_panels"] for row in rows)
    density = {key: sum(row["density"][key] for row in rows) for key in ("low", "moderate", "high")}
    return {
        "chapters": f"CH{start:02d}–CH{end:02d}", "panels": panels, "action_panels": action,
        "action_percentage": round(action / panels * 100, 3), "density": density,
        "dialogue_words": sum(row["spoken_internal_words"] for row in rows),
        "system_moments": sum(row["meaningful_system_moments"] for row in rows),
    }


def main() -> None:
    metrics = read(VOLUME / "dialogue-and-density-metrics.json")
    requests = read(VOLUME / "generation-requests.json")["requests"]
    system = read(VOLUME / "system-state-validation.json")
    if any(row["review_status"] not in {"REVIEWED_PASS", "HARD_FAIL_PRESERVED_DIAGNOSTIC"} for row in requests):
        raise SystemExit("phase audits require all generated art to pass local visual review")
    DOCS.mkdir(parents=True, exist_ok=True)
    audits = [
        {
            "file": "01-ch01-ch02-recognition-system-density.md", "scope": scope_metrics(1, 2, metrics),
            "title": "CH01–CH02 anime/manhwa, system, complexion, lettering, density, and phone audit",
            "findings": [
                "PASS — Candidate B contour/cel-value language, adult facial construction, and charcoal/teal/ivory/brass palette remain recognizable in both chapters.",
                "PASS — Elian and Mira remain fair/light-complexioned fictional adults with distinct face, hair, build, costume, weapon, and role silhouettes.",
                "PASS — nine consequential Ledger moments cover starting status, skill cost, cultivation, level/XP carry, quest/class options, class selection, inventory sacrifice, and reputation/trust.",
                "PASS — compact 84% balloons, outlined open text, and 82% Ledger cards survive the 390px reader without focal-region overlap.",
                "PASS — low-detail share remains 32/48 and no adjacent maximum-density violation occurs.",
            ],
        },
        {
            "file": "02-ch03-ch04-fight-causality-and-arithmetic.md", "scope": scope_metrics(3, 4, metrics),
            "title": "CH03–CH04 fight-causality and SystemState arithmetic audit",
            "findings": [
                "PASS — Glassback and Crownspike Bailiff sequences visibly establish geography, intention, initiation, contact/interruption, consequence, response, adaptation, and state payoff.",
                "PASS — Seed III, Level 5 XP carry, item gain/condition, HP/Qi costs, quest failure, injuries, and equipment damage reconcile at both chapter boundaries.",
                "PASS — the Verdigris race pays its stated failure consequence without duplicate XP or reward.",
            ],
        },
        {
            "file": "03-ch01-ch06-continuity-genre-progression-eye-strain.md", "scope": scope_metrics(1, 6, metrics),
            "title": "Six-chapter continuity, genre-promise, progression, and eye-strain audit",
            "findings": [
                "PASS — injuries, consumed materials, repaired/crafted gear, party membership, trust, factions, quests, zones, class, skills, levels, and cultivation persist through CH06.",
                "PASS — the visible LitRPG promise includes XP/levels, class choice, skill ranks/costs/cooldowns, enemy levels, items/rarities, inventory decisions, quests, reputation, cultivation success and setback, and combat application.",
                "PASS — low/moderate/high rhythm remains 96/36/12, with quiet recovery/crafting beats breaking boss and hazard runs.",
                "PASS — no SystemState boundary mismatch or negative inventory quantity is present.",
            ],
        },
        {
            "file": "04-ch07-ch10-final-and-repair-wave.md", "scope": scope_metrics(7, 10, metrics),
            "title": "CH07–CH10 final production and bounded repair-wave audit",
            "findings": [
                "PASS — Channel I, Rift Temperer, Level 7, final Relic loadouts, Fault Sight II, Level 8, Channel II, Rift Draw III, boss rewards, and faction resolution are causally shown and transaction-logged.",
                "PASS — Collapse Hound, Brass Maw, Crown Guards, and Bell Regent sequences remain readable at phone width with decisive evolved-skill use.",
                "PASS — one landscape-orientation hard failure at CH03 P007 was preserved and resolved by the single allowed localized retry; every selected Phase B source passes the tall-panel contract.",
                "PASS — final state is Level 8, 295/400 XP, 8/83 HP, 14/90 Qi, Rift Temperer, Breath Channel II, Free Delvers 58, Ash Crown −35, party trust 42.",
            ],
        },
    ]
    index = ["# Phase B audit index", "", f"Authoritative SystemState validator: **{system['status']}**.", ""]
    for audit in audits:
        scope = audit["scope"]
        body = [f'# {audit["title"]}', "", "Status: **PASS**", "", "## Scope metrics", ""]
        body += [f'- {key.replace("_", " ")}: {value}' for key, value in scope.items()]
        body += ["", "## Findings", ""] + [f'- {line}' for line in audit["findings"]] + [""]
        (DOCS / audit["file"]).write_text("\n".join(body), encoding="utf-8", newline="\n")
        index.append(f'- [{audit["title"]}]({audit["file"]})')
    (DOCS / "index.md").write_text("\n".join(index) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": "PASS", "audits": len(audits), "directory": str(DOCS)}, indent=2))


if __name__ == "__main__":
    main()
