"""Validate lifecycle application across all 12 CH05 batches."""
from __future__ import annotations
import copy,hashlib,json,subprocess
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]; EVIDENCE=ROOT/"docs/research/evidence/ch05-chapter-batch-lifecycle-application-r1.json"
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def errors(d):
    s=d.get("summary",{}); out=[]; expected=(50,12,11,11,1,11,1,2,5,4,7,8,49,0,0,0,0,0,0,0)
    actual=tuple(s.get(k) for k in ("plans","batches","lifecycle_states","legal_transitions","batches_entered","batches_not_entered","wave_1","wave_2","wave_3","wave_4","reusable_contracts","batch_specific_gates","planned_review_artifacts","prompts","renders","accepted","execution_ready_batches","provider_calls","uploads","paid_spend_usd"))
    if d.get("state")!="PASS_PLAN_ONLY" or actual!=expected: out.append("state/denominator invalid")
    if d.get("animation_shot_plan") is not None or d.get("e_conte") is not None: out.append("planning boundary invalid")
    return out
def main():
    d=json.loads(EVIDENCE.read_text(encoding="utf-8")); fail=errors(d)
    for x in [d["application"],*d["inputs"]]:
        p=ROOT/x["path"]
        if not p.is_file() or sha(p)!=x["sha256"]: fail.append(f"binding invalid: {x['path']}")
    app=json.loads((ROOT/d["application"]["path"]).read_text(encoding="utf-8")); rows=app.get("batches",[]); ids=[p for x in rows for p in x["panel_ids"]]
    if len(rows)!=12 or [x["sequence_id"] for x in rows]!=[f"seq{i:02d}" for i in range(1,13)] or len(ids)!=50 or len(set(ids))!=50: fail.append("batch/plan partition invalid")
    if [x["sequence_id"] for x in rows if x["lifecycle_current_state"]=="DRAFT_BLUEPRINTED"]!=["seq03"] or any(x["execution_ready"] or x["prompts"] or x["renders"] or x["accepted"] for x in rows): fail.append("lifecycle/activity fabricated")
    if any(len(x["reusable_contracts"])!=7 or len(x["batch_specific_gates"])!=8 for x in rows): fail.append("reuse boundary invalid")
    chart=ROOT/d["chart"]["path"]
    if not chart.is_file() or sha(chart)!=d["chart"]["sha256"] or list(Image.open(chart).size)!=[1900,1480] or subprocess.run(["git","check-ignore","-q",str(chart)],cwd=ROOT).returncode!=0: fail.append("chart invalid")
    muts=[lambda x:x.update(state="EXECUTABLE"),lambda x:x["summary"].update(plans=49),lambda x:x["summary"].update(batches=11),lambda x:x["summary"].update(lifecycle_states=10),lambda x:x["summary"].update(legal_transitions=10),lambda x:x["summary"].update(batches_entered=2),lambda x:x["summary"].update(batches_not_entered=10),lambda x:x["summary"].update(wave_1=2),lambda x:x["summary"].update(wave_2=1),lambda x:x["summary"].update(wave_3=4),lambda x:x["summary"].update(wave_4=5),lambda x:x["summary"].update(reusable_contracts=8),lambda x:x["summary"].update(batch_specific_gates=7),lambda x:x["summary"].update(planned_review_artifacts=48),lambda x:x["summary"].update(prompts=1),lambda x:x["summary"].update(renders=1),lambda x:x["summary"].update(accepted=1),lambda x:x["summary"].update(execution_ready_batches=1),lambda x:x["summary"].update(provider_calls=1),lambda x:x["summary"].update(uploads=1),lambda x:x["summary"].update(paid_spend_usd=1),lambda x:x.update(animation_shot_plan={})]
    rejected=0
    for mut in muts: y=copy.deepcopy(d); mut(y); rejected+=bool(errors(y))
    if rejected!=len(muts): fail.append(f"only {rejected}/{len(muts)} mutations rejected")
    print(f"CH05 batch lifecycle: {len(fail)} failures; 50 plans/12 batches; 1 entered/11 not; 49 artifacts; {rejected}/{len(muts)} mutations rejected")
    print("waves 1/2/5/4; reusable/batch-specific 7/8; prompts/renders/accepted/executable 0/0/0/0")
    for item in fail: print(f"FAIL: {item}")
    return 1 if fail else 0
if __name__=="__main__": raise SystemExit(main())
