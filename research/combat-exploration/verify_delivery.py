from pathlib import Path
import json,hashlib,struct
R=Path(__file__).resolve().parents[2];P=R/'production/combat-exploration';read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
plan=read(P/'combat-plan.json');ids={e['id'] for e in plan['entries']};assert len(ids)==18
rows=read(P/'candidates.json')['candidates'];by={r['attempt_id']:r for r in rows};assert len(by)==len(rows) and 18<=len(rows)<=24
assert {r['id'] for r in rows if r['attempt_id'].endswith('-P')}==ids and sum(r['attempt_id'].endswith('-P') for r in rows)==18
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
 for ref in c['references']:assert sha(R/ref['path'])==ref['sha256']
 if not aid.endswith('-P'):assert c['retry_of']==r['id']+'-P' and c['retry_reason']
refs=read(P/'references.json');assert len(refs)==9
for ref in refs:assert sha(R/ref['path'])==ref['sha256']
selected=read(P/'selected.json')['selected'];assert set(selected)==ids
for id,aid in selected.items():assert by[aid]['id']==id
data=read(R/'docs/combat-exploration/data.json');assert data['available_count']==18 and data['owner_approval'] is None and data.get('canon') is None
for e in data['entries']:
 c=e['candidate'];assert c['attempt_id']==selected[e['id']] and c['sha256']==by[c['attempt_id']]['sha256']
 assert (R/'docs/combat-exploration'/c['src']).resolve()==(R/c['path']).resolve()
assert data['plan_sha256']==sha(P/'combat-plan.json')
report={'schema':'CombatExplorationDeliveryVerification/1','pass':True,'components':18,'primary_generations':18,'repairs':len(rows)-18,'native_attempts':len(rows),'references':9,'selected_repairs':sum(a.endswith('-R1') for a in selected.values()),'original_tool_bytes_match':True,'direct_paid_spend_usd':0,'owner_approval':None,'dataset_sha256':data['dataset_sha256']}
(R/'research/combat-exploration/delivery-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
