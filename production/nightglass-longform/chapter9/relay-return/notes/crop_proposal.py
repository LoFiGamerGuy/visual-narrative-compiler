from pathlib import Path
from PIL import Image
import json,hashlib,sys
r=Path(__file__).resolve().parents[1];b=r.parents[3]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
spec=json.loads(Path(sys.argv[1]).read_text());out=[]
for x in spec:
 src=r/'candidates'/f"{x['attempt_id']}.png";im=Image.open(src);box=x['box_xyxy'];crop=im.crop(box);p=r/'crops'/f"{x['panel']}-{x['attempt_id'].rsplit('-',1)[1]}.png";assert not p.exists();crop.save(p);assert Image.open(p).tobytes()==crop.tobytes()
 out.append({'panel':x['panel'],'path':str(p.relative_to(b)),'sha256':sha(p),'attempt_id':x['attempt_id'],'crop':{'source_path':str(src.relative_to(b)),'source_sha256':sha(src),'source_dimensions':list(im.size),'box_xyxy':box,'operation':'lossless full horizontal story tier crop'},'selection_notes':x['selection_notes']})
name=sys.argv[2];dest=r/'notes'/name;assert not dest.exists();dest.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(dest)
