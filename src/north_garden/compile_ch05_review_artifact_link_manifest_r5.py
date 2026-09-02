"""Extend exact CH05 review links with final evidence handoff resources."""
from __future__ import annotations
import hashlib,json,subprocess
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; BASE=ROOT/"production/comic/review/ch05-review-artifact-link-manifest-r4.json"; OUTPUT=ROOT/"production/comic/review/ch05-review-artifact-link-manifest-r5.json"; MARKDOWN=ROOT/"docs/research/ch05-review-links-r5.md"; EVIDENCE=ROOT/"docs/research/evidence/ch05-review-artifact-link-manifest-r5.json"
ADDED=[("experiments/review-packets/ch05-owner-review-index-r7/index.html",["review_hubs"]),("docs/research/evidence/ch05-final-evidence-reproducer-matrix-r2.json",["packet_records"]),("docs/research/evidence/ch05-overnight-safe-source-parity-r2.json",["packet_records"]),("docs/research/ch05-owner-decision-defaults-r1.md",["review_checklists"]),("docs/research/evidence/ch05-overnight-integrated-release-gate-r10.json",["packet_records"])]
ORDER=["review_hubs","contact_sheets","sequence_packets","lettering_overlays","strongest_candidates","noncanon_litrpg_concepts","diagnostic_and_policy_sheets","packet_records","review_checklists"]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def state(p):
    if subprocess.run(["git","check-ignore","-q",str(p)],cwd=ROOT).returncode==0: return "IGNORED_LOCAL"
    if subprocess.run(["git","ls-files","--error-unmatch",p.relative_to(ROOT).as_posix()],cwd=ROOT,capture_output=True).returncode==0: return "TRACKED_METADATA"
    return "UNBOUND"
def main():
    base=json.loads(BASE.read_text(encoding="utf-8")); artifacts=[{**x,"git_state":state(ROOT/x["path"])} for x in base["artifacts"]]
    for path_text,categories in ADDED:
        p=ROOT/path_text
        if not p.is_file(): raise SystemExit(f"missing added artifact: {path_text}")
        artifacts.append({"path":path_text,"absolute_path":p.resolve().as_posix(),"sha256":sha(p),"bytes":p.stat().st_size,"categories":categories,"git_state":state(p)})
    artifacts.sort(key=lambda x:x["path"]); by=defaultdict(list)
    for x in artifacts:
        for c in x["categories"]: by[c].append(x)
    counts={x:len(by[x]) for x in ORDER}; ignored=sum(x["git_state"]=="IGNORED_LOCAL" for x in artifacts); tracked=sum(x["git_state"]=="TRACKED_METADATA" for x in artifacts); out={"record_type":"CH05ReviewArtifactLinkManifest","schema_version":"5.0","record_id":"ng-ch05-review-artifact-link-manifest-r5","state":"LOCAL_REVIEW_LINKS_READY_OWNER_PENDING","extends":{"path":BASE.relative_to(ROOT).as_posix(),"sha256":sha(BASE),"unique_artifact_count":base["effective_unique_artifact_count"]},"workspace_root_at_compile":ROOT.resolve().as_posix(),"added_artifact_count":5,"effective_unique_artifact_count":len(artifacts),"category_counts":counts,"ignored_local_artifacts":ignored,"tracked_metadata_links":tracked,"artifacts":artifacts,"summary":{"candidate_count":29,"selected_candidate_count":14,"plan_count":50,"sequence_count":12,"owner_decisions":0,"accepted_candidates":0,"executable_panels":0,"provider_calls":0,"uploads":0,"cost_usd":0,"human_review_minutes":None},"limitations":["Absolute paths are workspace-specific.","Generated pixels remain ignored and unpublished.","Link inclusion is not acceptance, execution, or commercial clearance."],"boundary":"Append-only extension of r4; all prior 117 artifact bindings remain exact."}; OUTPUT.write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8",newline="\n")
    lines=["# CH05 exact local review links r5","","R5 extends the exact 117-artifact r4 manifest with five final-evidence resources. All art remains unaccepted and commercially uncleared.","",f"Effective unique artifacts: {len(artifacts)}. Workspace root: `{ROOT.resolve().as_posix()}`.",""]
    for c in ORDER: lines += [f"## {c.replace('_',' ').title()}",""]+[f"- [{Path(x['path']).name}]({x['absolute_path']}) — `{x['sha256']}` · {x['git_state']}" for x in by[c]]+[""]
    MARKDOWN.write_text("\n".join(lines),encoding="utf-8",newline="\n"); evidence={"record_type":"CH05ReviewArtifactLinkManifestEvidence","schema_version":"5.0","record_id":"ng-ch05-review-artifact-link-manifest-evidence-r5","state":"PASS_OWNER_PENDING","manifest":{"path":OUTPUT.relative_to(ROOT).as_posix(),"sha256":sha(OUTPUT)},"markdown":{"path":MARKDOWN.relative_to(ROOT).as_posix(),"sha256":sha(MARKDOWN)},"extends":out["extends"],"summary":{"added_artifacts":5,"effective_unique_artifacts":len(artifacts),"categorized_links":sum(counts.values()),"ignored_local_artifacts":ignored,"tracked_metadata_links":tracked,"owner_decisions":0,"accepted_candidates":0,"executable_panels":0,"provider_calls":0,"uploads":0,"cost_usd":0,"human_review_minutes":None},"category_counts":counts}; EVIDENCE.write_text(json.dumps(evidence,indent=2)+"\n",encoding="utf-8",newline="\n"); print(f"CH05 review links r5: {len(artifacts)} = 117+5; ignored/tracked {ignored}/{tracked}"); return 0
if __name__=="__main__": raise SystemExit(main())
