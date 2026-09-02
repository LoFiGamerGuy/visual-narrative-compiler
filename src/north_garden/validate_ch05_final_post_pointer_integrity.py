"""Validate terminal CH05 post-pointer integrity record."""
from __future__ import annotations
import copy,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];EVIDENCE=ROOT/"docs/research/evidence/ch05-final-post-pointer-integrity-r1.json";SUMMARY=ROOT/"docs/research/ch05-final-post-pointer-integrity-r1.md";EXPECTED_UNTRACKED=["GITIGNORE_RECOMMENDED.txt","assets/","batch_generate.py","benchmarks/","garden/","get_ipadapter.cmd","run_batch.cmd","run_comfy.cmd","trainer/"]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def errors(document):
    summary=document.get("summary",{});keys=("release_commands","release_domains","pointer_steps","review_links","candidates","plans","worksheet_checks","safe_paths","frozen_paths","baseline_paths","provider_calls","uploads","owner_inputs","owner_decisions_ingested","visual_dispositions","accepted","commercially_cleared","executable","paid_spend_usd","human_review_minutes");expected=(9,18,9,134,29,50,112,971,16,4,0,0,0,0,0,0,0,0,0,None);out=[]
    if document.get("state")!="PASS_FINAL_DELIVERY_REMOTE_PARITY_OWNER_REVIEW_PENDING" or tuple(summary.get(key) for key in keys)!=expected:out.append("state/denominator invalid")
    source=document.get("source",{})
    if source.get("branch")!="main" or source.get("remote")!="https://github.com/LoFiGamerGuy/visual-narrative-compiler.git" or source.get("remote_parity") is not True or source.get("safe_capture_ancestor") is not True or source.get("frozen_integrity_pass") is not True or source.get("tracked_scope_pass") is not True or source.get("unrelated_untracked_items")!=EXPECTED_UNTRACKED or source.get("unrelated_untracked_items_count")!=9 or source.get("pending_integrity_files")!=["docs/research/ch05-final-post-pointer-integrity-r1.md","docs/research/evidence/ch05-final-post-pointer-integrity-r1.json","src/north_garden/compile_ch05_final_post_pointer_integrity.py","src/north_garden/validate_ch05_final_post_pointer_integrity.py"] or source.get("pending_integrity_files_count")!=4 or source.get("unrelated_items_tracked")!=0:out.append("source/boundary invalid")
    if document.get("animation_shot_plan") is not None or document.get("e_conte") is not None:out.append("planning boundary invalid")
    return out
def main():
    document=json.loads(EVIDENCE.read_text(encoding="utf-8"));failures=errors(document)
    for item in document["inputs"]:
        path=ROOT/item["path"]
        if not path.is_file() or sha(path)!=item["sha256"]:failures.append(f"input invalid: {item['path']}")
    if not SUMMARY.is_file():failures.append("summary missing")
    source=document["source"];head=subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,check=True,capture_output=True,text=True).stdout.strip();origin=subprocess.run(["git","rev-parse","origin/main"],cwd=ROOT,check=True,capture_output=True,text=True).stdout.strip()
    if head!=origin or subprocess.run(["git","merge-base","--is-ancestor",source["compile_head"],head],cwd=ROOT).returncode:failures.append("current remote lineage invalid")
    frozen=subprocess.run([sys.executable,"src/north_garden/validate_frozen_gauntlet_baseline_integrity.py"],cwd=ROOT,capture_output=True,text=True);scope=subprocess.run([sys.executable,"src/north_garden/validate_tracked_source_scope.py"],cwd=ROOT,capture_output=True,text=True)
    if frozen.returncode or scope.returncode:failures.append("current integrity command failed")
    mutations=[lambda x:x.update(state="FAIL"),lambda x:x.update(animation_shot_plan={}),lambda x:x["source"].update(remote_parity=False),lambda x:x["source"].update(unrelated_items_tracked=1)]+[lambda x,key=key:x["summary"].update({key:1 if key=="human_review_minutes" else -1}) for key in ("release_commands","release_domains","pointer_steps","review_links","candidates","plans","worksheet_checks","safe_paths","frozen_paths","baseline_paths","provider_calls","uploads","owner_inputs","owner_decisions_ingested","visual_dispositions","accepted","commercially_cleared","executable","paid_spend_usd","human_review_minutes")];rejected=0
    for mutate in mutations:altered=copy.deepcopy(document);mutate(altered);rejected+=bool(errors(altered))
    if rejected!=len(mutations):failures.append(f"only {rejected}/{len(mutations)} mutations rejected")
    print(f"CH05 final integrity: {len(failures)} failures; r13 9/9/18; pointer9/links134; source/frozen/scope/parity pass; {rejected}/{len(mutations)} mutations rejected")
    for failure in failures:print(f"FAIL: {failure}")
    return 1 if failures else 0
if __name__=="__main__":raise SystemExit(main())
