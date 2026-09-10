import json,hashlib,datetime,sys
from pathlib import Path
b=Path(__file__).resolve().parents[5]
r=b/'production/nightglass-longform/chapter8/lead'
g=json.loads((b/'research/nightglass-longform/CHAPTER8-PRODUCTION-GATE.json').read_text())
assert g['status']=='production-authorized-within-existing-user-scope'
assert hashlib.sha256((b/g['script_path']).read_bytes()).hexdigest()==g['script_sha256']
aid=sys.argv[1];refs=sys.argv[2:];unit,suffix=aid.rsplit('-',1)
phase={'P':'primary','R1':'repair','F1':'finish'}[suffix]
panels=[aid.split('-')[0]+'-'+part for part in aid.split('-')[1:-1] if part.isdigit()]
assert panels and all(p in [f'N8-{n:02d}' for n in [*range(2,15),*range(33,44)]] for p in panels)
records=[json.loads(p.read_text()) for p in (r/'calls').glob('*.json') if not p.name.endswith('-tool-return.json')]
assert sum(bool(c.get('invoked')) for c in records)<g['scope_ceilings']['lead'],'Local finite allowance exhausted'
if phase=='primary':assert not any(c.get('invoked') and c.get('phase')=='primary' and set(c.get('panels',[]))&set(panels) for c in records),'Original panel primary already invoked; no cap reset'
else:
 primary=json.loads((r/'calls'/f'{unit}-P.json').read_text());assert primary['status']=='returned'
 if phase=='repair':assert str((r/'candidates'/f'{unit}-P.png').relative_to(b)) in refs,'Repair must include the original primary'
 if phase=='finish':
  assert (r/'notes'/f'{unit}-finish-justification.json').is_file(),'Source-only finish needs recorded justification'
  assert len(refs)==1 and refs[0] in [str((r/'candidates'/f'{unit}-{s}.png').relative_to(b)) for s in ('P','R1')],'Finish must use only its own preserved source'
prompt=(r/'requests'/f'{aid}.txt').read_text();args={'prompt':prompt,'referenced_image_paths':[str(b/p) for p in refs]}
p=r/'calls'/f'{aid}.json';arguments=r/'requests'/f'{aid}.json';assert not p.exists() and not arguments.exists()
ref_records=[{'path':v,'sha256':hashlib.sha256((b/v).read_bytes()).hexdigest()} for v in refs]
arguments.write_text(json.dumps(args,indent=2)+'\n')
rec={'id':aid,'tool':'image_gen.imagegen','status':'submitted','phase':phase,'panels':panels,'args':args,'arguments_path':str(arguments),'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),'references':ref_records,'before_art_dependency':{'gate':'research/nightglass-longform/CHAPTER8-PRODUCTION-GATE.json','script_sha256':g['script_sha256'],'preceding_zip_sha256':g['preceding_zip_sha256'],'actual_reference_review':'Lead actually viewed each reference before this call; source roles/current state recorded in prompt.'},'model_snapshot':None,'seed':None,'billing':None,'owner_approval':None,'invoked':True,'submitted_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
p.write_text(json.dumps(rec,indent=2)+'\n');print(aid,'submitted provenance recorded; invoke the exact tool immediately')
