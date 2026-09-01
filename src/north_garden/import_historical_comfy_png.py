"""Import immutable provenance available inside historical ComfyUI PNG metadata.

The importer never reconstructs missing timings or claims byte-identical replay.
It preserves the embedded workflow graph as evidence and makes its limitations
explicit for archival production records.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", action="append", required=True, type=Path)
    parser.add_argument("--adapter", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    output: list[dict[str, object]] = []
    for image_arg in args.image:
        image_path = image_arg.resolve()
        prompt_text = Image.open(image_path).info.get("prompt")
        if not isinstance(prompt_text, str):
            raise ValueError(f"{image_path} does not contain a ComfyUI PNG prompt metadata chunk")
        graph = json.loads(prompt_text)
        samplers = [node["inputs"] for node in graph.values() if node.get("class_type") == "KSampler"]
        model_nodes = [
            {"node_id": node_id, "class_type": node["class_type"], "inputs": node["inputs"]}
            for node_id, node in graph.items()
            if node.get("class_type") in {"UNETLoader", "CLIPLoader", "VAELoader", "LoraLoaderModelOnly"}
        ]
        output.append({
            "record_type": "HistoricalRenderRecord",
            "schema_version": "1.0",
            "record_id": f"historical-{args.adapter}-{image_path.stem}",
            "adapter": args.adapter,
            "candidate": {
                "path": str(image_path.relative_to(ROOT)).replace("\\", "/"),
                "sha256": sha256_file(image_path),
                "embedded_workflow_graph_sha256": sha256_bytes(prompt_text.encode("utf-8")),
            },
            "embedded_workflow": graph,
            "samplers": samplers,
            "model_nodes": model_nodes,
            "provenance_state": "HISTORICAL_EMBEDDED_WORKFLOW_AVAILABLE",
            "limitations": [
                "Historical wall-clock generation time, candidate count, and human-review minutes were not recorded.",
                "Current local model hashes and runtime must not be retroactively attributed to this historical run.",
                "This record supports replay investigation but does not establish byte-identical reproducibility or commercial eligibility.",
            ],
            "imported_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        })
    output_path = args.output.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"imported {len(output)} historical ComfyUI records -> {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
