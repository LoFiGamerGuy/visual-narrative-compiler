from pathlib import Path
import sys,json,hashlib,shutil
r=Path(__file__).resolve().parents[4];d=Path(__file__).parent
ident,src,note=sys.argv[1:4];src=Path(src);dst=d/'candidates'/f'{ident}.png';shutil.copyfile(src,dst)
p=d/'calls'/f'{ident}.json';rec=json.loads(p.read_text());rec.update(status='returned',native=str(dst.relative_to(r)),sha256=hashlib.sha256(dst.read_bytes()).hexdigest(),tool_native=str(src),inspection=note);p.write_text(json.dumps(rec,indent=2)+'\n')
