"""Validate the synthetic, read-only CH05 owner-decision draft-validator evidence."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "docs/research/evidence/ch05-owner-decision-draft-validator-r1.json"
CONTRACT = ROOT / "production/comic/review/ch05-owner-decision-contract-r1.json"


def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()


def errors(data: dict) -> list[str]:
    out=[]; matrix=data.get("fixture_matrix",{}); activity=data.get("activity",{}); contract=data.get("contract",{})
    if (matrix.get("valid_fixture_count"),matrix.get("negative_fixture_count"),matrix.get("negative_rejected"))!=(3,14,14):out.append("fixture denominators invalid")
    if any(item.get("result")!="ACCEPT_AS_LOCAL_DRAFT" for item in matrix.get("valid_results",[])):out.append("valid fixture rejected")
    if any(item.get("result")!="REJECT" or item.get("failure_count",0)<1 for item in matrix.get("negative_results",[])):out.append("negative fixture accepted")
    if any(activity.get(k)!=0 for k in ("owner_drafts_read","events_created","contract_writes","plan_revisions","provider_calls","uploads","external_cost_usd")):out.append("activity fabricated")
    if (contract.get("subject_count"),contract.get("completed_decisions"),contract.get("events"),contract.get("human_review_minutes"))!=(39,0,0,None):out.append("contract summary invalid")
    return out


def main()->int:
    data=json.loads(EVIDENCE.read_text(encoding="utf-8")); contract=json.loads(CONTRACT.read_text(encoding="utf-8")); fail=errors(data)
    if data["contract"]["sha256"]!=sha(CONTRACT) or contract["event_contract"]["events"]!=[] or contract["summary"]["completed_decisions"]!=0:fail.append("live contract binding/state invalid")
    validator=ROOT/data["validator"]["path"]
    if not validator.is_file() or sha(validator)!=data["validator"]["sha256"]:fail.append("validator binding invalid")
    mutations=[lambda x:x["fixture_matrix"].update(valid_fixture_count=2),lambda x:x["fixture_matrix"].update(negative_fixture_count=13),lambda x:x["fixture_matrix"].update(negative_rejected=13),lambda x:x["fixture_matrix"]["valid_results"][0].update(result="REJECT"),lambda x:x["fixture_matrix"]["negative_results"][0].update(result="ACCEPT"),lambda x:x["fixture_matrix"]["negative_results"][0].update(failure_count=0),lambda x:x["activity"].update(owner_drafts_read=1),lambda x:x["activity"].update(events_created=1),lambda x:x["activity"].update(contract_writes=1),lambda x:x["activity"].update(plan_revisions=1),lambda x:x["activity"].update(provider_calls=1),lambda x:x["activity"].update(uploads=1),lambda x:x["activity"].update(external_cost_usd=1),lambda x:x["contract"].update(completed_decisions=1),lambda x:x["contract"].update(events=1),lambda x:x["contract"].update(human_review_minutes=1)]
    rejected=0
    for mutation in mutations:
        changed=copy.deepcopy(data);mutation(changed);rejected+=bool(errors(changed))
    if rejected!=len(mutations):fail.append(f"only {rejected}/{len(mutations)} mutations rejected")
    print(f"CH05 owner decision draft-validator evidence: {len(fail)} failures; 3 valid fixtures / 14 negative rejected; {rejected}/{len(mutations)} mutations rejected")
    print("contract unchanged: 39 pending / 0 decisions / 0 events / null minutes; activity 0")
    for item in fail:print(f"FAIL: {item}")
    return 1 if fail else 0


if __name__=="__main__":raise SystemExit(main())
