"""Validate that the pilot inventory preserves its quarantine and count conflict."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "garden-work/northgarden/pilot.md"
INVENTORY = ROOT / "research/historical/inventories/gardens-anchor-pilot-r1.json"


def main() -> None:
    payload = json.loads(INVENTORY.read_text(encoding="utf-8"))
    assert payload["classification"] == "HISTORICAL_NARRATIVE_AND_DESIGN_EVIDENCE_NOT_IMPORTED"
    assert payload["source_sha256"] == hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    assert [item["observed_count"] for item in payload["chapters"]] == [52, 44]
    assert all(item["contiguous_from_01"] for item in payload["chapters"])
    claims = payload["count_claims"]
    assert claims == {"opening_claim": 92, "footer_claim": 96, "observed_numbered_total": 96, "state": "INTERNALLY_INCONSISTENT"}
    print("0 failures, 0 warnings (quarantined historical pilot inventory validated)")


if __name__ == "__main__":
    main()
