"""Validate current CH05 delivery/release/source ancestry and remote configuration."""
from __future__ import annotations
import argparse,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; DELIVERY=ROOT/"docs/research/evidence/ch05-overnight-delivery-bundle-r2.json"; SAFE=ROOT/"docs/research/evidence/ch05-overnight-safe-source-parity-r2.json"; RELEASE=ROOT/"docs/research/evidence/ch05-overnight-integrated-release-gate-r10.json"
def git(*args): return subprocess.run(["git",*args],cwd=ROOT,capture_output=True,text=True,encoding="utf-8")
def main():
    p=argparse.ArgumentParser(); p.add_argument("--allow-unpushed-current",action="store_true"); a=p.parse_args(); fail=[]
    head,origin,branch,remote=[git(*x) for x in (("rev-parse","HEAD"),("rev-parse","origin/main"),("branch","--show-current"),("remote","get-url","origin"))]
    if any(x.returncode for x in (head,origin,branch,remote)): fail.append("required Git query failed")
    hv,ov=head.stdout.strip(),origin.stdout.strip()
    if branch.stdout.strip()!="main": fail.append("branch is not main")
    if remote.stdout.strip().removesuffix(".git")!="https://github.com/LoFiGamerGuy/visual-narrative-compiler": fail.append("origin URL differs")
    if not a.allow_unpushed_current and hv!=ov: fail.append("HEAD differs from origin/main")
    try:
        delivery=json.loads(DELIVERY.read_text(encoding="utf-8")); safe=json.loads(SAFE.read_text(encoding="utf-8")); release=json.loads(RELEASE.read_text(encoding="utf-8")); capture=safe["captured_commit"]
        for descendant,label in (("HEAD","HEAD"),("origin/main","origin/main")):
            if git("merge-base","--is-ancestor",capture,descendant).returncode: fail.append(f"safe capture is not ancestor of {label}")
        if delivery["state"]!="PASS_OWNER_PENDING" or delivery["summary"]["candidates"]!=29: fail.append("delivery state invalid")
        if safe["remote_parity_at_capture"] is not True or safe["summary"]["tracked_paths"]!=835: fail.append("safe-source state invalid")
        if release["state"]!="PASS" or release["summary"]["effective_command_count"]!=66: fail.append("release state invalid")
    except (FileNotFoundError,KeyError,json.JSONDecodeError) as er: fail.append(f"evidence read failed: {er}")
    if not a.allow_unpushed_current and (git("diff","--quiet").returncode or git("diff","--cached","--quiet").returncode): fail.append("tracked working tree or index differs")
    for item in fail: print(f"FAIL: {item}")
    if fail: return 1
    print("CH05 remote lineage r2: 0 failures; main/origin configured; current safe capture is ancestor of HEAD and origin/main")
    print("delivery r2/source r2/release r10 states exact; ignored and unrelated untracked items excluded")
    return 0
if __name__=="__main__": raise SystemExit(main())
