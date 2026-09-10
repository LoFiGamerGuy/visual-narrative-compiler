from pathlib import Path
from PIL import Image
import hashlib,json,shutil,sys
r=Path(__file__).parent; root=r.parents[3]
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
spec=json.loads((r/'notes'/sys.argv[1]).read_text());selpath=r/'selected-records.json';sels=json.loads(selpath.read_text()) if selpath.exists() else []
for q in spec:
 s=r/'candidates'/(q['attempt_id']+'.png');im=Image.open(s);box=q.get('box_xyxy',[0,0,*im.size]);p=r/'crops'/(q['panel_id']+q.get('suffix','')+'.png')
 assert not p.exists(), 'Refusing to overwrite a preserved crop'
 if box==[0,0,*im.size]:shutil.copy2(s,p)
 else:im.crop(box).save(p)
 rec={'panel_id':q['panel_id'],'path':str(p.relative_to(root)),'sha256':h(p),'attempt_id':q['attempt_id'],'crop':{'source_path':str(s.relative_to(root)),'source_sha256':h(s),'source_dimensions':list(im.size),'box_xyxy':box,'operation':'whole native frame copied unchanged' if box==[0,0,*im.size] else 'lossless full horizontal story tier crop'},'selection_reason':q['reason'],'limitations':q.get('limitations',[])}
 sels=[x for x in sels if x['panel_id']!=q['panel_id']];sels.append(rec);Image.open(p).resize((390,round(Image.open(p).height*390/Image.open(p).width))).save(r/'references'/(q['panel_id']+'-390.png'));print(q['panel_id'],rec['path'],rec['sha256'])
selpath.write_text(json.dumps(sorted(sels,key=lambda x:x['panel_id']),indent=2))
