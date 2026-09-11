#!/usr/bin/env python3
"""Focused CD additions to inherited ZIP safety tests; task-owned fixtures only."""
import importlib.util,json,tempfile,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent

def load(name):
 spec=importlib.util.spec_from_file_location(name,HERE/(name+'.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
b=load('bundle_assets');p=load('check_preservation');out=Path(tempfile.mkdtemp(prefix='cd-contracts-',dir=HERE/'local'));checks=[]
def rejects(label,fn):
 try:fn()
 except ValueError:checks.append(label)
 else:raise AssertionError(label+' accepted')
old={'/prior/tree':['HEAD '+'a'*40,'branch refs/heads/prior']};new={**old,str(p.ROOT):['HEAD '+'b'*40,'branch '+p.ACTIVE_REF]}
assert p.compare_topology(old,new)['pass'];checks.append('precreation topology allows exactly active addition')
assert not p.compare_topology(old,{**new,'/prior/tree':['HEAD '+'c'*40,'branch refs/heads/prior']})['pass'];checks.append('prior HEAD change fails topology')
rejects('second new worktree rejected',lambda:p.compare_topology(old,{**new,'/another':[]}))
rejects('active branch change rejected',lambda:p.compare_topology(old,{**new,str(p.ROOT):['HEAD '+'b'*40,'branch refs/heads/other']}))
rejects('active extra flags rejected',lambda:p.compare_topology(old,{**new,str(p.ROOT):new[str(p.ROOT)]+['locked']}))
assert p.compare_refs({'refs/heads/prior':'a'}, {'refs/heads/prior':'a',p.ACTIVE_REF:'b',p.REMOTE_REF:'b'})['pass'];checks.append('only active branch and remote refs exempt')
assert not p.compare_refs({'refs/heads/prior':'a'}, {'refs/heads/prior':'c'})['pass'];checks.append('prior ref change fails')
root=out/'transport';prod=root/'production/combat-depth';(prod/'calls').mkdir(parents=True);(prod/'transport-failures').mkdir();attempts={}
def add(i):
 ident='D%02d'%i;attempt=ident+'-F1';source='production/combat-depth/candidates/'+ident+'-P.png';failrel='production/combat-depth/transport-failures/'+attempt+'.json';f={'schema':'CombatDepthTransportFailure/1','id':ident,'attempt_id':attempt,'phase':'texture','category':'duel','retry_of':ident+'-P','prompt_path':'production/combat-depth/prompts/'+attempt+'.txt','prompt_sha256':'b'*64,'plan_sha256':'c'*64,'references':[{'path':source,'sha256':'a'*64}],'referenced_image_paths':['/original/'+source],'started':{'current_time':f'2026-09-08 01:0{i}:00 UTC'},'finished':{'current_time':f'2026-09-08 01:0{i}:30 UTC'},'status':'failed-no-artwork-returned','error':'HTTP503','returned_artwork':None};(root/failrel).write_bytes(b.encoded(f));r={k:v for k,v in f.items() if k not in ('schema','finished','status','error','returned_artwork')};r.update(started={'current_time':f'2026-09-08 02:0{i}:00 UTC'},transport_retry_of=failrel,transport_retry_sha256=b.hashed(root/failrel)[1],transport_retry_reason='identical service retry');(prod/'calls'/f'{attempt}.json').write_bytes(b.encoded(r));attempts[attempt]={};return r
r1=add(1);r2=add(2)
x=b.transport_ledger(root,attempts,56,True);assert x['invocation_count']==4 and x['native_artwork_count']==2 and x['transport_retry_invocations']==2;checks.append('two independent unchanged service retries accepted and counted')
add(3);rejects('third service retry rejected',lambda:b.transport_ledger(root,attempts,56,True))
pr=out/'plan-versions';pp=pr/'production/combat-depth';history=pp/'plan-history';history.mkdir(parents=True)
base={'schema':'CombatDepthPlan/1','experiment_id':'CD-20260908-01','entries':[{'id':i} for i in sorted(b.EXPECTED_IDS)],'budget':{'primary':24,'structural_repairs':6,'texture_passes':24,'maximum_native_attempts':54,'transport_retries':2,'maximum_total':56}}
def write_plan(path,record):
 path.write_bytes(b.encoded(record));digest=b.hashed(path)[1];path.with_suffix('.sha256').write_text(digest+'\n');return digest
oldsha=write_plan(history/'plan-v2.json',dict(base,title='old'))
newsha=write_plan(pp/'plan.json',dict(base,title='new'))
versions=b.plan_versions(pr);assert len(versions)==2
assert b.require_plan_version(oldsha,versions)['path'].endswith('/plan-v2.json');checks.append('historical call resolves exact preserved plan instead of current')
assert b.require_plan_version(newsha,versions)['path'].endswith('/plan.json');checks.append('current call resolves exact current plan')
rejects('unknown call plan SHA rejected',lambda:b.require_plan_version('0'*64,versions))
(history/'plan-v2.sha256').write_text('0'*64+'\n');rejects('archived sidecar mismatch rejected',lambda:b.plan_versions(pr));write_plan(history/'plan-v2.json',dict(base,title='old'))
(history/'plan-v2.sha256').unlink();rejects('missing archived SHA sidecar rejected',lambda:b.plan_versions(pr));write_plan(history/'plan-v2.json',dict(base,title='old'))
write_plan(history/'plan-v2.json',dict(base,experiment_id='WRONG'));rejects('historical wrong experiment rejected',lambda:b.plan_versions(pr))
write_plan(history/'plan-v2.json',dict(base,budget=dict(base['budget'],maximum_total=57)));rejects('historical changed budget rejected',lambda:b.plan_versions(pr))
result={'schema':'CombatDepthSpecificHelperTests/1','pass':True,'checks':checks,'bundle_helper_sha256':b.hashed(HERE/'bundle_assets.py')[1],'preservation_helper_sha256':b.hashed(HERE/'check_preservation.py')[1],'test_source_sha256':b.hashed(Path(__file__))[1],'fixture_directory':str(out.relative_to(b.ROOT)),'original_worktree_mutations':False,'final_archive_created':False};(out/'receipt.json').write_bytes(b.encoded(result));(HERE/'cd-contract-test-receipt.json').write_bytes(b.encoded(result));print(json.dumps(result,indent=2))
