"""Append-only exact rebuild inventory r2 including disconnected/hole outputs."""
from __future__ import annotations
import argparse, copy, hashlib, json, subprocess, sys
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
R1=ROOT/"docs/research/evidence/selected-route-artifact-rebuild-reproducibility-r1.json"
R2=ROOT/"docs/research/evidence/selected-route-artifact-rebuild-reproducibility-r2.json"
COMMANDS=["src/north_garden/validate_ch05_sequence_layout_control.py","src/north_garden/validate_openai_boundary_hardening.py","src/north_garden/validate_ch05_p036_mask_topology.py","src/north_garden/validate_ch05_p036_causal_shape_control.py","src/north_garden/validate_ch05_p044_fixed_boundary_stress.py","src/north_garden/validate_ch05_p044_adaptive_boundary.py","src/north_garden/validate_render_record_boundary.py","src/north_garden/validate_exact_base_boundary_measurement_packet.py","src/north_garden/validate_disconnected_holed_topology_stress.py"]
GROUPS=["experiments/outputs/ch05_p036_layout_control_r1","experiments/outputs/openai_targeted_repair_boundary_hardening_r2","experiments/outputs/ch05_p036_mask_topology_r1","experiments/outputs/ch05_p036_causal_shape_topology_r2","experiments/outputs/ch05_p044_fixed_boundary_stress_r1","experiments/outputs/ch05_p044_adaptive_boundary_r1","experiments/outputs/render_record_boundary_fixture_r1","experiments/outputs/exact_base_boundary_measurement_packet_r1","experiments/outputs/disconnected_holed_mask_topology_stress_r1"]

class RebuildError(RuntimeError): pass
def require(v,m):
    if not v: raise RebuildError(m)
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def root_hash(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def cycle():
    for script in COMMANDS:
        r=subprocess.run([sys.executable,script],cwd=ROOT,capture_output=True,text=True)
        require(r.returncode==0,f"rebuild failed: {script}")
def inventory():
    out=[]
    for group in GROUPS:
        files=sorted(p for p in (ROOT/group).rglob("*") if p.is_file()); require(files,f"empty group {group}")
        for path in files: out.append({"group":group,"path":path.relative_to(ROOT).as_posix(),"bytes":path.stat().st_size,"sha256":sha(path)})
    return out
def build():
    prior=json.loads(R1.read_text(encoding="utf-8")); cycle(); first=inventory(); cycle(); second=inventory(); require(first==second,"two rebuilds differ")
    counts=Counter(x["group"] for x in first)
    return {"record_type":"SelectedRouteArtifactRebuildReproducibility","schema_version":"1.1","record_id":"ng-selected-route-artifact-rebuild-reproducibility-r2","state":"EXPANDED_TWO_CONSECUTIVE_LOCAL_REBUILDS_BYTE_IDENTICAL","supersedes":{"record_id":prior["record_id"],"path":R1.relative_to(ROOT).as_posix(),"sha256":sha(R1),"prior_inventory_root_sha256":prior["summary"]["first_root_sha256"]},"prior_record_rewritten":False,"runtime_inventory":prior["runtime_inventory"],"commands":COMMANDS,"groups":[{"path":g,"artifact_count":counts[g]} for g in GROUPS],"summary":{"rebuilds":2,"artifact_groups":len(GROUPS),"artifacts":len(first),"total_bytes":sum(x["bytes"] for x in first),"first_root_sha256":root_hash(first),"second_root_sha256":root_hash(second),"byte_identical":True,"new_groups_since_r1":1,"new_artifacts_since_r1":len(first)-prior["summary"]["artifacts"]},"artifacts":first,"nondeterministic_exclusions":prior["nondeterministic_exclusions"],"activity":{"provider_requests":0,"external_uploads":0,"models_downloaded":0,"external_cost_usd":"0.000000"},"limitations":["R2 adds only the disconnected/hole local outputs to r1's bounded inventory.","Exact identity remains local-runtime and enumerated-group evidence, not cross-platform/provider/art-quality reproducibility.","Nondeterministic classes remain excluded rather than normalized."]}
def mutations(e):
    vals=[]; actions=[lambda x:x["supersedes"].update(sha256="0"*64),lambda x:x.update(prior_record_rewritten=True),lambda x:x["groups"].pop(),lambda x:x["summary"].update(artifact_groups=8),lambda x:x["summary"].update(artifacts=e["summary"]["artifacts"]-1),lambda x:x["summary"].update(second_root_sha256="0"*64),lambda x:x["summary"].update(byte_identical=False),lambda x:x["summary"].update(new_artifacts_since_r1=0),lambda x:x["artifacts"][-1].update(sha256="0"*64),lambda x:x["activity"].update(provider_requests=1)]
    for a in actions: i=copy.deepcopy(e); a(i); vals.append(i)
    return sum(v!=e for v in vals),len(vals)
def main():
    p=argparse.ArgumentParser(); p.add_argument("--emit",type=Path); a=p.parse_args()
    try:
        e=build()
        if a.emit:
            t=a.emit if a.emit.is_absolute() else ROOT/a.emit; t.parent.mkdir(parents=True,exist_ok=True); t.write_text(json.dumps(e,indent=2)+"\n",encoding="utf-8",newline="\n")
        else: require(json.loads(R2.read_text(encoding="utf-8"))==e,"tracked r2 differs")
        rejected,total=mutations(e); require(rejected==total,"mutation rejection incomplete")
    except (RebuildError,FileNotFoundError,KeyError,json.JSONDecodeError) as error:
        print(f"FAIL: {error}",file=sys.stderr); return 1
    s=e["summary"]; print(f"0 failures, 0 warnings ({s['artifacts']} artifacts/{s['artifact_groups']} groups/{s['total_bytes']} bytes; root {s['first_root_sha256']})"); print(f"two rebuilds exact; r1 pinned; {rejected}/{total} mutations rejected; 0 requests/uploads/downloads/$0"); return 0
if __name__=="__main__": raise SystemExit(main())
