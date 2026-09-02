"""Export tracked hashes for the ignored CH05 owner review index r2."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];PACKET=ROOT/"experiments/review-packets/ch05-owner-review-index-r2/owner-review-index-r2-packet.json";OUTPUT=ROOT/"docs/research/evidence/ch05-owner-review-index-r2.json"
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def main()->int:
 p=json.loads(PACKET.read_text(encoding="utf-8"));e={"record_type":"CH05OwnerReviewIndexEvidence","schema_version":"2.0","record_id":"ng-ch05-owner-review-index-evidence-r2","state":"LOCAL_REVIEW_HUB_READY_OWNER_PENDING","packet":{"path":PACKET.relative_to(ROOT).as_posix(),"sha256":sha(PACKET)},"extends":p["extends"],"decision_worksheet":p["decision_worksheet"],"contract":p["contract"],"summary":{"candidate_count":29,"selected_candidate_count":14,"pending_subject_count":39,"link_count":p["link_count"],"image_link_count":p["image_link_count"],"html_link_count":p["html_link_count"],"artifact_count":p["artifact_count"],"owner_decisions":0,"accepted_candidates":0,"provider_calls":0,"uploads":0,"cost_usd":0,"human_review_minutes":None},"links":[{"id":x["id"],"path":x["path"],"sha256":x["sha256"],"kind":x["kind"]} for x in p["links"]],"index":p["index"],"determinism":{"consecutive_build_count":2,"result":"BYTE_IDENTICAL_INDEX_PACKET_AND_THUMBNAILS"},"limitations":["The hub only links local evidence and does not capture browser interaction.","Owner decisions and timed review remain absent until a validated event workflow is used.","Generated pixels remain ignored and commercially uncleared."],"boundary":p["boundary"]};OUTPUT.parent.mkdir(parents=True,exist_ok=True)
 with OUTPUT.open("w",encoding="utf-8",newline="\n") as h:h.write(json.dumps(e,indent=2)+"\n")
 print(f"exported CH05 owner review index r2 evidence {sha(OUTPUT)}");return 0
if __name__=="__main__":raise SystemExit(main())
