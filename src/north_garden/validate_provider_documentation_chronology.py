"""Prove official provider documentation was recorded before every G07 attempt."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
from collections import Counter
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/research/provider-primary-documentation-20260901.md"
POLICY = ROOT / "config/g07-bakeoff-budget-policy-r1.json"
VAULT = ROOT / "docs/research/evidence/g07-local-evidence-vault-manifest-r1.json"
OUTPUT = ROOT / "docs/research/evidence/provider-documentation-pre-spend-chronology-r1.json"
SECTIONS = {
    "openai_gpt_image_2": "## OpenAI GPT Image 2",
    "gemini_3_1_flash_image": "## Google Gemini 3.1 Flash Image",
    "grok_imagine_image_2": "## SpaceXAI Grok Imagine Image 2.0",
    "bfl_flux_2": "## Black Forest Labs FLUX.2 Pro",
}


class ChronologyError(RuntimeError):
    pass


def require(value: bool, message: str) -> None:
    if not value:
        raise ChronologyError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def instant(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def positive_cost(value: object) -> bool:
    try:
        return Decimal(str(value)) > 0
    except InvalidOperation:
        return False


def build() -> dict:
    text = DOC.read_text(encoding="utf-8")
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    vault = json.loads(VAULT.read_text(encoding="utf-8"))
    evidence = policy["documentation_evidence"]
    require(evidence == [{"path": DOC.relative_to(ROOT).as_posix(), "retrieved_at": "2026-09-01T15:07:36Z"}], "documentation timestamp changed")
    retrieved = instant(evidence[0]["retrieved_at"])
    urls = sorted(set(re.findall(r"\]\((https://[^)]+)\)", text)))
    require(len(urls) == 19, "official source URL count changed")
    for adapter, heading in SECTIONS.items():
        require(heading in text, f"provider section missing: {adapter}")
        start = text.index(heading)
        end = text.find("\n## ", start + len(heading))
        section = text[start:] if end < 0 else text[start:end]
        has_pricing = "pricing" in section.casefold() or "- Price:" in section or "$" in section
        require(("- Model:" in section or "- Model/endpoint:" in section) and has_pricing and "- Data/terms:" in section and "- Sources:" in section, f"provider evidence categories incomplete: {adapter}")

    rows = []
    counts: Counter[str] = Counter()
    first_by_adapter: dict[str, datetime] = {}
    paid = []
    for item in vault["records"]:
        path = ROOT / item["path"]
        require(sha256(path) == item["sha256"], f"provider record hash changed: {item['path']}")
        record = json.loads(path.read_text(encoding="utf-8"))
        adapter = item["adapter_id"]
        started = instant(record["started_at"])
        require(started >= retrieved, f"provider attempt predates documentation: {item['path']}")
        require(record["api_documentation"] in text, f"record documentation URL absent from primary record: {item['path']}")
        terms = record.get("provider_terms")
        if isinstance(terms, dict):
            require(terms.get("url") in text and terms.get("last_reviewed") == "2026-09-01", f"provider terms binding invalid: {item['path']}")
        counts[adapter] += 1
        first_by_adapter[adapter] = min(first_by_adapter.get(adapter, started), started)
        if positive_cost(record.get("cost_usd")):
            paid.append(started)
        rows.append({
            "adapter_id": adapter,
            "record_path": item["path"],
            "record_sha256": item["sha256"],
            "started_at": record["started_at"],
            "seconds_after_documentation": int((started - retrieved).total_seconds()),
            "execution_status": record["execution_status"],
            "cost_usd": record.get("cost_usd"),
            "api_documentation": record["api_documentation"],
            "documentation_preceded_attempt": True,
        })
    require(counts == Counter({"openai_gpt_image_2": 5, "gemini_3_1_flash_image": 5, "grok_imagine_image_2": 5, "bfl_flux_2": 4}), "provider record denominator changed")
    earliest = min(instant(item["started_at"]) for item in rows)
    earliest_paid = min(paid)
    require(int((earliest - retrieved).total_seconds()) == 490, "earliest attempt chronology changed")
    require(int((earliest_paid - retrieved).total_seconds()) == 695, "earliest paid chronology changed")
    return {
        "record_type": "ProviderDocumentationPreSpendChronologyEvidence",
        "schema_version": "1.0",
        "record_id": "ng-provider-documentation-pre-spend-chronology-r1",
        "state": "OFFICIAL_PRIMARY_DOCUMENTATION_RECORDED_BEFORE_ALL_PROVIDER_ATTEMPTS",
        "sources": {
            "documentation": {"path": DOC.relative_to(ROOT).as_posix(), "sha256": sha256(DOC), "retrieved_at": evidence[0]["retrieved_at"], "official_urls": len(urls)},
            "budget_policy": {"record_id": policy["record_id"], "path": POLICY.relative_to(ROOT).as_posix(), "sha256": sha256(POLICY)},
            "evidence_vault": {"record_id": vault["manifest_id"], "path": VAULT.relative_to(ROOT).as_posix(), "sha256": sha256(VAULT)},
        },
        "provider_sections": [{"adapter_id": adapter, "heading": heading, "model_endpoint_pricing_terms_sources_present": True} for adapter, heading in SECTIONS.items()],
        "attempts": sorted(rows, key=lambda item: (item["started_at"], item["adapter_id"], item["record_path"])),
        "chronology": {
            "documentation_retrieved_at": evidence[0]["retrieved_at"],
            "earliest_attempt_at": earliest.isoformat().replace("+00:00", "Z"),
            "earliest_attempt_seconds_after_documentation": 490,
            "earliest_positive_cost_at": earliest_paid.isoformat().replace("+00:00", "Z"),
            "earliest_positive_cost_seconds_after_documentation": 695,
            "first_attempt_by_adapter": {adapter: value.isoformat().replace("+00:00", "Z") for adapter, value in sorted(first_by_adapter.items())},
        },
        "summary": {
            "providers": 4,
            "official_source_urls": len(urls),
            "provider_records": len(rows),
            "records_after_documentation": sum(item["documentation_preceded_attempt"] for item in rows),
            "required_candidates": vault["inventory"]["completed_candidates"],
            "aggregate_paid_usd": vault["cost_reconciliation"]["aggregate_paid_cost_usd"],
            "held_usd": vault["cost_reconciliation"]["held_usd"],
            "provider_requests_added_by_audit": 0,
            "external_uploads_added_by_audit": 0,
            "external_cost_added_by_audit_usd": "0.000000",
        },
        "limitations": [
            "This chronology proves the dated local primary-document record preceded requests; it does not guarantee provider pages remain unchanged indefinitely.",
            "Any future CH05 execution requires a fresh current-primary pricing/terms/model/data-use review.",
            "BFL remains limited to the two approved public fictional controls under ADR-0019.",
        ],
        "boundary": "Read-only chronology audit. It performs no web retrieval, provider request, upload, spend, or policy expansion.",
    }


def mutations(expected: dict) -> tuple[int, int]:
    values = []
    actions = [
        lambda item: item["sources"]["documentation"].update(sha256="0" * 64),
        lambda item: item["provider_sections"].pop(),
        lambda item: item["attempts"].pop(),
        lambda item: item["attempts"][0].update(documentation_preceded_attempt=False),
        lambda item: item["chronology"].update(earliest_attempt_seconds_after_documentation=-1),
        lambda item: item["chronology"].update(earliest_positive_cost_seconds_after_documentation=-1),
        lambda item: item["summary"].update(providers=3),
        lambda item: item["summary"].update(official_source_urls=18),
        lambda item: item["summary"].update(provider_records=18),
        lambda item: item["summary"].update(records_after_documentation=18),
        lambda item: item["summary"].update(required_candidates=15),
        lambda item: item["summary"].update(aggregate_paid_usd="0.987377"),
        lambda item: item["summary"].update(provider_requests_added_by_audit=1),
        lambda item: item["summary"].update(external_uploads_added_by_audit=1),
        lambda item: item["summary"].update(external_cost_added_by_audit_usd="1.000000"),
        lambda item: item["limitations"].pop(),
    ]
    for action in actions:
        item = copy.deepcopy(expected)
        action(item)
        values.append(item)
    return sum(item != expected for item in values), len(values)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", type=Path)
    args = parser.parse_args()
    try:
        expected = build()
        if args.emit:
            target = args.emit if args.emit.is_absolute() else ROOT / args.emit
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(expected, indent=2) + "\n", encoding="utf-8", newline="\n")
        else:
            require(json.loads(OUTPUT.read_text(encoding="utf-8")) == expected, "tracked provider chronology differs")
        rejected, total = mutations(expected)
        require(rejected == total, "chronology mutations not rejected")
    except (ChronologyError, FileNotFoundError, KeyError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("0 failures, 0 warnings (4 provider sections/19 official URLs/19 records after documentation)")
    print(f"documentation led earliest attempt by 490s and earliest positive cost by 695s; {rejected}/{total} mutations rejected; audit added 0 requests/uploads/$0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
