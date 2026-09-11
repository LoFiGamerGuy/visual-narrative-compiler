"""Freeze a completed chapter's exact reading copy and hash-verified artwork."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--asset-root", type=Path, required=True)
    args = parser.parse_args()
    output = ROOT / "research/aws-editorial-20260910"
    output.mkdir(exist_ok=True)
    snapshot_path = ROOT / "production/nightglass-longform/reader/snapshot.json"
    snapshot = json.loads(snapshot_path.read_text())
    chapter = snapshot["chapters"][0]
    script_path = ROOT / chapter["script_path"]
    script_hash = hashlib.sha256(script_path.read_bytes()).hexdigest()
    if script_hash != chapter["script_sha256"]:
        raise ValueError("Reading snapshot and source script disagree")
    script = json.loads(script_path.read_text())
    by_id = {panel["id"]: panel for panel in script["panels"]}
    assets = output / "assets"
    assets.mkdir(exist_ok=True)
    panels = []
    for panel in chapter["panels"]:
        source = args.asset_root / panel["source"]
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        if digest != panel["sha256"]:
            raise ValueError("Source image differs from committed edition: " + panel["id"])
        destination = assets / (panel["id"] + ".png")
        if destination.exists():
            if hashlib.sha256(destination.read_bytes()).hexdigest() != digest:
                raise ValueError("Refusing to overwrite a different frozen image")
        else:
            shutil.copyfile(source, destination)
        s = by_id[panel["id"]]
        panels.append({"id": panel["id"], "action_intent": s["action"],
                       "state_intent": s.get("current_state", ""),
                       "reading_copy": panel["copy"], "lettering": panel.get("lettering", []),
                       "image_path": str(destination.relative_to(ROOT)),
                       "image_sha256": digest, "source_path": panel["source"]})
    packet = {"schema": "NarrativeEditorialPacket/1", "source_commit": "23704e1",
              "chapter": 1, "title": chapter["title"],
              "script_sha256": script_hash,
              "reading_snapshot_sha256": hashlib.sha256(snapshot_path.read_bytes()).hexdigest(),
              "owner_acceptance": None, "panels": panels,
              "evidence_rule": "Action/state fields describe intent. Only attached images establish rendered visual facts."}
    (output / "packet.json").write_text(json.dumps(packet, indent=2) + "\n")
    print(json.dumps({"status": "prepared_not_evaluated", "panels": len(panels),
                      "hash_verified_images": len(panels), "packet": str(output / "packet.json")}, indent=2))


if __name__ == "__main__": main()
