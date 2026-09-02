"""Validate Tier-A hypotheses, observed effort scenarios, and empty owner decision intake."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HYPOTHESES = ROOT / "production/comic/coverage/ch05-tier-a-production-hypotheses-r1.json"
DECISIONS = ROOT / "production/comic/review/ch05-owner-decision-contract-r1.json"
EVIDENCE = ROOT / "docs/research/evidence/ch05-tier-a-effort-scenarios-r1.json"


def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()
def canonical_sha(value: object) -> str: return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def semantic_errors(h: dict, d: dict, e: dict) -> list[str]:
    out = []
    hs = h.get("summary", {}); ds = d.get("summary", {}); activity = e.get("activity", {})
    if tuple(hs.get(field) for field in ("tier_a_plans", "provisional_style_assignments", "prompts", "final_copy_bound", "owner_style_approvals", "owner_generation_authorities", "production_executable")) != (12, 12, 0, 0, 0, 0, 0): out.append("hypothesis denominator/promotion invalid")
    rows = h.get("rows", [])
    if len(rows) != 12 or len({row.get("panel_id") for row in rows}) != 12 or h.get("row_root_sha256") != canonical_sha(rows): out.append("hypothesis rows/root invalid")
    if any(row.get("prompt") is not None or row.get("final_copy") is not None or row.get("owner_style_approval") is not False or row.get("owner_generation_authority") is not False or row.get("production_executable") is not False for row in rows): out.append("row execution/prompt fabricated")
    if (ds.get("subject_count"), ds.get("ch05_candidate_subjects"), ds.get("noncanon_concept_subjects"), ds.get("higher_order_subjects"), ds.get("completed_decisions"), ds.get("events")) != (39, 26, 3, 10, 0, 0): out.append("decision denominator/state invalid")
    if ds.get("human_review_minutes") is not None or ds.get("accepted_production_candidates") != 0: out.append("decision review/acceptance fabricated")
    subjects = d.get("subjects", [])
    if len(subjects) != 39 or len({item.get("subject_id") for item in subjects}) != 39 or any(item.get("decision") is not None or item.get("reviewer") is not None or item.get("human_review_minutes") is not None for item in subjects): out.append("decision subject state invalid")
    if d.get("event_contract", {}).get("events") != []: out.append("decision event fabricated")
    if e.get("observed_basis", {}).get("candidate_count") != 26 or e.get("observed_basis", {}).get("generation_seconds") != 1230.058: out.append("observed basis invalid")
    if [x.get("candidate_count") for x in e.get("scenarios", [])] != [12, 16, 24] or any(x.get("monetary_cost_usd") is not None or x.get("human_review_minutes") is not None or x.get("executed") is not False for x in e.get("scenarios", [])): out.append("scenario boundary invalid")
    if any(activity.get(field) != 0 for field in ("prompts_created", "provider_calls", "uploads", "cost_usd", "owner_decisions_recorded")) or activity.get("human_review_minutes") is not None: out.append("activity fabricated")
    return sorted(set(out))


def main() -> int:
    h=json.loads(HYPOTHESES.read_text(encoding="utf-8"));d=json.loads(DECISIONS.read_text(encoding="utf-8"));e=json.loads(EVIDENCE.read_text(encoding="utf-8"))
    failures=semantic_errors(h,d,e)
    if sha(HYPOTHESES)!=e["hypotheses"]["sha256"] or sha(DECISIONS)!=e["decision_contract"]["sha256"]: failures.append("evidence binding mismatch")
    mutations=[
        lambda h,d,e:h["summary"].update(tier_a_plans=11),lambda h,d,e:h["summary"].update(prompts=1),lambda h,d,e:h["rows"].pop(),
        lambda h,d,e:h["rows"][0].update(prompt="fabricated"),lambda h,d,e:h["rows"][0].update(owner_generation_authority=True),
        lambda h,d,e:d["summary"].update(subject_count=38),lambda h,d,e:d["summary"].update(completed_decisions=1),lambda h,d,e:d["subjects"][0].update(decision="ACCEPT"),
        lambda h,d,e:d["event_contract"]["events"].append({}),lambda h,d,e:e["observed_basis"].update(candidate_count=25),
        lambda h,d,e:e["scenarios"][0].update(monetary_cost_usd=0),lambda h,d,e:e["scenarios"][0].update(executed=True),lambda h,d,e:e["activity"].update(provider_calls=1)
    ]
    rejected=0
    for mutation in mutations:
        hc,dc,ec=copy.deepcopy(h),copy.deepcopy(d),copy.deepcopy(e);mutation(hc,dc,ec);rejected+=bool(semantic_errors(hc,dc,ec))
    if rejected!=len(mutations):failures.append(f"only {rejected}/{len(mutations)} mutations rejected")
    print(f"CH05 Tier A effort/decision contract: {len(failures)} failures; 12 plans/3 scenarios/39 pending subjects; {rejected}/{len(mutations)} mutations rejected")
    print("26-candidate/1230.058s observed basis; cost/human time null; 0 prompts/decisions/executable/calls/uploads/$0")
    for failure in failures:print(f"FAIL: {failure}")
    return 1 if failures else 0


if __name__=="__main__":raise SystemExit(main())
