"""Compile the preflight-only S01 matched reference-ablation control."""
from __future__ import annotations

import json

from compile_ch05_s11_matched_reference_ablation_prompt import (
    ROOT,
    compile_ablation,
    sha256,
)

OUTPUT = ROOT / "production/comic/run-manifests/ch05-s01-flat-gouache-reference-ablation-prompt-r1.json"
TARGET = "flat-graphic-gouache-s01-opening-departure"
PLANNED_OUTPUT = (
    "experiments/review-packets/ch05-s01-flat-gouache-reference-ablation-r1/"
    "s01-opening-departure-flat-gouache-no-reference-r1.png"
)


def main() -> int:
    document = compile_ablation(
        target=TARGET,
        output=OUTPUT,
        record_type="CH05S01MatchedReferenceAblationPrompt",
        record_id="ng-ch05-s01-flat-gouache-reference-ablation-prompt-r1",
        ablation_sequence_id="flat-gouache-reference-ablation-s01-opening-departure",
        planned_output=PLANNED_OUTPUT,
        sequence_label="S01",
    )
    print(
        json.dumps(
            {
                "output": OUTPUT.relative_to(ROOT).as_posix(),
                "sha256": sha256(OUTPUT),
                "prompt_sha256": document["sequence"]["prompt_sha256"],
                "panel_count": document["sequence"]["panel_count"],
                "reference_uploads": document["boundary"]["reference_uploads"],
                "changed_prompt_lines": len(document["comparison_contract"]["changed_prompt_line_indexes_zero_based"]),
                "current_executions": document["boundary"]["current_executions"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
