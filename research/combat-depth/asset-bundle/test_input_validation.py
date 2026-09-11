#!/usr/bin/env python3
"""W06 exact preflight and mutation-rejection fixtures, no production writes."""
import copy,importlib.util,json,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('bundle',HERE/'bundle_assets.py');b=importlib.util.module_from_spec(sp);sp.loader.exec_module(b)
r=b.ROOT;prod=r/'production/combat-depth';out=Path(tempfile.mkdtemp(prefix='input-validation-tests-',dir=HERE/'local'));root=out/'fixture';p=root/'production/combat-depth';p.mkdir(parents=True)
failure=json.loads((prod/'input-validation-failures/W06-P.json').read_text());job=json.loads((prod/'batch-09b-jobs.json').read_text())[0]
for rel in ['production/combat-depth/plan.json','production/combat-depth/plan.sha256','production/combat-depth/plan-history/plan-v6.json','production/combat-depth/plan-history/plan-v6.sha256',failure['prompt_path'],job['prompt_path']]:
 target=root/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((r/rel).read_bytes())
checks=[]
def reject(label,fn):
 try:fn()
 except ValueError:checks.append(label)
 else:raise AssertionError(label+' unexpectedly accepted')
assert b.validate_input_retry(root,job,failure)['corrected_reference_count']==5;checks.append('exact frozen W06 six-to-five correction accepted')
for label,field,value in [('scene change','id','W05'),('phase change','phase','repair'),('transport mixing','transport_retry_of','other'),('no reason','input_validation_retry_reason','')]:
 modified=copy.deepcopy(job);modified[field]=value;reject(label,lambda m=modified:b.validate_input_retry(root,m,failure))
modified=copy.deepcopy(job);modified['references'][0]['sha256']='0'*64;reject('remaining reference changed',lambda:b.validate_input_retry(root,modified,failure))
modified=copy.deepcopy(job);modified['references']=failure['references'][:5];reject('wrong reference removed',lambda:b.validate_input_retry(root,modified,failure))
reject('ordinary six-reference preflight rejected',lambda:b.require_reference_limit(job|{'references':failure['references']}))
assert b.require_reference_limit(failure,rejected=True) is None;checks.append('exact original rejected6 preserved')
modified=copy.deepcopy(failure);modified['input_validation_retry_of']='earlier';reject('second correction chain rejected',lambda:b.validate_input_retry(root,job,modified))
newprompt=root/job['prompt_path'];original=newprompt.read_bytes();newprompt.write_bytes(original+b'Change the attack.\n');modified=copy.deepcopy(job);modified['prompt_sha256']=b.hashed(newprompt)[1];reject('arbitrary corrected prompt change rejected',lambda:b.validate_input_retry(root,modified,failure));newprompt.write_bytes(original)
failpath=root/job['input_validation_retry_of'];failpath.parent.mkdir(parents=True,exist_ok=True);failpath.write_bytes((r/job['input_validation_retry_of']).read_bytes());(p/'calls').mkdir();request=copy.deepcopy(job);request.pop('prompt',None);request.update(started={'current_time':'2026-09-09 01:00:00 UTC'},referenced_image_paths=[str(root/x['path']) for x in request['references']]);(p/'calls/W06-P.json').write_bytes(b.encoded(request))
sidecars=list((prod/'input-validation-failures').glob('*tool*.json'));assert len(sidecars)==1;target=p/'input-validation-failures'/sidecars[0].name;target.write_bytes(sidecars[0].read_bytes());
ledger=b.transport_ledger(root,{'W06-P':{}},56,True);assert ledger['invocation_count']==2 and ledger['native_artwork_count']==1 and ledger['input_validation_retry_invocations']==1;checks.append('one failed input and one corrected native counted as two calls one art')
reject('input failure consumes invocation cap',lambda:b.transport_ledger(root,{'W06-P':{}},1,True))
# One input correction plus two transport retries exceeds the shared two-slot cap.
(p/'transport-failures').mkdir()
for n in (1,2):
 ident=f'D{n:02}';attempt=ident+'-F1';ref='production/combat-depth/candidates/'+ident+'-P.png';rel='production/combat-depth/transport-failures/'+attempt+'.json';f={'id':ident,'attempt_id':attempt,'phase':'texture','category':'duel','retry_of':ident+'-P','prompt_path':'production/combat-depth/prompts/'+attempt+'.txt','prompt_sha256':'b'*64,'plan_sha256':'c'*64,'references':[{'path':ref,'sha256':'a'*64}],'referenced_image_paths':['/old/'+ref],'started':{'current_time':f'2026-09-09 02:0{n}:00 UTC'},'finished':{'current_time':f'2026-09-09 02:0{n}:30 UTC'},'status':'failed-no-artwork-returned','returned_artwork':None,'error':'HTTP503'};(root/rel).write_bytes(b.encoded(f));retry={k:v for k,v in f.items() if k not in ('status','returned_artwork','error','finished')};retry.update(started={'current_time':f'2026-09-09 03:0{n}:00 UTC'},transport_retry_of=rel,transport_retry_sha256=b.hashed(root/rel)[1],transport_retry_reason='unchanged');(p/'calls'/f'{attempt}.json').write_bytes(b.encoded(retry))
 if n==1:
  assert b.transport_ledger(root,{},56)['total_no_art_retry_invocations']==2;checks.append('one input plus one transport share two slots')
reject('input plus two transport retries exceeds shared cap',lambda:b.transport_ledger(root,{},56))
for n in (1,2):(p/'calls'/f'D{n:02}-F1.json').unlink();(p/'transport-failures'/f'D{n:02}-F1.json').unlink()
# A duplicate correction for the same rejected request is an actual extra invocation and fails.
second=request|{'started':{'current_time':'2026-09-09 01:01:00 UTC'}};(p/'calls/W06-P-duplicate.json').write_bytes(b.encoded(second));reject('second input resubmission rejected',lambda:b.transport_ledger(root,{},56))
result={'schema':'CombatDepthInputCorrectionTests/1','pass':True,'checks':checks,'fixture_directory':str(out.relative_to(r)),'helper_sha256':b.hashed(HERE/'bundle_assets.py')[1],'source_sha256':b.hashed(Path(__file__))[1],'production_mutations':False,'archive_created':False};(out/'receipt.json').write_bytes(b.encoded(result));(HERE/'input-validation-test-receipt.json').write_bytes(b.encoded(result));print(json.dumps(result,indent=2))
