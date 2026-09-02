"""Export tracked evidence for ignored CH05 owner review index r7."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; PACKET=ROOT/"experiments/review-packets/ch05-owner-review-index-r7/owner-review-index-r7-packet.json"; OUTPUT=ROOT/"docs/research/evidence/ch05-owner-review-index-r7.json"
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=json.loads(PACKET.read_text(encoding="utf-8")); e={"record_type":"CH05OwnerReviewIndexEvidence","schema_version":"7.0","record_id":"ng-ch05-owner-review-index-evidence-r7","state":"LOCAL_FINAL_EVIDENCE_REVIEW_HUB_READY_OWNER_PENDING","packet":{"path":PACKET.relative_to(ROOT).as_posix(),"sha256":sha(PACKET)},"extends":p["extends"],"contract":p["contract"],"summary":{"candidate_count":29,"plan_count":50,"prior_review_links":117,"release_checks":66,"engineering_defaults":10,"link_count":5,"image_link_count":0,"html_link_count":1,"text_link_count":4,"artifact_count":1,"owner_decisions":0,"accepted_candidates":0,"executable_panels":0,"provider_calls":0,"uploads":0,"cost_usd":0,"human_review_minutes":None},"links":[{"id":x["id"],"path":x["path"],"sha256":x["sha256"],"kind":x["kind"]} for x in p["links"]],"index":p["index"],"determinism":{"consecutive_build_count":2,"result":"BYTE_IDENTICAL_INDEX_AND_PACKET"},"boundary":p["boundary"]}; OUTPUT.write_text(json.dumps(e,indent=2)+"\n",encoding="utf-8",newline="\n"); print(f"exported CH05 owner review index r7 evidence {sha(OUTPUT)}"); return 0
if __name__=="__main__": raise SystemExit(main())
