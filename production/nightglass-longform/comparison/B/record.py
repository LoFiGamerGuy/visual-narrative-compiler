from pathlib import Path
import sys,json,hashlib,shutil
root=Path(__file__).resolve().parents[4];d=root/'production/nightglass-longform/comparison/B'
n=sys.argv[1];src=Path(sys.argv[2]);note=sys.argv[3];dst=d/f'candidates/B{n}-P.png';shutil.copyfile(src,dst)
p=d/f'calls/B{n}-P.json';r=json.loads(p.read_text());r.update(status='returned',native=str(dst.relative_to(root)),sha256=hashlib.sha256(dst.read_bytes()).hexdigest(),tool_native=str(src),inspection=note);p.write_text(json.dumps(r,indent=2))
