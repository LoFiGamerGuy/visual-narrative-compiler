"""Reproduce immutable CH05 release r2 directly while normalizing one mutable path-count diagnostic."""
from __future__ import annotations
import hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];R1=ROOT/"docs/research/evidence/ch05-overnight-integrated-release-gate-r1.json";R2=ROOT/"docs/research/evidence/ch05-overnight-integrated-release-gate-r2.json";EXPECTED_R2="08cb14e56334b7c3a3cb60bb6f4c110d3ad20b3b2ae8d45b45537b0df51b0138"
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def normalize(path:str,text:str)->str:return re.sub(r"\d+ tracked safe-source paths","<dynamic> tracked safe-source paths",text) if path.endswith("validate_tracked_source_scope.py") else text
def execute(item:dict)->list[str]:
 out=[];path=ROOT/item["path"]
 if not path.is_file() or sha(path)!=item["script_sha256"]:return [f"script mismatch: {item['path']}"]
 done=subprocess.run([sys.executable,str(path)],cwd=ROOT,capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=300);stdout=done.stdout.replace("\r\n","\n").strip()+"\n";expected=item.get("normalized_stdout",item.get("stdout","")).replace("\r\n","\n").strip()+"\n"
 if done.returncode!=0:out.append(f"return code: {item['path']}")
 if done.stderr:out.append(f"stderr: {item['path']}")
 if hashlib.sha256(normalize(item["path"],stdout).encode()).hexdigest()!=hashlib.sha256(normalize(item["path"],expected).encode()).hexdigest():out.append(f"stdout mismatch: {item['path']}")
 return out
def main()->int:
 fail=[]
 if sha(R2)!=EXPECTED_R2:fail.append("immutable r2 hash mismatch")
 r1=json.loads(R1.read_text(encoding="utf-8"));r2=json.loads(R2.read_text(encoding="utf-8"))
 if r2.get("state")!="PASS" or r2["summary"].get("effective_command_count")!=18 or r2["supersedes"].get("sha256")!=sha(R1):fail.append("r2 semantic/base binding mismatch")
 for item in r1["results"]:
  if item["path"].endswith("validate_ch05_instrumented_production_manifest.py"):
   path=ROOT/item["path"]
   if not path.is_file() or sha(path)!=item["script_sha256"]:fail.append("historical manifest-validator script mismatch")
   continue
  fail.extend(execute(item))
 for item in r2["results"][1:]:fail.extend(execute(item))
 print(f"CH05 release r2 compatibility: {len(fail)} failures; 17 current + 1 historical-pinned base checks; tracked-count normalization 1")
 print("historical manifest registry hash deferred to current r2 handoff validator; immutable r1/r2 bytes retained; 0 network/provider/upload/$0")
 for item in fail:print(f"FAIL: {item}")
 return 1 if fail else 0
if __name__=="__main__":raise SystemExit(main())
