"""Validate append-only CH05 cost ledger r31."""
from __future__ import annotations

import argparse, copy, hashlib, json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]; LEDGER = ROOT / "docs/research/evidence/ch05-production-cost-ledger-r31.json"; PRIOR = ROOT / "docs/research/evidence/ch05-production-cost-ledger-r30.json"
def sha256(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()
def validate(doc: dict[str, Any]) -> list[str]:
    errors=[]; check=lambda c,m: None if c else errors.append(m); prior=json.loads(PRIOR.read_text(encoding="utf-8")); rows=doc.get("local_zero_external_cost_evidence", [])
    check(doc.get("record_type")=="ProductionCostLedger" and doc.get("record_id")=="ng-ch05-production-cost-ledger-r31", "identity")
    check(doc.get("supersedes")=={"record_id":prior["record_id"],"path":PRIOR.relative_to(ROOT).as_posix(),"sha256":sha256(PRIOR)}, "supersedes")
    check(rows[:len(prior["local_zero_external_cost_evidence"])]==prior["local_zero_external_cost_evidence"], "append-only prefix")
    check(len(rows)==98 and doc.get("revision_summary")=={"prior_local_milestones":91,"appended_local_milestones":7,"total_local_milestones":98,"external_requests":0,"external_uploads":0,"external_cost_usd":"0.000000"}, "summary")
    activity=doc.get("built_in_product_activity", {}); check((activity.get("sequence_tool_calls"),activity.get("raster_outputs"),activity.get("comic_panel_plan_crops"),activity.get("authorized_reference_uses"),activity.get("overlap_adjusted_tool_call_wall_seconds"))==(11,11,50,23,954.3), "built-in counts")
    check(all(activity.get(k) is None for k in ("model","endpoint","provider_request_ids","usage","monetary_cost_usd","deterministic_seed")), "unavailable fields")
    check(doc.get("committed_actual_cost_usd")=="0.000000" and doc.get("approved_aggregate_cap_usd") is None, "paid domain")
    return errors
def self_test(doc):
    muts=[lambda d:d.__setitem__("record_id","bad"),lambda d:d["supersedes"].__setitem__("sha256","0"*64),lambda d:d["local_zero_external_cost_evidence"].pop(0),lambda d:d["revision_summary"].__setitem__("total_local_milestones",97),lambda d:d["built_in_product_activity"].__setitem__("sequence_tool_calls",50),lambda d:d["built_in_product_activity"].__setitem__("monetary_cost_usd",0),lambda d:d.__setitem__("committed_actual_cost_usd","1.000000")]; caught=0
    for m in muts: c=copy.deepcopy(doc);m(c);caught+=bool(validate(c))
    return caught,len(muts)
def main():
    p=argparse.ArgumentParser();p.add_argument("--self-test",action="store_true");a=p.parse_args();d=json.loads(LEDGER.read_text(encoding="utf-8"));e=validate(d);c=t=0
    if a.self_test:c,t=self_test(d);e+=[] if c==t else [f"self-test {c}/{t}"]
    print(json.dumps({"status":"PASS" if not e else "FAIL","errors":e,"self_test":f"{c}/{t}" if a.self_test else None},sort_keys=True));return 0 if not e else 1
if __name__=="__main__":raise SystemExit(main())
