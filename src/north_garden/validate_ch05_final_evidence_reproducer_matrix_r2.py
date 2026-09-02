"""Validate and reproduce the compact current CH05 evidence matrix r2."""
from __future__ import annotations
import copy,hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; EVIDENCE=ROOT/"docs/research/evidence/ch05-final-evidence-reproducer-matrix-r2.json"
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def norm(domain,text): return re.sub(r"\d+ tracked safe-source paths","<TRACKED_COUNT> tracked safe-source paths",text) if domain in {"safe_source_capture_r2","current_tracked_scope"} else text
def errors(d):
    out=[]; s=d.get("summary",{}); state=d.get("effective_state",{}); domains=d.get("required_domains",[]); results=d.get("results",[]); expected_domains=["integrated_release_r10","delivery_bundle_r2","safe_source_capture_r2","frozen_gauntlet_baseline","current_tracked_scope","zero_cost_ledger_r27","remote_lineage_r2"]
    if d.get("state")!="PASS" or domains!=expected_domains or tuple(s.get(k) for k in ("command_count","domain_count","passed","failed","release_effective_checks","tracked_count_only_normalizations"))!=(7,7,7,0,66,2): out.append("denominator/state invalid")
    if any(s.get(k)!=0 for k in ("network_capable_commands","provider_calls","uploads","downloads","paid_spend_usd","accepted_candidates","executable_panels","owner_decisions")) or s.get("human_review_minutes") is not None: out.append("activity/promotion invalid")
    if len(results)!=7 or [x.get("domain") for x in results]!=expected_domains or any(x.get("return_code")!=0 or x.get("network_capable") is not False or x.get("stderr") for x in results): out.append("results invalid")
    if [x.get("domain") for x in results if x.get("normalization")=="TRACKED_COUNT_ONLY"]!=["safe_source_capture_r2","current_tracked_scope"]: out.append("normalization scope invalid")
    if state!={"candidates":29,"comic_panel_plans":50,"review_links":117,"safe_source_capture_paths":835,"frozen_paths":16,"baseline_paths":4,"zero_cost_milestones":68,"remote_lineage_pass":True}: out.append("effective state invalid")
    if d.get("base_remote_parity") is not True or d.get("animation_shot_plan") is not None or d.get("e_conte") is not None: out.append("lineage/planning invalid")
    return sorted(set(out))
def main():
    d=json.loads(EVIDENCE.read_text(encoding="utf-8")); fail=errors(d)
    for item in d.get("inputs",[]):
        p=ROOT/item["path"]
        if not p.is_file() or sha(p)!=item["sha256"]: fail.append(f"input mismatch: {item['path']}")
    for item in d.get("results",[]):
        p=ROOT/item["path"]
        if not p.is_file() or sha(p)!=item["script_sha256"]: fail.append(f"script mismatch: {item['domain']}"); continue
        done=subprocess.run([sys.executable,str(p),*item.get("arguments",[])],cwd=ROOT,capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=600); stdout=done.stdout.replace("\r\n","\n").strip()+"\n"; normalized=norm(item["domain"],stdout)
        if done.returncode!=0 or done.stderr.replace("\r\n","\n") or hashlib.sha256(normalized.encode()).hexdigest()!=item["normalized_stdout_sha256"]: fail.append(f"reproducer mismatch: {item['domain']}")
    muts=[lambda x:x.update(state="FAIL"),lambda x:x.update(base_remote_parity=False)]+[lambda x,k=k:x["summary"].update({k:-1}) for k in ("command_count","domain_count","passed","failed","release_effective_checks","tracked_count_only_normalizations","provider_calls","uploads","paid_spend_usd","accepted_candidates","owner_decisions")]+[lambda x:x["summary"].update(human_review_minutes=1),lambda x:x["required_domains"].pop(),lambda x:x["results"].pop(),lambda x:x["results"][0].update(normalization="TRACKED_COUNT_ONLY")]+[lambda x,k=k:x["effective_state"].update({k:-1}) for k in ("candidates","review_links","safe_source_capture_paths","frozen_paths","zero_cost_milestones")]+[lambda x:x.update(animation_shot_plan={})]
    rejected=0
    for mut in muts: y=copy.deepcopy(d); mut(y); rejected+=bool(errors(y))
    if rejected!=len(muts): fail.append(f"only {rejected}/{len(muts)} mutations rejected")
    print(f"CH05 final reproducer matrix r2: {len(fail)} failures; 7/7 domains; release 66 checks; {rejected}/{len(muts)} mutations rejected")
    print("29 candidates/50 plans/117 links/835 captured paths/frozen 16+baseline 4/68 zero-cost milestones; 0 provider/promotion activity")
    for item in fail: print(f"FAIL: {item}")
    return 1 if fail else 0
if __name__=="__main__": raise SystemExit(main())
