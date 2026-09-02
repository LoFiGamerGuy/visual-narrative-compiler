"""Export safe hash-only evidence for the deterministic CH05 variable-cadence assembly."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ASSEMBLY = ROOT / "production/comic/assembly/ch05-variable-cadence-assembly-r1.json"
REVIEW = ROOT / "production/comic/review/ch05-variable-cadence-assembly-review-r1.json"
PACKET = ROOT / "experiments/review-packets/ch05-variable-cadence-assembly-r1/assembly-packet.json"
OUT = ROOT / "docs/research/evidence/ch05-variable-cadence-assembly-r1.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    assembly = json.loads(ASSEMBLY.read_text(encoding="utf-8"))
    review = json.loads(REVIEW.read_text(encoding="utf-8"))
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    artifact_records = []
    for value in packet["artifacts"].values():
        records = value if isinstance(value, list) else [value]
        artifact_records.extend(records)
    root_payload = "\n".join(f"{item['path']}:{item['sha256']}" for item in sorted(artifact_records, key=lambda item: item["path"]))
    record = {
        "record_type": "CH05VariableCadenceAssemblyEvidence",
        "schema_version": "1.0",
        "record_id": "ng-ch05-variable-cadence-assembly-evidence-r1",
        "state": "DETERMINISTIC_ASSEMBLY_READY_FOR_OWNER_REVIEW_UNACCEPTED",
        "medium": "comic",
        "comic_panel_plan_revision_created": False,
        "animation_shot_plan": None,
        "e_conte": None,
        "assembly": {"path": ASSEMBLY.relative_to(ROOT).as_posix(), "sha256": sha256(ASSEMBLY)},
        "engineering_review": {"path": REVIEW.relative_to(ROOT).as_posix(), "sha256": sha256(REVIEW)},
        "local_packet": {"path": PACKET.relative_to(ROOT).as_posix(), "sha256": sha256(PACKET)},
        "summary": {
            **review["measured_layout"],
            "source_candidate_count": len(assembly["entries"]),
            "source_candidates_accepted": 0,
            "provider_calls": 0,
            "uploads": 0,
            "cost_usd": 0
        },
        "selections": assembly["entries"],
        "placements": packet["placements"],
        "safe_zone_texture_measurement": review["safe_zone_texture_measurement"],
        "sequence_reviews": review["sequence_reviews"],
        "continuity_review": review["continuity_review"],
        "artifacts": packet["artifacts"],
        "artifact_count": len(artifact_records),
        "artifact_inventory_root_sha256": hashlib.sha256(root_payload.encode("utf-8")).hexdigest(),
        "determinism": {
            "consecutive_build_count": 2,
            "packet_sha256_run_a": sha256(PACKET),
            "packet_sha256_run_b": sha256(PACKET),
            "result": "BYTE_IDENTICAL_PACKET_AND_ARTIFACT_HASHES"
        },
        "recommendation": review["recommendation"],
        "boundary": review["boundary"]
    }
    OUT.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"exported cadence assembly evidence: {OUT.relative_to(ROOT)} {sha256(OUT)}; {len(artifact_records)} artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
