"""Extend exact CH05 review links with the final review-session resources."""
from __future__ import annotations
import hashlib, json, subprocess
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; BASE=ROOT/"production/comic/review/ch05-review-artifact-link-manifest-r5.json"; OUTPUT=ROOT/"production/comic/review/ch05-review-artifact-link-manifest-r6.json"; MARKDOWN=ROOT/"docs/research/ch05-review-links-r6.md"; EVIDENCE=ROOT/"docs/research/evidence/ch05-review-artifact-link-manifest-r6.json"
ADDED=[("experiments/review-packets/ch05-owner-review-index-r8/index.html",["review_hubs"]),("docs/research/ch05-final-review-session-starter-r1.md",["review_checklists"]),("docs/research/ch05-owner-response-guide-r1.md",["review_checklists"]),("docs/research/ch05-owner-ingestion-preflight-contract-r1.md",["review_checklists"]),("docs/research/ch05-final-model-license-provenance-audit-r1.md",["diagnostic_and_policy_sheets"]),("docs/research/ch05-overnight-closeout-r2.md",["review_checklists"])]
ORDER=["review_hubs","contact_sheets","sequence_packets","lettering_overlays","strongest_candidates","noncanon_litrpg_concepts","diagnostic_and_policy_sheets","packet_records","review_checklists"]
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def state(path):
    if subprocess.run(["git","check-ignore","-q",str(path)],cwd=ROOT).returncode==0: return "IGNORED_LOCAL"
    if subprocess.run(["git","ls-files","--error-unmatch",path.relative_to(ROOT).as_posix()],cwd=ROOT,capture_output=True).returncode==0: return "TRACKED_METADATA"
    return "UNBOUND"
def main():
    base=json.loads(BASE.read_text(encoding="utf-8")); artifacts=[{**item,"git_state":state(ROOT/item["path"])} for item in base["artifacts"]]
    for path_text,categories in ADDED:
        path=ROOT/path_text
        if not path.is_file(): raise SystemExit(f"missing added artifact: {path_text}")
        artifacts.append({"path":path_text,"absolute_path":path.resolve().as_posix(),"sha256":sha(path),"bytes":path.stat().st_size,"categories":categories,"git_state":state(path)})
    artifacts.sort(key=lambda item:item["path"]); grouped=defaultdict(list)
    for item in artifacts:
        for category in item["categories"]: grouped[category].append(item)
    counts={category:len(grouped[category]) for category in ORDER}; ignored=sum(item["git_state"]=="IGNORED_LOCAL" for item in artifacts); tracked=sum(item["git_state"]=="TRACKED_METADATA" for item in artifacts)
    output={"record_type":"CH05ReviewArtifactLinkManifest","schema_version":"6.0","record_id":"ng-ch05-review-artifact-link-manifest-r6","state":"LOCAL_REVIEW_SESSION_LINKS_READY_OWNER_INPUTS_ABSENT","extends":{"path":BASE.relative_to(ROOT).as_posix(),"sha256":sha(BASE),"unique_artifact_count":base["effective_unique_artifact_count"]},"workspace_root_at_compile":ROOT.resolve().as_posix(),"added_artifact_count":6,"effective_unique_artifact_count":len(artifacts),"category_counts":counts,"ignored_local_artifacts":ignored,"tracked_metadata_links":tracked,"artifacts":artifacts,"summary":{"candidate_count":29,"selected_candidate_count":14,"plan_count":50,"sequence_count":12,"pilot_roots":6,"owner_decisions_ingested":0,"accepted_candidates":0,"commercially_cleared":0,"executable_panels":0,"provider_calls":0,"uploads":0,"cost_usd":0,"human_review_minutes":None},"limitations":["Absolute paths are workspace-specific.","Generated pixels remain ignored and unpublished.","Link inclusion is not review completion, ingestion, acceptance, execution, or commercial clearance."],"boundary":"Append-only extension of r5; all prior 122 artifact bindings remain exact."}; OUTPUT.write_text(json.dumps(output,indent=2)+"\n",encoding="utf-8",newline="\n")
    lines=["# CH05 exact local review links r6","","R6 extends the exact 122-artifact r5 manifest with six final review-session resources. All art remains unaccepted and commercially uncleared.","",f"Effective unique artifacts: {len(artifacts)}. Workspace root: `{ROOT.resolve().as_posix()}`.",""]
    for category in ORDER: lines += [f"## {category.replace('_',' ').title()}",""]+[f"- [{Path(item['path']).name}]({item['absolute_path']}) — `{item['sha256']}` · {item['git_state']}" for item in grouped[category]]+[""]
    MARKDOWN.write_text("\n".join(lines),encoding="utf-8",newline="\n"); evidence={"record_type":"CH05ReviewArtifactLinkManifestEvidence","schema_version":"6.0","record_id":"ng-ch05-review-artifact-link-manifest-evidence-r6","state":"PASS_OWNER_INPUTS_ABSENT","manifest":{"path":OUTPUT.relative_to(ROOT).as_posix(),"sha256":sha(OUTPUT)},"markdown":{"path":MARKDOWN.relative_to(ROOT).as_posix(),"sha256":sha(MARKDOWN)},"extends":output["extends"],"summary":{"added_artifacts":6,"effective_unique_artifacts":len(artifacts),"categorized_links":sum(counts.values()),"ignored_local_artifacts":ignored,"tracked_metadata_links":tracked,"pilot_roots":6,"owner_decisions_ingested":0,"accepted_candidates":0,"commercially_cleared":0,"executable_panels":0,"provider_calls":0,"uploads":0,"cost_usd":0,"human_review_minutes":None},"category_counts":counts}; EVIDENCE.write_text(json.dumps(evidence,indent=2)+"\n",encoding="utf-8",newline="\n"); print(f"CH05 review links r6: {len(artifacts)} = 122+6; ignored/tracked {ignored}/{tracked}"); return 0
if __name__=="__main__": raise SystemExit(main())
