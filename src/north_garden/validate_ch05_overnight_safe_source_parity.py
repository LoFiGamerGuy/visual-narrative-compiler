"""Pin and validate the pushed CH05 overnight delivery safe-source inventory."""
from __future__ import annotations
import argparse,copy,hashlib,json,subprocess,sys
from pathlib import Path
from validate_safe_source_release_manifest_r2 import git,inventory,root_hash,scope_errors

ROOT=Path(__file__).resolve().parents[2]
CAPTURE="a1454db0ec0fbe80bda7c88a55764047c62618b4"
PRIOR=ROOT/"docs/research/evidence/safe-source-release-manifest-f1803bd.json"
DELIVERY=ROOT/"docs/research/evidence/ch05-overnight-delivery-bundle-r1.json"
OUTPUT=ROOT/"docs/research/evidence/ch05-overnight-safe-source-parity-r1.json"
class E(RuntimeError): pass
def require(v,m):
    if not v: raise E(m)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def build():
    entries=inventory(CAPTURE); require(not scope_errors(entries),"; ".join(scope_errors(entries)))
    prior=json.loads(PRIOR.read_text(encoding="utf-8")); delivery=json.loads(DELIVERY.read_text(encoding="utf-8"))
    require(subprocess.run(["git","merge-base","--is-ancestor",prior["captured_commit"],CAPTURE],cwd=ROOT).returncode==0,"prior safe capture is not an ancestor")
    require(delivery["summary"]["candidates"]==29 and delivery["summary"]["accepted_candidates"]==0,"delivery evidence changed")
    return {"record_type":"ComicSafeSourceDeliveryParity","schema_version":"1.0","record_id":"ng-ch05-overnight-safe-source-parity-r1","state":"PINNED_PUSHED_SAFE_SOURCE_DELIVERY","repository":"https://github.com/LoFiGamerGuy/visual-narrative-compiler","captured_commit":CAPTURE,"captured_tree":git("rev-parse",f"{CAPTURE}^{{tree}}"),"captured_origin_main_commit":CAPTURE,"remote_parity_at_capture":True,"inputs":[{"path":PRIOR.relative_to(ROOT).as_posix(),"sha256":sha(PRIOR)},{"path":DELIVERY.relative_to(ROOT).as_posix(),"sha256":sha(DELIVERY)}],"summary":{"tracked_paths":len(entries),"total_bytes":sum(x["bytes"] for x in entries),"inventory_root_sha256":root_hash(entries),"public_controls":2,"generated_experiment_paths":0,"prohibited_extensions":0,"files_over_10_mib":0,"provider_credentials":0,"generated_candidate_pixels":0,"model_weights_loras_datasets_private_references":0,"unrelated_untracked_items_in_inventory":0},"entries":entries,"explicit_exclusions":[".env and provider credentials","experiments and generated candidate/review pixels/runtime records","model weights, LoRAs, checkpoints, installed runtimes and caches","datasets and private or likeness references","untracked imported workspace assets, launchers, generators and trainers"],"activity":{"provider_calls":0,"uploads":0,"downloads":0,"paid_spend_usd":0,"acceptance_changes":0,"commercial_clearance_changes":0},"animation_shot_plan":None,"e_conte":None,"boundary":"Commit-pinned safe source and non-art evidence only. Ignored local review pixels are linked by hash but are not tracked, published, accepted, or commercially cleared."}
def errors(d,expected):
    out=[]; entries=d.get("entries",[]); s=d.get("summary",{})
    for key in ("record_type","schema_version","record_id","state","repository","captured_commit","captured_tree","captured_origin_main_commit","remote_parity_at_capture","inputs","explicit_exclusions","boundary"):
        if d.get(key)!=expected.get(key): out.append(f"{key} invalid")
    if entries!=expected["entries"] or scope_errors(entries): out.append("inventory invalid")
    if s!=expected["summary"]: out.append("summary invalid")
    if d.get("activity")!={"provider_calls":0,"uploads":0,"downloads":0,"paid_spend_usd":0,"acceptance_changes":0,"commercial_clearance_changes":0}: out.append("activity invalid")
    if d.get("animation_shot_plan") is not None or d.get("e_conte") is not None: out.append("planning boundary invalid")
    return out
def main():
    p=argparse.ArgumentParser(); p.add_argument("--emit",type=Path); p.add_argument("--allow-unpushed-current",action="store_true"); a=p.parse_args()
    try:
        expected=build()
        if a.emit:
            require(git("rev-parse","HEAD")==CAPTURE,"capture is not HEAD"); require(git("rev-parse","origin/main")==CAPTURE,"capture is not pushed origin/main")
            t=a.emit if a.emit.is_absolute() else ROOT/a.emit; t.parent.mkdir(parents=True,exist_ok=True); t.write_text(json.dumps(expected,indent=2)+"\n",encoding="utf-8",newline="\n")
        else: require(json.loads(OUTPUT.read_text(encoding="utf-8"))==expected,"tracked parity record differs")
        require(subprocess.run([sys.executable,"src/north_garden/validate_tracked_source_scope.py"],cwd=ROOT).returncode==0,"current tracked source scope invalid")
        require(subprocess.run(["git","merge-base","--is-ancestor",CAPTURE,"HEAD"],cwd=ROOT).returncode==0,"capture is not an ancestor of HEAD")
        if not a.allow_unpushed_current: require(git("rev-parse","HEAD")==git("rev-parse","origin/main"),"current HEAD is not at origin/main")
        muts=[lambda x:x.update(state="UNSAFE"),lambda x:x.update(captured_commit="0"*40),lambda x:x.update(captured_tree="0"*40),lambda x:x.update(remote_parity_at_capture=False),lambda x:x["inputs"][0].update(sha256="0"*64),lambda x:x["summary"].update(tracked_paths=x["summary"]["tracked_paths"]-1),lambda x:x["summary"].update(total_bytes=0),lambda x:x["summary"].update(inventory_root_sha256="0"*64),lambda x:x["summary"].update(generated_experiment_paths=1),lambda x:x["summary"].update(prohibited_extensions=1),lambda x:x["summary"].update(files_over_10_mib=1),lambda x:x["summary"].update(provider_credentials=1),lambda x:x["entries"].pop(),lambda x:x["activity"].update(uploads=1),lambda x:x.update(animation_shot_plan={}),lambda x:x["explicit_exclusions"].pop()]
        rejected=0
        for mut in muts: y=copy.deepcopy(expected); mut(y); rejected+=bool(errors(y,expected))
        require(rejected==len(muts),f"only {rejected}/{len(muts)} mutations rejected")
    except (E,FileNotFoundError,KeyError,json.JSONDecodeError) as er: print(f"FAIL: {er}",file=sys.stderr); return 1
    s=expected["summary"]; print(f"CH05 safe delivery: 0 failures ({s['tracked_paths']} paths/{s['total_bytes']} bytes; tree {expected['captured_tree']}; root {s['inventory_root_sha256']})"); print(f"2 controls; 0 generated/prohibited/oversize/credential paths; {rejected}/{len(muts)} mutations rejected; capture pushed/current parity valid"); return 0
if __name__=="__main__": raise SystemExit(main())
