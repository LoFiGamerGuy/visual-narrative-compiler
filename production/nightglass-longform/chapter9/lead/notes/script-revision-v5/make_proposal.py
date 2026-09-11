from pathlib import Path
import json, hashlib, copy, datetime
B=Path.cwd(); O=B/'production/nightglass-longform/chapter9/lead/notes/script-revision-v5'; S=B/'production/nightglass-longform/scripts'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p, data):
    assert not p.exists(),str(p)
    p.write_bytes(data if isinstance(data,bytes) else data.encode())
original={}
for ext in ['json','md']:
    src=S/f'chapter-9.{ext}'; dest=O/f'before-v5-chapter-9.{ext}'
    save(dest,src.read_bytes()); original[str(src.relative_to(B))]=sha(src)
src=S/'chapter-9-state-route.md'; save(O/'before-v5-chapter-9-state-route.md',src.read_bytes()); original[str(src.relative_to(B))]=sha(src)
a=json.loads((O/'before-v5-chapter-9.json').read_text()); b=copy.deepcopy(a)
p7,p8=b['panels'][6:8]
p7['action']='With Aren’s EMPTY gray bag already open on the bench and harness fully OFF his shoulders, Neris’s RIGHT bare hand passes the one tied amber pouch into his RIGHT glove. His LEFT glove rests on the empty bag rim.'
p7['current_state']=p7['current_state'].replace('ONE amber/black-tied pouch Neris→Aren.','ONE amber/black-tied pouch NerisRIGHT→ArenRIGHT; his LEFT glove steadies the empty bag rim.')
p8['action']='Aren lowers the ONE tied amber pouch into the open gray bag with his RIGHT glove while his LEFT steadies the rim. Neris’s empty hands are clear of the opening.'
p8['current_state']=p8['current_state'].replace('LEFT glove places pouch, RIGHT steadies rim.','RIGHT glove places pouch, LEFT steadies rim.')
deltas=[]
for i,(x,y) in enumerate(zip(a['panels'],b['panels']),1):
    for k in x:
        if x[k]!=y[k]: deltas.append({'panel':i,'field':k,'before':x[k],'after':y[k]})
assert {(d['panel'],d['field']) for d in deltas}=={(7,'action'),(7,'current_state'),(8,'action'),(8,'current_state')}
assert {k:v for k,v in a.items() if k!='panels'}=={k:v for k,v in b.items() if k!='panels'}
assert all(x['copy']==y['copy'] for x,y in zip(a['panels'],b['panels']))
assert sum(len(p['copy']) for p in b['panels'])==34
assert len(b['panels'])==42
md=(O/'before-v5-chapter-9.md').read_text()
for d in deltas:
    assert md.count(d['before'])==1
    md=md.replace(d['before'],d['after'])
# Match every story field against its own full MD panel section.
for i,p in enumerate(b['panels'],1):
    section=md.split(f'## N9-{i:02d}\n',1)[1].split('\n## N9-',1)[0]
    for k in ['action','camera','current_state']: assert p[k] in section,(i,k)
    for line in p['copy']:
        # Exact serialized copy objects are invariant; rendered source text stays untouched.
        for k,v in line.items():
            if k=='text': assert v in section,(i,v)
save(O/'chapter-9-v5-proposed.json',json.dumps(b,ensure_ascii=False,indent=2)+'\n')
save(O/'chapter-9-v5-proposed.md',md)
st=(O/'before-v5-chapter-9-state-route.md').read_text()
st=st.replace('07 NerisRIGHT→ArenLEFT over dry bench, RIGHT glove at empty bag rim.','07 NerisRIGHT→ArenRIGHT over dry bench, LEFT glove at empty bag rim.')
st=st.replace('08 amber pouch goes inside.','08 RIGHT glove places the amber pouch inside while LEFT steadies the rim.')
save(O/'chapter-9-state-route-v5-proposed.md',st)
notes='''# Chapter9 v5 proposed ordinary packing staging

Independent actual whole-native review of both N9-07-08-P and its sole R1: the primary shows Neris RIGHT bare hand→Aren RIGHT receiving glove, with Aren LEFT on the empty bag rim. The original lower tier continues with that same RIGHT glove placing the ONE closed amber/black-tied pouch into the same supported open bag. Neris’s other hand rests on the bench; Sera retains her closed brown ledger. Harness is off Aren and lies with the bag. Current near LEFT upper-sleeve tear and intact other sleeve are readable in the upper frame; no contradictory weapon or second load appears. Lower close framing does not prove feet or every waist fitting.

The repair did not achieve the requested pair: upper07 still uses RIGHT, while lower08 switches to LEFT. Do not call that a successful hand-role repair. Recommend BOTH ORIGINAL PRIMARY tiers under this explicit proposal. Both complete native attempts remain preserved; no image crop or selection is created by this manuscript proposal.

This is ordinary packing with no action or skill restriction tied to the receiving hand. The pouch remains closed and unique; authorization and custody occur in the same order. Bag closure/refitting follows before09, and this does not constrain the later20 unpacking hand. No extra event, hidden hand switch or force capability is needed to use both primary tiers.

Exactly four JSON fields change:07/08 action and current_state. All42 beats,34 exact editable copy entries, both cameras, all other40 panel objects, reuse values and every top-level field—including status and reading_premise—are unchanged. Matching MD is produced by those same four literal substitutions; its existing header remains unchanged. Compact state proposal changes only the07/08 custody sentences. Filename/this note identify these as UNPROMOTED proposals; retained v4 headers are historical, not a gate claim.

The original07–08 unit has spent ONE primary and its sole R1. Both remain counted and preserved. This proposal authorizes no new call, reset, source finish or shared selection. Root must independently review and promote before using the revised staging. No official script, state, gate, reader or shared selected files changed; no image generation invoked.
'''
save(O/'REVISION-REVIEW.md',notes)
art={}
for n in ['N9-07-08-P.png','N9-07-08-R1.png']:
    p=B/'production/nightglass-longform/chapter9/lead/candidates'/n
    art[str(p.relative_to(B))]=sha(p)
receipt={'kind':'unpromoted Chapter9 v5 ordinary-packing proposal','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_sha256':original,'actual_whole_natives_inspected':art,'recommended_source_for_07_and_08':'N9-07-08-P.png','repair_result':'07 hand role still RIGHT;08 switched LEFT; not accepted as consistent requested repair','deltas':deltas,'validation':{'panels':42,'copy_entries':34,'copy_unchanged':True,'other_40_panel_objects_exact':True,'all_top_level_fields_exact':True,'json_md_all_action_camera_state_and_copy_text_match':True,'md_only_four_literal_field_substitutions':True,'official_source_bytes_unchanged':all(sha(B/p)==h for p,h in original.items()),'new_image_calls':0,'original_unit_calls_spent':2,'cap_reset':False},'files':{p.name:sha(p) for p in sorted(O.iterdir()) if p.is_file()}}
save(O/'V5-DIFF-AND-PRESERVATION-RECEIPT.json',json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'proposal_sha256':sha(O/'chapter-9-v5-proposed.json'),'md_sha256':sha(O/'chapter-9-v5-proposed.md'),'state_sha256':sha(O/'chapter-9-state-route-v5-proposed.md'),'receipt_sha256':sha(O/'V5-DIFF-AND-PRESERVATION-RECEIPT.json'),'validation':receipt['validation'],'art':art},indent=2))
