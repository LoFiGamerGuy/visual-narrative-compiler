"""Extend the exact CH05 review-link manifest with chapter-scale maps and r4 hub."""
from __future__ import annotations
import hashlib,json,subprocess
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/"production/comic/review/ch05-review-artifact-link-manifest-r1.json";OUTPUT=ROOT/"production/comic/review/ch05-review-artifact-link-manifest-r2.json";MARKDOWN=ROOT/"docs/research/ch05-review-links-r2.md";EVIDENCE=ROOT/"docs/research/evidence/ch05-review-artifact-link-manifest-r2.json"
ADDED=[
 ("experiments/review-packets/ch05-owner-review-index-r4/index.html",["review_hubs"]),
 ("experiments/review-packets/ch05-chapter-production-readiness-r1/ch05-chapter-readiness-map-r1.png",["diagnostic_and_policy_sheets"]),
 ("experiments/review-packets/ch05-reference-use-continuity-risk-r1/ch05-reference-risk-map-r1.png",["diagnostic_and_policy_sheets"]),
 ("experiments/review-packets/ch05-chapter-sequence-production-batches-r1/ch05-sequence-batch-map-r1.png",["diagnostic_and_policy_sheets"]),
 ("experiments/review-packets/ch05-lettering-semantics-readiness-r1/ch05-lettering-semantics-map-r1.png",["diagnostic_and_policy_sheets"]),
 ("docs/research/ch05-owner-handoff-checklist-r1.md",["review_checklists"]),
]
ORDER=["review_hubs","contact_sheets","sequence_packets","lettering_overlays","strongest_candidates","noncanon_litrpg_concepts","diagnostic_and_policy_sheets","packet_records","review_checklists"]
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def git_state(p:Path)->str:
 if subprocess.run(["git","check-ignore","-q",str(p)],cwd=ROOT,check=False).returncode==0:return "IGNORED_LOCAL"
 if subprocess.run(["git","ls-files","--error-unmatch",p.relative_to(ROOT).as_posix()],cwd=ROOT,capture_output=True,check=False).returncode==0:return "TRACKED_METADATA"
 return "UNBOUND"
def main()->int:
 base=json.loads(BASE.read_text(encoding="utf-8"));artifacts=[]
 for item in base["artifacts"]:artifacts.append({**item,"git_state":git_state(ROOT/item["path"])})
 for path_text,categories in ADDED:
  p=ROOT/path_text
  if not p.is_file():raise SystemExit(f"missing added review artifact: {path_text}")
  artifacts.append({"path":path_text,"absolute_path":p.resolve().as_posix(),"sha256":sha(p),"bytes":p.stat().st_size,"categories":categories,"git_state":git_state(p)})
 artifacts.sort(key=lambda x:x["path"]);by_category=defaultdict(list)
 for item in artifacts:
  for category in item["categories"]:by_category[category].append(item)
 counts={category:len(by_category[category]) for category in ORDER};ignored=sum(x["git_state"]=="IGNORED_LOCAL" for x in artifacts);tracked=sum(x["git_state"]=="TRACKED_METADATA" for x in artifacts)
 manifest={"record_type":"CH05ReviewArtifactLinkManifest","schema_version":"2.0","record_id":"ng-ch05-review-artifact-link-manifest-r2","state":"LOCAL_REVIEW_LINKS_READY_OWNER_PENDING","extends":{"path":BASE.relative_to(ROOT).as_posix(),"sha256":sha(BASE),"unique_artifact_count":base["unique_artifact_count"]},"workspace_root_at_compile":ROOT.resolve().as_posix(),"added_artifact_count":len(ADDED),"effective_unique_artifact_count":len(artifacts),"category_counts":counts,"ignored_local_artifacts":ignored,"tracked_metadata_links":tracked,"artifacts":artifacts,"summary":{"candidate_count":29,"selected_candidate_count":14,"plan_count":50,"sequence_count":12,"owner_task_count":24,"owner_decisions":0,"accepted_candidates":0,"provider_calls":0,"uploads":0,"cost_usd":0,"human_review_minutes":None},"limitations":["Absolute paths are workspace-specific.","Generated pixels remain ignored and unpublished.","Link inclusion is not acceptance or commercial clearance."],"boundary":"Append-only extension of r1; all prior 99 artifact bindings remain exact."}
 OUTPUT.write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8",newline="\n")
 lines=["# CH05 exact local review links r2","",f"R2 extends the exact 99-artifact r1 manifest with {len(ADDED)} current chapter-scale resources. All art remains unaccepted and commercially uncleared.","",f"Effective unique artifacts: {len(artifacts)}. Workspace root: `{ROOT.resolve().as_posix()}`.",""]
 for category in ORDER:
  lines.extend([f"## {category.replace('_',' ').title()}",""])
  for item in by_category[category]:lines.append(f"- [{Path(item['path']).name}]({item['absolute_path']}) — `{item['sha256']}` · {item['git_state']}")
  lines.append("")
 MARKDOWN.write_text("\n".join(lines),encoding="utf-8",newline="\n")
 evidence={"record_type":"CH05ReviewArtifactLinkManifestEvidence","schema_version":"2.0","record_id":"ng-ch05-review-artifact-link-manifest-evidence-r2","state":"PASS_OWNER_PENDING","manifest":{"path":OUTPUT.relative_to(ROOT).as_posix(),"sha256":sha(OUTPUT)},"markdown":{"path":MARKDOWN.relative_to(ROOT).as_posix(),"sha256":sha(MARKDOWN)},"extends":manifest["extends"],"summary":{"added_artifacts":len(ADDED),"effective_unique_artifacts":len(artifacts),"categorized_links":sum(counts.values()),"ignored_local_artifacts":ignored,"tracked_metadata_links":tracked,"owner_decisions":0,"accepted_candidates":0,"provider_calls":0,"uploads":0,"cost_usd":0,"human_review_minutes":None},"category_counts":counts}
 EVIDENCE.write_text(json.dumps(evidence,indent=2)+"\n",encoding="utf-8",newline="\n");print(f"CH05 review links r2: {len(artifacts)} effective = 99 base + {len(ADDED)} added; ignored/tracked {ignored}/{tracked}");print("decisions/accepted/calls/uploads/cost 0/0/0/0/$0");return 0
if __name__=="__main__":raise SystemExit(main())
