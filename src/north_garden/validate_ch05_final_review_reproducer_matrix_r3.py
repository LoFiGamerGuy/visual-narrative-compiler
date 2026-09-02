"""Validate and replay final CH05 review reproducer matrix r3."""
from __future__ import annotations
import copy,hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; EVIDENCE=ROOT/"docs/research/evidence/ch05-final-review-reproducer-matrix-r3.json"; NORMALIZED={"src/north_garden/validate_ch05_final_safe_source_parity_r4.py":"decimal tracked-path diagnostic only","src/north_garden/validate_tracked_source_scope.py":"decimal tracked-path diagnostic only"}
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def normalize(path,text):return re.sub(r"\d+ tracked safe-source paths","<LIVE_COUNT> tracked safe-source paths",text) if path in NORMALIZED else text
def errors(document):
    summary=document.get("summary",{}); keys=("domains","commands","passed","failed","normalized_live_diagnostics","network_capable_commands","candidates","plans","batches","review_links","priority_links","worksheet_checks","release_checks","safe_paths","zero_cost_milestones","frozen_paths","baseline_paths","provider_calls","uploads","owner_decisions_ingested","accepted","commercially_cleared","executable","paid_spend_usd","human_review_minutes"); expected=(10,10,10,0,2,0,29,50,12,134,67,112,84,934,82,16,4,0,0,0,0,0,0,0,None); out=[]
    if document.get("state")!="PASS" or tuple(summary.get(key) for key in keys)!=expected:out.append("state/denominator invalid")
    if len(document.get("results",[]))!=10 or any(row.get("return_code")!=0 or row.get("network_capable") is not False or row.get("stderr") for row in document.get("results",[])):out.append("results invalid")
    if [row["path"] for row in document.get("results",[]) if row.get("normalization") is not None]!=list(NORMALIZED):out.append("normalization scope invalid")
    if document.get("animation_shot_plan") is not None or document.get("e_conte") is not None:out.append("planning boundary invalid")
    return out
def main():
    document=json.loads(EVIDENCE.read_text(encoding="utf-8")); failures=errors(document)
    for item in document.get("results",[]):
        path=ROOT/item["path"]
        if not path.is_file() or sha(path)!=item["script_sha256"]:failures.append(f"script mismatch: {item['path']}");continue
        done=subprocess.run([sys.executable,str(path),*item.get("arguments",[])],cwd=ROOT,capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=1800); raw=done.stdout.replace("\r\n","\n").strip()+"\n"; stdout=normalize(item["path"],raw)
        if done.returncode!=0 or done.stderr.replace("\r\n","\n") or hashlib.sha256(stdout.encode()).hexdigest()!=item["stdout_sha256"]:failures.append(f"reproducer mismatch: {item['domain']}")
    mutations=[lambda x:x.update(state="FAIL"),lambda x:x.update(animation_shot_plan={}),lambda x:x["results"].pop(),lambda x:x["results"][0].update(normalization="broad")]+[lambda x,key=key:x["summary"].update({key:1 if key=="human_review_minutes" else -1}) for key in ("domains","commands","passed","failed","normalized_live_diagnostics","network_capable_commands","candidates","plans","batches","review_links","priority_links","worksheet_checks","release_checks","safe_paths","zero_cost_milestones","frozen_paths","baseline_paths","provider_calls","uploads","owner_decisions_ingested","accepted","commercially_cleared","executable","paid_spend_usd","human_review_minutes")]; rejected=0
    for mutate in mutations:altered=copy.deepcopy(document);mutate(altered);rejected+=bool(errors(altered))
    if rejected!=len(mutations):failures.append(f"only {rejected}/{len(mutations)} mutations rejected")
    print(f"CH05 final review reproducer r3: {len(failures)} failures; 10/10 domains; {rejected}/{len(mutations)} mutations rejected")
    for failure in failures:print(f"FAIL: {failure}")
    return 1 if failures else 0
if __name__=="__main__":raise SystemExit(main())
