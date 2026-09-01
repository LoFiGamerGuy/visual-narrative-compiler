"""Build and validate provider-hidden, timed G07 human-review instrumentation."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from io import BytesIO
from pathlib import Path
from typing import Any

from PIL import Image

from review_session import ReviewSessionError, append_event, start_session, validate_session
from validate_g07_evidence_vault import MANIFEST, ROOT, build_snapshot, canonical_sha256


PACKET_DIR = ROOT / "experiments/review-packets/g07-blinded-human-review-r1"
PACKET_PATH = PACKET_DIR / "review-packet.json"
PROTOCOL_PATH = ROOT / "config/g07-blinded-human-review-protocol-r1.json"

CASES = {
    "independent-01": {"code": "I1", "control": "public-controls/g07a-role-id-r1.png"},
    "independent-02": {"code": "I2", "control": "public-controls/g07a-role-id-r1.png"},
    "target-change": {"code": "TC", "control": "public-controls/g07a-role-id-r1.png"},
    "no-change": {"code": "NC", "control": "public-controls/g07a-no-change-r1.png"},
}

COMMON_ASSERTIONS = [
    "proxy_role_count_exactly_two",
    "orange_proxy_is_left_role",
    "right_proxy_has_case_expected_color",
    "both_roles_share_one_table_set",
    "roles_do_not_contact_or_merge",
    "no_salient_undeclared_object",
    "no_generated_role_label_or_stray_text",
]

CASE_ASSERTIONS = {
    "independent-01": ["scene_blocking_is_legible"],
    "independent-02": ["scene_blocking_is_legible"],
    "target-change": [
        "right_proxy_changes_teal_to_green",
        "orange_proxy_is_preserved",
        "shared_set_and_blocking_are_preserved",
    ],
    "no-change": [
        "right_proxy_remains_teal",
        "orange_proxy_is_preserved",
        "shared_set_and_blocking_are_preserved",
        "no_unrequested_visual_change_is_observed",
    ],
}

PAIR_ASSERTIONS = [
    "role_count_consistent_across_repeat",
    "role_order_consistent_across_repeat",
    "shared_set_and_blocking_consistent_across_repeat",
    "uncontrolled_visual_variation_is_explicitly_noted",
]

FORBIDDEN_IDENTITY_TOKENS = [
    "openai", "gemini", "google", "grok", "xai", "black forest", "bfl", "flux",
    "openai_gpt_image_2", "gemini_3_1_flash_image", "grok_imagine_image_2", "bfl_flux_2",
    "request_id", "cost_usd", "experiments/outputs/",
]


class ReviewProtocolError(RuntimeError):
    """Blinded review protocol construction or validation failure."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReviewProtocolError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def neutral_png(source: Path) -> tuple[bytes, str, int, int]:
    with Image.open(source) as image:
        rgb = image.convert("RGB")
        width, height = rgb.size
        pixel_digest = sha256_bytes(width.to_bytes(4, "big") + height.to_bytes(4, "big") + rgb.tobytes())
        output = BytesIO()
        rgb.save(output, format="PNG", compress_level=6, optimize=False)
    return output.getvalue(), pixel_digest, width, height


def candidate_sources(manifest: dict[str, Any]) -> dict[str, dict[str, dict[str, Any]]]:
    sources: dict[str, dict[str, dict[str, Any]]] = {case: {} for case in CASES}
    for record in manifest["records"]:
        if not record["candidate"]:
            continue
        filename = Path(record["path"]).stem
        case = filename.removeprefix("g07a-")
        require(case in CASES, f"unexpected review case: {case}")
        sources[case][record["adapter_id"]] = record["candidate"]
    require(all(len(by_adapter) == 4 for by_adapter in sources.values()), "each review case must have four provider candidates")
    return sources


def stable_order(values: list[str], *, vault_root: str, namespace: str) -> list[str]:
    return sorted(values, key=lambda value: sha256_bytes(f"{vault_root}|{namespace}|{value}".encode("utf-8")))


def write_if_absent_or_equal(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        require(path.read_bytes() == data, f"existing review artifact differs; refusing overwrite: {path.relative_to(ROOT)}")
    else:
        path.write_bytes(data)


def build_packet(manifest: dict[str, Any], *, write: bool) -> tuple[dict[str, Any], dict[str, str]]:
    vault_root = manifest["integrity"]["vault_root_sha256"]
    sources = candidate_sources(manifest)
    subjects: list[dict[str, Any]] = []
    case_groups: list[dict[str, Any]] = []
    mapping: dict[str, str] = {}
    by_adapter_blinds: dict[str, dict[str, str]] = {}
    letters = "ABCD"
    for case, case_config in CASES.items():
        adapters = stable_order(list(sources[case]), vault_root=vault_root, namespace=f"case:{case}")
        blinds: list[str] = []
        for ordinal, adapter in enumerate(adapters):
            blind_id = f"G07-{case_config['code']}-{letters[ordinal]}"
            candidate = sources[case][adapter]
            source_path = ROOT / candidate["path"]
            require(sha256_bytes(source_path.read_bytes()) == candidate["sha256"], f"candidate source changed: {candidate['path']}")
            presentation_bytes, pixel_digest, width, height = neutral_png(source_path)
            presentation_path = PACKET_DIR / "candidates" / f"{blind_id}.png"
            if write:
                write_if_absent_or_equal(presentation_path, presentation_bytes)
            subject = {
                "record_id": blind_id,
                "subject_kind": "candidate",
                "case": case,
                "presentation_path": presentation_path.relative_to(ROOT).as_posix(),
                "presentation_sha256": sha256_bytes(presentation_bytes),
                "decoded_rgb_sha256": pixel_digest,
                "width": width,
                "height": height,
                "required_assertion_ids": COMMON_ASSERTIONS + CASE_ASSERTIONS[case],
            }
            subjects.append(subject)
            blinds.append(blind_id)
            mapping[blind_id] = adapter
            by_adapter_blinds.setdefault(adapter, {})[case] = blind_id
        case_groups.append({
            "case": case,
            "control_path": case_config["control"],
            "blind_candidate_ids_in_presentation_order": blinds,
        })

    pair_groups: list[dict[str, Any]] = []
    pair_subjects: list[dict[str, Any]] = []
    pair_adapters = stable_order(list(by_adapter_blinds), vault_root=vault_root, namespace="repeat-pairs")
    for ordinal, adapter in enumerate(pair_adapters):
        pair_id = f"G07-RP-{letters[ordinal]}"
        member_ids = [by_adapter_blinds[adapter]["independent-01"], by_adapter_blinds[adapter]["independent-02"]]
        descriptor = {
            "record_type": "G07BlindedRepeatPair",
            "schema_version": "1.0",
            "pair_id": pair_id,
            "member_blind_ids": member_ids,
            "required_assertion_ids": PAIR_ASSERTIONS,
        }
        descriptor_bytes = (json.dumps(descriptor, indent=2, sort_keys=True) + "\n").encode("utf-8")
        descriptor_path = PACKET_DIR / "pairs" / f"{pair_id}.json"
        if write:
            write_if_absent_or_equal(descriptor_path, descriptor_bytes)
        pair_groups.append({"pair_id": pair_id, "member_blind_ids": member_ids})
        pair_subjects.append({
            "record_id": pair_id,
            "subject_kind": "independent_repeat_pair",
            "presentation_path": descriptor_path.relative_to(ROOT).as_posix(),
            "presentation_sha256": sha256_bytes(descriptor_bytes),
            "required_assertion_ids": PAIR_ASSERTIONS,
        })
        mapping[pair_id] = adapter

    all_subjects = subjects + pair_subjects
    packet_core = {
        "record_type": "G07BlindedHumanReviewPacket",
        "schema_version": "1.0",
        "packet_id": "g07-blinded-human-review-packet-r1",
        "state": "AWAITING_IDENTIFIED_HUMAN_REVIEW",
        "source_vault_root_sha256": vault_root,
        "provider_identity_disclosed_in_packet": False,
        "reviewer_id": None,
        "review_session_id": None,
        "human_minutes": None,
        "decision_count": 0,
        "accepted_subject_count": 0,
        "case_groups": case_groups,
        "repeat_pair_groups": pair_groups,
        "subjects": all_subjects,
        "decision_rule": {
            "coverage": "one timed immutable decision per subject",
            "candidate_acceptance": "all required assertions pass; failures must carry tags",
            "pair_interpretation": "repeat judgments describe observed consistency only; two samples do not establish a reproducibility rate",
        },
        "blinding_limit": "Provider names, source paths, request IDs, and costs are absent from this packet, but repository-aware reviewers could infer identity from source evidence; this is presentation blinding, not cryptographic secrecy.",
    }
    packet_core["assignment_root_sha256"] = canonical_sha256({
        "case_groups": case_groups,
        "repeat_pair_groups": pair_groups,
        "subjects": all_subjects,
    })
    packet_core["packet_sha256"] = canonical_sha256(packet_core)
    return packet_core, mapping


def build_protocol(packet: dict[str, Any]) -> dict[str, Any]:
    return {
        "record_type": "G07BlindedHumanReviewProtocol",
        "schema_version": "1.0",
        "protocol_id": "g07-blinded-human-review-protocol-r1",
        "source_vault_root_sha256": packet["source_vault_root_sha256"],
        "packet_sha256": packet["packet_sha256"],
        "assignment_root_sha256": packet["assignment_root_sha256"],
        "case_order": list(CASES),
        "candidate_subjects": 16,
        "repeat_pair_subjects": 4,
        "total_decisions_required": 20,
        "common_candidate_assertion_ids": COMMON_ASSERTIONS,
        "case_specific_assertion_ids": CASE_ASSERTIONS,
        "repeat_pair_assertion_ids": PAIR_ASSERTIONS,
        "timing": "Use append-only TimedHumanReviewSession START/PAUSE/RESUME/COMPLETE events; never type minutes manually.",
        "deblinding": "Map blind IDs to provider arms only after a complete valid session; never expose mapping in the presentation packet.",
        "acceptance_boundary": "Candidate acceptance is separate from mechanism selection, commercial clearance, and production/upload authority.",
    }


def packet_errors(packet: dict[str, Any], expected: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if packet != expected:
        errors.append("packet differs from deterministic assignment")
    serialized = json.dumps(packet, sort_keys=True).lower()
    if any(token in serialized for token in FORBIDDEN_IDENTITY_TOKENS):
        errors.append("provider identity or execution metadata leaks into packet")
    if packet.get("state") != "AWAITING_IDENTIFIED_HUMAN_REVIEW":
        errors.append("packet review state changed")
    if any(packet.get(field) is not None for field in ("reviewer_id", "review_session_id", "human_minutes")):
        errors.append("packet invents review identity/session/minutes")
    if packet.get("decision_count") != 0 or packet.get("accepted_subject_count") != 0:
        errors.append("packet invents decisions or acceptance")
    return sorted(set(errors))


def session_subjects(packet: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {"record_id": item["record_id"], "path": item["presentation_path"], "sha256": item["presentation_sha256"]}
        for item in packet["subjects"]
    ]


def synthetic_session(packet: dict[str, Any]) -> dict[str, Any]:
    session = start_session(
        session_id="SYNTHETIC-G07-REVIEW-SESSION-R1",
        reviewer_id="SYNTHETIC_VALIDATOR_NOT_HUMAN",
        subjects=session_subjects(packet),
        started_at="2026-09-01T18:00:00Z",
        validation_fixture=True,
    )
    decisions = []
    by_id = {item["record_id"]: item for item in packet["subjects"]}
    for subject in session["subjects"]:
        required = by_id[subject["record_id"]]["required_assertion_ids"]
        decisions.append({
            "subject_record_id": subject["record_id"],
            "accepted": False,
            "hard_assertions": [{"assertion_id": item, "passed": False} for item in required],
            "failure_tags": ["synthetic_validation_only"],
        })
    return append_event(session, event_type="COMPLETE", occurred_at="2026-09-01T18:20:00Z", data={"decisions": decisions})


def g07_session_errors(session: dict[str, Any], packet: dict[str, Any]) -> list[str]:
    errors = validate_session(session)
    if session.get("subjects") != session_subjects(packet):
        errors.append("session subjects or order differ from packet")
    if session.get("state") == "COMPLETED":
        decisions = session["events"][-1].get("data", {}).get("decisions", [])
        expected_assertions = {item["record_id"]: item["required_assertion_ids"] for item in packet["subjects"]}
        for decision in decisions:
            actual = [item.get("assertion_id") for item in decision.get("hard_assertions", [])]
            if actual != expected_assertions.get(decision.get("subject_record_id")):
                errors.append("decision assertions incomplete or reordered")
        if session.get("validation_fixture") and session.get("summary", {}).get("review_evidence_eligible"):
            errors.append("validation fixture became eligible review evidence")
    return sorted(set(errors))


def mutation_checks(packet: dict[str, Any], synthetic: dict[str, Any]) -> tuple[int, int]:
    packet_mutations: list[dict[str, Any]] = []
    changed = copy.deepcopy(packet); changed["subjects"][0]["provider"] = "openai"; packet_mutations.append(changed)
    changed = copy.deepcopy(packet); changed["subjects"][0], changed["subjects"][1] = changed["subjects"][1], changed["subjects"][0]; packet_mutations.append(changed)
    changed = copy.deepcopy(packet); changed["subjects"].pop(); packet_mutations.append(changed)
    changed = copy.deepcopy(packet); changed["subjects"][0]["presentation_sha256"] = "0" * 64; packet_mutations.append(changed)
    changed = copy.deepcopy(packet); changed["case_groups"][0]["blind_candidate_ids_in_presentation_order"].pop(); packet_mutations.append(changed)
    changed = copy.deepcopy(packet); changed["repeat_pair_groups"][0]["member_blind_ids"][0] = "G07-I1-Z"; packet_mutations.append(changed)
    changed = copy.deepcopy(packet); changed["subjects"][0]["required_assertion_ids"].pop(); packet_mutations.append(changed)
    changed = copy.deepcopy(packet); changed["assignment_root_sha256"] = "f" * 64; packet_mutations.append(changed)
    changed = copy.deepcopy(packet); changed["reviewer_id"] = "invented"; packet_mutations.append(changed)
    rejected = sum(bool(packet_errors(item, packet)) for item in packet_mutations)

    session_mutations: list[dict[str, Any]] = []
    changed = copy.deepcopy(synthetic); changed["events"][-1]["data"]["decisions"].pop(); session_mutations.append(changed)
    changed = copy.deepcopy(synthetic); changed["summary"]["human_minutes"] = 999; session_mutations.append(changed)
    changed = copy.deepcopy(synthetic); changed["subjects"][0], changed["subjects"][1] = changed["subjects"][1], changed["subjects"][0]; session_mutations.append(changed)
    changed = copy.deepcopy(synthetic); changed["events"][-1]["data"]["decisions"][0]["hard_assertions"].pop(); session_mutations.append(changed)
    rejected += sum(bool(g07_session_errors(item, packet)) for item in session_mutations)
    return rejected, len(packet_mutations) + len(session_mutations)


def validate_presentation_files(packet: dict[str, Any]) -> None:
    for subject in packet["subjects"]:
        path = ROOT / subject["presentation_path"]
        require(path.is_file(), f"review presentation missing: {subject['presentation_path']}")
        data = path.read_bytes()
        require(sha256_bytes(data) == subject["presentation_sha256"], f"review presentation hash mismatch: {subject['record_id']}")
        if subject["subject_kind"] == "candidate":
            with Image.open(BytesIO(data)) as image:
                rgb = image.convert("RGB")
                digest = sha256_bytes(rgb.width.to_bytes(4, "big") + rgb.height.to_bytes(4, "big") + rgb.tobytes())
            require(digest == subject["decoded_rgb_sha256"], f"review presentation pixels changed: {subject['record_id']}")
        else:
            descriptor = json.loads(data)
            require(descriptor["pair_id"] == subject["record_id"], f"repeat descriptor mismatch: {subject['record_id']}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true", help="create neutral presentation artifacts if absent")
    parser.add_argument("--emit-protocol", type=Path, help="write deterministic tracked protocol metadata")
    args = parser.parse_args()
    try:
        actual_vault = build_snapshot()
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        require(actual_vault == manifest, "G07 vault differs before review packet build")
        expected_packet, mapping = build_packet(manifest, write=args.build)
        require(len(mapping) == 20, "blind mapping must cover 20 subjects")
        if args.build:
            packet_bytes = (json.dumps(expected_packet, indent=2, sort_keys=True) + "\n").encode("utf-8")
            write_if_absent_or_equal(PACKET_PATH, packet_bytes)
        require(PACKET_PATH.is_file(), "blinded review packet missing; run with --build")
        packet = json.loads(PACKET_PATH.read_text(encoding="utf-8"))
        errors = packet_errors(packet, expected_packet)
        require(not errors, "; ".join(errors))
        validate_presentation_files(packet)
        protocol = build_protocol(packet)
        if args.emit_protocol:
            output = args.emit_protocol if args.emit_protocol.is_absolute() else ROOT / args.emit_protocol
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json.dumps(protocol, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
            print(f"wrote {output.relative_to(ROOT).as_posix()}")
        else:
            tracked_protocol = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
            require(tracked_protocol == protocol, "tracked blinded-review protocol differs")
        fixture = synthetic_session(packet)
        require(not g07_session_errors(fixture, packet), "synthetic timed session does not validate")
        rejected, total = mutation_checks(packet, fixture)
        require(rejected == total, "review mutation rejection incomplete")
    except (ReviewProtocolError, ReviewSessionError, FileNotFoundError, KeyError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("0 failures, 0 warnings")
    print("16/16 provider-hidden candidate presentations and 4/4 repeat pairs verified")
    print("20 timed decisions required; 0 real decisions, null human minutes, 0 accepted")
    print(f"{rejected}/{total} identity/order/coverage/timing/assertion mutations rejected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
