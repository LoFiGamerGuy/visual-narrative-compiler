"""Reproduce r8 while normalizing only its live tracked-path diagnostic count."""
from __future__ import annotations
import argparse,copy,hashlib,json,re,subprocess,sys
from pathlib import Path
from validate_ch05_overnight_integrated_release_gate_r8 import errors

ROOT=Path(__file__).resolve().parents[2]
R8=ROOT/"docs/research/evidence/ch05-overnight-integrated-release-gate-r8.json"
ATTEMPT=ROOT/"docs/research/evidence/ch05-overnight-integrated-release-r8-post-commit-attempt-1-failed.json"
OUTPUT=ROOT/"docs/research/evidence/ch05-overnight-integrated-release-r8-compatibility-r1.json"
SAFE="src/north_garden/validate_ch05_overnight_safe_source_parity.py"
class E(RuntimeError): pass
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def canonical(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def normalize(path,text):
    return re.sub(r"\d+ tracked safe-source paths","<TRACKED_COUNT> tracked safe-source paths",text) if path==SAFE else text
def run_all(d):
    rows=[]
    for item in d["results"]:
        p=ROOT/item["path"]; done=subprocess.run([sys.executable,str(p),*item.get("arguments",[])],cwd=ROOT,capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=360); stdout=done.stdout.replace("\r\n","\n").strip()+"\n"; stderr=done.stderr.replace("\r\n","\n")
        rows.append({"path":item["path"],"return_code":done.returncode,"stderr":stderr,"observed_stdout_sha256":hashlib.sha256(stdout.encode()).hexdigest(),"expected_stdout_sha256":item["stdout_sha256"],"normalized_observed_sha256":hashlib.sha256(normalize(item["path"],stdout).encode()).hexdigest(),"normalized_expected_sha256":hashlib.sha256(normalize(item["path"],item["stdout"]).encode()).hexdigest(),"normalization":"TRACKED_COUNT_ONLY" if item["path"]==SAFE else "NONE"})
    return rows
def build(d,rows):
    mismatch=[x for x in rows if x["observed_stdout_sha256"]!=x["expected_stdout_sha256"]]
    return {"record_type":"CH05IntegratedReleaseCompatibilityEvidence","schema_version":"1.0","record_id":"ng-ch05-overnight-integrated-release-r8-compatibility-r1","state":"PASS_NARROW_DYNAMIC_DIAGNOSTIC_NORMALIZATION","source_release":{"path":R8.relative_to(ROOT).as_posix(),"sha256":sha(R8),"record_id":d["record_id"],"effective_checks":49},"normalization_policy":{"paths":[SAFE],"field":"human-readable live tracked-path diagnostic count only","pattern":"\\d+ tracked safe-source paths","replacement":"<TRACKED_COUNT> tracked safe-source paths","semantic_inventory_normalization":False,"hash_or_state_normalization":False},"results":rows,"summary":{"commands":4,"raw_stdout_mismatches":len(mismatch),"normalized_matches":sum(x["normalized_observed_sha256"]==x["normalized_expected_sha256"] for x in rows),"return_code_failures":sum(x["return_code"]!=0 for x in rows),"stderr_nonempty":sum(bool(x["stderr"]) for x in rows),"effective_checks":49,"release_semantic_errors":len(errors(d))},"activity":{"provider_calls":0,"uploads":0,"downloads":0,"cost_usd":0,"acceptance_changes":0},"boundary":"Compatibility is limited to the live tracked-path count printed by current-scope validation. The captured 735-path inventory, its hashes, scripts, return codes, all other stdout, and release semantics remain exact."}
def validate(e,d):
    out=[]; s=e.get("summary",{}); policy=e.get("normalization_policy",{})
    if e.get("state")!="PASS_NARROW_DYNAMIC_DIAGNOSTIC_NORMALIZATION" or e.get("source_release")!={"path":R8.relative_to(ROOT).as_posix(),"sha256":sha(R8),"record_id":d["record_id"],"effective_checks":49}: out.append("identity/source invalid")
    if policy.get("paths")!=[SAFE] or policy.get("semantic_inventory_normalization") is not False or policy.get("hash_or_state_normalization") is not False: out.append("normalization scope invalid")
    rows=e.get("results",[])
    if len(rows)!=4 or s!={"commands":4,"raw_stdout_mismatches":1,"normalized_matches":4,"return_code_failures":0,"stderr_nonempty":0,"effective_checks":49,"release_semantic_errors":0}: out.append("result summary invalid")
    if sum(x.get("normalization")=="TRACKED_COUNT_ONLY" for x in rows)!=1 or any(x.get("normalized_observed_sha256")!=x.get("normalized_expected_sha256") for x in rows): out.append("normalized reproduction invalid")
    if e.get("activity")!={"provider_calls":0,"uploads":0,"downloads":0,"cost_usd":0,"acceptance_changes":0}: out.append("activity invalid")
    if errors(d): out.append("r8 semantic state invalid")
    return out
def main():
    p=argparse.ArgumentParser(); p.add_argument("--emit",action="store_true"); a=p.parse_args(); d=json.loads(R8.read_text(encoding="utf-8")); rows=run_all(d); expected=build(d,rows)
    if a.emit:
        mismatch=[x for x in rows if x["observed_stdout_sha256"]!=x["expected_stdout_sha256"]]
        failed={"record_type":"FailedReproductionAttempt","schema_version":"1.0","record_id":"ng-ch05-release-r8-post-commit-attempt-1-failed","state":"EXPECTED_FAILURE_PRESERVED","source_release":{"path":R8.relative_to(ROOT).as_posix(),"sha256":sha(R8)},"failure_count":len(mismatch),"failures":mismatch,"cause":"The safe-source validator embeds a live current tracked-path count in stdout. Committing r8 increased that count while the pinned 735-path capture remained exact.","resolution":"Preserve r8 and normalize only the human-readable tracked-count diagnostic in append-only compatibility evidence."}; ATTEMPT.write_text(json.dumps(failed,indent=2)+"\n",encoding="utf-8",newline="\n"); OUTPUT.write_text(json.dumps(expected,indent=2)+"\n",encoding="utf-8",newline="\n")
    try:
        e=json.loads(OUTPUT.read_text(encoding="utf-8")); fail=validate(e,d)
        # Current reproduction may have another live count but must normalize to the same exact output.
        live=build(d,rows)
        if any(x["normalized_observed_sha256"]!=x["normalized_expected_sha256"] for x in live["results"]): fail.append("current normalized reproduction differs")
        muts=[lambda x:x.update(state="FAIL"),lambda x:x["source_release"].update(sha256="0"*64),lambda x:x["normalization_policy"].update(paths=[]),lambda x:x["normalization_policy"].update(semantic_inventory_normalization=True),lambda x:x["summary"].update(commands=3),lambda x:x["summary"].update(raw_stdout_mismatches=0),lambda x:x["summary"].update(normalized_matches=3),lambda x:x["summary"].update(release_semantic_errors=1),lambda x:x["results"].pop(),lambda x:x["activity"].update(uploads=1)]
        rejected=0
        for mut in muts: y=copy.deepcopy(e); mut(y); rejected+=bool(validate(y,d))
        if rejected!=len(muts): fail.append(f"only {rejected}/{len(muts)} mutations rejected")
    except (FileNotFoundError,KeyError,json.JSONDecodeError) as er: print(f"FAIL: {er}",file=sys.stderr); return 1
    print(f"CH05 r8 compatibility: {len(fail)} failures; 4/4 normalized reproductions; one tracked-count-only raw mismatch; {rejected}/{len(muts)} mutations rejected")
    for item in fail: print(f"FAIL: {item}")
    return 1 if fail else 0
if __name__=="__main__": raise SystemExit(main())
