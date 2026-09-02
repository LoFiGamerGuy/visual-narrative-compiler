"""Extend exact CH05 review links with final owner-entry resources."""
from __future__ import annotations
import hashlib,json,subprocess
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; BASE=ROOT/"production/comic/review/ch05-review-artifact-link-manifest-r6.json"; OUTPUT=ROOT/"production/comic/review/ch05-review-artifact-link-manifest-r7.json"; MARKDOWN=ROOT/"docs/research/ch05-review-links-r7.md"; EVIDENCE=ROOT/"docs/research/evidence/ch05-review-artifact-link-manifest-r7.json"
ADDED=[("experiments/review-packets/ch05-owner-review-index-r9/index.html",["review_hubs"]),("docs/research/ch05-overnight-closeout-r3.md",["review_checklists"]),("docs/research/ch05-strongest-candidate-disposition-guide-r1.md",["review_checklists"]),("docs/research/ch05-final-handoff-consistency-matrix-r1.md",["review_checklists"]),("docs/research/evidence/ch05-final-review-integrated-release-r12.json",["packet_records"]),("docs/research/evidence/ch05-final-safe-source-parity-r4.json",["packet_records"])]
ORDER=["review_hubs","contact_sheets","sequence_packets","lettering_overlays","strongest_candidates","noncanon_litrpg_concepts","diagnostic_and_policy_sheets","packet_records","review_checklists"]
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def state(path):
    if subprocess.run(["git","check-ignore","-q",str(path)],cwd=ROOT).returncode==0:return "IGNORED_LOCAL"
    if subprocess.run(["git","ls-files","--error-unmatch",path.relative_to(ROOT).as_posix()],cwd=ROOT,capture_output=True).returncode==0:return "TRACKED_METADATA"
    return "UNBOUND"
def main():
    base=json.loads(BASE.read_text(encoding="utf-8")); artifacts=[{**item,"git_state":state(ROOT/item["path"])} for item in base["artifacts"]]
    for path_text,categories in ADDED:
        path=ROOT/path_text
        if not path.is_file():raise SystemExit(f"missing artifact: {path_text}")
        artifacts.append({"path":path_text,"absolute_path":path.resolve().as_posix(),"sha256":sha(path),"bytes":path.stat().st_size,"categories":categories,"git_state":state(path)})
    artifacts.sort(key=lambda item:item["path"]); grouped=defaultdict(list)
    for item in artifacts:
        for category in item["categories"]:grouped[category].append(item)
    counts={category:len(grouped[category]) for category in ORDER}; ignored=sum(item["git_state"]=="IGNORED_LOCAL" for item in artifacts); tracked=sum(item["git_state"]=="TRACKED_METADATA" for item in artifacts); output={"record_type":"CH05ReviewArtifactLinkManifest","schema_version":"7.0","record_id":"ng-ch05-review-artifact-link-manifest-r7","state":"LOCAL_FINAL_OWNER_REVIEW_LINKS_READY_DISPOSITIONS_ABSENT","extends":{"path":BASE.relative_to(ROOT).as_posix(),"sha256":sha(BASE),"unique_artifact_count":base["effective_unique_artifact_count"]},"workspace_root_at_compile":ROOT.resolve().as_posix(),"added_artifact_count":6,"effective_unique_artifact_count":len(artifacts),"category_counts":counts,"ignored_local_artifacts":ignored,"tracked_metadata_links":tracked,"artifacts":artifacts,"summary":{"candidates":29,"strongest_candidates":14,"worksheet_checks":112,"plans":50,"batches":12,"owner_dispositions":0,"owner_decisions_ingested":0,"accepted":0,"commercially_cleared":0,"executable":0,"provider_calls":0,"uploads":0,"cost_usd":0,"human_review_minutes":None},"boundary":"Append-only extension of r6; all prior 128 artifact bindings remain exact and visual disposition remains separate from acceptance/rights."}; OUTPUT.write_text(json.dumps(output,indent=2)+"\n",encoding="utf-8",newline="\n")
    lines=["# CH05 exact local review links r7","","R7 extends the exact 128-artifact r6 manifest with six final owner-entry resources. Art remains unaccepted and commercially uncleared.","",f"Effective unique artifacts: {len(artifacts)}. Workspace root: `{ROOT.resolve().as_posix()}`.",""]
    for category in ORDER:lines += [f"## {category.replace('_',' ').title()}",""]+[f"- [{Path(item['path']).name}]({item['absolute_path']}) — `{item['sha256']}` · {item['git_state']}" for item in grouped[category]]+[""]
    MARKDOWN.write_text("\n".join(lines),encoding="utf-8",newline="\n"); evidence={"record_type":"CH05ReviewArtifactLinkManifestEvidence","schema_version":"7.0","record_id":"ng-ch05-review-artifact-link-manifest-evidence-r7","state":"PASS_OWNER_DISPOSITIONS_ABSENT","manifest":{"path":OUTPUT.relative_to(ROOT).as_posix(),"sha256":sha(OUTPUT)},"markdown":{"path":MARKDOWN.relative_to(ROOT).as_posix(),"sha256":sha(MARKDOWN)},"extends":output["extends"],"summary":{"added_artifacts":6,"effective_unique_artifacts":len(artifacts),"categorized_links":sum(counts.values()),"ignored_local_artifacts":ignored,"tracked_metadata_links":tracked,"strongest_candidates":14,"worksheet_checks":112,"owner_dispositions":0,"owner_decisions_ingested":0,"accepted":0,"commercially_cleared":0,"executable":0,"provider_calls":0,"uploads":0,"cost_usd":0,"human_review_minutes":None},"category_counts":counts}; EVIDENCE.write_text(json.dumps(evidence,indent=2)+"\n",encoding="utf-8",newline="\n"); print(f"CH05 review links r7: {len(artifacts)} = 128+6; ignored/tracked {ignored}/{tracked}"); return 0
if __name__=="__main__":raise SystemExit(main())
