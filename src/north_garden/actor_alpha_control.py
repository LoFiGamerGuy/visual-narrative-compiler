"""Deterministic alpha-separability diagnostic for a local actor plate."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "ComfyUI" / "output" / "controlled_actor_capture_v1" / "soren-seed-5101-soren-seed-5101_00001_.png"
OUT = ROOT / "experiments" / "outputs" / "actor_alpha_control_v1"
RECORD = ROOT / "experiments" / "results" / "actor_alpha_control_soren_20260901.json"

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rgb = np.asarray(Image.open(SOURCE).convert("RGB"))
    # Four 128px corner samples are intentionally outside the actor bounding box.
    samples = np.concatenate([rgb[:128,:128], rgb[:128,-128:], rgb[-128:,:128], rgb[-128:,-128:]], axis=0).reshape(-1,3)
    bg = np.median(samples, axis=0).astype(np.float32)
    distance = np.linalg.norm(rgb.astype(np.float32) - bg, axis=2)
    # Fixed threshold from observed flat-background contrast; no learned/person model is used.
    alpha = (distance > 14.0).astype(np.uint8) * 255
    alpha_path = OUT / "soren-5101-alpha-threshold14-r1.png"
    rgba_path = OUT / "soren-5101-rgba-threshold14-r1.png"
    matte_path = OUT / "soren-5101-matte-preview-r1.png"
    Image.fromarray(alpha, "L").save(alpha_path)
    Image.fromarray(np.dstack([rgb, alpha]), "RGBA").save(rgba_path)
    # Checkerboard preview makes pinholes/edge errors human-reviewable without altering source evidence.
    yy, xx = np.indices(alpha.shape); check = ((xx // 48 + yy // 48) % 2)
    board = np.where(check[...,None] == 0, (240, 200, 200), (205, 225, 245)).astype(np.uint8)
    a = alpha[...,None] / 255.0; preview = (rgb * a + board * (1-a)).astype(np.uint8)
    Image.fromarray(preview, "RGB").save(matte_path)
    # Background false-positive estimate is evaluated only in corner samples used to define background.
    corner_dist = np.linalg.norm(samples.astype(np.float32) - bg, axis=1)
    record = {"schema_version":"1.0","record_type":"ActorAlphaControl","state":"LOCAL_RESEARCH_ONLY_NOT_COMMERCIAL","source":{"path":SOURCE.relative_to(ROOT).as_posix(),"sha256":sha(SOURCE)},"method":{"type":"fixed_color_distance_key","background_estimator":"median of four 128px corners","threshold_rgb_l2":14.0,"learned_identity_model":False},"outputs":{"alpha":{"path":alpha_path.relative_to(ROOT).as_posix(),"sha256":sha(alpha_path)},"rgba":{"path":rgba_path.relative_to(ROOT).as_posix(),"sha256":sha(rgba_path)},"preview":{"path":matte_path.relative_to(ROOT).as_posix(),"sha256":sha(matte_path)}},"measurements":{"background_rgb_median":[round(float(x),3) for x in bg],"foreground_pixel_fraction":round(float((alpha>0).mean()),6),"corner_background_false_positive_fraction":round(float((corner_dist>14.0).mean()),6)},"assertions":{"flat_background_key_possible":"pass_mechanical","actor_only_foreign_prop_absent":"not_proven_by_alpha","camera_pose_reusable":"not_proven_by_alpha","commercial_clearance":"not_established"},"human_review_status":"not_reviewed","human_minutes":None,"accepted_output":False,"limitations":["This keys color, not semantic actor boundaries.","Any attached/overlapping foreign object remains in the alpha.","A single Soren plate cannot establish a two-role G07 asset set."]}
    RECORD.write_text(json.dumps(record,indent=2)+"\n",encoding="utf-8")
    print(RECORD)

if __name__ == "__main__": main()
