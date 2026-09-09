"""Build only the isolated pilot-chapters reader; production sources are read-only."""
from pathlib import Path
import argparse, hashlib, json, os, re, struct
import xml.etree.ElementTree as ET
ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / 'production/pilot-chapters'
OUT = ROOT / 'docs/pilot-chapters'
DIMENSIONS = ['overall','drawing','impact','movement','power','causality','anatomy','scale','ground','texture']

def lettering_contract(rows):
    if not isinstance(rows,list) or len(rows)>6:raise ValueError('Lettering must be a short list')
    result=[];seen=set()
    for row in rows:
        c=dict(row)
        if not isinstance(c.get('id'),str) or c['id'] in seen:raise ValueError('Unique lettering ID required')
        seen.add(c['id'])
        if c.get('kind') not in ('speech','thought','caption','sfx') or not isinstance(c.get('text'),str) or not c['text'].strip() or len(c['text'])>600:raise ValueError('Invalid frozen lettering')
        if 'show_speaker' in c and type(c['show_speaker']) is not bool:raise ValueError('Speaker-label layout flag must be boolean')
        if 'offscreen' in c and type(c['offscreen']) is not bool:raise ValueError('Offscreen attribution flag must be boolean')
        if 'attribution' in c and (not isinstance(c['attribution'],str) or not c['attribution'].strip()):raise ValueError('Visible attribution must be plain text')
        c.setdefault('position','overlay')
        if c['position'] not in ('overlay','below'):raise ValueError('Unknown lettering position')
        if c['position']=='overlay':
            for k in ('x','y','w','h'):
                if type(c.get(k)) not in (int,float) or not 0<=c[k]<=1:raise ValueError('Lettering zones must be normalized')
            if c['w']<=0 or c['h']<=0 or c['x']+c['w']>1.000001 or c['y']+c['h']>1.000001:raise ValueError('Lettering zone leaves panel')
        if 'tail' in c:
            if not isinstance(c['tail'],dict) or any(type(c['tail'].get(k)) not in (int,float) or not 0<=c['tail'][k]<=1 for k in ('x','y')):raise ValueError('Invalid speech tail point')
        result.append(c)
    return result

def plan_contract(plan):
    if plan.get('schema')!='PilotChaptersPlan/1' or plan.get('experiment_id')!='PC-20260909-01':raise ValueError('Wrong pilot plan identity')
    raw=plan.get('entries',[]);support=plan.get('support_entries',[])
    if len(raw)!=80 or len(support)>5:raise ValueError('Expected eighty panels and at most five separate sheets')
    entries=[{**e,'sequence_id':e.get('chapter_id',e.get('sequence_id')),'caption':e.get('caption',e.get('title','')),'scale':e.get('scale',''),'drawing_direction':e.get('drawing_direction',e.get('chapter_id','')),'category':e.get('category','panel'),'subjects':e.get('subjects',[]),'group':e.get('group',e.get('chapter_id','')),'lettering':lettering_contract(e.get('lettering',[]))} for e in raw]
    ids=[e['id'] for e in entries+support]
    if len(ids)!=len(set(ids)) or {e['id'] for e in entries}!={f'{c}{i:02}' for c in ('NG','BP','ST','RC','FL') for i in range(1,17)}:raise ValueError('Invalid pilot panel IDs')
    chapters=plan.get('chapters',[])
    if len(chapters)!=5 or {c['id'] for c in chapters}!={'NG','BP','ST','RC','FL'}:raise ValueError('Expected five chapters')
    grouped=[];normalized=[]
    for chapter in chapters:
        panels=sorted([e for e in entries if e['sequence_id']==chapter['id']],key=lambda e:e.get('sequence_order',0));panel_ids=[e['id'] for e in panels]
        if len(panels)!=16 or [e.get('sequence_order') for e in panels]!=list(range(1,17)) or chapter.get('panel_ids',chapter.get('entries',panel_ids))!=panel_ids:raise ValueError('Chapter must contain sixteen ordered panels')
        normalized.append({**chapter,'panel_ids':panel_ids,'dimensions':['comprehension','continuity']});grouped+=panels
    return grouped,support,normalized

def process_controls(plan):
    path=SOURCE/'controls/manifest.json'
    if not path.exists():return []
    doc=read(path);result=[]
    for original in doc.get('controls',[]):
        c=dict(original);c['manifest_id']=c['id'];c['id']=c['id']+'-CONTROL'
        for dst,src in [('path','png_path'),('sha256','png_sha256'),('source_path','svg_path'),('source_sha256','svg_sha256')]:
            if src in c:c[dst]=c[src]
        item={**c,**asset(c)};source=bound_file(c['source_path'],c['source_sha256']);ET.fromstring(source.read_text());item['source_src']=os.path.relpath(source,OUT).replace(os.sep,'/');result.append(item)
    if len(result)!=len({r['id'] for r in result}):raise ValueError('Duplicate control IDs')
    return result


def edit_provenance(*records):
    """Normalize recorded aliases without changing source records; conflicts fail."""
    result=[]
    for aliases in [('retry_of','source_attempt_id'),('retry_reason','reason')]:
        values=[]
        for record in records:
            if all(k in record for k in aliases) and record[aliases[0]]!=record[aliases[1]]:
                raise ValueError('Conflicting edit provenance aliases: '+str(aliases))
            for key in aliases:
                if record.get(key) is not None:
                    value=record[key]
                    if not isinstance(value,str) or not value.strip():raise ValueError('Edit provenance must be nonempty text')
                    values.append(value)
        if len(set(values))>1:raise ValueError('Conflicting edit provenance across records')
        result.append(values[0] if values else None)
    return tuple(result)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(path, default=None):
    return json.loads(path.read_text()) if path.exists() else default

def asset(value, board=False, allowed=None):
    path = (ROOT / value['path']).resolve()
    if not path.is_relative_to((allowed or SOURCE).resolve()):
        raise ValueError('Image path leaves the pilot-chapters namespace')
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
    if isinstance(spec,list):
        if len(spec)!=1:raise ValueError('Expected one exact historical choice export')
        spec=spec[0]
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
    paths = [plan_path] if plan_path.exists() else []
    paths += sorted((SOURCE/'plan-history').glob('plan-*.json'))
    for path in paths:
        if not path.resolve().is_relative_to(SOURCE.resolve()):
            raise ValueError('Frozen plan source leaves its namespace')
        value = read(path)
        if value.get('schema') != 'PilotChaptersPlan/1' or value.get('experiment_id') != 'PC-20260909-01':
            raise ValueError('Frozen plan source belongs to another experiment')
        plan_contract(value)
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
        source_attempt, reason = edit_provenance(f)
        before = attempts.get(source_attempt)
        if (source_attempt or not f['attempt_id'].endswith('-P')) and (not before or before['id'] != f['id'] or not any(ref['path']==before['path'] and ref['sha256']==before['sha256'] for ref in refs)):
            raise ValueError('Failure retained edit source does not match references')
        side_path = path.with_name(path.stem+'-tool-output.json')
        side = read(side_path)
        relative = path.relative_to(ROOT).as_posix()
        if not side or side.get('schema') != 'PilotChaptersToolFailure/1' or side.get('failure_record_path') != relative or side.get('failure_record_sha256') != sha(path) or side.get('outcome',{}).get('id') != f['attempt_id'] or side['outcome'].get('status') != 'error' or not isinstance(side['outcome'].get('error'),str):
            raise ValueError('Failure tool-output sidecar is missing or unbound')
        retry = read(SOURCE/'calls'/f"{f['attempt_id']}.json",{})
        if retry.get('transport_retry_of'):
            if retry['transport_retry_of'] != relative or retry.get('transport_retry_sha256') != sha(path) or any(retry.get(k)!=f.get(k) for k in ['id','attempt_id','prompt_path','prompt_sha256','plan_sha256','references','retry_of','source_attempt_id','retry_reason','reason']):
                raise ValueError('Transport retry differs from its exact failed request')
        grouped[f['id']].append({'attempt_id':f['attempt_id'],'status':f['status'],'error':f['error'],
            'record_path':relative,'record_sha256':sha(path),'tool_output_path':side_path.relative_to(ROOT).as_posix(),
            'tool_output_sha256':sha(side_path),'prompt_path':f['prompt_path'],'prompt_sha256':f['prompt_sha256'],
            'retry_of':source_attempt,'references':refs,'plan_sha256':f['plan_sha256'],'plan_path':plan_hashes[f['plan_sha256']]})
    return grouped

def build(require_complete=False):
    plan_path = SOURCE / 'plan.json'
    plan = read(plan_path, {'schema':'PilotChaptersPlan/1','experiment_id':'PC-20260909-01','entries':[]})
    if plan.get('schema','PilotChaptersPlan/1') != 'PilotChaptersPlan/1' or plan.get('experiment_id') != 'PC-20260909-01':
        raise ValueError('Invalid pilot-chapters plan identity')
    entries,support_entries,sequences=plan_contract(plan)
    support_entries=[{**e,'caption':e.get('caption','Supplemental cast and equipment reference; separate from finished compositions.'),'subjects':e.get('subjects',[])} for e in support_entries]
    main_ids={e['id'] for e in entries};support_ids={e['id'] for e in support_entries};ids=list(main_ids|support_ids)
    for e in entries+support_entries:
        if not isinstance(e.get('paired_ids',[]),list) or len(set(e.get('paired_ids',[])))!=len(e.get('paired_ids',[])) or any(p not in main_ids or p==e['id'] for p in e.get('paired_ids',[])):raise ValueError('Invalid paired composition')
        if any(not isinstance(e.get(k),str) or not e[k].strip() for k in ['title','caption']):raise ValueError('Entry title and caption required')
        if e['id'] in main_ids and (not isinstance(e.get('scale'),str) or not isinstance(e.get('drawing_direction'),str) or not isinstance(e.get('category'),str)):raise ValueError('Composition scale/drawing/category required')
        if not isinstance(e.get('subjects',[]),list):raise ValueError('Subject IDs require list')
    controls=process_controls(plan)
    option_doc=read(SOURCE/'options.json',{'items':[]});options=[{**o,**asset(o)} for o in option_doc.get('items',[])]
    if len({o['id'] for o in options})!=len(options):raise ValueError('Duplicate option IDs')
    references = plan.get('reference_library',read(SOURCE/'references.json',{'references':[]})['references'])
    if len({r['id'] for r in references}) != len(references):
        raise ValueError('Duplicate reference ID')
    references = [{**r,**asset(r)} for r in references]
    if len({r['id'] for r in references}|{c['id'] for c in controls})!=len(references)+len(controls):raise ValueError('Reference/control ID collision')
    for entry in entries+support_entries:
        raw_refs=list(entry.get('references',[]))
        if entry.get('control'):raw_refs.append(entry['control'])
        if entry.get('subject_reference_id'):raw_refs.append(entry['subject_reference_id'])
        if entry.get('reference_id'):raw_refs.append(entry['reference_id'])
        normalized=[]
        for ref in raw_refs:
            if isinstance(ref,str):normalized.append(ref);continue
            if not isinstance(ref,dict):raise ValueError('Reference must be a key or exact source object')
            asset(ref)
            matched=next((r for r in references+controls+options if r['path']==ref['path'] and r['sha256']==ref['sha256']),None)
            if not matched:
                matched={**ref,**asset(ref),'id':'REF-'+ref['sha256'][:16],'title':ref.get('title',ref.get('role','Bound scene reference'))};references.append(matched)
            normalized.append(matched['id'])
        entry['references']=list(dict.fromkeys(normalized))

    for e in entries+support_entries:
        if not isinstance(e.get('references',[]),list) or set(e.get('references',[]))-({r['id'] for r in references}|{c['id'] for c in controls}|{o['id'] for o in options}|set(ids)|{'@'+i for i in ids}):
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
    for entry in entries+support_entries:
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
                if raw['id'] not in {e['id'] for group in plan_contract(read(ROOT/frozen_plans[call['plan_sha256']]))[:2] for e in group}:
                    raise ValueError('Call panel is absent from its frozen plan')
                if call.get('prompt_path'):
                    bound_file(call['prompt_path'],call['prompt_sha256'])
                    item.update(prompt_path=call['prompt_path'],prompt_sha256=call['prompt_sha256'])
                if 'references' in call:
                    if not isinstance(call['references'],list) or not 1 <= len(call['references']) <= 5:
                        raise ValueError('Call references require a list')
                    for reference in call['references']:
                        asset(reference)
                    item['references'] = call['references']
                item.update(call_path=call_path.relative_to(ROOT).as_posix(), call_sha256=sha(call_path), plan_sha256=call['plan_sha256'], plan_path=frozen_plans[call['plan_sha256']])
            retry_of, reason = edit_provenance(call,raw)
            if retry_of or re.search(r'-[RF]\d*$', raw['attempt_id']):
                before = attempts.get(retry_of)
                if not before or before['id'] != entry['id'] or not isinstance(reason, str) or not reason.strip() or not call:
                    raise ValueError('Retry needs a retained source attempt and correction call record')
                item.update(retry_of=retry_of, retry_reason=reason)
                if call.get('evidence_path'):
                    evidence=(ROOT/call['evidence_path']).resolve()
                    if not any(evidence.is_relative_to(ROOT/p) for p in ['research/pilot-chapters','production/pilot-chapters']) or not evidence.is_file():
                        raise ValueError('Edit evidence path missing or outside encounter namespaces')
                    observed=sha(evidence)
                    if call.get('evidence_sha256') and call['evidence_sha256']!=observed:raise ValueError('Recorded edit evidence hash differs')
                    item['evidence']={'path':call['evidence_path'],'recorded_sha256':call.get('evidence_sha256'),'inspection_sha256':observed,'binding_status':'call-recorded hash' if call.get('evidence_sha256') else 'path recorded in call; bytes hashed at reader inspection only'}
            history.append(item)
        history.sort(key=lambda c: {'P':0,'R1':1,'F1':2}.get(c['attempt_id'].rsplit('-',1)[-1],99))
        cards.append({**entry, 'power':{**entry['power'],'growth':[entry['power']['growth']] if isinstance(entry['power'].get('growth'),str) else entry['power'].get('growth',[])} if entry.get('power') else None, 'candidate':selected.get(entry['id']), 'history':history, 'service_failures':failures[entry['id']]})
    layout_overrides=read(SOURCE/'lettering-overrides.json',{'entries':{}}).get('entries',{})
    for card in cards:
        card['lettering']=lettering_contract(card.get('lettering',[]));override=layout_overrides.get(card['id'])
        if override:
            c=card['candidate']
            if not c or override.get('attempt_id')!=c['attempt_id'] or override.get('sha256')!=c['sha256']:raise ValueError('Lettering override source is stale')
            corrected=lettering_contract(override['lettering'])
            if [(r['id'],r['text'],r.get('speaker'),r['kind'],r.get('attribution'),r.get('offscreen',False)) for r in corrected]!=[(r['id'],r['text'],r.get('speaker'),r['kind'],r.get('attribution'),r.get('offscreen',False)) for r in card['lettering']]:raise ValueError('Layout override may not rewrite frozen copy')
            card['lettering']=corrected;card['lettering_source_sha256']=c['sha256']
    notes_path = SOURCE / 'review-notes.json'
    notes = read(notes_path)
    if notes:
        if notes.get('schema') != 'PilotChaptersReviewNotes/1' or notes.get('experiment_id') != plan['experiment_id']:
            raise ValueError('Technical notes belong to another experiment')
        for id, note in notes.get('entries', {}).items():
            c = selected.get(id)
            if not c or note.get('attempt_id') != c['attempt_id'] or note.get('sha256') != c['sha256']:
                raise ValueError('Stale technical note source')
            if not isinstance(note.get('observations'), list) or any(not isinstance(t, str) for t in note['observations']):
                raise ValueError('Technical observations must be plain strings')
    cards = [{**e, 'ai_observations': (notes or {}).get('entries', {}).get(e['id'], {}).get('observations', [])} for e in cards]
    support_cards=[e for e in cards if e['id'] in support_ids]
    cards=[e for e in cards if e['id'] in main_ids]
    if require_complete and (set(selected)!=(main_ids|support_ids)):
        raise ValueError('Final reader requires every composition and support sheet')
    bindings = [{'id':e['id'],'attempt_id':e['candidate']['attempt_id'] if e['candidate'] else None,
                 'sha256':e['candidate']['sha256'] if e['candidate'] else None} for e in cards]
    identity = {'experiment_id':plan['experiment_id'],'plan_sha256':sha(plan_path) if plan_path.exists() else None,'source_bindings':bindings,'lettering_bindings':[{'id':e['id'],'lettering':e['lettering']} for e in cards],'process_bindings':[{'id':e['id'],'attempt_id':e['candidate']['attempt_id'] if e['candidate'] else None,'sha256':e['candidate']['sha256'] if e['candidate'] else None} for e in support_cards]+[{'id':c['id'],'sha256':c.get('sha256'),'source_sha256':c.get('source_sha256')} for c in controls]}
    data = {'schema':'PilotChaptersReader/1',**identity,
            'dataset_sha256':hashlib.sha256(json.dumps(identity,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
            'categories':[{'id':k,'title':next((c['title'] for c in sequences if c['id']==k),k.replace('_',' ').title()),'dimensions':DIMENSIONS} for k in dict.fromkeys(e['category'] for e in entries)],
            'sequences':sequences,'chapters':sequences,'options':options,
            'entries':cards,'support_entries':support_cards,'controls':controls,'references':references,'plan_sources':[{'path':p,'sha256':h} for h,p in frozen_plans.items()],'previous':previous(plan.get('prior_choices') or ({'path':(SOURCE/'previous/ce-selection.json').relative_to(ROOT).as_posix(),'sha256':sha(SOURCE/'previous/ce-selection.json')} if (SOURCE/'previous/ce-selection.json').exists() else None)),
            'available_count':len(main_ids&set(selected)),'total_count':len(entries),'support_available_count':len(support_ids&set(selected)),'support_total_count':len(support_entries),'owner_approval':None,
            'review_notes_sha256':sha(notes_path) if notes else None,
            'report_links':[{'label':label,'path':f'../../research/pilot-chapters/{name}'} for name,label in [('START_HERE.md','Study details'),('RESULTS.md','Results & observations'),('PIPELINE.md','How the study was made'),('editorial/production-review/SERIES-PATHS.md','Possible series paths')] if (ROOT/f'research/pilot-chapters/{name}').exists()]}
    OUT.mkdir(parents=True,exist_ok=True)
    text=json.dumps(data,indent=2,ensure_ascii=False)
    (OUT/'data.json').write_text(text+'\n')
    (OUT/'data.js').write_text('window.PILOT_CHAPTERS_DATA = '+text+';\n')
    return data

if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--require-complete',action='store_true')
    data=build(parser.parse_args().require_complete)
    print(json.dumps({'available':data['available_count'],'total':data['total_count'],'dataset_sha256':data['dataset_sha256']}))
