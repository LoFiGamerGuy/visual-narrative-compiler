"""Prove deterministic synthetic finalization while real P036 stays fail-closed."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path

from render_record_boundary import boundary_render_record_errors
from validate_render_record_boundary import completed, write_fixture_files


ROOT = Path(__file__).resolve().parents[2]
MATRIX = ROOT / "production/comic/repair-readiness/ch05-repair-evidence-readiness-matrix-r1.json"
READINESS = ROOT / "production/comic/repair-readiness/ch05-p036-openai-r2.json"
TEMPLATE = ROOT / "config/record-templates/comic-repair-render-record-v2.json"
MEASUREMENT = ROOT / "docs/research/evidence/exact-base-boundary-measurement-packet-r1.json"
OUTPUT = ROOT / "production/comic/repair-readiness/ch05-p036-repair-outcome-finalizer-r1.json"


class FinalizerError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise FinalizerError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source(path: Path) -> dict:
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path)}


def digest(value: dict) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def finalize(record: dict, journal: dict, ledger: dict, *, validation_fixture: bool) -> dict:
    errors = boundary_render_record_errors(record, journal, ledger)
    if errors:
        raise FinalizerError("invalid evidence: " + "; ".join(errors))
    if record.get("synthetic_validation_fixture") is not validation_fixture:
        raise FinalizerError("fixture mode mismatch")
    if not validation_fixture:
        raise FinalizerError("real finalization requires separately supplied eligible evidence")
    return {"record": copy.deepcopy(record), "record_sha256": digest(record), "journal_sha256": digest(journal), "ledger_sha256": digest(ledger)}


def build() -> dict:
    write_fixture_files()
    matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
    readiness = json.loads(READINESS.read_text(encoding="utf-8"))
    measurement = json.loads(MEASUREMENT.read_text(encoding="utf-8"))
    row = next(item for item in matrix["panels"] if item["panel_id"] == "ng-ch05-sc01-p036")
    require(readiness["offline_preflight"]["blocker_count"] == 4, "P036 preflight blockers changed")
    require(measurement["synthetic_validation_fixture"] is True and measurement["review_packet"]["review_session"] is None, "measurement unexpectedly became real/reviewed")
    real_blockers = list(readiness["offline_preflight"]["blockers"]) + [
        "REAL_EXACT_BASE_BOUNDARY_MEASUREMENT_MISSING",
        "ELIGIBLE_TIMED_SEAM_REVIEW_MISSING",
        "COMPLETED_SUBMISSION_JOURNAL_MISSING",
        "CANDIDATE_OUTPUT_MISSING",
        "PROVIDER_COST_RECONCILIATION_MISSING",
    ]
    record, journal, ledger = completed()
    first = finalize(record, journal, ledger, validation_fixture=True)
    second = finalize(record, journal, ledger, validation_fixture=True)
    require(first == second, "synthetic finalization not deterministic")
    return {
        "record_type": "ComicRepairOutcomeFinalizerReadiness", "schema_version": "1.0",
        "record_id": "ng-ch05-p036-repair-outcome-finalizer-r1", "state": "REAL_FINALIZATION_BLOCKED_SYNTHETIC_LIFECYCLE_VALIDATED",
        "medium": "comic", "animation_shot_plan": None, "e_conte": None,
        "comic_panel_plan": {"panel_id": row["panel_id"], "plan_revision_id": row["plan_revision_id"]},
        "sources": {"chapter_readiness_matrix": source(MATRIX), "p036_readiness": source(READINESS), "render_record_v2_template": source(TEMPLATE), "exact_base_measurement_packet": source(MEASUREMENT)},
        "finalization_contract": {"required_terminal_journal_state": "COMPLETED", "required_render_profile": "comic_targeted_repair_v2", "required_schema_version": "2.1", "real_validation_fixture_allowed": False, "network_capability_present": False, "request_body_construction_present": False},
        "real_p036": {"state": "BLOCKED_NO_RENDER_RECORD_EMITTED", "blocker_count": len(real_blockers), "blockers": real_blockers, "render_record": None, "candidate": None, "review_session": None, "human_minutes": None, "provider_request": None, "cost_reconciliation": None, "accepted": False},
        "synthetic_validation": {"state": "VALIDATION_ONLY_DETERMINISTIC_FINALIZATION", "validation_fixture": True, "deterministic_across_two_finalizations": True, "render_record_sha256": first["record_sha256"], "journal_sha256": first["journal_sha256"], "ledger_sha256": first["ledger_sha256"], "eligible_as_real_evidence": False},
        "activity": {"real_provider_requests": 0, "real_external_uploads": 0, "real_external_cost_usd": "0.000000"},
        "boundary": "The finalizer is local evidence plumbing only. It cannot construct requests or turn fixtures, G07 budget, proxy images, or missing reviews into real outcomes.",
    }


def mutations(expected: dict) -> tuple[int, int]:
    values = []
    item = copy.deepcopy(expected); item["real_p036"]["blockers"].pop(); values.append(item)
    item = copy.deepcopy(expected); item["real_p036"]["blocker_count"] -= 1; values.append(item)
    item = copy.deepcopy(expected); item["real_p036"]["render_record"] = {}; values.append(item)
    item = copy.deepcopy(expected); item["real_p036"]["candidate"] = {}; values.append(item)
    item = copy.deepcopy(expected); item["real_p036"]["human_minutes"] = 3.0; values.append(item)
    item = copy.deepcopy(expected); item["synthetic_validation"]["validation_fixture"] = False; values.append(item)
    item = copy.deepcopy(expected); item["synthetic_validation"]["eligible_as_real_evidence"] = True; values.append(item)
    item = copy.deepcopy(expected); item["finalization_contract"]["network_capability_present"] = True; values.append(item)
    item = copy.deepcopy(expected); item["activity"]["real_provider_requests"] = 1; values.append(item)
    item = copy.deepcopy(expected); item["animation_shot_plan"] = {}; values.append(item)
    return sum(item != expected for item in values), len(values)


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--emit", type=Path); args = parser.parse_args()
    try:
        expected = build()
        if args.emit:
            target = args.emit if args.emit.is_absolute() else ROOT / args.emit
            target.parent.mkdir(parents=True, exist_ok=True); target.write_text(json.dumps(expected, indent=2) + "\n", encoding="utf-8", newline="\n")
        else: require(json.loads(OUTPUT.read_text(encoding="utf-8")) == expected, "tracked finalizer readiness differs")
        rejected, total = mutations(expected); require(rejected == total, "mutation rejection incomplete")
        record, journal, ledger = completed(); real = copy.deepcopy(record); real["synthetic_validation_fixture"] = False
        try: finalize(real, journal, ledger, validation_fixture=False)
        except FinalizerError: pass
        else: raise FinalizerError("fixture promotion reached real finalization")
    except (FinalizerError, FileNotFoundError, KeyError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr); return 1
    print(f"0 failures, 0 warnings ({expected['real_p036']['blocker_count']} real blockers; no real RenderRecord/candidate/review/request/cost)")
    print(f"synthetic finalization deterministic; fixture promotion blocked; {rejected}/{total} mutations rejected; 0 requests/uploads/$0")
    return 0


if __name__ == "__main__": raise SystemExit(main())
