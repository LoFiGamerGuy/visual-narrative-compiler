from __future__ import annotations

import argparse
import atexit
import hashlib
import json
import msvcrt
import shutil
import time
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[3]
REQUESTS = ROOT / "production" / "reimaginings" / "ember-lattice" / "volume" / "generation-requests.json"
LOCK = ROOT / "experiments" / "reimaginings" / "ember-lattice" / ".generation-requests.lock"


def acquire_lock():
    LOCK.parent.mkdir(parents=True, exist_ok=True)
    handle = LOCK.open("a+b")
    if handle.tell() == 0:
        handle.write(b"0")
        handle.flush()
    while True:
        try:
            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            break
        except OSError:
            time.sleep(.1)
    def release() -> None:
        try:
            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        finally:
            handle.close()
    atexit.register(release)
    return handle


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("request_id")
    parser.add_argument("generated_source")
    parser.add_argument("elapsed_seconds", type=float)
    args = parser.parse_args()
    lock_handle = acquire_lock()

    document = json.loads(REQUESTS.read_text(encoding="utf-8"))
    request = next(row for row in document["requests"] if row["request_id"] == args.request_id)
    source = Path(args.generated_source).resolve()
    target = (ROOT / request["output_path"]).resolve()
    if ROOT not in target.parents:
        raise SystemExit(f"unsafe output path: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        raise SystemExit(f"refusing to overwrite generated source: {target}")
    shutil.copy2(source, target)

    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    with Image.open(target) as image:
        dimensions = {"width": image.width, "height": image.height}
    request.update({
        "measured_elapsed_seconds": round(args.elapsed_seconds, 3),
        "model": "imagegen-default",
        "endpoint": "built-in-image_gen",
        "provider_request_id": source.stem,
        "usage": None,
        "monetary_cost": 0,
        "seed": None,
        "review_status": "GENERATED_PENDING_REVIEW",
        "failure_classes": [],
        "sha256": digest,
        "dimensions": dimensions,
    })
    REQUESTS.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"request_id": args.request_id, "output_path": request["output_path"], "sha256": digest, **dimensions}))


if __name__ == "__main__":
    main()
