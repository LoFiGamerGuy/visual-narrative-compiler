"""Verify native art, exact prompt/reference binding, bounded attempts and reader inputs."""
from pathlib import Path
import hashlib,json,struct
R=Path(__file__).resolve().parents[2];P=R/'production/world-components'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
plan=json.loads((P/'kit-plan.json').read_text());expected={e['id'] for e in plan['entries']}
assert len(expected)==54
rows=json.loads((P/'candidates.json').read_text())['candidates'];byid={r['attempt_id']:r for r in rows}
assert len(byid)==len(rows) and 54<=len(rows)<=63
assert {r['id'] for r in rows if r['attempt_id'].endswith('-P')}==expected
assert sum(r['attempt_id'].endswith('-P') for r in rows)==54
assert len({r['id'] for r in rows if r['attempt_id'].endswith('-R')})==len(rows)-54
calls={p.stem:json.loads(p.read_text()) for p in (P/'calls').glob('*.json')}
assert set(calls)==set(byid),'Every attempted call must be accounted for'
native_bytes=0
for aid,c in calls.items():
 r=byid[aid];p=R/r['path'];raw=p.read_bytes()
 assert r['id']==c['id'] and r['status']=='reviewable-unaccepted' and r['owner_approval'] is None
 assert sha(p)==r['sha256']==sha(Path(r['source_path']))
 assert struct.unpack('>II',raw[16:24])==(r['width'],r['height'])
 assert sha(R/c['prompt_path'])==c['prompt_sha256']==r['prompt_sha256']
 assert c['finished'] and c['output_hint'] and c['direct_paid_spend_usd']==0
 for ref in c['references']:assert sha(R/ref['path'])==ref['sha256']
 if aid.endswith('-R'):assert c.get('retry_of')==r['id']+'-P' and c.get('retry_reason')
 native_bytes+=len(raw)
refs=json.loads((P/'references.json').read_text());assert len(refs)==9
for ref in refs:assert sha(R/ref['path'])==ref['sha256']
selected=json.loads((P/'selected.json').read_text())['selected'];assert set(selected)==expected
for id,aid in selected.items():assert byid[aid]['id']==id
data=json.loads((R/'docs/world-components/data.json').read_text());assert data['available_count']==54 and data['owner_approval'] is None and data['canon'] is None
assert len(data['entries'])==54 and data['plan_sha256']==sha(P/'kit-plan.json')
for e in data['entries']:
 c=e['candidate'];assert c['attempt_id']==selected[e['id']] and c['sha256']==byid[c['attempt_id']]['sha256']
 assert (R/'docs/world-components'/c['src']).resolve()==(R/c['path']).resolve()
assert (R/'docs/world-components/data.js').read_text()=='window.WORLD_COMPONENT_DATA = '+(R/'docs/world-components/data.json').read_text().rstrip()+';\n'
report={'schema':'WorldComponentDeliveryVerification/1','pass':True,'components':54,'native_attempts':len(rows),'primaries':54,'retries':len(rows)-54,'native_bytes':native_bytes,'original_references':9,'source_bound_reader':True,'original_tool_bytes_match':True,'direct_paid_spend_usd':0,'owner_approval':None,'dataset_sha256':data['dataset_sha256']}
(R/'research/world-components/delivery-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
