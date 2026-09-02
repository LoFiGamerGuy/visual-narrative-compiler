"""Export tracked hashes and boundaries for the ignored offline CH05 decision worksheet."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PACKET=ROOT/"experiments/review-packets/ch05-owner-decision-worksheet-r1/decision-worksheet-packet.json"
OUTPUT=ROOT/"docs/research/evidence/ch05-owner-decision-worksheet-r1.json"
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def main()->int:
 p=json.loads(PACKET.read_text(encoding="utf-8"))
 e={"record_type":"CH05OwnerDecisionWorksheetEvidence","schema_version":"1.0","record_id":"ng-ch05-owner-decision-worksheet-evidence-r1","state":"OFFLINE_DRAFT_TOOL_READY_NO_DECISIONS",
    "packet":{"path":PACKET.relative_to(ROOT).as_posix(),"sha256":sha(PACKET)},"contract":p["contract"],"review_index_packet":p["review_index_packet"],"index":p["index"],
    "summary":{"subject_count":p["subject_count"],"linked_candidate_count":p["linked_candidate_count"],"linked_higher_order_count":p["linked_higher_order_count"],"network_calls":0,"uploads":0,"repository_writes_from_html":0,"decisions_recorded":0,"human_review_minutes":None},
    "determinism":{"consecutive_build_count":2,"index_sha256_run_a":p["index"]["sha256"],"index_sha256_run_b":p["index"]["sha256"],"result":"BYTE_IDENTICAL_OFFLINE_WORKSHEET"},
    "limitations":["Browser selections are ephemeral until the owner exports a local JSON draft.","An exported draft is not a hash-chained decision event and must pass a future ingestion validator.","The worksheet contains no timer; human minutes remain null until an immutable review session exists.","No remote asset, script, fetch, form submission, or repository-write capability is included."],
    "boundary":"Zero decisions are recorded; the empty tracked contract remains unchanged."}
 OUTPUT.parent.mkdir(parents=True,exist_ok=True)
 with OUTPUT.open("w",encoding="utf-8",newline="\n") as h:h.write(json.dumps(e,indent=2)+"\n")
 print(f"exported owner decision worksheet evidence: {OUTPUT.relative_to(ROOT)} {sha(OUTPUT)}");return 0
if __name__=="__main__":raise SystemExit(main())
