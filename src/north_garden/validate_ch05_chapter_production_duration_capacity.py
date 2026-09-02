"""Validate measured CH05 generation-only duration capacity."""
from __future__ import annotations
import copy,hashlib,json,subprocess
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]; EVIDENCE=ROOT/"docs/research/evidence/ch05-chapter-production-duration-capacity-r1.json"
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def errors(d):
    s=d.get("summary",{}); out=[]; expected=(50,12,36,13,49,68,6,12,20,11,0,0,0,0)
    actual=tuple(s.get(k) for k in ("plans","batches","remaining_initial_candidates","bounded_repair_slots","planning_candidates","fresh_arm_candidates","wave_1_candidates","wave_2_candidates","wave_3_candidates","wave_4_candidates","executed_candidates","provider_calls","uploads","paid_spend_usd"))
    if d.get("state")!="PASS_NONEXECUTABLE" or actual!=expected or s.get("human_review_minutes") is not None or s.get("built_in_monetary_cost_usd") is not None: out.append("state/denominator invalid")
    if d.get("animation_shot_plan") is not None or d.get("e_conte") is not None: out.append("planning boundary invalid")
    return out
def main():
    d=json.loads(EVIDENCE.read_text(encoding="utf-8")); fail=errors(d)
    for x in [d["capacity"],*d["inputs"]]:
        p=ROOT/x["path"]
        if not p.is_file() or sha(p)!=x["sha256"]: fail.append(f"binding invalid: {x['path']}")
    c=json.loads((ROOT/d["capacity"]["path"]).read_text(encoding="utf-8")); rows=c.get("batches",[]); waves=c.get("waves",[])
    if len(rows)!=12 or sum(x["remaining_initial_candidates"] for x in rows)!=36 or sum(x["bounded_repair_slots"] for x in rows)!=13 or sum(x["planning_candidate_count"] for x in rows)!=49: fail.append("batch allocation invalid")
    if len(waves)!=4 or sum(x["candidate_count"] for x in waves)!=49 or any(x["executed"] or x["monetary_cost_usd"] is not None or x["human_review_minutes"] is not None for x in waves): fail.append("wave state invalid")
    if c["remaining_plan_envelope"]["duration_seconds"]!={"p10":1496.019,"median":2510.123,"p90":2769.676} or c["fresh_chapter_consistency_arm"]["duration_seconds"]!={"p10":2076.108,"median":3483.436,"p90":3843.632}: fail.append("duration arithmetic invalid")
    if len(c.get("limitations",[]))!=6 or any(c["activity"].get(k)!=0 for k in ("prompts","renders","provider_calls","uploads","accepted","executable")): fail.append("boundary/activity invalid")
    chart=ROOT/d["chart"]["path"]
    if not chart.is_file() or sha(chart)!=d["chart"]["sha256"] or list(Image.open(chart).size)!=[1800,1580] or subprocess.run(["git","check-ignore","-q",str(chart)],cwd=ROOT).returncode: fail.append("chart invalid")
    muts=[lambda x:x.update(state="EXECUTED"),lambda x:x["summary"].update(plans=49),lambda x:x["summary"].update(batches=11),lambda x:x["summary"].update(remaining_initial_candidates=35),lambda x:x["summary"].update(bounded_repair_slots=12),lambda x:x["summary"].update(planning_candidates=48),lambda x:x["summary"].update(fresh_arm_candidates=67),lambda x:x["summary"].update(wave_1_candidates=5),lambda x:x["summary"].update(wave_2_candidates=13),lambda x:x["summary"].update(wave_3_candidates=19),lambda x:x["summary"].update(wave_4_candidates=10),lambda x:x["summary"].update(executed_candidates=1),lambda x:x["summary"].update(provider_calls=1),lambda x:x["summary"].update(uploads=1),lambda x:x["summary"].update(paid_spend_usd=1),lambda x:x["summary"].update(human_review_minutes=1),lambda x:x["summary"].update(built_in_monetary_cost_usd=1),lambda x:x.update(animation_shot_plan={})]
    rejected=0
    for mut in muts: y=copy.deepcopy(d); mut(y); rejected+=bool(errors(y))
    if rejected!=len(muts): fail.append(f"only {rejected}/{len(muts)} mutations rejected")
    print(f"CH05 duration capacity: {len(fail)} failures; 36+13=49 / fresh 68; waves 6/12/20/11; {rejected}/{len(muts)} mutations rejected")
    print("median remaining/fresh 2510.123/3483.436s; cost/review minutes null; executed/provider 0/0")
    for item in fail: print(f"FAIL: {item}")
    return 1 if fail else 0
if __name__=="__main__": raise SystemExit(main())
