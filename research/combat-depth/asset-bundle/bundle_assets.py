#!/usr/bin/env python3
"""CD-20260908-01 portable share archive: frozen inputs, safe restore, offline rebuild."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
import tempfile
import zipfile
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PREFIXES = ('production/combat-depth/', 'research/combat-depth/', 'docs/combat-depth/', 'docs/texture-refinement-kit/skill/texture-refinement/')
ROOT_FILES = {'START_HERE.cmd', 'START_HERE.md', 'AGENTS.md', 'docs/texture-refinement-kit/GUIDE.md'}
MANIFEST = 'ASSET-MANIFEST.json'
EXTERNAL_RECEIPTS = {'archive-receipt.json', 'verification.json', 'asset-manifest.json', 'coverage-preflight.json'}
EXPECTED_IDS = {*(f'D{i:02}' for i in range(1,13)), *(f'G{i:02}' for i in range(1,7)), *(f'W{i:02}' for i in range(1,7))}
MAX_FILES, MAX_FILE, MAX_TOTAL, MAX_MANIFEST = 5000, 256*1024**2, 8*1024**3, 8*1024**2
EXCLUDED = {'.scratch', 'local', '__pycache__', '.git', 'node_modules', 'venv', '.venv', 'runtime', 'cache', 'caches', 'browser-profile', 'browser', 'profile'}
EXTENSIONS = {'.png', '.jpg', '.jpeg', '.webp', '.json', '.md', '.txt', '.sha256', '.html', '.js', '.css', '.svg', '.py', '.cmd', '.mjs', '.yaml', '.yml', '.sh'}

def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False)+'\n').encode()

def hashed_stream(source):
    h, size = hashlib.sha256(), 0
    for block in iter(lambda: source.read(1024*1024), b''):
        h.update(block); size += len(block)
    return size, h.hexdigest()

def hashed(path):
    with path.open('rb') as source:
        return hashed_stream(source)

def safe_path(name):
    if not isinstance(name, str) or not name or '\\' in name or ':' in name or '\x00' in name:
        raise ValueError('Unsafe member path')
    p = PurePosixPath(name)
    if p.is_absolute() or str(p) != name or any(x in ('.', '..') for x in p.parts):
        raise ValueError('Unsafe member path: '+name)
    if name not in ROOT_FILES and not name.startswith(PREFIXES):
        raise ValueError('Outside experiment prefixes: '+name)
    for part in p.parts:
        if part in EXCLUDED: raise ValueError('Excluded runtime/local member: '+name)
        if part.endswith((' ', '.')) or re.match(r'^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\.|$)', part, re.I):
            raise ValueError('Windows-unsafe member: '+name)
        if any(ord(c)<32 or c in '<>"|?*' for c in part):
            raise ValueError('Unsafe filename')
    return p

def regular(path):
    for part in (path, *path.parents):
        if part.is_symlink():
            raise ValueError('Symlink source/destination rejected: '+str(part))
    if not path.is_file():
        raise ValueError('Expected regular file: '+str(path))

def validate_entries(manifest):
    if manifest.get('schema') != 'CombatDepthPortable/1' or manifest.get('experiment_id') != 'CD-20260908-01':
        raise ValueError('Wrong package schema or experiment')
    entries = manifest['files']
    if not isinstance(entries, list) or not 0 < len(entries) <= MAX_FILES:
        raise ValueError('File count limit')
    names = set(); total = 0
    for e in entries:
        safe_path(e['path'])
        key = e['path'].casefold()
        if key in names:
            raise ValueError('Duplicate/case-colliding member')
        names.add(key)
        if type(e['bytes']) is not int or not 0 <= e['bytes'] <= MAX_FILE:
            raise ValueError('Member size limit')
        if not re.fullmatch('[0-9a-f]{64}', e['sha256']):
            raise ValueError('Invalid SHA256')
        total += e['bytes']
    for name in names:
        if any(str(p) in names for p in PurePosixPath(name).parents if str(p) != '.'):
            raise ValueError('File/directory member collision')
    if total > MAX_TOTAL or manifest.get('total_bytes') != total:
        raise ValueError('Total size limit/mismatch')
    return entries

def resolve_budget(root, plan, attempts):
    expected={'primary':24,'structural_repairs':6,'texture_passes':24,'maximum_native_attempts':54,'transport_retries':2,'maximum_total':56}
    base={k:plan['budget'].get(k) for k in expected}
    if base!=expected or any(type(v) is not int for v in base.values()):
        raise ValueError('Frozen CD budget must be 24P/6R1/24F1, 54 natives, 56 invocations and two unchanged transport retries')
    if list((root/'production/combat-depth').glob('budget-amendment*.json')):
        raise ValueError('This round has no authorized budget amendment')
    return {'base_budget':base,'effective_budget':dict(base),'amendment':None}


INPUT_ERROR = '`referenced_image_paths` must contain at most 5 paths'
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
    remove='Image 5: '+failure['references'][4]['role']+'\n'
    if prompts[0].count(remove)!=1:raise ValueError('Rejected prompt lacks exact redundant reference description')
    expected=prompts[0].replace(remove,'',1).replace('Image 6: '+failure['references'][5]['role'],'Image 5: '+failure['references'][5]['role'],1)
    if prompts[1]!=expected:raise ValueError('Input correction changed prompt beyond one removed/renumbered reference')
    return {'rejected_reference_count':6,'corrected_reference_count':5,'removed_reference':INPUT_OLD_REFS[4],'creative_brief_and_state_unchanged':True,'old_plan_path':oldplan['path'],'new_plan_path':newplan['path']}

def transport_ledger(root, attempts, maximum, strict=False):
    """Count requests, including preserved no-art failures, independently of natives."""
    prod=root/'production/combat-depth'; failures={}; events={}; ledger=[]; tool_receipts=[]
    def identity(record):
        start=record.get('started',{}).get('current_time')
        if not isinstance(start,str) or not start:raise ValueError('Invocation lacks a recorded start time')
        return (record.get('attempt_id'),start)
    fields=('id','attempt_id','phase','category','retry_of','prompt_path','prompt_sha256','plan_sha256','references')
    def actual_references(record):
        require_reference_limit(record,rejected=record.get('status')=='failed-no-artwork-returned')
        declared=[x['path'] for x in record.get('references',[])];actual=record.get('referenced_image_paths',[])
        if len(declared)!=len(actual) or any(not a.replace(chr(92),'/').endswith('/'+d) and a!=d for a,d in zip(actual,declared)):
            raise ValueError('Invocation actual reference paths differ from hashed references')
    def same_request(a,b):
        if any(a.get(k)!=b.get(k) for k in fields):raise ValueError('Transport retry changed creative request/source binding')
    for p in sorted([*(prod/'transport-failures').glob('*.json'),*(prod/'input-validation-failures').glob('*.json')]):
        regular(p);record=json.loads(p.read_text());rel=p.relative_to(root).as_posix()
        if record.get('schema')=='CombatDepthToolFailure/1':
            tool_receipts.append({'path':rel,'sha256':hashed(p)[1],'record':record});continue
        is_input=p.parent.name=='input-validation-failures'
        if record.get('schema') not in (None,'CombatDepthInputValidationFailure/1' if is_input else 'CombatDepthTransportFailure/1'):raise ValueError('Unknown no-art failure schema')
        if is_input and not rejected_input(record):raise ValueError('Unexpected input-validation failure contract')
        if record.get('id') not in EXPECTED_IDS or record.get('attempt_id') not in [record['id']+'-'+x for x in ('P','R1','F1')] or record.get('phase') not in ('primary','repair','texture'):raise ValueError('Transport failure identity/phase differs')
        if record.get('status')!='failed-no-artwork-returned' or 'returned_artwork' not in record or record['returned_artwork'] is not None:
            raise ValueError('Transport failure must explicitly return no artwork')
        if not isinstance(record.get('error'),str) or not record['error'] or not record.get('finished',{}).get('current_time'):
            raise ValueError('Failure lacks error/finish evidence')
        if any(record.get(k) for k in ('output_hint','image_url','image_path','native_path','output_path')):raise ValueError('Failure contains an artwork output')
        actual_references(record)
        require_reference_limit(record,rejected=is_input)
        if record['phase']=='texture' and len(record['references'])!=1:raise ValueError('Source-only finishing failure needs one source')
        key=identity(record)
        if key in events:raise ValueError('Duplicate preserved failed invocation')
        events[key]={'state':'failed','record':record}; failures[rel]=record
        ledger.append({'path':rel,'sha256':hashed(p)[1],'attempt_id':record['attempt_id'],'started':key[1],'state':'failed-no-artwork-returned','failure_kind':'input-validation' if is_input else 'transport','schema_validation':'CombatDepthTransportFailure/1' if record.get('schema') else 'explicit field contract; source has no schema tag'})
    for item in tool_receipts:
        record=item['record'];target=record.get('failure_record_path');outcome=record.get('outcome',{})
        if target not in failures or hashed(root/target)[1]!=record.get('failure_record_sha256'):raise ValueError('Tool failure receipt source binding differs')
        if outcome.get('id')!=failures[target]['attempt_id'] or outcome.get('status')!='error' or outcome.get('error')!=failures[target].get('error'):
            raise ValueError('Tool failure receipt outcome differs')
        if rejected_input(failures[target]):
            if not record.get('source') or record.get('returned_artwork','missing') is not None:raise ValueError('Input failure sidecar lacks caught-error source/null-art declaration')
        elif not record.get('functions_cell_id'):raise ValueError('Transport tool failure receipt lacks cell ID')
    referenced_failures=set()
    def retry_binding(record):
        input_rel=record.get('input_validation_retry_of')
        if input_rel:
            if input_rel not in failures or hashed(root/input_rel)[1]!=record.get('input_validation_retry_sha256'):raise ValueError('Input correction failed-record binding differs')
            validate_input_retry(root,record,failures[input_rel]);referenced_failures.add(input_rel)
        rel=record.get('transport_retry_of')
        if not rel:return
        if rel not in failures or hashed(root/rel)[1]!=record.get('transport_retry_sha256'):raise ValueError('Transport retry failure hash/path mismatch')
        if rejected_input(failures[rel]):raise ValueError('Input-validation failure is not an unchanged transport retry')
        same_request(record,failures[rel])
        if not record.get('transport_retry_reason'):raise ValueError('Transport retry lacks recorded reason')
        referenced_failures.add(rel)
    for record in failures.values():retry_binding(record)
    for jobfile in sorted([*prod.glob('transport-retry-*-jobs.json'),*prod.glob('input-validation-retry-*-jobs.json')]):
        for record in json.loads(jobfile.read_text()):retry_binding(record)
    for p in sorted((prod/'calls').glob('*.json')):
        record=json.loads(p.read_text());actual_references(record);key=identity(record);retry_binding(record)
        if key in events:
            same_request(record,events[key]['record'])
            if record.get('status')!='failed-no-artwork-returned' or record.get('returned_artwork','missing') is not None or record.get('error')!=events[key]['record'].get('error'):
                raise ValueError('Call alias conflicts with preserved failure')
            continue  # Same failed invocation preserved under two paths; count once.
        state='native-returned' if p.stem in attempts else 'pending'
        if record.get('status')=='failed-no-artwork-returned':raise ValueError('Failed call lacks separately preserved failure record')
        events[key]={'state':state,'record':record}
        ledger.append({'path':p.relative_to(root).as_posix(),'sha256':hashed(p)[1],'attempt_id':p.stem,'started':key[1],'state':state,'transport_retry_of':record.get('transport_retry_of'),'input_validation_retry_of':record.get('input_validation_retry_of')})
    transport_retries=sum(bool(x['record'].get('transport_retry_of')) for x in events.values())
    input_retries=sum(bool(x['record'].get('input_validation_retry_of')) for x in events.values())
    if input_retries>1:raise ValueError('Only one W06 input-validation resubmission authorized')
    if transport_retries+input_retries>2:raise ValueError('Input/transport retries share at most two no-art retry slots')
    retry_targets=[x['record'].get('transport_retry_of') or x['record'].get('input_validation_retry_of') for x in events.values() if x['record'].get('transport_retry_of') or x['record'].get('input_validation_retry_of')]
    if len(set(retry_targets))!=len(retry_targets):raise ValueError('A failed invocation was retried more than once')
    if any(failures[x].get('transport_retry_of') or failures[x].get('input_validation_retry_of') for x in retry_targets):raise ValueError('A failed retry cannot be retried again')
    pending=sum(x['state']=='pending' for x in events.values())
    if strict and pending:raise ValueError('Final archive contains an unfinished invocation')
    if len(events)>maximum:raise ValueError('Invocations including failures exceed effective total budget')
    return {'invocation_count':len(events),'native_artwork_count':len(attempts),'failed_no_artwork_count':len(failures),'pending_invocations':pending,'maximum_invocations':maximum,'transport_retry_invocations':transport_retries,'input_validation_retry_invocations':input_retries,'total_no_art_retry_invocations':transport_retries+input_retries,'entries':ledger,'supporting_tool_receipts':tool_receipts,'failures_do_not_consume_additional_creative_attempt_ids':True}

def plan_versions(root):
    """Resolve current and preserved full plans by exact bytes; never rewrite calls."""
    prod=root/'production/combat-depth';versions={}
    paths=[prod/'plan.json',*sorted((prod/'plan-history').glob('plan-v*.json'))]
    for path in paths:
        if path.name!='plan.json' and not re.fullmatch(r'plan-v[1-9][0-9]*\.json',path.name):raise ValueError('Unexpected archived plan filename')
        regular(path);record=json.loads(path.read_text())
        if record.get('schema')!='CombatDepthPlan/1' or record.get('experiment_id')!='CD-20260908-01' or len(record.get('entries',[]))!=24 or {e.get('id') for e in record['entries']}!=EXPECTED_IDS:raise ValueError('Historical plan schema/experiment/IDs differ')
        resolve_budget(root,record,{})
        digest=hashed(path)[1];sidecar=path.with_suffix('.sha256')
        if not sidecar.is_file():raise ValueError('Full plan lacks preserved SHA sidecar: '+str(path))
        regular(sidecar)
        if sidecar.read_text().strip()!=digest:raise ValueError('Historical/current plan SHA sidecar differs')
        item={'path':path.relative_to(root).as_posix(),'sha256':digest,'sha256_path':sidecar.relative_to(root).as_posix(),'sha256_file_hash':hashed(sidecar)[1]}
        versions.setdefault(digest,[]).append(item)
    return versions

def require_plan_version(digest,versions):
    if not isinstance(digest,str) or digest not in versions:raise ValueError('Job/call plan hash has no exact preserved full version')
    return versions[digest][0]

def source_bindings(root, strict=False, expected_art=None):
    """Read-only current source check. Missing planned primaries allowed only in inspect."""
    root = root.resolve(); prod=root/'production/combat-depth'
    plan=json.loads((prod/'plan.json').read_text())
    if plan.get('schema')!='CombatDepthPlan/1' or plan.get('experiment_id')!='CD-20260908-01' or len(plan['entries'])!=24 or {e['id'] for e in plan['entries']}!=EXPECTED_IDS:
        raise ValueError('Expected exact frozen 12D/6G/6W CD plan')
    rows=json.loads((prod/'candidates.json').read_text())['candidates']
    attempts={e['attempt_id']:e for e in rows}
    if len(attempts)!=len(rows): raise ValueError('Duplicate registered attempts')
    phases={'P':0,'R1':0,'F1':0}; checked={}; archived_jobs=[]
    def binding(path,digest):
        safe_path(path); p=root/path; regular(p)
        if hashed(p)[1]!=digest: raise ValueError('Source binding mismatch: '+path)
        if path in checked and checked[path]!=digest: raise ValueError('Conflicting source digest: '+path)
        checked[path]=digest
    plan_sha=hashed(prod/'plan.json')[1]
    versions=plan_versions(root); call_plans=[]
    for records in versions.values():
        for version in records:
            binding(version['path'],version['sha256']);binding(version['sha256_path'],version['sha256_file_hash'])
    def walk(value, job_origin=None):
        if isinstance(value,list):
            for x in value: walk(x,job_origin)
        elif isinstance(value,dict):
            if value.get('attempt_id') and isinstance(value.get('references'),list):
                if len(value['references'])>5 and job_origin:
                    preserved=root/'production/combat-depth/input-validation-failures/W06-P.json'
                    failure=json.loads(preserved.read_text()) if preserved.is_file() else {}
                    fields=('id','attempt_id','phase','category','plan_sha256','prompt_path','prompt_sha256','references')
                    if not rejected_input(failure) or any(value.get(k)!=failure.get(k) for k in fields):raise ValueError('Only exact preserved rejected job may exceed five refs')
                else:require_reference_limit(value,rejected=value.get('status')=='failed-no-artwork-returned')
            if isinstance(value.get('path'),str) and value['path'].startswith(PREFIXES) and 'sha256' in value:
                binding(value['path'],value['sha256'])
            for prefix in ('prompt','call','evidence','failure_record','tool_output','control_source'):
                if value.get(prefix+'_path') and value.get(prefix+'_sha256'):
                    path,digest=value[prefix+'_path'],value[prefix+'_sha256']
                    if prefix=='prompt' and job_origin:
                        if not isinstance(value.get('prompt'),str) or hashlib.sha256(value['prompt'].encode()).hexdigest()!=digest:
                            raise ValueError('Frozen job embedded prompt digest differs')
                        if not (root/path).is_file() or hashed(root/path)[1]!=digest:
                            archived=[p for p in (prod/'unrun').glob('*.txt') if hashed(p)[1]==digest]
                            if len(archived)!=1:raise ValueError('Superseded job prompt lacks one exact archived source')
                            actual=archived[0].relative_to(root).as_posix()
                            archived_jobs.append({'job_path':job_origin,'attempt_id':value.get('attempt_id'),'intended_prompt_path':path,'archived_prompt_path':actual,'prompt_sha256':digest})
                            path=actual
                    binding(path,digest)
            if value.get('input_validation_retry_of'):
                binding(value['input_validation_retry_of'],value['input_validation_retry_sha256'])
                validate_input_retry(root,value,json.loads((root/value['input_validation_retry_of']).read_text()))
            if value.get('transport_retry_of'):
                binding(value['transport_retry_of'],value['transport_retry_sha256'])
            if value.get('plan_sha256'):require_plan_version(value['plan_sha256'],versions)
            for x in value.values(): walk(x,job_origin)
    refs=json.loads((prod/'reference-library.json').read_text())
    if refs!=plan['reference_library']: raise ValueError('Reference library disagrees with frozen plan')
    walk(plan); walk(refs); walk(json.loads((prod/'previous/ce-source-binding.json').read_text()))
    controls_path=root/'research/combat-depth/controls/manifest.json'
    controls=json.loads(controls_path.read_text())
    if controls.get('schema')!='CombatDepthControls/1' or controls.get('experiment_id')!='CD-20260908-01':raise ValueError('Wrong control manifest')
    expected_controls={'map-duel','map-squad','map-war','guide-D04','guide-D10','guide-G03','guide-G04'}
    if {x['id'] for x in controls['controls']}!=expected_controls or len(controls['controls'])!=7:raise ValueError('Control IDs incomplete or duplicated')
    binding(controls_path.relative_to(root).as_posix(),hashed(controls_path)[1])
    for item in controls['controls']:
        if not item['path'].startswith('research/combat-depth/controls/') or not item['path'].endswith('.png') or not item['source_path'].endswith('.svg'):raise ValueError('Invalid control image/editable source paths')
        binding(item['path'],item['sha256']);binding(item['source_path'],item['source_sha256'])
    if plan.get('prior_choices',{}).get('path')!='production/combat-depth/previous/ce-selection.json':
        raise ValueError('Exact prior choice export must be local')
    for e in rows:
        if any(not isinstance(e.get(k),str) or not e[k] for k in ('id','attempt_id','path','sha256','prompt_path','prompt_sha256','call_path','call_sha256')): raise ValueError('Incomplete registered source binding')
        if e['id'] not in EXPECTED_IDS or e['attempt_id'] not in [e['id']+'-'+s for s in phases]: raise ValueError('Unknown attempt identity')
        phases[e['attempt_id'].rsplit('-',1)[1]]+=1; walk(e)
        if e['path']!='production/combat-depth/candidates/'+e['attempt_id']+'.png': raise ValueError('Unexpected native path')
        callpath=e.get('call_path')
        if callpath!='production/combat-depth/calls/'+e['attempt_id']+'.json': raise ValueError('Missing exact call record')
        call=json.loads((root/callpath).read_text()); walk(call)
        version=require_plan_version(call.get('plan_sha256'),versions)
        call_plans.append({'attempt_id':e['attempt_id'],'call_path':callpath,'plan_sha256':call['plan_sha256'],'preserved_plan_path':version['path']})
        if call.get('id')!=e['id'] or call.get('attempt_id')!=e['attempt_id']: raise ValueError('Call/image identity mismatch')
        if e.get('prompt_path')!=call.get('prompt_path') or e.get('prompt_sha256')!=call.get('prompt_sha256'): raise ValueError('Call/image prompt binding differs')
        actual=call.get('referenced_image_paths',[]); declared=[x['path'] for x in call.get('references',[])]
        if len(actual)!=len(declared) or any(not a.replace(chr(92),'/').endswith('/'+d) and a!=d for a,d in zip(actual,declared)):
            raise ValueError('Actual tool reference paths disagree with hashed local references')
        if e['attempt_id'].endswith('-F1'):
            if len(call.get('references',[]))!=1 or call['references'][0]['path']!=attempts.get(call.get('retry_of'),{}).get('path'):raise ValueError('F1 must reference only its exact source native')
        for ref in call.get('references',[]):
            if ref['path'].startswith('research/combat-depth/controls/'):
                if not ref.get('control_source_path') or not ref.get('control_source_sha256'):raise ValueError('Control PNG call lacks editable SVG binding')
        if not e['attempt_id'].endswith('-P'):
            original=call.get('retry_of') or e.get('retry_of'); reason=call.get('retry_reason') or e.get('retry_reason')
            if original not in attempts or attempts[original]['id']!=e['id'] or not reason: raise ValueError('Edit lacks exact retained source/reason')
    for p in sorted(prod.glob('*jobs.json')): walk(json.loads(p.read_text()),p.relative_to(root).as_posix())
    # Every registered native and copied reference is bound. Preserve unregistered calls,
    # but final closure requires each call to have a registered returned native.
    calls={p.stem for p in (prod/'calls').glob('*.json')}
    nonfailed_calls={p.stem for p in (prod/'calls').glob('*.json') if json.loads(p.read_text()).get('status')!='failed-no-artwork-returned'}
    if strict and nonfailed_calls!=set(attempts): raise ValueError('Final successful calls/registered attempt inventory differs')
    for p in sorted((prod/'calls').glob('*.json')): walk(json.loads(p.read_text()))
    for p in sorted([*(prod/'transport-failures').glob('*.json'),*(prod/'input-validation-failures').glob('*.json')]): walk(json.loads(p.read_text()))
    native_files={p.relative_to(root).as_posix() for p in (prod/'candidates').glob('*.png')}
    if native_files!={e['path'] for e in rows}: raise ValueError('Unregistered or missing local candidate PNG')
    budget_record=resolve_budget(root,plan,attempts);budget=budget_record['effective_budget']
    if phases['P']>24 or phases['R1']>budget['structural_repairs'] or phases['F1']>budget['texture_passes'] or len(rows)>budget['maximum_native_attempts']:
        raise ValueError('Attempt counts exceed frozen plan budget')
    invocations=transport_ledger(root,attempts,budget['maximum_total'],strict)
    selections=json.loads((prod/'selected.json').read_text())['selected']
    if any(k not in EXPECTED_IDS or v not in attempts or attempts[v]['id']!=k for k,v in selections.items()): raise ValueError('Invalid display selection')
    missing=sorted(EXPECTED_IDS-{e['id'] for e in rows if e['attempt_id'].endswith('-P')})
    if strict and (missing or set(selections)!=EXPECTED_IDS): raise ValueError('Final package needs all24 primaries and selections')
    if strict and (expected_art is None or expected_art!=len(rows)): raise ValueError('Explicit --expected-art must match final registry')
    return {'pass':True,'complete':not missing and len(selections)==24,'registered_attempts':len(rows),'phase_counts':phases,'selected_count':len(selections),'missing_primaries':missing,'checked_bindings':checked,'plan_sha256':plan_sha,'preserved_plan_versions':versions,'call_plan_bindings':call_plans,'budget':budget_record,'archived_unrun_job_prompts':archived_jobs,'invocation_ledger':invocations}

def gather(root, expected_art=None, strict=False):
    root=root.resolve(); binding_report=source_bindings(root,strict,expected_art)
    helper=root/'research/combat-depth/asset-bundle'; sources={}; excluded=[]
    for prefix in PREFIXES:
        base=root/prefix
        if not base.is_dir(): raise ValueError('Missing package namespace: '+prefix)
        for directory, folders, files in os.walk(base,followlinks=False):
            for folder in folders:
                if (Path(directory)/folder).is_symlink(): raise ValueError('Symlink source directory rejected')
            folders[:]=sorted(f for f in folders if f not in EXCLUDED)
            for name in sorted(files):
                p=Path(directory)/name
                if p.parent==helper and (name in EXTERNAL_RECEIPTS or name in {'START_HERE.cmd','START_HERE.md'}):
                    excluded.append(p.relative_to(root).as_posix()); continue
                if p.suffix.lower() not in EXTENSIONS and name not in {'.gitignore','.gitattributes'}:
                    raise ValueError('Unclassified package source; explicitly classify: '+str(p))
                regular(p); rel=p.relative_to(root).as_posix(); safe_path(rel); sources[rel]=p
    for name in ROOT_FILES:
        sources[name]=helper/name if name.startswith('START_HERE.') else root/name
    entries=[]
    for name,p in sorted(sources.items()):
        regular(p); size,sha=hashed(p); entries.append({'path':name,'bytes':size,'sha256':sha})
    if set(binding_report['checked_bindings'])-set(sources): raise ValueError('Bound source omitted from payload')
    manifest={'schema':'CombatDepthPortable/1','experiment_id':'CD-20260908-01','files':entries,'total_bytes':sum(e['bytes'] for e in entries),'source_bindings':binding_report,'explicit_external_receipt_or_launcher_mappings':excluded,'exclusions':'Scratch/runtime/caches/venvs/browser profiles/local directories; no old galleries or original tool-return locations. Complete new namespaces plus AGENTS and textual texture skill/guide only.'}
    validate_entries(manifest); return manifest,sources

def write_archive(path, manifest, sources):
    validate_entries(manifest)
    if path.exists():
        raise FileExistsError('Archive already exists; use a new version directory')
    for e in manifest['files']:
        regular(sources[e['path']])
        if hashed(sources[e['path']]) != (e['bytes'], e['sha256']):
            raise ValueError('Source changed before packing')
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, 'x', compression=zipfile.ZIP_STORED, allowZip64=True) as z:
        for name,e in [(MANIFEST,None)]+[(e['path'],e) for e in manifest['files']]:
            info = zipfile.ZipInfo(name, (1980,1,1,0,0,0))
            info.create_system = 3; info.external_attr = (stat.S_IFREG|0o644)<<16
            with z.open(info,'w',force_zip64=True) as dest:
                if e is None:
                    dest.write(encoded(manifest))
                else:
                    with sources[name].open('rb') as source:
                        for block in iter(lambda:source.read(1024*1024),b''): dest.write(block)
    size,sha = hashed(path)
    return dict(schema='CombatDepthPortableReceipt/1',archive_bytes=size,archive_sha256=sha,manifest_sha256=hashlib.sha256(encoded(manifest)).hexdigest(),file_count=len(manifest['files']))

def verify(path, receipt):
    regular(path)
    if hashed(path) != (receipt['archive_bytes'], receipt['archive_sha256']):
        raise ValueError('Archive hash/size mismatch')
    with zipfile.ZipFile(path) as z:
        infos = z.infolist()
        if len(infos)>MAX_FILES+1 or len({i.filename.casefold() for i in infos}) != len(infos):
            raise ValueError('Archive duplicate/count limit')
        info = z.getinfo(MANIFEST)
        if info.file_size > MAX_MANIFEST:
            raise ValueError('Manifest size limit')
        raw = z.read(MANIFEST)
        if hashlib.sha256(raw).hexdigest() != receipt['manifest_sha256']:
            raise ValueError('Manifest hash mismatch')
        manifest = json.loads(raw); entries = validate_entries(manifest)
        if receipt.get('file_count') != len(entries):
            raise ValueError('Receipt file count differs from manifest')
        if [i.filename for i in infos] != [MANIFEST]+[e['path'] for e in entries]:
            raise ValueError('Unexpected/missing archive members')
        for info in infos:
            mode = info.external_attr>>16
            if info.is_dir() or stat.S_IFMT(mode) not in (0,stat.S_IFREG) or info.flag_bits & 1:
                raise ValueError('Nonregular/encrypted archive member')
        for e in entries:
            if z.getinfo(e['path']).file_size != e['bytes']:
                raise ValueError('ZIP member declared size mismatch')
            with z.open(e['path']) as source:
                if hashed_stream(source) != (e['bytes'],e['sha256']):
                    raise ValueError('ZIP member content mismatch')
        bad=z.testzip()
        if bad: raise ValueError('ZIP CRC failed: '+bad)
    return manifest

def restore(path, receipt, target):
    manifest = verify(path,receipt)
    for ancestor in (target,*target.parents):
        if ancestor.is_symlink(): raise ValueError('Symlink target ancestor')
    target = target.resolve(); missing = []; identical = 0
    if target.exists() and not target.is_dir(): raise FileExistsError('Target root is a file')
    for e in manifest['files']:
        rel = safe_path(e['path']); dest = target.joinpath(*rel.parts); current = target
        for index,part in enumerate(rel.parts):
            if current.exists() and current.is_dir():
                collisions = [p.name for p in current.iterdir() if p.name.casefold() == part.casefold() and p.name != part]
                if collisions: raise FileExistsError('Case-colliding existing destination; nothing restored')
            current = current/part
            if current.is_symlink(): raise ValueError('Symlink destination')
            if index<len(rel.parts)-1 and current.exists() and not current.is_dir():
                raise FileExistsError('Destination parent is a file; nothing restored')
        if dest.exists():
            if not dest.is_file() or hashed(dest)!=(e['bytes'],e['sha256']):
                raise FileExistsError('Existing file differs; nothing restored: '+str(dest))
            identical += 1
        else: missing.append(e)
    with zipfile.ZipFile(path) as z:
        for e in missing:
            dest = target/e['path']; dest.parent.mkdir(parents=True,exist_ok=True)
            with z.open(e['path']) as source,dest.open('xb') as out:
                for block in iter(lambda:source.read(1024*1024),b''):out.write(block)
            if hashed(dest)!=(e['bytes'],e['sha256']):raise ValueError('Restored content mismatch')
    return dict(verified_files=len(manifest['files']),written_files=len(missing),identical_skipped=identical)

def check_inventory(target, manifest, exact=False):
    target=target.resolve(); expected={e['path'] for e in manifest['files']}
    for e in manifest['files']:
        p=target/e['path']; regular(p)
        if hashed(p)!=(e['bytes'],e['sha256']): raise ValueError('Restored/checkout source parity mismatch: '+e['path'])
    if exact:
        actual={p.relative_to(target).as_posix() for p in target.rglob('*') if p.is_file()}
        if actual!=expected: raise ValueError('Fresh extraction file inventory differs')
    return {'pass':True,'verified_files':len(expected),'exact_inventory':exact}

class Links(HTMLParser):
    def __init__(self): super().__init__(); self.links=[]
    def handle_starttag(self,tag,attrs):
        self.links.extend(v for k,v in attrs if k in ('href','src') and v)

def local_links(root):
    root=root.resolve(); docs=root/'docs/combat-depth'; count=0; external=set()
    def check(value,base):
        nonlocal count
        u=urlsplit(value)
        if u.scheme or u.netloc:
            if u.scheme not in ('data','blob','mailto','http','https'): raise ValueError('Unsupported URL scheme: '+value)
            external.add(value); return
        if not u.path:return
        p=(base/unquote(u.path)).resolve()
        if not p.is_relative_to(root):raise ValueError('Local URL escapes extracted root: '+value)
        if not p.is_file():raise ValueError('Missing local href/src dependency: '+str(p))
        regular(p); count+=1
    for p in docs.rglob('*.html'):
        parser=Links();parser.feed(p.read_text())
        for v in parser.links:check(v,p.parent)
    for p in docs.rglob('*.css'):
        for v in re.findall(r'url\(\s*[\"\']?([^\)\"\']+)',p.read_text()):check(v.strip(),p.parent)
    def walk(value):
        if isinstance(value,list):
            for v in value:walk(v)
        elif isinstance(value,dict):
            for k,v in value.items():
                if isinstance(v,str) and (k in ('src','href','download_src','path') or k.endswith('_path') and k not in ('source_path','story_path')):
                    check(v,root if v.startswith(('production/','research/','docs/')) else docs)
                elif isinstance(v,(list,dict)):walk(v)
    walk(json.loads((docs/'data.json').read_text()))
    return {'pass':True,'checked_local_urls':count,'external_urls_not_fetched':sorted(external),'scope':'Static HTML href/src, CSS url(), and dynamic gallery data paths; query and fragment stripped. Runtime JS behavior is covered by separate reader QA.'}

def rebuild_check(target):
    target=target.resolve()
    if target==ROOT:raise ValueError('Rebuild check must use isolated restored/checkout target')
    docs=target/'docs/combat-depth'; names=['data.json','data.js']; before={n:hashed(docs/n) for n in names}
    binding=source_bindings(target,strict=True,expected_art=len(json.loads((target/'production/combat-depth/candidates.json').read_text())['candidates']))
    run=subprocess.run([sys.executable,str(target/'research/combat-depth/reader/build_reader.py'),'--require-complete'],cwd=target,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},text=True,capture_output=True,check=True)
    if before!={n:hashed(docs/n) for n in names}:raise ValueError('Rebuilt gallery data differs from frozen source/display bindings')
    return {'rebuild':'pass','exact_data_hashes':{n:v[1] for n,v in before.items()},'source_bindings':binding,'local_links':local_links(target),'builder_output':run.stdout.strip()}

def create(root,out,count):
    root,out=root.resolve(),out.resolve()
    allowed=root/'research/combat-depth/asset-bundle/local'
    if not out.is_relative_to(allowed) or out==allowed:raise ValueError('--output must be a new task-local version directory')
    if out.exists():raise FileExistsError('Preserve output; choose a new version directory')
    manifest,sources=gather(root,count,strict=True)
    local_links(root)
    out.mkdir(parents=True)
    archive=out/'combat-depth-portable.zip'
    receipt=write_archive(archive,manifest,sources)
    # Preserve useful archive receipts even if a later integration step fails.
    for name,value in [('asset-manifest.json',manifest),('archive-receipt.json',receipt)]:
        with (out/name).open('xb') as f:f.write(encoded(value))
    try:
        verify(archive,receipt);target=out/'fresh-restoration'
        result={'restore':restore(archive,receipt,target),'inventory':check_inventory(target,manifest,exact=True)}
        result.update(rebuild_check(target)); result['post_rebuild_inventory']=check_inventory(target,manifest,exact=True)
        result['pass']=True
    except Exception as error:
        with (out/'verification-failure.json').open('xb') as f:f.write(encoded({'pass':False,'error_type':type(error).__name__,'error':str(error)}))
        raise
    with (out/'verification.json').open('xb') as f:f.write(encoded(result))
    print(json.dumps(dict(**receipt,restored_root=str(target),pass_=True),indent=2))

def self_test():
    local = HERE/'local'; local.mkdir(exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix='security-fixtures-',dir=local))
    sources={}
    for name,body in [('a.txt',b'AAA'),('b.txt',b'BBB')]:
        p=tmp/name;p.write_bytes(body);sources['production/combat-depth/'+name]=p
    entries=[dict(path=name,bytes=hashed(p)[0],sha256=hashed(p)[1]) for name,p in sorted(sources.items())]
    manifest=dict(schema='CombatDepthPortable/1',experiment_id='CD-20260908-01',files=entries,total_bytes=6);archive=tmp/'good.zip';receipt=write_archive(archive,manifest,sources)
    checks=[]
    def rejects(label,fn,types=(ValueError,FileExistsError)):
        try:fn()
        except types:checks.append(label)
        else:raise AssertionError(label+' accepted')
    target=tmp/'restore';clash=target/'production/combat-depth/b.txt';clash.parent.mkdir(parents=True);clash.write_bytes(b'BAD')
    rejects('clash preflight',lambda:restore(archive,receipt,target));assert not (clash.parent/'a.txt').exists()
    clash.write_bytes(b'BBB');r=restore(archive,receipt,target);assert r['written_files']==1 and r['identical_skipped']==1
    assert restore(archive,receipt,target)['written_files']==0;checks+=['exact missing restore','identical skip/idempotence']
    for bad in ['../escape','production/combat-depth/../escape','other/a.png','production/combat-depth/AUX.txt','production\\combat-depth\\a','/absolute']:
        rejects('unsafe path '+bad,lambda bad=bad:safe_path(bad))
    rejects('duplicate case collision',lambda:validate_entries(dict(manifest,files=entries+[dict(entries[0],path=entries[0]['path'].replace('a.txt','A.txt'))],total_bytes=9)))
    rejects('size limit',lambda:validate_entries(dict(manifest,files=[dict(entries[0],bytes=MAX_FILE+1)],total_bytes=MAX_FILE+1)))
    rejects('archive hash mismatch',lambda:verify(archive,dict(receipt,archive_sha256='0'*64)))
    rejects('receipt count mismatch',lambda:verify(archive,dict(receipt,file_count=99)))
    link=tmp/'symlink-target';link.symlink_to(target,target_is_directory=True)
    rejects('target symlink',lambda:restore(archive,receipt,link))
    parent=tmp/'parent-file';parent.mkdir();(parent/'production').write_bytes(b'FILE')
    rejects('parent file',lambda:restore(archive,receipt,parent))
    case_target=tmp/'case-clash';case_target.mkdir();(case_target/'Production').mkdir()
    rejects('existing case-colliding directory',lambda:restore(archive,receipt,case_target))
    assert [child.name for child in case_target.iterdir()] == ['Production']
    assert not list((case_target/'Production').iterdir())
    rejects('wrong experiment schema',lambda:validate_entries(dict(manifest,experiment_id='WRONG')))
    rejects('file directory collision',lambda:validate_entries(dict(manifest,files=entries+[dict(path=entries[0]['path']+'/child.txt',bytes=0,sha256=hashlib.sha256(b'').hexdigest())])))
    rejects('total byte mismatch',lambda:validate_entries(dict(manifest,total_bytes=7)))
    rejects('invalid digest',lambda:validate_entries(dict(manifest,files=[dict(entries[0],sha256='bad')],total_bytes=3)))
    for name in ('AGENTS.md','START_HERE.cmd','docs/combat-depth/index.html'):
        safe_path(name)
    checks.append('CD allowed namespace and root instruction paths')
    for bad in ['production/combat-depthx/a.txt','research/world-combat/a.txt','docs/combat-depth/name.','docs/combat-depth/x:y']:
        rejects('strict prefix/windows '+bad,lambda bad=bad:safe_path(bad))
    # Malformed ZIPs use internally consistent receipts to exercise member validation.
    for label,names,mode in [('duplicate archive',[entries[0]['path'],entries[0]['path']],None),('symlink archive',[e['path'] for e in entries],stat.S_IFLNK|0o777),('unexpected member',[e['path'] for e in entries]+['production/combat-depth/c.txt'],None)]:
        p=tmp/(label.replace(' ','-')+'.zip')
        with zipfile.ZipFile(p,'x') as z:
            z.writestr(MANIFEST,encoded(manifest))
            for name in names:
                info=zipfile.ZipInfo(name);info.create_system=3;info.external_attr=(mode or (stat.S_IFREG|0o644))<<16
                z.writestr(info,b'AAA' if name.endswith('a.txt') else b'BBB')
        size,sha=hashed(p);badreceipt=dict(receipt,archive_bytes=size,archive_sha256=sha)
        rejects(label,lambda p=p,badreceipt=badreceipt:verify(p,badreceipt))
    # Focused portability checks: URLs retain query/fragment semantics while files resolve.
    web=tmp/'web';docs=web/'docs/combat-depth';docs.mkdir(parents=True)
    (docs/'index.html').write_text('<link href="style.css?v=2#theme"><img src="sample%20image.png?x=1#view">')
    (docs/'style.css').write_text('body{background:url("sample%20image.png?bg=1#x")}')
    (docs/'sample image.png').write_bytes(b'fixture only; no artwork')
    (docs/'data.json').write_text(json.dumps({'src':'sample%20image.png?native=1#crop','record_path':'docs/combat-depth/data.json?record=1#x','tool_output_path':'docs/combat-depth/data.json','prompt_path':'docs/combat-depth/data.json','source_path':'/historical/unneeded.png','story_path':'arrival'}))
    assert local_links(web)['checked_local_urls']==7; checks.append('HTML CSS data URLs query/fragment/encoding and generic file-path fields')
    (docs/'index.html').write_text('<img src="missing.png?v=1#x">')
    rejects('missing local URL',lambda:local_links(web))
    (docs/'index.html').write_text('<img src="../../../outside.png">')
    rejects('local URL escapes root',lambda:local_links(web))
    assert check_inventory(target,manifest,exact=True)['pass'];checks.append('exact fresh restored inventory')
    (target/'extra.txt').write_bytes(b'extra')
    rejects('unexpected extraction file',lambda:check_inventory(target,manifest,exact=True))
    # Git checkouts can carry unrelated tracked files; every bundled member must still match.
    assert check_inventory(target,manifest,exact=False)['pass'];checks.append('additive checkout member parity')
    (target/entries[0]['path']).write_bytes(b'changed')
    rejects('restored source changed',lambda:check_inventory(target,manifest))
    for bad in ['production/combat-depth/.git/config','research/combat-depth/asset-bundle/local/a.zip']:
        rejects('excluded member '+bad,lambda bad=bad:safe_path(bad))
    budgetroot=tmp/'budget';bp=budgetroot/'production/combat-depth';bp.mkdir(parents=True)
    base={'budget':{'primary':24,'texture_passes':24,'structural_repairs':6,'maximum_native_attempts':54,'transport_retries':2,'maximum_total':56}}
    (bp/'plan.json').write_bytes(encoded(base));records={}
    assert resolve_budget(budgetroot,base,records)['effective_budget']==base['budget'];checks.append('fixed 24P 6R1 24F1 54-native 56-invocation budget')
    for key in base['budget']:
        bad={'budget':dict(base['budget'],**{key:base['budget'][key]+1})}
        rejects('budget rejects changed '+key,lambda bad=bad:resolve_budget(budgetroot,bad,records))
    (bp/'budget-amendment-01.json').write_text('{}')
    rejects('unapproved amendment rejected',lambda:resolve_budget(budgetroot,base,records))
    tr=tmp/'transport';tp=tr/'production/combat-depth';(tp/'transport-failures').mkdir(parents=True);(tp/'calls').mkdir()
    failrel='production/combat-depth/transport-failures/D01-F1-service-call-01.json';fp=tr/failrel
    reference={'path':'production/combat-depth/candidates/D01-P.png','sha256':'a'*64}
    failed={'id':'D01','attempt_id':'D01-F1','phase':'texture','category':'vista','retry_of':'D01-P','prompt_path':'production/combat-depth/prompts/D01-F1.txt','prompt_sha256':'b'*64,'plan_sha256':'c'*64,'references':[reference],'referenced_image_paths':['/original/'+reference['path']],'started':{'current_time':'2026-09-08 01:00:00 UTC'},'finished':{'current_time':'2026-09-08 01:01:00 UTC'},'status':'failed-no-artwork-returned','error':'HTTP503','returned_artwork':None}
    fp.write_bytes(encoded(failed))
    retry={k:v for k,v in failed.items() if k not in ('finished','status','error','returned_artwork')}
    retry.update(started={'current_time':'2026-09-08 01:02:00 UTC'},transport_retry_of=failrel,transport_retry_sha256=hashed(fp)[1],transport_retry_reason='unchanged HTTP503 retry')
    cp=tp/'calls/D01-F1.json';cp.write_bytes(encoded(retry))
    x=transport_ledger(tr,{},2);assert x['invocation_count']==2 and x['pending_invocations']==1 and x['native_artwork_count']==0;checks.append('failed and pending invocations consume total cap')
    rejects('pending final invocation',lambda:transport_ledger(tr,{},2,True))
    rejects('failed invocation included in cap',lambda:transport_ledger(tr,{},1))
    x=transport_ledger(tr,{'D01-F1':{}},2,True);assert x['invocation_count']==2 and x['native_artwork_count']==1;checks.append('successful retry remains one native plus failed invocation')
    for label,change in [('prompt changed',{'prompt_sha256':'d'*64}),('reference changed',{'references':[dict(reference,sha256='d'*64)]}),('failure binding changed',{'transport_retry_sha256':'d'*64})]:
        cp.write_bytes(encoded(dict(retry,**change)));rejects('transport '+label,lambda:transport_ledger(tr,{},2))
    cp.write_bytes(encoded(retry))
    fp.write_bytes(encoded(dict(failed,returned_artwork='not null')));rejects('failure artwork output rejected',lambda:transport_ledger(tr,{},2));fp.write_bytes(encoded(failed))
    tool={'schema':'CombatDepthToolFailure/1','functions_cell_id':'fixture','failure_record_path':failrel,'failure_record_sha256':hashed(fp)[1],'outcome':{'id':'D01-F1','status':'error','error':'HTTP503'}}
    (tp/'transport-failures/tool-output.json').write_bytes(encoded(tool));assert transport_ledger(tr,{},2)['invocation_count']==2;checks.append('tool failure receipt is evidence not extra invocation')
    # A second failure retained both in calls and in the ledger counts once.
    again=dict(retry,status='failed-no-artwork-returned',returned_artwork=None,error='HTTP503',finished={'current_time':'2026-09-08 01:03:00 UTC'})
    cp.write_bytes(encoded(again));(tp/'transport-failures/D01-F1-service-call-02.json').write_bytes(encoded(again))
    x=transport_ledger(tr,{},2,True);assert x['invocation_count']==2 and x['failed_no_artwork_count']==2;checks.append('failed retry alias deduplicated by invocation without native')
    result=dict(schema='CombatDepthBundleSecurityTests/1',status='pass',checks=checks,fixture_directory=str(tmp.relative_to(ROOT)),production_archive_created=False,helper_sha256=hashed(HERE/'bundle_assets.py')[1])
    (tmp/'test-receipt.json').write_bytes(encoded(result))
    (HERE/'security-test-receipt.json').write_bytes(encoded(result))
    print(json.dumps(result,indent=2))

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['inspect','create','verify','restore','rebuild-check','self-test'])
    parser.add_argument('--root',type=Path,default=ROOT)
    parser.add_argument('--output','--out',dest='out',type=Path,default=HERE/'local/final-v1')
    parser.add_argument('--expected-art',type=int)
    parser.add_argument('--archive',type=Path)
    parser.add_argument('--receipt',type=Path)
    parser.add_argument('--target',type=Path)
    args=parser.parse_args()
    if args.action=='self-test':self_test();return
    if args.action=='inspect':
        manifest,sources=gather(args.root,strict=False)
        print(json.dumps({'source_bindings':manifest['source_bindings'],'payload_files':len(sources),'payload_bytes':manifest['total_bytes'],'archive_created':False},indent=2));return
    if args.action=='create':create(args.root,args.out,args.expected_art);return
    if args.action=='rebuild-check':
        if not args.target:parser.error('--target required')
        print(json.dumps(rebuild_check(args.target),indent=2));return
    if not args.archive or not args.receipt:parser.error('--archive and --receipt are required')
    receipt=json.loads(args.receipt.read_text())
    if args.action=='verify':print(json.dumps(dict(verified_files=len(verify(args.archive,receipt)['files']))));return
    if not args.target:parser.error('--target required')
    print(json.dumps(restore(args.archive,receipt,args.target)))

if __name__=='__main__':main()
