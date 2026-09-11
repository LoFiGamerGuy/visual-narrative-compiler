from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
VOLUME = ROOT / "production" / "reimaginings" / "ember-lattice" / "volume"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("chapter", choices=[f"ch{i:02d}" for i in range(1, 11)])
    parser.add_argument("notes")
    args = parser.parse_args()
    path = VOLUME / "generation-requests.json"
    document = json.loads(path.read_text(encoding="utf-8"))
    rows = [row for row in document["requests"] if row["chapter"] == args.chapter]
    pending = [row for row in rows if row["review_status"] == "GENERATED_PENDING_REVIEW"]
    unexpected = [row["request_id"] for row in rows if row["review_status"] not in {"GENERATED_PENDING_REVIEW", "HARD_FAIL_PRESERVED_DIAGNOSTIC"}]
    if len(pending) != (8 if args.chapter == "ch01" else 24) or unexpected:
        raise SystemExit(f"cannot mark {args.chapter}: pending={len(pending)}, unexpected={unexpected}")
    for row in pending:
        row["review_status"] = "REVIEWED_PASS"
        row["visual_review"] = {
            "reviewer": "primary_agent_local_visual_inspection",
            "date": date.today().isoformat(),
            "method": "chapter source contact sheet plus original-size spot checks",
            "notes": args.notes,
            "repair_request": None,
        }
    path.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"chapter": args.chapter, "reviewed_pass": len(pending), "preserved_diagnostics": len(rows) - len(pending), "notes": args.notes}))


if __name__ == "__main__":
    main()
