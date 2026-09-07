from pathlib import Path
import hashlib,json,struct,shutil
ROOT=Path(__file__).resolve().parents[3]
P=ROOT/'production/visual-directions/cover-examples'
D=ROOT/'docs/research/visual-directions/cover-examples'
rows=[]
for receipt in sorted((P/'calls').glob('*-returned.json')):
    r=json.loads(receipt.read_text());cid=r['id'];source=Path(r['source_path']);dest=D/f'art-{cid}.png'
    digest=hashlib.sha256(source.read_bytes()).hexdigest()
    if dest.exists():assert hashlib.sha256(dest.read_bytes()).hexdigest()==digest
    else:
        with source.open('rb') as inp,dest.open('xb') as out:shutil.copyfileobj(inp,out)
    data=dest.read_bytes();assert data[:8]==b'\x89PNG\r\n\x1a\n';width,height=struct.unpack('>II',data[16:24])
    row={'id':cid,'attempt_id':r['attempt_id'],'path':dest.relative_to(ROOT).as_posix(),'sha256':digest,'bytes':len(data),'width':width,'height':height,'tool_original_retained':True,'model':None,'snapshot':None,'seed':None,'usage':None,'billing_allocation':None,'direct_paid_usd':0}
    rows.append(row)
(P/'images.json').write_text(json.dumps({'schema':'BlackPetalCoverImages/1','images':rows},indent=2)+'\n')
print(json.dumps({'registered':len(rows),'ids':[r['id'] for r in rows]}))
