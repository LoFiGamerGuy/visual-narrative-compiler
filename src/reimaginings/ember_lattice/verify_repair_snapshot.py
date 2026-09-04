from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
VOLUME = ROOT / "production" / "reimaginings" / "ember-lattice" / "volume"


def main() -> None:
    before = json.loads((VOLUME / "repair-snapshots" / "ch03-p007-before.json").read_text(encoding="utf-8"))
    changed = []
    for row in before["non_target_outputs"]:
        path = ROOT / row["path"]
        actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None
        if actual != row["sha256"]:
            changed.append({"request_id": row["request_id"], "expected": row["sha256"], "actual": actual})
    report = {
        "schema": "TargetedRepairValidation/1.0", "status": "PASS" if not changed else "FAIL",
        "target": before["target"], "failure_class": "non_vertical_source",
        "preserved_original": "experiments/reimaginings/ember-lattice/volume/ch03/diagnostics/p007-r1-landscape.png",
        "selected_retry": "experiments/reimaginings/ember-lattice/volume/ch03/source/p007.png",
        "non_target_hashes_checked": len(before["non_target_outputs"]), "non_target_changes": changed,
    }
    (VOLUME / "repair-validation.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if not changed else 1)


if __name__ == "__main__":
    main()
