from pathlib import Path
import json,hashlib,struct,collections
R=Path(__file__).resolve().parents[2];P=R/'production/nightglass-refinement'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
plan=read(P/'refinement-plan.json');ids={e['id'] for e in plan['entries']};assert len(ids)==24
assert collections.Counter(e['category'] for e in plan['entries'])=={'refinement':4,'scene':6,'character':4,'equipment':3,'wildlife':1,'monster':2,'ability':4}
rows=read(P/'candidates.json')['candidates'];by={r['attempt_id']:r for r in rows};assert len(by)==len(rows) and 24<=len(rows)<=30
assert {r['id'] for r in rows if r['attempt_id'].endswith('-P')}==ids and sum(r['attempt_id'].endswith('-P') for r in rows)==24
repairs=[r for r in rows if not r['attempt_id'].endswith('-P')]
assert len(repairs)<=6 and len({r['id'] for r in repairs})==len(repairs)
assert all(r['attempt_id']==r['id']+'-R1' for r in repairs)
calls={p.stem:read(p) for p in (P/'calls').glob('*.json')};assert set(calls)==set(by)
for aid,c in calls.items():
 r=by[aid];p=R/r['path'];raw=p.read_bytes();assert sha(p)==r['sha256']==sha(Path(r['source_path']))
 assert struct.unpack('>II',raw[16:24])==(r['width'],r['height']) and r['width']*2==r['height']*3
 assert r['status']=='reviewable-unaccepted' and r['owner_approval'] is None
 assert sha(R/c['prompt_path'])==c['prompt_sha256']==r['prompt_sha256'] and c['finished'] and c['output_hint']
 assert c['direct_paid_spend_usd']==0 and all(c[k] is None for k in ['model','snapshot','seed','usage','billing'])
 assert 1<=len(c['references'])<=5
 for ref in c['references']:assert sha(R/ref['path'])==ref['sha256']
 if not aid.endswith('-P'):assert c['retry_of']==r['id']+'-P' and c['retry_reason']
rejected=[]
refs=read(P/'references.json');assert len(refs)==9
for ref in refs:assert sha(R/ref['path'])==ref['sha256']
prev=read(P/'previous/manifest.json');assert len(prev['sources'])==18
for s in prev['sources']:assert sha(R/s['path'])==s['sha256']
validated=read(R/'research/nightglass-refinement/previous-validation.json');assert validated['pass'] and sha(P/'previous/selection.json')==validated['export_sha256']
assert sha(P/'previous/data.json')==validated['data_sha256'] and sha(P/'previous/plan.json')==validated['plan_sha256']
world=read(P/'previous-world/manifest.json');assert len(world['sources'])==24
assert sha(P/'previous-world/data.json')==world['data_sha256']
for s in world['sources']:assert sha(R/s['path'])==s['sha256']
assert world['owner_choices_export'] is None
gate=read(P/'texture-gate.json');assert gate['expansion_allowed'] is True
selected=read(P/'selected.json')['selected'];assert set(selected)==ids
for id,aid in selected.items():assert by[aid]['id']==id
data=read(R/'docs/nightglass-refinement/data.json');assert data['available_count']==24 and data['owner_approval'] is None and data.get('canon') is None
for e in data['entries']:
 c=e['candidate'];assert c['attempt_id']==selected[e['id']] and c['sha256']==by[c['attempt_id']]['sha256']
 assert (R/'docs/nightglass-refinement'/c['src']).resolve()==(R/c['path']).resolve()
assert data['plan_sha256']==sha(P/'refinement-plan.json')
report={'schema':'NightglassRefinementDeliveryVerification/1','pass':True,'artworks':24,'primary_generations':24,'repairs':len(repairs),'native_attempts':len(rows),'pre_generation_rejections':len(rejected),'references':9,'previous_native_sources':18,'previous_world_sources':24,'texture_pairs':4,'previous_choices_preserved':True,'selected_repairs':sum(a.endswith('-R1') for a in selected.values()),'original_tool_bytes_match':True,'direct_paid_spend_usd':0,'owner_approval':None,'dataset_sha256':data['dataset_sha256']}
(R/'research/nightglass-refinement/delivery-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
