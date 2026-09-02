"""Validate corrected CH05 final push record r2."""
from __future__ import annotations
import copy,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];EVIDENCE=ROOT/"docs/research/evidence/ch05-final-push-record-r2.json";EXPECTED=["GITIGNORE_RECOMMENDED.txt","assets/","batch_generate.py","benchmarks/","garden/","get_ipadapter.cmd","run_batch.cmd","run_comfy.cmd","trainer/"]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def errors(document):
    summary=document.get("summary",{});keys=("release_commands","release_domains","review_steps","review_links","candidates","plans","worksheet_checks","remaining_decisions","provider_calls","uploads","owner_decisions_ingested","visual_dispositions","accepted","commercially_cleared","executable","paid_spend_usd","human_review_minutes");expected=(9,18,9,134,29,50,112,10,0,0,0,0,0,0,0,0,None);out=[]
    if document.get("state")!="PASS_CORRECTED_FINAL_PUSH_OWNER_REVIEW_PENDING" or tuple(summary.get(key) for key in keys)!=expected:out.append("state invalid")
    source=document.get("source",{});failure=document.get("preserved_failed_attempt",{})
    if source.get("branch")!="main" or source.get("remote_parity") is not True or source.get("unrelated_untracked_items")!=EXPECTED or source.get("unrelated_untracked_count")!=9 or source.get("pending_r2_files")!=["src/north_garden/compile_ch05_final_push_record_r2.py","src/north_garden/validate_ch05_final_push_record_r2.py"] or failure.get("recorded_untracked_count")!=10 or "misclassified" not in failure.get("validator_failure",""):out.append("source/failure boundary invalid")
    if document.get("animation_shot_plan") is not None or document.get("e_conte") is not None:out.append("planning invalid")
    return out
def main():
    document=json.loads(EVIDENCE.read_text(encoding="utf-8"));failures=errors(document)
    for item in [document["supersedes"],*document["inputs"]]:
        path=ROOT/item["path"]
        if not path.is_file() or sha(path)!=item["sha256"]:failures.append(f"input invalid: {item['path']}")
    head=subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,check=True,capture_output=True,text=True).stdout.strip();origin=subprocess.run(["git","rev-parse","origin/main"],cwd=ROOT,check=True,capture_output=True,text=True).stdout.strip()
    if head!=origin or subprocess.run(["git","merge-base","--is-ancestor",document["source"]["recorded_commit"],head],cwd=ROOT).returncode:failures.append("lineage invalid")
    mutations=[lambda x:x.update(state="FAIL"),lambda x:x.update(animation_shot_plan={}),lambda x:x["source"].update(unrelated_untracked_count=10),lambda x:x["preserved_failed_attempt"].update(recorded_untracked_count=9)]+[lambda x,key=key:x["summary"].update({key:1 if key=="human_review_minutes" else -1}) for key in ("release_commands","release_domains","review_steps","review_links","candidates","plans","worksheet_checks","remaining_decisions","provider_calls","uploads","owner_decisions_ingested","visual_dispositions","accepted","commercially_cleared","executable","paid_spend_usd","human_review_minutes")];rejected=0
    for mutate in mutations:altered=copy.deepcopy(document);mutate(altered);rejected+=bool(errors(altered))
    if rejected!=len(mutations):failures.append(f"only {rejected}/{len(mutations)} mutations rejected")
    print(f"CH05 final push r2: {len(failures)} failures; r13 9/9/18; links134/candidates29/decisions10; r1 preserved; {rejected}/{len(mutations)} mutations rejected")
    for failure in failures:print(f"FAIL: {failure}")
    return 1 if failures else 0
if __name__=="__main__":raise SystemExit(main())
