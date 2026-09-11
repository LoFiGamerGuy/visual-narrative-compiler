from pathlib import Path
import json,hashlib,zipfile,datetime
ROOT=Path(__file__).resolve().parents[3]
P=ROOT/'production/visual-directions/cover-examples'
D=ROOT/'docs/research/visual-directions/cover-examples'
R=Path(__file__).resolve().parent
def sha(data):return hashlib.sha256(data).hexdigest()
def read(p):return json.loads(p.read_text())
contract=read(P/'concepts.json');assert sha((P/'concepts.json').read_bytes())==(P/'concepts.json.sha256').read_text().strip()
images=read(P/'images.json')['images'];assert len(images)==10 and {i['id'] for i in images}=={f'{i:02}' for i in range(1,11)}
assert len(list((P/'calls').glob('*-returned.json')))==10
reference=ROOT/contract['reference'];assert sha(reference.read_bytes())==contract['reference_sha256']
payload={}
for r in images:
    cid=r['id'];returned=read(P/'calls'/f'{cid}-returned.json');reserved=read(P/'calls'/f'{cid}-reservation.json')
    assert sha((ROOT/r['path']).read_bytes())==r['sha256']==sha(Path(returned['source_path']).read_bytes())
    assert sha((ROOT/reserved['prompt_path']).read_bytes())==reserved['prompt_sha256']
    assert r['width']==1024 and r['height']==1536
    payload[f'art-{cid}.png']=(ROOT/r['path']).read_bytes()
    payload[f'cover-{cid}.png']=(D/f'cover-{cid}.png').read_bytes()
    payload[f'source/prompts/{cid}.txt']=(ROOT/reserved['prompt_path']).read_bytes()
    payload[f'source/calls/{cid}-reservation.json']=(P/'calls'/f'{cid}-reservation.json').read_bytes()
    payload[f'source/calls/{cid}-returned.json']=(P/'calls'/f'{cid}-returned.json').read_bytes()
qa=read(R/'browser-qa.json');assert qa['pass']
for b in qa['bindings']+qa['covers']+[qa['overview']]:assert sha((ROOT/b['path']).read_bytes())==b['sha256']
for name in ('index.html','overview.html','style.css','app.js','START_HERE.txt','overview.png'):payload[name]=(D/name).read_bytes()
payload['source/concepts.json']=(P/'concepts.json').read_bytes();payload['source/images.json']=(P/'images.json').read_bytes()
kit=ROOT/'research/visual-directions/black-petal-cover-kit';kit_receipt=read(kit/'archive-receipt.json');kit_zip=kit/kit_receipt['archive'];assert sha(kit_zip.read_bytes())==kit_receipt['sha256']
with zipfile.ZipFile(kit_zip) as z:
    for info in z.infolist():
        assert not info.is_dir() and '/' not in info.filename and '\\' not in info.filename
        payload['source/kit/'+info.filename]=z.read(info)
payload['source/README.txt']=b'All ten example prompts use kit/black-petal-reference.png as a STYLE reference. The titles and author names are separate HTML/CSS. The original kit and exact call records are preserved here. Model snapshots and seeds were not exposed.\n'
result={'schema':'BlackPetalCoverResults/1','verified_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'tool':'image_gen.imagegen','primary_calls':10,'retry_calls':0,'native_illustrations':10,'cover_mockups':10,'overview_sheets':1,'source_reference_sha256':contract['reference_sha256'],'frozen_concepts_sha256':sha((P/'concepts.json').read_bytes()),'all_prompts_and_tool_originals_verified':True,'source_bindings':images,'browser_qa_pass':True,'model':None,'snapshot':None,'seed':None,'usage':None,'billing_allocation':None,'direct_paid_usd':0,'owner_or_wife_acceptance':None,'sample_titles_are_invented':True,'new_anime_refinement_calls':0}
(R/'results.json').write_text(json.dumps(result,indent=2)+'\n');payload['source/results.json']=(R/'results.json').read_bytes()
manifest={'schema':'BlackPetalCoverShareFiles/1','files':[{'path':name,'bytes':len(data),'sha256':sha(data)} for name,data in sorted(payload.items())]};manifest_data=(json.dumps(manifest,indent=2)+'\n').encode();(R/'share-manifest.json').write_bytes(manifest_data);payload['manifest.json']=manifest_data
local=R/'local';local.mkdir(exist_ok=True);archive=local/'Black-Petal-Ten-Cover-Examples.zip'
with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_STORED) as z:
    for name,data in sorted(payload.items()):
        info=zipfile.ZipInfo(name,(2026,9,7,0,0,0));info.external_attr=0o100644<<16;z.writestr(info,data)
with zipfile.ZipFile(archive) as z:
    assert set(z.namelist())==set(payload) and z.testzip() is None
    for name,data in payload.items():assert z.read(name)==data
receipt={'schema':'BlackPetalCoverShareArchive/1','archive':'local/'+archive.name,'bytes':archive.stat().st_size,'sha256':sha(archive.read_bytes()),'members':len(payload),'all_member_bytes_verified':True}
(R/'archive-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
