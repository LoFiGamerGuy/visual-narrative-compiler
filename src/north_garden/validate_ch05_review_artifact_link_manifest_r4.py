"""Validate append-only CH05 review-link manifest r4."""
from __future__ import annotations
import copy,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; EVIDENCE=ROOT/"docs/research/evidence/ch05-review-artifact-link-manifest-r4.json"; BASE=ROOT/"production/comic/review/ch05-review-artifact-link-manifest-r3.json"
EXPECTED={"review_hubs":7,"contact_sheets":10,"sequence_packets":9,"lettering_overlays":34,"strongest_candidates":14,"noncanon_litrpg_concepts":3,"diagnostic_and_policy_sheets":17,"packet_records":19,"review_checklists":4}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def errors(d):
    s=d.get("summary",{}); out=[]; expected=(5,117,117,108,9,0,0,0,0,0,0)
    actual=tuple(s.get(k) for k in ("added_artifacts","effective_unique_artifacts","categorized_links","ignored_local_artifacts","tracked_metadata_links","owner_decisions","accepted_candidates","executable_panels","provider_calls","uploads","cost_usd"))
    if d.get("state")!="PASS_OWNER_PENDING" or actual!=expected or d.get("category_counts")!=EXPECTED or s.get("human_review_minutes") is not None: out.append("state/denominator invalid")
    return out
def main():
    d=json.loads(EVIDENCE.read_text(encoding="utf-8")); fail=errors(d); mp=ROOT/d["manifest"]["path"]; md=ROOT/d["markdown"]["path"]
    if not mp.is_file() or sha(mp)!=d["manifest"]["sha256"] or not md.is_file() or sha(md)!=d["markdown"]["sha256"]: fail.append("output binding invalid"); m={}
    else: m=json.loads(mp.read_text(encoding="utf-8"))
    if sha(BASE)!=d["extends"]["sha256"]: fail.append("r3 binding invalid")
    base=json.loads(BASE.read_text(encoding="utf-8")); effective={x["path"]:x for x in m.get("artifacts",[])}
    if len(effective)!=117 or any(path not in effective or any(effective[path].get(k)!=item.get(k) for k in ("absolute_path","sha256","bytes","categories")) for path,item in {x["path"]:x for x in base["artifacts"]}.items()): fail.append("base lineage invalid")
    markdown=md.read_text(encoding="utf-8") if md.is_file() else ""
    for item in m.get("artifacts",[]):
        p=ROOT/item["path"]
        if not p.is_file() or sha(p)!=item["sha256"] or p.stat().st_size!=item["bytes"] or p.resolve().as_posix()!=item["absolute_path"]: fail.append(f"artifact invalid: {item['path']}"); continue
        ignored=subprocess.run(["git","check-ignore","-q",str(p)],cwd=ROOT).returncode==0; tracked=subprocess.run(["git","ls-files","--error-unmatch",p.relative_to(ROOT).as_posix()],cwd=ROOT,capture_output=True).returncode==0; expected="IGNORED_LOCAL" if ignored else "TRACKED_METADATA" if tracked else "UNBOUND"
        if item["git_state"]!=expected or expected=="UNBOUND" or f"]({item['absolute_path']})" not in markdown: fail.append(f"state/link invalid: {item['path']}")
    if markdown.count("\n- [")!=117: fail.append("Markdown denominator invalid")
    muts=[lambda x:x.update(state="FAIL")]+[lambda x,k=k:x["summary"].update({k:-1}) for k in ("added_artifacts","effective_unique_artifacts","categorized_links","ignored_local_artifacts","tracked_metadata_links","owner_decisions","accepted_candidates","executable_panels","provider_calls","uploads","cost_usd")]+[lambda x:x["summary"].update(human_review_minutes=1),lambda x:x["category_counts"].update(review_hubs=6),lambda x:x["category_counts"].update(packet_records=18)]
    rejected=0
    for mut in muts: y=copy.deepcopy(d); mut(y); rejected+=bool(errors(y))
    if rejected!=len(muts): fail.append(f"only {rejected}/{len(muts)} mutations rejected")
    print(f"CH05 review links r4: {len(fail)} failures; 117=112+5 / 108 ignored + 9 tracked; {rejected}/{len(muts)} mutations rejected")
    for item in fail: print(f"FAIL: {item}")
    return 1 if fail else 0
if __name__=="__main__": raise SystemExit(main())
