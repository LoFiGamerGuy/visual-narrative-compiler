"""Apply the bounded W06 input-validation retry contract to the CD helper."""
from pathlib import Path
p=Path(__file__).with_name('bundle_assets.py');s=p.read_text();pos=s.index('def transport_ledger(')
addition='''INPUT_ERROR = '`referenced_image_paths` must contain at most 5 paths'
INPUT_OLD_REFS = ['production/combat-depth/references/'+n+'.png' for n in ('neris','kellan','ilyra')]+['production/combat-depth/candidates/'+n+'.png' for n in ('W05-P','W01-F1','W04-F1')]

def rejected_input(record):
    return (record.get('id')=='W06' and record.get('attempt_id')=='W06-P' and record.get('phase')=='primary' and record.get('category')=='war' and record.get('status')=='failed-no-artwork-returned' and record.get('returned_artwork','missing') is None and record.get('error')==INPUT_ERROR and [r.get('path') for r in record.get('references',[])]==INPUT_OLD_REFS)

def require_reference_limit(record, rejected=False):
    n=len(record.get('references',[]))
    if 1<=n<=5:return
    if rejected and n==6 and rejected_input(record):return
    raise ValueError('Request must contain one to five reference paths; only exact preserved rejected W06 has six')

def validate_input_retry(root, record, failure):
    if not rejected_input(failure):raise ValueError('Only the exact W06 six-reference rejection may receive input correction')
    if record.get('transport_retry_of') or failure.get('transport_retry_of') or failure.get('input_validation_retry_of'):raise ValueError('Input correction cannot chain or combine retries')
    for key in ('id','attempt_id','phase','category'):
        if record.get(key)!=failure.get(key):raise ValueError('Input correction changed scene identity/phase')
    if not record.get('input_validation_retry_reason'):raise ValueError('Input correction lacks explicit reason')
    require_reference_limit(record)
    if record.get('references')!=failure['references'][:4]+failure['references'][5:]:raise ValueError('Input correction must only remove redundant W01 reference, preserving order and hashes')
    versions=plan_versions(root)
    oldplan=require_plan_version(failure.get('plan_sha256'),versions);newplan=require_plan_version(record.get('plan_sha256'),versions)
    old=json.loads((root/oldplan['path']).read_text());new=json.loads((root/newplan['path']).read_text())
    oldentry=next(e for e in old['entries'] if e['id']=='W06');newentry=next(e for e in new['entries'] if e['id']=='W06')
    if oldentry.get('references')!=['neris','kellan','ilyra','@W05','@W01','@W04'] or newentry.get('references')!=['neris','kellan','ilyra','@W05','@W04']:raise ValueError('Input correction plan references differ')
    if {k:v for k,v in oldentry.items() if k!='references'}!={k:v for k,v in newentry.items() if k!='references'}:raise ValueError('Input correction changed frozen creative scene brief/state')
    prompts=[]
    for request in (failure,record):
        safe_path(request['prompt_path']);path=root/request['prompt_path'];regular(path)
        if hashed(path)[1]!=request.get('prompt_sha256'):raise ValueError('Input correction prompt source hash differs')
        prompts.append(path.read_text())
    remove='Image 5: '+failure['references'][4]['role']+'\\n'
    if prompts[0].count(remove)!=1:raise ValueError('Rejected prompt lacks exact redundant reference description')
    expected=prompts[0].replace(remove,'',1).replace('Image 6: '+failure['references'][5]['role'],'Image 5: '+failure['references'][5]['role'],1)
    if prompts[1]!=expected:raise ValueError('Input correction changed prompt beyond one removed/renumbered reference')
    return {'rejected_reference_count':6,'corrected_reference_count':5,'removed_reference':INPUT_OLD_REFS[4],'creative_brief_and_state_unchanged':True,'old_plan_path':oldplan['path'],'new_plan_path':newplan['path']}

'''
s=s[:pos]+addition+s[pos:]
s=s.replace("    def actual_references(record):\n", "    def actual_references(record):\n        require_reference_limit(record,rejected=record.get('status')=='failed-no-artwork-returned')\n")
s=s.replace("    for p in sorted((prod/'transport-failures').glob('*.json')):\n", "    for p in sorted([*(prod/'transport-failures').glob('*.json'),*(prod/'input-validation-failures').glob('*.json')]):\n",1)
s=s.replace("        if record.get('schema') not in (None,'CombatDepthTransportFailure/1'):raise ValueError('Unknown transport failure schema')", "        is_input=p.parent.name=='input-validation-failures'\n        if record.get('schema') not in (None,'CombatDepthInputValidationFailure/1' if is_input else 'CombatDepthTransportFailure/1'):raise ValueError('Unknown no-art failure schema')\n        if is_input and not rejected_input(record):raise ValueError('Unexpected input-validation failure contract')")
s=s.replace("        if not record.get('references') or len(record['references'])>5:raise ValueError('Transport failure needs one to five exact references')", "        require_reference_limit(record,rejected=is_input)")
s=s.replace("'state':'failed-no-artwork-returned','schema_validation':", "'state':'failed-no-artwork-returned','failure_kind':'input-validation' if is_input else 'transport','schema_validation':")
s=s.replace("    def retry_binding(record):\n        rel=record.get('transport_retry_of')", "    def retry_binding(record):\n        input_rel=record.get('input_validation_retry_of')\n        if input_rel:\n            if input_rel not in failures or hashed(root/input_rel)[1]!=record.get('input_validation_retry_sha256'):raise ValueError('Input correction failed-record binding differs')\n            validate_input_retry(root,record,failures[input_rel]);referenced_failures.add(input_rel)\n        rel=record.get('transport_retry_of')")
s=s.replace("        same_request(record,failures[rel])", "        if rejected_input(failures[rel]):raise ValueError('Input-validation failure is not an unchanged transport retry')\n        same_request(record,failures[rel])")
s=s.replace("    for jobfile in sorted(prod.glob('transport-retry-*-jobs.json')):", "    for jobfile in sorted([*prod.glob('transport-retry-*-jobs.json'),*prod.glob('input-validation-retry-*-jobs.json')]):")
s=s.replace("'transport_retry_of':record.get('transport_retry_of')", "'transport_retry_of':record.get('transport_retry_of'),'input_validation_retry_of':record.get('input_validation_retry_of')")
s=s.replace("    if transport_retries>2:raise ValueError('At most two transport retry invocations authorized')", "    input_retries=sum(bool(x['record'].get('input_validation_retry_of')) for x in events.values())\n    if input_retries>1:raise ValueError('Only one W06 input-validation resubmission authorized')\n    if transport_retries+input_retries>2:raise ValueError('Input/transport retries share at most two no-art retry slots')")
s=s.replace("x['record'].get('transport_retry_of') for x in events.values() if x['record'].get('transport_retry_of')", "x['record'].get('transport_retry_of') or x['record'].get('input_validation_retry_of') for x in events.values() if x['record'].get('transport_retry_of') or x['record'].get('input_validation_retry_of')")
s=s.replace("any(failures[x].get('transport_retry_of') for x in retry_targets)", "any(failures[x].get('transport_retry_of') or failures[x].get('input_validation_retry_of') for x in retry_targets)")
s=s.replace("'transport_retry_invocations':transport_retries,'entries':", "'transport_retry_invocations':transport_retries,'input_validation_retry_invocations':input_retries,'total_no_art_retry_invocations':transport_retries+input_retries,'entries':")
s=s.replace("            if value.get('transport_retry_of'):\n                binding", "            if value.get('input_validation_retry_of'):\n                binding(value['input_validation_retry_of'],value['input_validation_retry_sha256'])\n            if value.get('transport_retry_of'):\n                binding")
s=s.replace("    for p in sorted((prod/'transport-failures').glob('*.json')): walk(json.loads(p.read_text()))", "    for p in sorted([*(prod/'transport-failures').glob('*.json'),*(prod/'input-validation-failures').glob('*.json')]): walk(json.loads(p.read_text()))")
p.write_text(s)
