"""Emit or validate a commit-pinned final CH05 safe-source inventory r2."""
from __future__ import annotations
import argparse,copy,hashlib,json,subprocess,sys
from pathlib import Path
from validate_safe_source_release_manifest_r2 import git,inventory,root_hash,scope_errors
ROOT=Path(__file__).resolve().parents[2]; PRIOR=ROOT/"docs/research/evidence/ch05-overnight-safe-source-parity-r1.json"; DELIVERY=ROOT/"docs/research/evidence/ch05-overnight-delivery-bundle-r2.json"; RELEASE=ROOT/"docs/research/evidence/ch05-overnight-integrated-release-gate-r10.json"; OUTPUT=ROOT/"docs/research/evidence/ch05-overnight-safe-source-parity-r2.json"
class E(RuntimeError): pass
def require(v,m):
    if not v: raise E(m)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def build(capture):
    entries=inventory(capture); require(not scope_errors(entries),"; ".join(scope_errors(entries))); prior=json.loads(PRIOR.read_text(encoding="utf-8")); delivery=json.loads(DELIVERY.read_text(encoding="utf-8")); release=json.loads(RELEASE.read_text(encoding="utf-8"))
    require(subprocess.run(["git","merge-base","--is-ancestor",prior["captured_commit"],capture],cwd=ROOT).returncode==0,"r1 capture is not ancestor"); require(delivery["summary"]["candidates"]==29 and delivery["summary"]["accepted_candidates"]==0,"delivery evidence changed"); require(release["state"]=="PASS" and release["summary"]["effective_command_count"]==66,"release evidence changed")
    return {"record_type":"ComicSafeSourceDeliveryParity","schema_version":"2.0","record_id":"ng-ch05-overnight-safe-source-parity-r2","state":"PINNED_PUSHED_SAFE_SOURCE_CURRENT_DELIVERY","repository":"https://github.com/LoFiGamerGuy/visual-narrative-compiler","captured_commit":capture,"captured_tree":git("rev-parse",f"{capture}^{{tree}}"),"captured_origin_main_commit":capture,"remote_parity_at_capture":True,"supersedes":{"path":PRIOR.relative_to(ROOT).as_posix(),"sha256":sha(PRIOR),"tracked_paths":prior["summary"]["tracked_paths"]},"inputs":[{"path":DELIVERY.relative_to(ROOT).as_posix(),"sha256":sha(DELIVERY)},{"path":RELEASE.relative_to(ROOT).as_posix(),"sha256":sha(RELEASE)}],"summary":{"tracked_paths":len(entries),"total_bytes":sum(x["bytes"] for x in entries),"inventory_root_sha256":root_hash(entries),"public_controls":2,"generated_experiment_paths":0,"prohibited_extensions":0,"files_over_10_mib":0,"provider_credentials":0,"generated_candidate_pixels":0,"model_weights_loras_datasets_private_references":0,"unrelated_untracked_items_in_inventory":0},"entries":entries,"explicit_exclusions":[".env and provider credentials","experiments and generated candidate/review pixels/runtime records","model weights, LoRAs, checkpoints, installed runtimes and caches","datasets and private or likeness references","untracked imported workspace assets, launchers, generators and trainers"],"activity":{"provider_calls":0,"uploads":0,"downloads":0,"paid_spend_usd":0,"acceptance_changes":0,"commercial_clearance_changes":0},"animation_shot_plan":None,"e_conte":None,"boundary":"Commit-pinned safe source and non-art evidence only. Ignored local review pixels are linked by hash but are not tracked, published, accepted, or commercially cleared."}
def errors(d,e):
    out=[]
    for key in ("record_type","schema_version","record_id","state","repository","captured_commit","captured_tree","captured_origin_main_commit","remote_parity_at_capture","supersedes","inputs","explicit_exclusions","boundary"):
        if d.get(key)!=e.get(key): out.append(f"{key} invalid")
    if d.get("entries")!=e["entries"] or scope_errors(d.get("entries",[])): out.append("inventory invalid")
    if d.get("summary")!=e["summary"]: out.append("summary invalid")
    if d.get("activity")!={"provider_calls":0,"uploads":0,"downloads":0,"paid_spend_usd":0,"acceptance_changes":0,"commercial_clearance_changes":0}: out.append("activity invalid")
    if d.get("animation_shot_plan") is not None or d.get("e_conte") is not None: out.append("planning boundary invalid")
    return out
def main():
    p=argparse.ArgumentParser(); p.add_argument("--emit",action="store_true"); p.add_argument("--capture"); p.add_argument("--allow-unpushed-current",action="store_true"); a=p.parse_args()
    try:
        if a.emit:
            require(a.capture is not None,"--capture required with --emit"); capture=git("rev-parse",a.capture); require(git("rev-parse","HEAD")==capture,"capture is not HEAD"); require(git("rev-parse","origin/main")==capture,"capture is not pushed origin/main"); expected=build(capture); OUTPUT.write_text(json.dumps(expected,indent=2)+"\n",encoding="utf-8",newline="\n")
        else:
            tracked=json.loads(OUTPUT.read_text(encoding="utf-8")); capture=tracked["captured_commit"]; expected=build(capture); require(tracked==expected,"tracked r2 parity record differs")
        require(subprocess.run([sys.executable,"src/north_garden/validate_tracked_source_scope.py"],cwd=ROOT).returncode==0,"current tracked source scope invalid"); require(subprocess.run(["git","merge-base","--is-ancestor",capture,"HEAD"],cwd=ROOT).returncode==0,"capture is not ancestor of HEAD")
        if not a.allow_unpushed_current: require(git("rev-parse","HEAD")==git("rev-parse","origin/main"),"current HEAD is not at origin/main")
        muts=[lambda x:x.update(state="UNSAFE"),lambda x:x.update(captured_commit="0"*40),lambda x:x.update(captured_tree="0"*40),lambda x:x.update(remote_parity_at_capture=False),lambda x:x["supersedes"].update(sha256="0"*64),lambda x:x["inputs"][0].update(sha256="0"*64),lambda x:x["summary"].update(tracked_paths=x["summary"]["tracked_paths"]-1),lambda x:x["summary"].update(total_bytes=0),lambda x:x["summary"].update(inventory_root_sha256="0"*64),lambda x:x["summary"].update(generated_experiment_paths=1),lambda x:x["summary"].update(prohibited_extensions=1),lambda x:x["summary"].update(files_over_10_mib=1),lambda x:x["summary"].update(provider_credentials=1),lambda x:x["entries"].pop(),lambda x:x["activity"].update(uploads=1),lambda x:x.update(animation_shot_plan={}),lambda x:x["explicit_exclusions"].pop()]
        rejected=0
        for mut in muts: y=copy.deepcopy(expected); mut(y); rejected+=bool(errors(y,expected))
        require(rejected==len(muts),f"only {rejected}/{len(muts)} mutations rejected")
    except (E,FileNotFoundError,KeyError,json.JSONDecodeError) as er: print(f"FAIL: {er}",file=sys.stderr); return 1
    s=expected["summary"]; print(f"CH05 safe delivery r2: 0 failures ({s['tracked_paths']} paths/{s['total_bytes']} bytes; tree {expected['captured_tree']}; root {s['inventory_root_sha256']})"); print(f"2 controls; 0 generated/prohibited/oversize/credential paths; {rejected}/{len(muts)} mutations rejected; capture pushed/current parity valid"); return 0
if __name__=="__main__": raise SystemExit(main())
