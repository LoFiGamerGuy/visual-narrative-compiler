"""Validate append-only CH05 review-link manifest r7."""
from __future__ import annotations
import copy,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; EVIDENCE=ROOT/"docs/research/evidence/ch05-review-artifact-link-manifest-r7.json"; BASE=ROOT/"production/comic/review/ch05-review-artifact-link-manifest-r6.json"; EXPECTED={"review_hubs":10,"contact_sheets":10,"sequence_packets":9,"lettering_overlays":34,"strongest_candidates":14,"noncanon_litrpg_concepts":3,"diagnostic_and_policy_sheets":18,"packet_records":24,"review_checklists":12}
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def errors(document):
    summary=document.get("summary",{}); keys=("added_artifacts","effective_unique_artifacts","categorized_links","ignored_local_artifacts","tracked_metadata_links","strongest_candidates","worksheet_checks","owner_dispositions","owner_decisions_ingested","accepted","commercially_cleared","executable","provider_calls","uploads","cost_usd","human_review_minutes"); expected=(6,134,134,111,23,14,112,0,0,0,0,0,0,0,0,None); out=[]
    if document.get("state")!="PASS_OWNER_DISPOSITIONS_ABSENT" or tuple(summary.get(key) for key in keys)!=expected or document.get("category_counts")!=EXPECTED:out.append("state/denominator invalid")
    return out
def main():
    document=json.loads(EVIDENCE.read_text(encoding="utf-8")); failures=errors(document); manifest_path=ROOT/document["manifest"]["path"]; markdown_path=ROOT/document["markdown"]["path"]
    if not manifest_path.is_file() or sha(manifest_path)!=document["manifest"]["sha256"] or not markdown_path.is_file() or sha(markdown_path)!=document["markdown"]["sha256"]:failures.append("output binding invalid"); manifest={}
    else:manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
    base=json.loads(BASE.read_text(encoding="utf-8")); effective={item["path"]:item for item in manifest.get("artifacts",[])}
    if sha(BASE)!=document["extends"]["sha256"] or len(effective)!=134 or any(path not in effective or any(effective[path].get(key)!=item.get(key) for key in ("absolute_path","sha256","bytes","categories")) for path,item in {row["path"]:row for row in base["artifacts"]}.items()):failures.append("base lineage invalid")
    markdown=markdown_path.read_text(encoding="utf-8") if markdown_path.is_file() else ""
    for item in manifest.get("artifacts",[]):
        path=ROOT/item["path"]; ignored=subprocess.run(["git","check-ignore","-q",str(path)],cwd=ROOT).returncode==0; tracked=subprocess.run(["git","ls-files","--error-unmatch",path.relative_to(ROOT).as_posix()],cwd=ROOT,capture_output=True).returncode==0; expected_state="IGNORED_LOCAL" if ignored else "TRACKED_METADATA" if tracked else "UNBOUND"
        if not path.is_file() or sha(path)!=item["sha256"] or item["git_state"]!=expected_state or expected_state=="UNBOUND" or f"]({item['absolute_path']})" not in markdown:failures.append(f"artifact/state invalid: {item['path']}")
    if markdown.count("\n- [")!=134:failures.append("Markdown denominator invalid")
    mutations=[lambda x:x.update(state="FAIL")]+[lambda x,key=key:x["summary"].update({key:1 if key=="human_review_minutes" else -1}) for key in ("added_artifacts","effective_unique_artifacts","categorized_links","ignored_local_artifacts","tracked_metadata_links","strongest_candidates","worksheet_checks","owner_dispositions","owner_decisions_ingested","accepted","commercially_cleared","executable","provider_calls","uploads","cost_usd","human_review_minutes")]+[lambda x:x["category_counts"].update(review_hubs=9),lambda x:x["category_counts"].update(review_checklists=11)]; rejected=0
    for mutate in mutations:altered=copy.deepcopy(document);mutate(altered);rejected+=bool(errors(altered))
    if rejected!=len(mutations):failures.append(f"only {rejected}/{len(mutations)} mutations rejected")
    print(f"CH05 review links r7: {len(failures)} failures; 134=128+6 / 111 ignored + 23 tracked; {rejected}/{len(mutations)} mutations rejected")
    for failure in failures:print(f"FAIL: {failure}")
    return 1 if failures else 0
if __name__=="__main__":raise SystemExit(main())
