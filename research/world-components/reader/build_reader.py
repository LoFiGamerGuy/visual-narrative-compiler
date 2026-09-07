"""Build only the offline world-component reader; never select or alter source art."""
from pathlib import Path
import argparse, hashlib, json, os, struct, re
ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / 'production/world-components'
OUT = ROOT / 'docs/world-components'
STYLES = ['01','02','05','06','13','15','17','18','19']
CATEGORIES = ['C1','C2','E1','E2','M1','G1']
DISPLAY_OVERRIDES = Path(__file__).resolve().parent / 'display-text-overrides.json'
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path, default=None): return json.loads(path.read_text()) if path.exists() else default
def asset(value):
    path = (ROOT / value['path']).resolve()
    if not path.is_relative_to(SOURCE.resolve()): raise ValueError('Image path leaves the new world-component namespace')
    raw = path.read_bytes()
    if raw[:8] != b'\x89PNG\r\n\x1a\n' or sha(path) != value['sha256']: raise ValueError('Image signature or source hash mismatch')
    width,height = struct.unpack('>II',raw[16:24])
    if ('width' in value and value['width'] != width) or ('height' in value and value['height'] != height): raise ValueError('Declared image dimensions do not match PNG')
    if width < 1 or height < 1: raise ValueError('Invalid image dimensions')
    return {**{k:value[k] for k in ['path','sha256','attempt_id'] if k in value},'width':width,'height':height,'src':os.path.relpath(path,OUT).replace(os.sep,'/')}
def build(require_complete=False):
    plan_path=SOURCE/'kit-plan.json';plan=read(plan_path)
    if not plan: raise ValueError('The frozen kit plan is required')
    if plan.get('schema') != 'WorldComponentPlan/1': raise ValueError('Unexpected world component plan schema')
    if sorted(s['id'] for s in plan['styles']) != STYLES: raise ValueError('Exactly the nine original favorite styles are required')
    if sorted(c['id'] for c in plan['categories']) != sorted(CATEGORIES): raise ValueError('Exactly six independent categories are required')
    entries=plan['entries'];expected={f'{s}-{c}' for s in STYLES for c in CATEGORIES}
    if len(entries)!=54 or {e['id'] for e in entries} != expected: raise ValueError('Exactly54 distinct world-component IDs are required')
    if any(e['id']!=f'{e["style_id"]}-{e["category_id"]}' for e in entries): raise ValueError('Component ID does not match its style/category')
    references=read(SOURCE/'references.json',[])
    if sorted(r['id'] for r in references)!=STYLES: raise ValueError('Nine original reference anchors are required')
    references=[{'id':r['id'],**asset(r)} for r in references]
    rows=read(SOURCE/'candidates.json',{'candidates':[]})['candidates'];attempts={c['attempt_id']:c for c in rows}
    if len(attempts)!=len(rows): raise ValueError('Duplicate candidate attempt')
    selections=read(SOURCE/'selected.json',{'selected':{}})['selected']
    if set(selections)-expected: raise ValueError('Selected unknown component')
    selected={}
    for id,attempt in selections.items():
        raw=attempts.get(attempt)
        if not raw or raw['id']!=id or raw.get('status')!='reviewable-unaccepted': raise ValueError('Selected component/attempt/status mismatch')
        selected[id]=asset(raw)
    overrides=read(DISPLAY_OVERRIDES,{'entries':{}})
    if overrides.get('schema')!='WorldComponentDisplayTextOverrides/1': raise ValueError('Unexpected reader text override schema')
    display_categories=[]
    for raw_category in plan['categories']:
        category={**raw_category};change=overrides.get('categories',{}).get(category['id'])
        if change and 'description' in category:
            if category['description']!=change['source']: raise ValueError('Reader override no longer matches frozen category description')
            category['display_description']=change['display']
        display_categories.append(category)
    cards=[]
    for raw_entry in entries:
        e={**raw_entry};override=overrides['entries'].get(e['id'],{})
        if 'caption' in override and 'caption' in e:
            if e['caption']!=override['caption']['source']: raise ValueError('Reader text override no longer matches frozen caption')
            e['display_caption']=override['caption']['display']
        if e['category_id']=='G1':
            items=e.get('items',[])
            if not isinstance(items,list) or len(items)>3 or any(not isinstance(i,dict) or not isinstance(i.get('name'),str) or not isinstance(i.get('function'),str) for i in items): raise ValueError('Gear captions require at most three named items with functions')
        if 'items' in e:
            e['items']=[{**item} for item in e['items']]
            for item in e['items']:
                change=override.get('items',{}).get(item['name'])
                if change:
                    if item['function']!=change['source']: raise ValueError('Reader text override no longer matches frozen function')
                    item['display_function']=change['display']
        history=[]
        for raw in rows:
            if raw['id']!=e['id']: continue
            item=asset(raw);call_path=SOURCE/'calls'/f'{raw["attempt_id"]}.json';call=read(call_path,{})
            if call:
                if call.get('id',raw['id'])!=raw['id'] or call.get('attempt_id',raw['attempt_id'])!=raw['attempt_id']: raise ValueError('Call record belongs to another image')
                item.update(call_path=call_path.relative_to(ROOT).as_posix(),call_sha256=sha(call_path))
            for field in ['retry_of','retry_reason']:
                if raw.get(field) and call.get(field) and raw[field]!=call[field]: raise ValueError('Conflicting retry provenance')
            retry_of=call.get('retry_of') or raw.get('retry_of');reason=call.get('retry_reason') or raw.get('retry_reason')
            if retry_of or re.search(r'-R\d*$',raw['attempt_id']):
                before=attempts.get(retry_of)
                if not before or before['id']!=e['id'] or not isinstance(reason,str) or not reason.strip() or not call: raise ValueError('Retry needs a retained source attempt and exact correction call record')
                item.update(retry_of=retry_of,retry_reason=reason)
            history.append(item)
        cards.append({**e,'candidate':selected.get(e['id']),'history':history})
    notes_path=SOURCE/'review-notes.json';notes=read(notes_path)
    if notes:
        if notes.get('schema')!='WorldComponentReviewNotes/1' or notes.get('experiment_id')!=plan['experiment_id']: raise ValueError('Technical notes belong to another experiment')
        for id,note in notes.get('entries',{}).items():
            c=selected.get(id)
            if not c or note.get('attempt_id')!=c['attempt_id'] or note.get('sha256')!=c['sha256']: raise ValueError('Stale technical note source')
            if not isinstance(note.get('observations'),list) or any(not isinstance(t,str) for t in note['observations']): raise ValueError('Technical observations must be plain strings')
        cards=[{**e,'ai_observations':notes.get('entries',{}).get(e['id'],{}).get('observations',[])} for e in cards]
    if require_complete and len(selected)!=54: raise ValueError('Final reader requires all54 actual selected component images')
    bindings=[{'id':e['id'],'attempt_id':e['candidate']['attempt_id'] if e['candidate'] else None,'sha256':e['candidate']['sha256'] if e['candidate'] else None} for e in cards]
    identity={'experiment_id':plan['experiment_id'],'plan_sha256':sha(plan_path),'source_bindings':bindings}
    data={'schema':'WorldComponentReader/1',**identity,'dataset_sha256':hashlib.sha256(json.dumps(identity,sort_keys=True,separators=(',',':')).encode()).hexdigest(),'styles':plan['styles'],'categories':display_categories,'entries':cards,'references':references,'available_count':len(selected),'total_count':54,'owner_approval':None,'canon':None,'review_notes_sha256':sha(notes_path) if notes else None,'display_text_overrides_sha256':sha(DISPLAY_OVERRIDES),'report_links':[{'label':label,'path':f'../../research/world-components/{name}'} for name,label in [('START_HERE.md','Study details'),('RESULTS.md','Results & observations')] if (ROOT/f'research/world-components/{name}').exists()]}
    OUT.mkdir(parents=True,exist_ok=True);text=json.dumps(data,indent=2,ensure_ascii=False)
    (OUT/'data.json').write_text(text+'\n');(OUT/'data.js').write_text('window.WORLD_COMPONENT_DATA = '+text+';\n')
    return data
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--require-complete',action='store_true');a=p.parse_args();d=build(a.require_complete);print(json.dumps({'available':d['available_count'],'total':54,'dataset_sha256':d['dataset_sha256']}))
