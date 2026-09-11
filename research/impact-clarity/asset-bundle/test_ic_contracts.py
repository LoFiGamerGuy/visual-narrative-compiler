#!/usr/bin/env python3
"""Focused IC additions to inherited ZIP safety tests; task-owned fixtures only."""
import importlib.util,json,tempfile,hashlib,copy
from pathlib import Path
HERE=Path(__file__).resolve().parent

def load(name):
 spec=importlib.util.spec_from_file_location(name,HERE/(name+'.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
b=load('bundle_assets');p=load('check_preservation');out=Path(tempfile.mkdtemp(prefix='ic-contracts-',dir=HERE/'local'));checks=[]
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
root=out/'transport';prod=root/'production/impact-clarity';(prod/'calls').mkdir(parents=True);(prod/'transport-failures').mkdir();attempts={}
def add(i):
 ident=('M%02d'%i) if i<3 else 'X01';attempt=ident+'-F1';source='production/impact-clarity/candidates/'+ident+'-P.png';failrel='production/impact-clarity/transport-failures/'+attempt+'.json';f={'schema':'ImpactClarityTransportFailure/1','id':ident,'attempt_id':attempt,'phase':'texture','category':'duel','retry_of':ident+'-P','prompt_path':'production/impact-clarity/prompts/'+attempt+'.txt','prompt_sha256':'b'*64,'plan_sha256':'c'*64,'references':[{'path':source,'sha256':'a'*64}],'referenced_image_paths':['/original/'+source],'started':{'current_time':f'2026-09-08 01:0{i}:00 UTC'},'finished':{'current_time':f'2026-09-08 01:0{i}:30 UTC'},'status':'failed-no-artwork-returned','error':'HTTP503','returned_artwork':None};(root/failrel).write_bytes(b.encoded(f));r={k:v for k,v in f.items() if k not in ('schema','finished','status','error','returned_artwork')};r.update(started={'current_time':f'2026-09-08 02:0{i}:00 UTC'},transport_retry_of=failrel,transport_retry_sha256=b.hashed(root/failrel)[1],transport_retry_reason='identical service retry');(prod/'calls'/f'{attempt}.json').write_bytes(b.encoded(r));attempts[attempt]={};return r
r1=add(1);r2=add(2)
x=b.transport_ledger(root,attempts,56,True);assert x['invocation_count']==4 and x['native_artwork_count']==2 and x['transport_retry_invocations']==2;checks.append('two independent unchanged service retries accepted and counted')
add(3);rejects('third service retry rejected',lambda:b.transport_ledger(root,attempts,56,True))
pr=out/'plan-versions';pp=pr/'production/impact-clarity';history=pp/'plan-history';history.mkdir(parents=True)
for rel in ['plan.json','plan.sha256','plan-history/plan-v1.json','plan-history/plan-v1.sha256','scope-amendment-01.json']:
 source=b.ROOT/'production/impact-clarity'/rel;target=pp/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(source.read_bytes())
oldsha=b.BASE_PLAN_SHA256;newsha=b.hashed(pp/'plan.json')[1];versions=b.plan_versions(pr);assert len(versions)==2
assert b.require_plan_version(oldsha,versions,'M01')['path'].endswith('/plan-v1.json');checks.append('original call resolves preserved V1 under original budget')
assert b.require_plan_version(newsha,versions,'Y01')['path'].endswith('/plan.json');checks.append('new Y call resolves expanded authorized plan')
rejects('Y call cannot bind original12 plan',lambda:b.require_plan_version(oldsha,versions,'Y01'))
rejects('unknown call plan SHA rejected',lambda:b.require_plan_version('0'*64,versions))
sidecar=history/'plan-v1.sha256';saved_sidecar=sidecar.read_bytes();sidecar.write_text('0'*64+'\n');rejects('archived sidecar mismatch rejected',lambda:b.plan_versions(pr));sidecar.write_bytes(saved_sidecar)
sidecar.unlink();rejects('missing archived SHA sidecar rejected',lambda:b.plan_versions(pr));sidecar.write_bytes(saved_sidecar)
original=history/'plan-v1.json';saved_original=original.read_bytes();record=json.loads(saved_original);original.write_bytes(b.encoded(dict(record,experiment_id='WRONG')));rejects('historical wrong experiment rejected',lambda:b.plan_versions(pr));original.write_bytes(saved_original)
current=json.loads((pp/'plan.json').read_text());assert b.resolve_budget(pr,current,{})['effective_budget']==b.EXPANDED_BUDGET;checks.append('exact scope amendment authorizes16 studies with unchanged repair slots')
modified=copy.deepcopy(current);modified['budget']['structural_repairs']=5;rejects('expanded repair cap cannot increase',lambda:b.resolve_budget(pr,modified,{}))
modified=copy.deepcopy(current);modified.pop('scope_amendment');rejects('expanded budget without authorization rejected',lambda:b.resolve_budget(pr,modified,{}))
modified=copy.deepcopy(current);modified['entries'][0]['brief']='different';rejects('original study mutation rejected',lambda:b.resolve_budget(pr,modified,{}))
modified=copy.deepcopy(current);modified['entries'][-1]['id']='Y05';rejects('unapproved new study ID rejected',lambda:b.resolve_budget(pr,modified,{}))
modified=copy.deepcopy(current);modified['reference_library'][0]['sha256']='0'*64;rejects('original reference library mutation rejected',lambda:b.resolve_budget(pr,modified,{}))
amend=pp/'scope-amendment-01.json';saved_amend=amend.read_bytes();amend.write_bytes(saved_amend+b' ');rejects('authorization record bytes changed rejected',lambda:b.resolve_budget(pr,current,{}));amend.write_bytes(saved_amend)
original.write_bytes(saved_original+b' ');rejects('original plan must remain byte-exact',lambda:b.resolve_budget(pr,current,{}));original.write_bytes(saved_original)
rejects('six-reference preflight rejected',lambda:b.require_reference_limit({'references':[{}]*6}))
rejects('zero-reference preflight rejected',lambda:b.require_reference_limit({'references':[]}))
rejects('no inherited changed-input exception',lambda:b.require_reference_limit({'references':[{}],'input_validation_retry_of':'old-W06'}))
histroot=out/'prior';hp=histroot/'production/impact-clarity/previous';hp.mkdir(parents=True);export=hp/'ce-selection.json';export.write_bytes(b.encoded({'schema':'CombatExplorationChoices/1','experiment_id':'historical-CE','plan_sha256':'d'*64,'dataset_sha256':'e'*64,'choices':[]}));expected=b.hashed(export)[1];priorplan={'prior_choices':{'path':'production/impact-clarity/previous/ce-selection.json','sha256':expected}}
def prior_binding(path,digest):
 b.safe_path(path)
 if b.hashed(histroot/path)[1]!=digest:raise ValueError('Prior source mismatch')
prior=b.prior_source_records(histroot,priorplan,prior_binding);assert prior[0]['historical_plan_sha256']=='d'*64 and prior[0]['sha256']==expected;checks.append('foreign CE plan identity preserved without IC reinterpretation')
rejects('foreign CE SHA still rejected as new IC call plan',lambda:b.require_plan_version('d'*64,versions))
export.write_bytes(b'{}');rejects('changed prior export bytes rejected',lambda:b.prior_source_records(histroot,priorplan,prior_binding))
rejects('prior export outside current namespace rejected',lambda:b.prior_source_records(histroot,{'prior_choices':{'path':'production/combat-exploration/old.json','sha256':expected}},prior_binding))
webroot=out/'nested-reference-data';web=webroot/'docs/impact-clarity';nested=web/'combat-references';nested.mkdir(parents=True);(web/'data.json').write_text('{}');(nested/'data.json').write_text(json.dumps({'entries':[{'image':'images/sample.jpg?view=1#crop'}]}));(nested/'images').mkdir();image=nested/'images/sample.jpg';image.write_bytes(b'fixture file; no generated image')
assert b.local_links(webroot)['checked_local_urls']==1;checks.append('nested research image path resolves from its own data directory')
image.unlink();rejects('missing nested research image rejected',lambda:b.local_links(webroot))
rejects('research local source cache excluded from payload',lambda:b.safe_path('research/impact-clarity/combat-reference-research/local/full-source.jpg'))
result={'schema':'ImpactClaritySpecificHelperTests/1','pass':True,'checks':checks,'bundle_helper_sha256':b.hashed(HERE/'bundle_assets.py')[1],'preservation_helper_sha256':b.hashed(HERE/'check_preservation.py')[1],'test_source_sha256':b.hashed(Path(__file__))[1],'fixture_directory':str(out.relative_to(b.ROOT)),'original_worktree_mutations':False,'final_archive_created':False};(out/'receipt.json').write_bytes(b.encoded(result));(HERE/'ic-contract-test-receipt.json').write_bytes(b.encoded(result));print(json.dumps(result,indent=2))
