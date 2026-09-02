"""Validate CH05 handoff ancestry, configured origin, and current remote parity."""
from __future__ import annotations
import argparse,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
CAPTURE="a1454db0ec0fbe80bda7c88a55764047c62618b4"
RELEASE7="65e6119"
FILES=[ROOT/"docs/research/evidence/ch05-overnight-delivery-bundle-r1.json",ROOT/"docs/research/evidence/ch05-overnight-safe-source-parity-r1.json",ROOT/"docs/research/evidence/ch05-overnight-integrated-release-gate-r8.json",ROOT/"docs/research/evidence/ch05-overnight-integrated-release-r8-compatibility-r1.json"]
def git(*args): return subprocess.run(["git",*args],cwd=ROOT,capture_output=True,text=True,encoding="utf-8")
def main():
    p=argparse.ArgumentParser(); p.add_argument("--allow-unpushed-current",action="store_true"); a=p.parse_args(); fail=[]
    head=git("rev-parse","HEAD"); origin=git("rev-parse","origin/main"); branch=git("branch","--show-current"); remote=git("remote","get-url","origin")
    if any(x.returncode for x in (head,origin,branch,remote)): fail.append("required Git query failed")
    hv=head.stdout.strip(); ov=origin.stdout.strip()
    if branch.stdout.strip()!="main": fail.append("branch is not main")
    if remote.stdout.strip().removesuffix(".git")!="https://github.com/LoFiGamerGuy/visual-narrative-compiler": fail.append("origin URL differs")
    if not a.allow_unpushed_current and hv!=ov: fail.append("HEAD differs from origin/main")
    for ancestor,label in ((RELEASE7,"release-r7 base"),(CAPTURE,"safe-source capture")):
        if git("merge-base","--is-ancestor",ancestor,"HEAD").returncode: fail.append(f"{label} is not an ancestor of HEAD")
        if git("merge-base","--is-ancestor",ancestor,"origin/main").returncode: fail.append(f"{label} is not an ancestor of origin/main")
    if git("diff","--quiet").returncode or git("diff","--cached","--quiet").returncode: fail.append("tracked working tree or index differs")
    try:
        delivery,safe,r8,compat=[json.loads(x.read_text(encoding="utf-8")) for x in FILES]
        if delivery["base_remote_parity"] is not True or safe["captured_commit"]!=CAPTURE or safe["remote_parity_at_capture"] is not True: fail.append("captured parity evidence invalid")
        if r8["state"]!="PASS" or compat["state"]!="PASS_NARROW_DYNAMIC_DIAGNOSTIC_NORMALIZATION": fail.append("release lineage state invalid")
    except (FileNotFoundError,KeyError,json.JSONDecodeError) as er: fail.append(f"evidence read failed: {er}")
    for item in fail: print(f"FAIL: {item}")
    if fail: return 1
    print("CH05 remote lineage: 0 failures; main/origin configured; release-r7 and safe-source capture are ancestors; tracked tree/index clean")
    print("historical delivery/source parity exact; r8 semantic pass + narrow compatibility pass; unrelated untracked items excluded")
    return 0
if __name__=="__main__": raise SystemExit(main())
