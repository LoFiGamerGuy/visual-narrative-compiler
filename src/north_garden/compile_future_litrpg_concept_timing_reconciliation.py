"""Record the exact concept timing/reference reconciliation without rewriting historical evidence."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];SOURCE=ROOT/"docs/research/evidence/future-litrpg-visual-concepts-r1.json";INITIAL=ROOT/"docs/research/evidence/ch05-overnight-production-r1.json";HARD=ROOT/"docs/research/evidence/ch05-cadence-hardening-r1.json";OUTPUT=ROOT/"docs/research/evidence/future-litrpg-concept-timing-reconciliation-r1.json"
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def main()->int:
 d=json.loads(SOURCE.read_text(encoding="utf-8"));initial=json.loads(INITIAL.read_text(encoding="utf-8"));hard=json.loads(HARD.read_text(encoding="utf-8"));times=[c["execution"]["elapsed_seconds"] for c in d["candidates"]];refs=sum(len(c["references"]) for c in d["candidates"]);exact=round(sum(times),3);total=round(initial["generation_summary"]["total_elapsed_seconds"]+hard["summary"]["total_elapsed_seconds"]+exact,3)
 out={"record_type":"FutureLitRPGConceptTimingReconciliation","schema_version":"1.0","record_id":"ng-future-litrpg-concept-timing-reconciliation-r1","state":"EXACT_RECORD_TOTAL_SUPERSEDES_LEGACY_NARRATIVE_TOTAL","source":{"path":SOURCE.relative_to(ROOT).as_posix(),"sha256":sha(SOURCE)},"candidate_elapsed_seconds":times,"candidate_sum_seconds":exact,"batch_summary_seconds":d["summary"]["total_elapsed_seconds"],"candidate_reference_uses":refs,"aggregate":{"initial_ch05_seconds":initial["generation_summary"]["total_elapsed_seconds"],"hardening_seconds":hard["summary"]["total_elapsed_seconds"],"concept_seconds":exact,"exact_29_candidate_seconds":total,"exact_29_candidate_reference_uses":23+11+refs},"legacy_narrative":{"concept_seconds":155.766,"total_29_candidate_seconds":1385.824,"delta_seconds":round(155.766-exact,3)},"resolution":"Use exact candidate/batch evidence: 154.978 concept seconds, 1385.036 total seconds, and 39 reference uses. Preserve earlier 155.766/1385.824 prose as historical error with append-only correction; do not rewrite source evidence.","source_records_rewritten":0,"provider_calls":0,"uploads":0,"cost_usd":0,"human_review_minutes":None,"boundary":"Timing reconciliation only; no render, acceptance, canon, plan, or commercial state changes."}
 with OUTPUT.open("w",encoding="utf-8",newline="\n") as h:h.write(json.dumps(out,indent=2)+"\n")
 print(f"future LitRPG timing reconciliation: 3 records {times} = {exact}s; refs {refs}; exact 29 total {total}s/39 refs")
 print("legacy delta 0.788s recorded; source rewrites/calls/uploads/cost 0/0/0/$0")
 return 0
if __name__=="__main__":raise SystemExit(main())
