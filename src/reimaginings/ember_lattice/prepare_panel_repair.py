from __future__ import annotations

import copy
import hashlib
import json
import shutil
from datetime import date
from pathlib import Path

from record_generated_panel import ROOT, REQUESTS, acquire_lock


FAILED_ID = "volume-ch03-p007-r1"
RETRY_ID = "volume-ch03-p007-r2"
NORMAL_PATH = "experiments/reimaginings/ember-lattice/volume/ch03/source/p007.png"
DIAGNOSTIC_PATH = "experiments/reimaginings/ember-lattice/volume/ch03/diagnostics/p007-r1-landscape.png"
SNAPSHOT = ROOT / "production" / "reimaginings" / "ember-lattice" / "volume" / "repair-snapshots" / "ch03-p007-before.json"


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    lock_handle = acquire_lock()
    document = json.loads(REQUESTS.read_text(encoding="utf-8"))
    failed = next(row for row in document["requests"] if row["request_id"] == FAILED_ID)
    if any(row["request_id"] == RETRY_ID for row in document["requests"]):
        raise SystemExit("retry already prepared")
    source = (ROOT / NORMAL_PATH).resolve()
    diagnostic = (ROOT / DIAGNOSTIC_PATH).resolve()
    if ROOT not in source.parents or ROOT not in diagnostic.parents or not source.exists():
        raise SystemExit("unsafe or missing repair source")
    diagnostic.parent.mkdir(parents=True, exist_ok=True)
    if diagnostic.exists():
        raise SystemExit("diagnostic target already exists")

    non_target = []
    for row in document["requests"]:
        candidate = ROOT / row["output_path"]
        if row["request_id"] != FAILED_ID and candidate.exists():
            non_target.append({"request_id": row["request_id"], "path": row["output_path"], "sha256": file_hash(candidate)})
    SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
    SNAPSHOT.write_text(json.dumps({"schema": "NonTargetRepairSnapshot/1.0", "target": FAILED_ID, "non_target_outputs": non_target}, indent=2) + "\n", encoding="utf-8", newline="\n")
    shutil.move(source, diagnostic)
    failed["output_path"] = DIAGNOSTIC_PATH
    failed["review_status"] = "HARD_FAIL_PRESERVED_DIAGNOSTIC"
    failed["failure_classes"] = ["non_vertical_source"]
    failed["visual_review"] = {"reviewer": "primary_agent_local_visual_inspection", "date": date.today().isoformat(), "result": "FAIL", "notes": "1536x1024 landscape return violates tall vertical-scroll source contract; localized retry authorized."}

    retry = copy.deepcopy(failed)
    retry.update({
        "request_id": RETRY_ID,
        "exact_prompt": failed["exact_prompt"] + "\nRepair directive: return one unmistakably tall 9:16 vertical-scroll panel, portrait orientation, at least 1200 pixels high and strictly taller than wide; preserve the same single cultivation-menu story moment, adult identities, quiet negative space, and Candidate B visual language; do not add any text or UI.",
        "output_path": NORMAL_PATH,
        "measured_elapsed_seconds": None, "model": None, "endpoint": None, "provider_request_id": None,
        "usage": None, "monetary_cost": None, "seed": None, "review_status": "NOT_GENERATED",
        "failure_classes": [], "sha256": None, "dimensions": None,
    })
    retry["prompt_hash"] = hashlib.sha256(retry["exact_prompt"].encode("utf-8")).hexdigest()
    retry.pop("visual_review", None)
    index = document["requests"].index(failed)
    document["requests"].insert(index + 1, retry)
    REQUESTS.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": "PREPARED", "failed_preserved": DIAGNOSTIC_PATH, "retry": RETRY_ID, "non_target_hashes": len(non_target)}, indent=2))


if __name__ == "__main__":
    main()
