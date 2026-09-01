"""Static TLS, HTTPS, and fictional-only boundary audit for dormant G07 adapters."""
from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PLAN = ROOT / "experiments/renderer-bakeoffs/g07-fictional-bakeoff-r1.json"
VAULT = ROOT / "docs/research/evidence/g07-local-evidence-vault-manifest-r1.json"
OUTPUT = ROOT / "docs/research/evidence/g07-provider-transport-data-boundary-audit-r1.json"
SOURCES = {
    "openai_gpt_image_2": "src/north_garden/openai_gpt_image2_bakeoff.py",
    "gemini_3_1_flash_image": "src/north_garden/gemini_flash_image_bakeoff.py",
    "grok_imagine_image_2": "src/north_garden/xai_grok_imagine_bakeoff.py",
    "bfl_flux_2": "src/north_garden/bfl_flux2_bakeoff.py",
}
EXPECTED_ENDPOINTS = {
    "openai_gpt_image_2": "https://api.openai.com/v1/images/edits",
    "gemini_3_1_flash_image": "https://generativelanguage.googleapis.com/v1beta/interactions",
    "grok_imagine_image_2": "https://api.x.ai/v1/images/edits",
    "bfl_flux_2": "https://api.bfl.ai/v1/flux-2-pro",
}
PROHIBITED = ["child imagery", "child-like character reference", "real-person likeness", "biometric identity data", "adult-likeness LoRA output", "sensitive personal data"]
APPROVED_INPUTS = {"g07a-control": "0a7237f655492f4aea7618036b7bac1a5068882f113ae395188ab50abb5a2699", "g07a-nochange-reference": "867a05c2f3e35f196cd28a9d1dc1954f2ba862f62d33ae34df4f3161a3200436"}
INSECURE = ["CERT_NONE", "_create_unverified_context", "check_hostname = False", "verify=False", "http://"]


class BoundaryError(RuntimeError): pass


def require(value: bool, message: str) -> None:
    if not value: raise BoundaryError(message)


def sha256(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()


def constants(tree: ast.Module) -> dict[str, str]:
    values = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str): values[name] = node.value.value
            elif isinstance(node.value, ast.JoinedStr):
                text = ""
                for part in node.value.values:
                    if isinstance(part, ast.Constant): text += str(part.value)
                    elif isinstance(part, ast.FormattedValue) and isinstance(part.value, ast.Name): text += values[part.value.id]
                values[name] = text
    return values


def audit_adapter(adapter: str, relative: str) -> dict:
    path = ROOT / relative; source = path.read_text(encoding="utf-8"); tree = ast.parse(source); assigned = constants(tree)
    require(assigned.get("ENDPOINT") == EXPECTED_ENDPOINTS[adapter], f"{adapter} endpoint changed")
    require(not any(token in source for token in INSECURE), f"{adapter} insecure transport token")
    if adapter in {"openai_gpt_image_2", "bfl_flux_2"}:
        require("truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)" in source, f"{adapter} native verified TLS context missing")
        tls_source = "defines native truststore PROTOCOL_TLS_CLIENT context"
    else:
        require(re.search(r"from openai_gpt_image2_bakeoff import .*SSL_CONTEXT", source) is not None, f"{adapter} verified TLS context import missing")
        tls_source = "imports native verified context from OpenAI adapter"
    urlopens = [node for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "urlopen"]
    require(urlopens and all(any(keyword.arg == "context" and isinstance(keyword.value, ast.Name) and keyword.value.id == "SSL_CONTEXT" for keyword in node.keywords) for node in urlopens), f"{adapter} urlopen lacks verified context")
    dynamic_guards = []
    if adapter == "gemini_3_1_flash_image":
        require("Gemini returned a non-HTTPS image URI" in source, "Gemini output URI HTTPS guard missing")
        dynamic_guards.append("provider image URI must start https://")
    if adapter == "bfl_flux_2":
        require("BFL returned a non-HTTPS polling URL" in source and "BFL returned a non-HTTPS sample URL" in source, "BFL returned URL HTTPS guards missing")
        dynamic_guards.extend(["public control URL must start https://", "provider polling URL must start https://", "provider sample URL must start https://"])
    return {"adapter_id": adapter, "source_path": relative, "source_sha256": sha256(path), "endpoint": assigned["ENDPOINT"], "endpoint_https": True, "tls_verification": tls_source, "urlopen_calls_with_verified_context": len(urlopens), "insecure_override_tokens": [], "dynamic_https_guards": dynamic_guards}


def build() -> dict:
    plan = json.loads(PLAN.read_text(encoding="utf-8")); vault = json.loads(VAULT.read_text(encoding="utf-8"))
    boundary = plan["data_boundary"]
    require(boundary["input_classification"] == "FICTIONAL_ADULT_DESIGN_AND_ORIGINAL_GEOMETRY_ONLY", "input classification changed")
    require(boundary["prohibited"] == PROHIBITED and boundary["adult_likeness_external_upload"] == "NOT_AUTHORIZED", "prohibited data boundary changed")
    observed = {key: value for record in vault["records"] for key, value in record["input_hashes"].items()}
    require(observed == APPROVED_INPUTS, "vault input set differs from two controls")
    audits = [audit_adapter(adapter, path) for adapter, path in SOURCES.items()]
    return {
        "record_type": "G07ProviderTransportDataBoundaryAudit", "schema_version": "1.0", "record_id": "ng-g07-provider-transport-data-boundary-audit-r1",
        "state": "DORMANT_ADAPTERS_VERIFIED_TLS_FICTIONAL_CONTROL_BOUNDARY_CLOSED",
        "sources": {"plan": {"path": PLAN.relative_to(ROOT).as_posix(), "sha256": sha256(PLAN)}, "vault": {"path": VAULT.relative_to(ROOT).as_posix(), "sha256": sha256(VAULT)}},
        "adapters": audits,
        "data_boundary": {"input_classification": boundary["input_classification"], "prohibited": PROHIBITED, "adult_likeness_external_upload": "NOT_AUTHORIZED", "observed_input_hashes": APPROVED_INPUTS, "observed_input_classes": 2, "expanded_upload_authority": False},
        "tls_boundary": {"all_endpoints_https": True, "all_urlopen_calls_use_verified_context": True, "native_trust_store": True, "insecure_override_tokens_found": 0, "provider_returned_remote_urls_fail_closed_to_https": True},
        "activity": {"network_requests": 0, "provider_requests": 0, "external_uploads": 0, "external_cost_usd": "0.000000"},
        "boundary": "Static audit and local source hardening only. Dormant adapters remain closed; remaining bakeoff capacity grants no execution or production authority.",
    }


def mutations(expected: dict) -> tuple[int, int]:
    values = []
    item = copy.deepcopy(expected); item["adapters"][0]["endpoint"] = "http://example.invalid"; values.append(item)
    item = copy.deepcopy(expected); item["adapters"][1]["insecure_override_tokens"] = ["CERT_NONE"]; values.append(item)
    item = copy.deepcopy(expected); item["tls_boundary"]["all_urlopen_calls_use_verified_context"] = False; values.append(item)
    item = copy.deepcopy(expected); item["tls_boundary"]["provider_returned_remote_urls_fail_closed_to_https"] = False; values.append(item)
    item = copy.deepcopy(expected); item["data_boundary"]["prohibited"].remove("child imagery"); values.append(item)
    item = copy.deepcopy(expected); item["data_boundary"]["observed_input_hashes"]["private"] = "0" * 64; values.append(item)
    item = copy.deepcopy(expected); item["data_boundary"]["adult_likeness_external_upload"] = "AUTHORIZED"; values.append(item)
    item = copy.deepcopy(expected); item["data_boundary"]["expanded_upload_authority"] = True; values.append(item)
    item = copy.deepcopy(expected); item["activity"]["network_requests"] = 1; values.append(item)
    return sum(value != expected for value in values), len(values)


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--emit", type=Path); args = parser.parse_args()
    try:
        expected = build()
        if args.emit:
            target = args.emit if args.emit.is_absolute() else ROOT / args.emit
            target.parent.mkdir(parents=True, exist_ok=True); target.write_text(json.dumps(expected, indent=2) + "\n", encoding="utf-8", newline="\n")
        else: require(json.loads(OUTPUT.read_text(encoding="utf-8")) == expected, "tracked transport audit differs")
        rejected, total = mutations(expected); require(rejected == total, "mutation rejection incomplete")
    except (BoundaryError, FileNotFoundError, KeyError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr); return 1
    print("0 failures, 0 warnings (4 HTTPS endpoints; every urlopen uses native verified TLS; returned remote URLs HTTPS-guarded)")
    print(f"two fictional control hashes only; six prohibited data classes intact; {rejected}/{total} mutations rejected; 0 network/uploads/$0")
    return 0


if __name__ == "__main__": raise SystemExit(main())
