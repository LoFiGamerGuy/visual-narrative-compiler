"""Build only the isolated impact-clarity reader; production sources are read-only."""
from pathlib import Path
import argparse, hashlib, json, os, re, struct
import xml.etree.ElementTree as ET
ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / 'production/impact-clarity'
OUT = ROOT / 'docs/impact-clarity'
CATEGORY_IDS = {'melee':['M01','M02'], 'movement':['V01','V02'], 'magic':['A01','A02'], 'giant':['S01','S02'], 'radical':[f'X{i:02}' for i in range(1,5)], 'style':[f'Y{i:02}' for i in range(1,5)]}
DIMENSIONS = ['overall','drawing','impact','movement','power','causality','anatomy','scale','ground','texture']
LABELS = {'melee':'Melee','movement':'Movement','magic':'Magic','giant':'Giant scale','radical':'Radical alternative','style':'Other liked styles'}
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(path, default=None):
    return json.loads(path.read_text()) if path.exists() else default

def asset(value, board=False, allowed=None):
    path = (ROOT / value['path']).resolve()
    if not path.is_relative_to((allowed or SOURCE).resolve()):
        raise ValueError('Image path leaves the impact-clarity namespace')
    raw = path.read_bytes()
    if raw[:8] != b'\x89PNG\r\n\x1a\n' or sha(path) != value['sha256']:
        raise ValueError('Image signature or source hash mismatch')
    width, height = struct.unpack('>II', raw[16:24])
    if width < 1 or height < 1:
        raise ValueError('Invalid native dimensions')
    if any(k in value and value[k] != v for k, v in [('width', width), ('height', height)]):
        raise ValueError('Declared image dimensions do not match PNG')
    return {**{k: value[k] for k in ['path', 'sha256', 'attempt_id'] if k in value},
            'width': width, 'height': height, 'src': os.path.relpath(path, OUT).replace(os.sep, '/')}


def previous(spec):
    if not spec:
        return None
    path = (ROOT / spec['path']).resolve()
    if not path.is_relative_to(SOURCE.resolve()) or sha(path) != spec['sha256']:
        raise ValueError('Preserved choices path or hash mismatch')
    original = read(path)
    if not isinstance(original,dict) or not isinstance(original.get('choices'),dict):
        raise ValueError('Preserved choice export requires exact choices')
    return {'label':spec.get('label','Earlier character choices'),'sha256':sha(path),'path':spec['path'],
            'download_src':os.path.relpath(path,OUT).replace(os.sep,'/'),'export':original}

def bound_file(path, expected):
    file = (ROOT / path).resolve()
    if not file.is_relative_to(SOURCE.resolve()) or sha(file) != expected:
        raise ValueError('Service failure source path or hash mismatch')
    return file

def plan_sources(plan_path):
    sources = {}
    expected = {id:category for category,ids in CATEGORY_IDS.items() for id in ids}
    paths = [plan_path] if plan_path.exists() else []
    paths += sorted((SOURCE/'plan-history').glob('plan-*.json'))
    for path in paths:
        if not path.resolve().is_relative_to(SOURCE.resolve()):
            raise ValueError('Frozen plan source leaves its namespace')
        value = read(path)
        if value.get('schema') != 'ImpactClarityPlan/1' or value.get('experiment_id') != 'IC-20260909-01':
            raise ValueError('Frozen plan source belongs to another experiment')
        entries = value.get('entries',[])
        actual = {e['id']:e.get('category') for e in entries}
        original = {id:category for id,category in expected.items() if not id.startswith('Y')}
        if len(entries) != len(actual) or actual not in [expected, original]:
            raise ValueError('Frozen plan source changes the panel/category contract')
        sources[sha(path)] = path.relative_to(ROOT).as_posix()
    return sources

def service_failures(ids, attempts, plan_hashes):
    grouped = {id:[] for id in ids}
    folder = SOURCE / 'transport-failures'
    for path in sorted(folder.glob('*.json')):
        if path.name.endswith('-tool-output.json'):
            continue
        f = read(path)
        if f.get('id') not in grouped or f.get('status') != 'failed-no-artwork-returned' or 'returned_artwork' not in f or f['returned_artwork'] is not None or f.get('plan_sha256') not in plan_hashes:
            raise ValueError('Invalid no-artwork service failure record')
        if not isinstance(f.get('error'),str) or not f['error'] or not re.fullmatch(re.escape(f['id'])+r'-[PFR]\d*',f.get('attempt_id','')):
            raise ValueError('Failure error or attempt identity is invalid')
        bound_file(f['prompt_path'],f['prompt_sha256'])
        refs = f.get('references')
        if not isinstance(refs,list) or not refs:
            raise ValueError('Failure needs exact source references')
        for ref in refs:
            asset(ref)
        before = attempts.get(f.get('retry_of'))
        if not before or before['id'] != f['id'] or not any(ref['path']==before['path'] and ref['sha256']==before['sha256'] for ref in refs):
            raise ValueError('Failure retained edit source does not match references')
        side_path = path.with_name(path.stem+'-tool-output.json')
        side = read(side_path)
        relative = path.relative_to(ROOT).as_posix()
        if not side or side.get('schema') != 'ImpactClarityToolFailure/1' or side.get('failure_record_path') != relative or side.get('failure_record_sha256') != sha(path) or side.get('outcome',{}).get('id') != f['attempt_id'] or side['outcome'].get('status') != 'error' or not isinstance(side['outcome'].get('error'),str):
            raise ValueError('Failure tool-output sidecar is missing or unbound')
        retry = read(SOURCE/'calls'/f"{f['attempt_id']}.json",{})
        if retry.get('transport_retry_of'):
            if retry['transport_retry_of'] != relative or retry.get('transport_retry_sha256') != sha(path) or any(retry.get(k)!=f.get(k) for k in ['id','attempt_id','prompt_path','prompt_sha256','plan_sha256','references','retry_of']):
                raise ValueError('Transport retry differs from its exact failed request')
        grouped[f['id']].append({'attempt_id':f['attempt_id'],'status':f['status'],'error':f['error'],
            'record_path':relative,'record_sha256':sha(path),'tool_output_path':side_path.relative_to(ROOT).as_posix(),
            'tool_output_sha256':sha(side_path),'prompt_path':f['prompt_path'],'prompt_sha256':f['prompt_sha256'],
            'retry_of':f['retry_of'],'references':refs,'plan_sha256':f['plan_sha256'],'plan_path':plan_hashes[f['plan_sha256']]})
    return grouped

def build(require_complete=False):
    plan_path = SOURCE / 'plan.json'
    plan = read(plan_path, {'schema':'ImpactClarityPlan/1','experiment_id':'IC-20260909-01','entries':[]})
    if plan.get('schema','ImpactClarityPlan/1') != 'ImpactClarityPlan/1' or plan.get('experiment_id') != 'IC-20260909-01':
        raise ValueError('Invalid impact-clarity plan identity')
    entries = plan.get('entries',[])
    expected = {i for values in CATEGORY_IDS.values() for i in values}
    ids = [e['id'] for e in entries]
    if len(ids) != len(set(ids)) or set(ids)-expected:
        raise ValueError('Duplicate or unknown scene ID')
    for e in entries:
        if e.get('group') != ('radical' if e['id'].startswith('X') else 'comparison' if e['id'].startswith('Y') else 'core'):
            raise ValueError('Study group mismatch')
        if not isinstance(e.get('paired_ids',[]),list) or len(set(e.get('paired_ids',[]))) != len(e.get('paired_ids',[])) or any(p not in ids or p == e['id'] for p in e.get('paired_ids',[])):
            raise ValueError('Unknown, self or duplicate paired study')
        if e.get('category') not in CATEGORY_IDS or e['id'] not in CATEGORY_IDS[e['category']]:
            raise ValueError('Scene category mismatch')
        if any(not isinstance(e.get(k),str) or not e[k].strip() for k in ['title','caption','scale']):
            raise ValueError('Title, caption and scale must be text')
        if not isinstance(e.get('subjects'),list) or any(not isinstance(v,str) or not v for v in e['subjects']):
            raise ValueError('Subject IDs must be a text list')
        if e.get('power') is not None:
            p=e['power']
            if not isinstance(p,dict) or any(not isinstance(p.get(k,''),str) for k in ['name','description','limitation']) or not isinstance(p.get('growth',[]),(list,str)) or isinstance(p.get('growth',[]),list) and any(not isinstance(v,str) for v in p.get('growth',[])):
                raise ValueError('Power description and growth must be plain text')
    references = plan.get('reference_library',read(SOURCE/'reference-library.json',[]))
    if len({r['id'] for r in references}) != len(references):
        raise ValueError('Duplicate reference ID')
    references = [{**r,**asset(r)} for r in references]
    for e in entries:
        if not isinstance(e.get('references',[]),list) or set(e.get('references',[]))-({r['id'] for r in references}|{'@'+i for i in ids}):
            raise ValueError('Unknown scene reference')
    rows = read(SOURCE / 'candidates.json', {'candidates': []})['candidates']
    attempts = {c['attempt_id']: c for c in rows}
    if len(attempts) != len(rows) or any(c['id'] not in set(ids) for c in rows):
        raise ValueError('Duplicate attempt or unknown scene')
    selections = read(SOURCE / 'selected.json', {'selected': {}})['selected']
    if set(selections) - set(ids):
        raise ValueError('Selected unknown scene')
    selected = {}
    for id, attempt in selections.items():
        raw = attempts.get(attempt)
        if not raw or raw['id'] != id or raw.get('status') != 'reviewable-unaccepted':
            raise ValueError('Selected scene, attempt or status mismatch')
        selected[id] = asset(raw)
    frozen_plans = plan_sources(plan_path)
    failures = service_failures(ids, attempts, frozen_plans)
    cards = []
    for entry in entries:
        history = []
        for raw in rows:
            if raw['id'] != entry['id']:
                continue
            item = asset(raw)
            call_path = SOURCE / 'calls' / f'{raw["attempt_id"]}.json'
            call = read(call_path, {})
            if call:
                if call.get('id', raw['id']) != raw['id'] or call.get('attempt_id', raw['attempt_id']) != raw['attempt_id']:
                    raise ValueError('Call record belongs to another image')
                if call.get('plan_sha256') not in frozen_plans:
                    raise ValueError('Call plan hash has no exact current or preserved plan source')
                if not any(e['id']==raw['id'] for e in read(ROOT/frozen_plans[call['plan_sha256']])['entries']):
                    raise ValueError('Call panel is absent from its frozen plan')
                if call.get('prompt_path'):
                    bound_file(call['prompt_path'],call['prompt_sha256'])
                    item.update(prompt_path=call['prompt_path'],prompt_sha256=call['prompt_sha256'])
                if 'references' in call:
                    if not isinstance(call['references'],list):
                        raise ValueError('Call references require a list')
                    for reference in call['references']:
                        asset(reference)
                    item['references'] = call['references']
                item.update(call_path=call_path.relative_to(ROOT).as_posix(), call_sha256=sha(call_path), plan_sha256=call['plan_sha256'], plan_path=frozen_plans[call['plan_sha256']])
            for field in ['retry_of', 'retry_reason']:
                if raw.get(field) and call.get(field) and raw[field] != call[field]:
                    raise ValueError('Conflicting retry provenance')
            retry_of = call.get('retry_of') or raw.get('retry_of')
            reason = call.get('retry_reason') or raw.get('retry_reason')
            if retry_of or re.search(r'-[RF]\d*$', raw['attempt_id']):
                before = attempts.get(retry_of)
                if not before or before['id'] != entry['id'] or not isinstance(reason, str) or not reason.strip() or not call:
                    raise ValueError('Retry needs a retained source attempt and correction call record')
                item.update(retry_of=retry_of, retry_reason=reason)
            history.append(item)
        cards.append({**entry, 'power':{**entry['power'],'growth':[entry['power']['growth']] if isinstance(entry['power'].get('growth'),str) else entry['power'].get('growth',[])} if entry.get('power') else None, 'candidate':selected.get(entry['id']), 'history':history, 'service_failures':failures[entry['id']]})
    notes_path = SOURCE / 'review-notes.json'
    notes = read(notes_path)
    if notes:
        if notes.get('schema') != 'ImpactClarityReviewNotes/1' or notes.get('experiment_id') != plan['experiment_id']:
            raise ValueError('Technical notes belong to another experiment')
        for id, note in notes.get('entries', {}).items():
            c = selected.get(id)
            if not c or note.get('attempt_id') != c['attempt_id'] or note.get('sha256') != c['sha256']:
                raise ValueError('Stale technical note source')
            if not isinstance(note.get('observations'), list) or any(not isinstance(t, str) for t in note['observations']):
                raise ValueError('Technical observations must be plain strings')
    cards = [{**e, 'ai_observations': (notes or {}).get('entries', {}).get(e['id'], {}).get('observations', [])} for e in cards]
    if require_complete and (set(ids) != expected or len(selected) != 16):
        raise ValueError('Final reader requires all16 actual selected studies')
    bindings = [{'id':e['id'],'attempt_id':e['candidate']['attempt_id'] if e['candidate'] else None,
                 'sha256':e['candidate']['sha256'] if e['candidate'] else None} for e in cards]
    identity = {'experiment_id':plan['experiment_id'],'plan_sha256':sha(plan_path) if plan_path.exists() else None,'source_bindings':bindings}
    data = {'schema':'ImpactClarityReader/1',**identity,
            'dataset_sha256':hashlib.sha256(json.dumps(identity,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
            'categories':[{'id':k,'title':LABELS[k],'dimensions':DIMENSIONS} for k in CATEGORY_IDS],
            'entries':cards,'references':references,'plan_sources':[{'path':p,'sha256':h} for h,p in frozen_plans.items()],'previous':previous(plan.get('prior_choices')),
            'available_count':len(selected),'total_count':16,'owner_approval':None,
            'review_notes_sha256':sha(notes_path) if notes else None,
            'report_links':[{'label':label,'path':f'../../research/impact-clarity/{name}'} for name,label in [('START_HERE.md','Study details'),('RESULTS.md','Results & observations')] if (ROOT/f'research/impact-clarity/{name}').exists()] + ([{'label':'Combat reference board','path':'combat-references/index.html'}] if (OUT/'combat-references/index.html').exists() else [])}
    OUT.mkdir(parents=True,exist_ok=True)
    text=json.dumps(data,indent=2,ensure_ascii=False)
    (OUT/'data.json').write_text(text+'\n')
    (OUT/'data.js').write_text('window.IMPACT_CLARITY_DATA = '+text+';\n')
    return data

if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--require-complete',action='store_true')
    data=build(parser.parse_args().require_complete)
    print(json.dumps({'available':data['available_count'],'total':16,'dataset_sha256':data['dataset_sha256']}))
