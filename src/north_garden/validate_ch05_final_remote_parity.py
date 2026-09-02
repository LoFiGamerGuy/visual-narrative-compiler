"""Validate final CH05 capture, release, closeout, frozen state, and Git remote parity."""
from __future__ import annotations
import argparse,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; SAFE=ROOT/"docs/research/evidence/ch05-overnight-safe-source-parity-r3.json"; RELEASE=ROOT/"docs/research/evidence/ch05-overnight-integrated-release-gate-r11.json"; CLOSEOUT=ROOT/"docs/research/evidence/ch05-overnight-closeout-bundle-r1.json"
def git(*args): return subprocess.run(["git",*args],cwd=ROOT,capture_output=True,text=True,encoding="utf-8")
def main():
    p=argparse.ArgumentParser(); p.add_argument("--allow-unpushed-current",action="store_true"); a=p.parse_args(); fail=[]; head,origin,branch,remote=[git(*x) for x in (("rev-parse","HEAD"),("rev-parse","origin/main"),("branch","--show-current"),("remote","get-url","origin"))]; hv,ov=head.stdout.strip(),origin.stdout.strip()
    if any(x.returncode for x in (head,origin,branch,remote)): fail.append("Git query failed")
    if branch.stdout.strip()!="main": fail.append("branch is not main")
    if remote.stdout.strip().removesuffix(".git")!="https://github.com/LoFiGamerGuy/visual-narrative-compiler": fail.append("origin URL differs")
    if not a.allow_unpushed_current and hv!=ov: fail.append("HEAD differs from origin/main")
    try:
        safe=json.loads(SAFE.read_text(encoding="utf-8")); release=json.loads(RELEASE.read_text(encoding="utf-8")); closeout=json.loads(CLOSEOUT.read_text(encoding="utf-8")); capture=safe["captured_commit"]
        if safe["remote_parity_at_capture"] is not True or release["state"]!="PASS" or release["summary"]["effective_command_count"]!=74 or closeout["state"]!="PASS_OWNER_PENDING": fail.append("evidence state invalid")
        for descendant,label in (("HEAD","HEAD"),("origin/main","origin/main")):
            if git("merge-base","--is-ancestor",capture,descendant).returncode: fail.append(f"capture is not ancestor of {label}")
    except (FileNotFoundError,KeyError,json.JSONDecodeError) as er: fail.append(f"evidence read failed: {er}")
    for script in ("src/north_garden/validate_tracked_source_scope.py","src/north_garden/validate_frozen_gauntlet_baseline_integrity.py"):
        if subprocess.run([sys.executable,script],cwd=ROOT,capture_output=True).returncode: fail.append(f"validator failed: {script}")
    if not a.allow_unpushed_current and (git("diff","--quiet").returncode or git("diff","--cached","--quiet").returncode): fail.append("tracked tree/index differs")
    for item in fail: print(f"FAIL: {item}")
    if fail: return 1
    print("CH05 final remote parity: 0 failures; main/origin configured; final capture ancestor; release 74/closeout/frozen/scope pass")
    print("generated pixels and unrelated untracked items excluded; provider/promotion state unchanged")
    return 0
if __name__=="__main__": raise SystemExit(main())
