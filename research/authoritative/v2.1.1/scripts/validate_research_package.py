#!/usr/bin/env python3
"""Package self-validation.

v2.0's lesson was "tags describe provenance, not currency."
v2.1's lesson is: narrative research artifacts also need machine-checkable internal
consistency. Prose counts drift from data; corrections get announced in one file and
not applied in six others. This script fails the build on both.

Usage:  python3 scripts/validate_research_package.py [--write-status]
Exit 0 = clean, 1 = failures.
"""
import json, re, sys, os
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def P(*a): return os.path.join(ROOT, *a)
FAIL, WARN = [], []
def fail(c, m): FAIL.append(f"[{c}] {m}")
def warn(c, m): WARN.append(f"[{c}] {m}")

DOCS = ["README.md","docs/CORRECTIONS_V2_1.md","docs/RESEARCH_BRIEF_V2.md","docs/ARCHITECTURE_V0_1.md",
        "docs/DECISION_LOG.md","docs/EXPERIMENT_BACKLOG.md","docs/NEXT_ACTIONS.md",
        "bench/CONTINUITY_GAUNTLET.md","registry/CANDIDATE_REGISTRY.md","registry/POLICY_LICENSE_REGISTRY.md"]

def read(p):
    fp = P(p)
    return open(fp, encoding="utf-8").read() if os.path.exists(fp) else ""

# ---------------------------------------------------------------- 1. benchmark
G = json.load(open(P("bench/gauntlet.json"), encoding="utf-8"))
rc, ctl, inj = G["render_cases"], G["qa_controls"], G["qa_error_injection"]
ids = [c["id"] for c in rc]

if len(ids) != len(set(ids)): fail("BENCH", "duplicate render_case ids")
tier = Counter(c["tier"] for c in rc)
sb_seeds = G["evaluation_protocol"]["stage_b_full"]["seeds_per_case"]
sa = G["evaluation_protocol"]["stage_a_smoke"]
sa_seeds = sa["seeds_per_case"]

# seed arrays must agree with the declared per-case seed count
bad = [c["id"] for c in rc if len(c.get("seeds", [])) != sb_seeds]
if bad: fail("BENCH", f"{len(bad)} render_cases whose seeds[] length != stage_b seeds_per_case={sb_seeds}: {bad[:5]}")
badc = [c["id"] for c in ctl if len(c.get("seeds", [])) != sb_seeds]
if badc: fail("BENCH", f"qa_controls with seeds[] != {sb_seeds}: {badc}")

# stage A ids must exist
missing = [i for i in sa["case_ids"] if i not in ids]
if missing: fail("BENCH", f"stage_a_smoke references non-existent case_ids: {missing}")

# controls must point at real parents; injections too
for c in ctl:
    if c["control_of"] not in ids: fail("BENCH", f"control {c['id']} parent {c['control_of']} missing")
for e in inj:
    if e["derived_from"] not in ids: fail("BENCH", f"injection {e['id']} parent {e['derived_from']} missing")

# paired variants must be symmetric, typed, and discriminable
by_id = {c["id"]: c for c in rc}
pairs = [(c["paired_variant_of"], c["id"]) for c in rc if c.get("paired_variant_of")]
for a, b in pairs:
    if a not in by_id: fail("BENCH", f"{b} paired_variant_of missing case {a}"); continue
    ca, cb = by_id[a], by_id[b]
    if ca.get("variant_axis") != cb.get("variant_axis"):
        fail("BENCH", f"pair {a}/{b} disagree on variant_axis")
    d = cb.get("variant_discriminator")
    if not d: fail("BENCH", f"pair {a}/{b} has no variant_discriminator")
    elif d not in ca.get("manifest", {}) or d not in cb.get("manifest", {}):
        fail("BENCH", f"pair {a}/{b} axis '{cb.get('variant_axis')}' not machine-checkable: "
                      f"manifest key '{d}' absent — the pair is prose, not executable")
    elif ca["manifest"][d] == cb["manifest"][d]:
        fail("BENCH", f"pair {a}/{b} discriminator '{d}' is IDENTICAL in both — no swap encoded")

COMPUTED = {
    "render_cases": len(rc),
    "tiers": dict(tier),
    "paired_variant_relations": len(pairs),
    "cases_in_pairs": len(pairs) * 2,
    "variant_axes": dict(Counter(c["variant_axis"] for c in rc if c.get("variant_axis"))),
    "stage_a_generations": len(sa["case_ids"]) * sa_seeds,
    "stage_b_renderer_generations": len(rc) * sb_seeds,
    "qa_control_comparisons": len(ctl) * sb_seeds,
    "qa_injection_cases": len(inj),
    "spatial_modes": dict(Counter(c.get("spatial_mode") for c in rc)),
}

# ------------------------------------------------- 2. hard-coded counts in prose
NUM = {
 "render_cases": COMPUTED["render_cases"],
 "stage_b_renderer_generations": COMPUTED["stage_b_renderer_generations"],
 "paired_variant_relations": COMPUTED["paired_variant_relations"],
}
# any doc asserting a shot/generation count must match the computed value
for d in DOCS:
    t = read(d)
    for m in re.finditer(r"\b(\d{2,3})[- ](?:shot|shots)\b", t):
        n = int(m.group(1))
        if n != NUM["render_cases"]:
            fail("COUNT", f"{d}: hard-coded '{n}-shot' but render_cases={NUM['render_cases']}")
    for m in re.finditer(r"\b(\d{2,4}) generations\b", t):
        n = int(m.group(1))
        if n not in (NUM["stage_b_renderer_generations"], COMPUTED["stage_a_generations"]):
            fail("COUNT", f"{d}: '{n} generations' matches neither stage A ({COMPUTED['stage_a_generations']}) "
                          f"nor stage B ({NUM['stage_b_renderer_generations']})")
    for m in re.finditer(r"\b(\d{1,2}) mirrored", t):
        n = int(m.group(1))
        if n != NUM["paired_variant_relations"]:
            fail("COUNT", f"{d}: '{n} mirrored' but paired_variant_relations={NUM['paired_variant_relations']}")

# ------------------------------------------------- 3. stale claims after correction
# Operational docs must state ONLY the corrected rule. CORRECTIONS may quote the old one.
HISTORY_OK = {"docs/CORRECTIONS_V2_1.md"}
STALE = [
 (r"bars? (?:it |them )?from monetization entirely", "GlobalComix monetization prohibition (corrected v2.1)"),
 (r"not eligible for monetization", "GlobalComix monetization prohibition (corrected v2.1)"),
 (r"licence unverified|license unverified|Unstated — verify LICENSE", "ToonComposer licence (MIT, verified)"),
 (r"≤\s*24\s*GB", "withdrawn ≤24GB animation gate"),
 (r"[Dd]eferred? ~?12 months|deferred ~12 months", "withdrawn 12-month animation calendar gate"),
 (r"VLM (?:auditor )?(?:should be |is )?last", "'VLM last' (corrected to optional/non-gating)"),
 (r"last and smallest", "'VLM last and smallest' (corrected)"),
 (r"leading question by construction", "misattributed M³-Verse 12.32 framing"),
 (r"SCRFD and RetinaFace ship through InsightFace and inherit", "architecture-name licence over-generalisation"),
 (r"~?70% of the \*?asset|~70%.{0,40}~0%", "withdrawn reuse percentages"),
]
for d in DOCS:
    if d in HISTORY_OK: continue
    t = read(d)
    for pat, why in STALE:
        for m in re.finditer(pat, t):
            ln = t[:m.start()].count("\n") + 1
            fail("STALE", f"{d}:{ln} contains stale claim — {why} — matched {m.group(0)!r}")

# ------------------------------------------------- 4. conflict-resolution order
CANON = ["reproducible", "official", "corrections", "research package", "master brief"]
def order_of(text):
    m = re.search(r"[Cc]onflict[- ]resolution order(.{0,900})", text, re.S)
    if not m: return None
    seq, blob = [], m.group(1).lower()
    for line in blob.split("\n"):
        if not re.match(r"\s*\d[\.\)]", line): continue
        if "local_experiment" in line or "reproducible" in line: seq.append("reproducible")
        elif "licence" in line or "license" in line or "policy" in line: seq.append("official")
        elif "correction" in line or "handoff" in line: seq.append("corrections")
        elif "research package" in line or "v2 research" in line: seq.append("research package")
        elif "master brief" in line: seq.append("master brief")
    return seq
ref = order_of(read("README.md"))
if ref != CANON:
    fail("ORDER", f"README conflict order is {ref}, expected {CANON}")
for d in ["docs/CORRECTIONS_V2_1.md","docs/HANDOFF_CODEX_V2.md"]:
    o = order_of(read(d))
    if o is None: warn("ORDER", f"{d}: no conflict-resolution order found")
    elif o != CANON: fail("ORDER", f"{d} conflict order is {o}, expected {CANON} (README is canonical)")

# ------------------------------------------------- 5. legal gates
reg = read("registry/POLICY_LICENSE_REGISTRY.md") + read("registry/CANDIDATE_REGISTRY.md")
# restricted weights must be named as files, not architecture families
for fam in ["SCRFD", "RetinaFace"]:
    for m in re.finditer(rf"{fam}[^.\n]{{0,80}}(non-commercial|restricted|BLOCKED)", reg, re.I):
        fail("LEGAL", f"restricted-weight entry uses architecture family name {fam!r} rather than an exact "
                      f"distributed artifact: {m.group(0)[:90]!r}")
for gate, need in [("BLOCKED_FROM_COMMERCIAL_PIPELINE", "NoobAI"), ("Apache 2.0", "Qwen")]:
    if gate not in reg: warn("LEGAL", f"expected gate marker {gate!r} not found in registries")

# ------------------------------------------------- 6. child-safety wording
for d in DOCS:
    t = read(d)
    for m in re.finditer(r"no identity data anywhere", t):
        fail("SAFETY", f"{d}: 'no identity data anywhere' must read 'no real-person likeness/biometric "
                       f"identity data anywhere' — a fictional character legitimately has persistent identity assets")

# ------------------------------------------------- report
status = ["# PACKAGE_STATUS.md", "", "*Generated by `scripts/validate_research_package.py`. Do not hand-edit.*",
          "", "## Computed benchmark counts", "", "| Metric | Value |", "|---|---|"]
for k, v in COMPUTED.items():
    status.append(f"| `{k}` | {v} |")
status += ["", "## Validation", ""]
status.append(f"- failures: **{len(FAIL)}**")
status.append(f"- warnings: **{len(WARN)}**")
if FAIL: status += [""] + [f"- ❌ {f}" for f in FAIL]
if WARN: status += [""] + [f"- ⚠️ {w}" for w in WARN]
status += ["", "## Rule", "",
  "Counts in prose are forbidden to disagree with `bench/gauntlet.json`. Prefer citing this file.", ""]

if "--write-status" in sys.argv:
    open(P("PACKAGE_STATUS.md"), "w", encoding="utf-8").write("\n".join(status) + "\n")

print(json.dumps(COMPUTED, indent=1))
for f in FAIL: print("FAIL", f)
for w in WARN: print("WARN", w)
print(f"\n{len(FAIL)} failures, {len(WARN)} warnings")
sys.exit(1 if FAIL else 0)
