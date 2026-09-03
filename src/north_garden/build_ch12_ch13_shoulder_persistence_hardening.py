"""Build the text-only CH12-CH13 irreversible-state hardening packet."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from build_ch06_default_route_review import (
    font,
    labeled_canvas,
    rel,
    sha256,
    stack,
)
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
PACKET_DIR = ROOT / "experiments/review-packets/ch12-ch13-shoulder-persistence-hardening-r1"
SOURCE = PACKET_DIR / "source/ng-ch12-ch13-shoulder-persistence-r1.png"
PROMPT_MANIFEST = ROOT / "production/comic/run-manifests/ch12-ch13-shoulder-persistence-hardening-prompt-r1.json"
EXECUTION = ROOT / "production/comic/run-manifests/ch12-ch13-shoulder-persistence-hardening-execution-r1.json"
REVIEW = ROOT / "production/comic/run-manifests/ch12-ch13-shoulder-persistence-hardening-review-r1.json"
TARGETS = (
    ("ng-ch12-sc01-p036", "ch12"),
    ("ng-ch12-sc01-p038", "ch12"),
    ("ng-ch13-sc01-p020", "ch13"),
    ("ng-ch13-sc01-p031", "ch13"),
    ("ng-ch13-sc01-p036", "ch13"),
)
PROMPT = """Create exactly ONE wide horizontal comic sequence strip containing exactly FIVE clearly separated panels in one left-to-right row. No title, no captions, no dialogue, no lettering, no symbols that resemble text, and no panel numbers. Mature clear-line adventure webcomic art with restrained painterly color, practical realistic anatomy, strong silhouettes, clear hands, wet stone/root/brass environments, and phone-readable causal action. All people are clearly fictional adults with mature proportions and practical non-sexualized clothing. This is a narrow continuity-repair diagnostic spanning two consecutive chapters; preserve the SAME two adult protagonists across all five panels: Soren is a rugged adult man in his thirties with tousled dark-blond/light-brown hair and short stubble, pale oatmeal work coat, rigid metal-and-leather left lower-leg brace, and a simple long wooden polehook named Warden's Reach with a fused brass key/socket at its head—never a gun. Sigrid is a capable adult woman in her thirties with dark near-black hair tied in the same practical low knot, grey layers, shortened dark blue-brown plaid wrap whose sacrificed strips remain tied as route flags, compact wooden bow, and utility seax. CRITICAL IRREVERSIBLE STATE IN EVERY PANEL WHERE SOREN APPEARS: the LEFT SHOULDER OUTER PANEL of his oatmeal coat is physically missing because it was cut away earlier for a gate splint. Show a clearly visible rough cut seam and exposed dark inner work layer at that left shoulder. Do not restore a sleeve cap or matching oatmeal shoulder panel. No blood, no gore, no fresh wound, and do not remove his arm. This is garment loss, not amputation. Panel 1: CH12 sealed North Garden gate, Soren and Sigrid stand full figure in mutual assent; compose so Soren's missing left coat shoulder is unmistakably visible, his braced leg bears limited weight, fused polehook present. Panel 2: close two-shot at the gate, their hands meet around separate load and route controls without romance posing; Soren's missing left coat shoulder remains visible and Sigrid's shortened plaid route flags remain visible. Panel 3: inside a moving glasshouse, Soren and Sigrid redirect a heavy stream through a root-and-brass doorway using polehook leverage and a taut bow line; Soren's missing left shoulder remains visible during causal action. Panel 4: at the boundary heart, Soren seats the fused polehook in a brass socket while transferring load through a waist line to a stone column because his leg brace buckles; missing left shoulder remains visible, no healing. Panel 5: large climax reveal from behind the pair: Crownroot is a vast NON-HUMANOID botanical-and-architectural guardian made of interlocked roots, irrigation pipes, arches, valves, and flowing water. Crownroot must have NO human face, NO human head, NO human torso, NO eyes, and NO mask-like relief; its identity comes from a radial root knot and seven water channels. Soren's missing left oatmeal shoulder panel is still visibly absent from the rear. Preserve clear top/side negative space for later local lettering without covering faces, bodies, hands, polehook, bow, controls, root knot, or water channels. The five panels must be distinct and must remain in the exact stated order."""


def prompt_hash() -> str:
    return hashlib.sha256(PROMPT.encode("utf-8")).hexdigest()


def dark_gutter_boxes(image: Image.Image) -> tuple[list[list[int]], list[list[int]]]:
    gray = image.convert("L")
    width, height = gray.size
    pixels = gray.load()
    dark_columns = [x for x in range(width) if sum(pixels[x, y] < 16 for y in range(height)) / height > 0.94]
    clusters: list[list[int]] = []
    for value in dark_columns:
        if not clusters or value > clusters[-1][1] + 1:
            clusters.append([value, value])
        else:
            clusters[-1][1] = value
    internal = [row for row in clusters if row[0] > 12 and row[1] < width - 13]
    if len(internal) != 4:
        raise ValueError(f"expected four internal dark gutters, got {clusters}")
    boxes = []
    left = 0
    for start, end in internal:
        boxes.append([left, 0, start, height])
        left = end + 1
    boxes.append([left, 0, width, height])
    return boxes, clusters


def pair_row(original: Image.Image, repair: Image.Image, label: str) -> Image.Image:
    left = labeled_canvas(original.convert("RGB"), f"{label} · BASELINE FAIL", 570, 34)
    right = labeled_canvas(repair.convert("RGB"), f"{label} · TEXT-ONLY HARDENING", 570, 34)
    height = max(left.height, right.height)
    row = Image.new("RGB", (1200, height), "#11151b")
    row.paste(left, (15, 0))
    row.paste(right, (615, 0))
    return row


def main() -> int:
    PACKET_DIR.mkdir(parents=True, exist_ok=True)
    crop_dir = PACKET_DIR / "crops"
    crop_dir.mkdir(parents=True, exist_ok=True)
    with Image.open(SOURCE) as opened:
        source = opened.convert("RGB")
    boxes, gutters = dark_gutter_boxes(source)
    prompt_doc = {
        "record_type": "ComicTargetedHardeningPromptManifest",
        "schema_version": "1.0",
        "record_id": "ng-ch12-ch13-shoulder-persistence-hardening-prompt-r1",
        "state": "EXECUTED",
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "mechanism": "OPENAI_BUILT_IN_IMAGEGEN_TEXT_ONLY",
        "request": {
            "request_id": "ng-ch12-ch13-shoulder-persistence-r1",
            "target_panel_ids": [panel_id for panel_id, _ in TARGETS],
            "exact_prompt": PROMPT,
            "prompt_sha256": prompt_hash(),
            "reference_images": [],
            "reference_uploads": 0,
        },
        "authority": {"new_provider": False, "paid_api": False, "cloud_gpu": False, "output_reupload": False},
    }
    PROMPT_MANIFEST.write_text(json.dumps(prompt_doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")

    candidates = []
    pair_rows = []
    for (panel_id, chapter), box in zip(TARGETS, boxes, strict=True):
        repair = source.crop(tuple(box))
        repair_path = crop_dir / f"{panel_id}-shoulder-persistence-r1.png"
        repair.save(repair_path, format="PNG", compress_level=9)
        original_path = ROOT / f"experiments/review-packets/{chapter}-default-house-route-r1/crops/{panel_id}-default-r1.png"
        with Image.open(original_path) as opened:
            original = opened.convert("RGB")
        pair_rows.append(pair_row(original, repair, panel_id.upper()))
        candidates.append(
            {
                "candidate_id": f"ng-candidate-{panel_id}-shoulder-persistence-r1",
                "target_panel_id": panel_id,
                "source_box": box,
                "path": rel(repair_path),
                "sha256": sha256(repair_path),
                "dimensions": [repair.width, repair.height],
                "triage": "PASS",
                "failure_classes": [],
                "note": "Missing left oatmeal shoulder panel remains visibly absent; owner review and assembly disposition remain pending.",
                "accepted": False,
                "commercially_cleared": False,
                "exact_production_base": False,
            }
        )

    comparison = PACKET_DIR / "ch12-ch13-shoulder-persistence-comparison-r1.png"
    stack(pair_rows, 1200, 12, "#11151b").save(comparison, format="PNG", compress_level=9)
    source_review = PACKET_DIR / "ch12-ch13-shoulder-persistence-strip-r1.png"
    banner = Image.new("RGB", (source.width, source.height + 48), "#11151b")
    ImageDraw.Draw(banner).text((12, 12), "CH12–CH13 · irreversible shoulder-state text-only hardening", fill="#e9edf2", font=font(20))
    banner.paste(source, (0, 48))
    banner.save(source_review, format="PNG", compress_level=9)

    execution = {
        "record_type": "ComicTargetedHardeningExecution",
        "schema_version": "1.0",
        "record_id": "ng-ch12-ch13-shoulder-persistence-hardening-execution-r1",
        "state": "AGENT_TRIAGED_OWNER_REVIEW_PENDING",
        "prompt_manifest": {"path": rel(PROMPT_MANIFEST), "sha256": sha256(PROMPT_MANIFEST)},
        "render_record": {
            "request_id": "ng-ch12-ch13-shoulder-persistence-r1",
            "exact_prompt": PROMPT,
            "prompt_sha256": prompt_hash(),
            "input_references": [],
            "output": {"path": rel(SOURCE), "sha256": sha256(SOURCE), "dimensions": [source.width, source.height]},
            "crop_method": {"method": "DETERMINISTIC_DARK_VERTICAL_GUTTER_DETECTION", "clusters_inclusive": gutters},
            "client_observed_elapsed_seconds": 108.2,
            "model": None,
            "endpoint": None,
            "provider_request_id": None,
            "provider_usage": None,
            "monetary_cost_usd": None,
            "deterministic_seed": None,
            "unavailable_fields": ["model", "endpoint", "provider_request_id", "provider_usage", "monetary_cost_usd", "deterministic_seed"],
            "reproducible": False,
        },
        "candidates": candidates,
        "summary": {"targets": 5, "candidates": 5, "triage": {"PASS": 5, "WARN": 0, "FAIL": 0}, "reference_uploads": 0, "paid_api_cloud_spend_usd": "0.000000"},
        "limitations": [
            "One strip tests within-call persistence; it does not prove state persistence across independent calls.",
            "Text-only generation avoids a contradictory intact-shoulder reference but weakens identity reproducibility.",
            "No diagnostic candidate is assembled, accepted, rights-cleared, commercially cleared, or an exact production base.",
        ],
    }
    EXECUTION.write_text(json.dumps(execution, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")

    artifacts = []
    for kind, path in (("repair_strip", source_review), ("baseline_repair_comparison", comparison)):
        with Image.open(path) as opened:
            dimensions = [opened.width, opened.height]
        artifacts.append({"type": kind, "path": rel(path), "sha256": sha256(path), "dimensions": dimensions})
    review: dict[str, Any] = {
        "record_type": "ComicTargetedHardeningReviewPacket",
        "schema_version": "1.0",
        "record_id": "ng-ch12-ch13-shoulder-persistence-hardening-review-r1",
        "state": "OWNER_REVIEW_PENDING",
        "execution": {"path": rel(EXECUTION), "sha256": sha256(EXECUTION)},
        "summary": execution["summary"],
        "artifacts": artifacts,
    }
    REVIEW.write_text(json.dumps(review, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"artifacts": 2, "candidates": 5, "elapsed": 108.2, "triage": execution["summary"]["triage"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
