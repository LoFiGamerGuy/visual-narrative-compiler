"""Validate append-only exact concept timing/reference reconciliation."""
from __future__ import annotations
import copy,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];EVIDENCE=ROOT/"docs/research/evidence/future-litrpg-concept-timing-reconciliation-r1.json"
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def errors(d:dict)->list[str]:
 out=[]
 if d.get("candidate_elapsed_seconds")!=[48.174,55.935,50.869] or (d.get("candidate_sum_seconds"),d.get("batch_summary_seconds"),d.get("candidate_reference_uses"))!=(154.978,154.978,5):out.append("concept exact totals invalid")
 a=d.get("aggregate",{});l=d.get("legacy_narrative",{})
 if (a.get("exact_29_candidate_seconds"),a.get("exact_29_candidate_reference_uses"))!=(1385.036,39) or (l.get("concept_seconds"),l.get("total_29_candidate_seconds"),l.get("delta_seconds"))!=(155.766,1385.824,0.788):out.append("aggregate/legacy reconciliation invalid")
 if any(d.get(k)!=0 for k in ("source_records_rewritten","provider_calls","uploads","cost_usd")) or d.get("human_review_minutes") is not None:out.append("activity fabricated")
 return out
def main()->int:
 d=json.loads(EVIDENCE.read_text(encoding="utf-8"));fail=errors(d);source=ROOT/d["source"]["path"]
 if not source.is_file() or sha(source)!=d["source"]["sha256"]:fail.append("source binding invalid")
 mutations=[lambda x:x.update(candidate_elapsed_seconds=[48.174,55.935,51.657]),lambda x:x.update(candidate_sum_seconds=155.766),lambda x:x.update(batch_summary_seconds=155.766),lambda x:x.update(candidate_reference_uses=4),lambda x:x["aggregate"].update(exact_29_candidate_seconds=1385.824),lambda x:x["aggregate"].update(exact_29_candidate_reference_uses=38),lambda x:x["legacy_narrative"].update(delta_seconds=0),lambda x:x.update(source_records_rewritten=1),lambda x:x.update(provider_calls=1),lambda x:x.update(uploads=1),lambda x:x.update(cost_usd=1),lambda x:x.update(human_review_minutes=1)]
 rejected=0
 for mutation in mutations:y=copy.deepcopy(d);mutation(y);rejected+=bool(errors(y))
 if rejected!=len(mutations):fail.append(f"only {rejected}/{len(mutations)} mutations rejected")
 print(f"future LitRPG timing reconciliation: {len(fail)} failures; 154.978s/5 refs; exact 29 total 1385.036s/39 refs; {rejected}/{len(mutations)} mutations rejected")
 print("legacy 0.788s delta retained; source rewrites/calls/uploads/cost 0/0/0/$0")
 for item in fail:print(f"FAIL: {item}")
 return 1 if fail else 0
if __name__=="__main__":raise SystemExit(main())
