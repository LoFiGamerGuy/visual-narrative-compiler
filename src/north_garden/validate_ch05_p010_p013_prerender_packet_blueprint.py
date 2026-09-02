"""Validate P010-P013 pre-render packet blueprint and dry-run builder."""
from __future__ import annotations
import copy,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; EVIDENCE=ROOT/"docs/research/evidence/ch05-p010-p013-prerender-packet-blueprint-r1.json"
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def errors(d):
    s=d.get("summary",{}); out=[]; expected=(4,0,4,5,0,11,44,4,4,4,2,0,0,0,0)
    actual=tuple(s.get(k) for k in ("candidate_slots","candidates_present","candidates_missing","artifacts_planned","artifacts_built","checks_per_candidate","total_empty_candidate_checks","proposed_safe_zones","phone_previews_planned","density_targets","repair_slots","provider_calls","uploads","renders","paid_spend_usd"))
    if d.get("state")!="PASS_NOT_BUILT" or actual!=expected: out.append("state/denominator invalid")
    if d.get("animation_shot_plan") is not None or d.get("e_conte") is not None: out.append("planning boundary invalid")
    return out
def main():
    d=json.loads(EVIDENCE.read_text(encoding="utf-8")); fail=errors(d)
    for x in [d["blueprint"],*d["inputs"]]:
        p=ROOT/x["path"]
        if not p.is_file() or sha(p)!=x["sha256"]: fail.append(f"binding invalid: {x['path']}")
    b=json.loads((ROOT/d["blueprint"]["path"]).read_text(encoding="utf-8")); slots=b.get("candidate_slots",[]); artifacts=b.get("artifacts",[]); activity=b.get("activity",{})
    if len(slots)!=4 or any(x["candidate_exists"] or x["output_sha256"] is not None or any(v is not None for v in x["review_values"].values()) or x["decision"] is not None for x in slots): fail.append("candidate state fabricated")
    if len(artifacts)!=5 or any(x["state"]!="NOT_BUILT" or x["sha256"] is not None or x["dimensions"] is not None for x in artifacts): fail.append("artifact state fabricated")
    if len(b.get("failure_vocabulary",[]))!=11 or len(b.get("renderrecord_required_fields",[]))!=16 or b.get("builder",{}).get("network_capable") is not False: fail.append("review/builder contract invalid")
    if any(activity.get(k)!=0 for k in ("prompts_compiled","provider_calls","uploads","renders","accepted","commercially_cleared","executable")) or activity.get("human_review_minutes") is not None: fail.append("activity fabricated")
    builder=ROOT/"src/north_garden/build_ch05_p010_p013_review_packet.py"; done=subprocess.run([sys.executable,str(builder),"--dry-run"],cwd=ROOT,capture_output=True,text=True,encoding="utf-8"); stdout=done.stdout.replace("\r\n","\n").strip()+"\n"
    if done.returncode!=0 or done.stderr or hashlib.sha256(stdout.encode()).hexdigest()!=d["builder_dry_run"]["stdout_sha256"]: fail.append("builder dry-run mismatch")
    muts=[lambda x:x.update(state="PASS_BUILT"),lambda x:x["summary"].update(candidate_slots=3),lambda x:x["summary"].update(candidates_present=1),lambda x:x["summary"].update(candidates_missing=3),lambda x:x["summary"].update(artifacts_planned=4),lambda x:x["summary"].update(artifacts_built=1),lambda x:x["summary"].update(checks_per_candidate=10),lambda x:x["summary"].update(total_empty_candidate_checks=43),lambda x:x["summary"].update(proposed_safe_zones=3),lambda x:x["summary"].update(phone_previews_planned=3),lambda x:x["summary"].update(density_targets=3),lambda x:x["summary"].update(repair_slots=3),lambda x:x["summary"].update(provider_calls=1),lambda x:x["summary"].update(uploads=1),lambda x:x["summary"].update(renders=1),lambda x:x["summary"].update(paid_spend_usd=1),lambda x:x.update(animation_shot_plan={})]
    rejected=0
    for mut in muts: y=copy.deepcopy(d); mut(y); rejected+=bool(errors(y))
    if rejected!=len(muts): fail.append(f"only {rejected}/{len(muts)} mutations rejected")
    print(f"P010-P013 prerender packet: {len(fail)} failures; 4 missing/5 NOT_BUILT/44 empty checks/4 zones; {rejected}/{len(muts)} mutations rejected")
    print("builder dry-run no-write pass; prompts/provider/uploads/renders/acceptance 0/0/0/0/0")
    for item in fail: print(f"FAIL: {item}")
    return 1 if fail else 0
if __name__=="__main__": raise SystemExit(main())
