"""Export tracked evidence for ignored CH05 owner review index r9."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; PACKET=ROOT/"experiments/review-packets/ch05-owner-review-index-r9/owner-review-index-r9-packet.json"; OUTPUT=ROOT/"docs/research/evidence/ch05-owner-review-index-r9.json"
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    packet=json.loads(PACKET.read_text(encoding="utf-8")); evidence={"record_type":"CH05OwnerReviewIndexEvidence","schema_version":"9.0","record_id":"ng-ch05-owner-review-index-evidence-r9","state":"LOCAL_FINAL_OWNER_REVIEW_HUB_READY_DISPOSITIONS_ABSENT","packet":{"path":PACKET.relative_to(ROOT).as_posix(),"sha256":sha(PACKET)},"extends":packet["extends"],"summary":{**packet["summary"],"link_count":6,"image_link_count":0,"html_link_count":1,"text_link_count":5,"artifact_count":1},"links":[{"id":item["id"],"path":item["path"],"sha256":item["sha256"],"kind":item["kind"]} for item in packet["links"]],"index":packet["index"],"determinism":{"consecutive_build_count":2,"result":"BYTE_IDENTICAL_INDEX_AND_PACKET"},"animation_shot_plan":None,"e_conte":None,"boundary":packet["boundary"]}; OUTPUT.write_text(json.dumps(evidence,indent=2)+"\n",encoding="utf-8",newline="\n"); print(f"exported CH05 owner review index r9 evidence {sha(OUTPUT)}"); return 0
if __name__=="__main__": raise SystemExit(main())
