from pathlib import Path
import json,hashlib
r=Path(__file__).parent
before=json.loads((r/'chapter-7-draft-v3.json').read_text())
d=json.loads(json.dumps(before));p={x['id']:x for x in d['panels']}
p['N7-22']['current_state']='Same established Rusk: stocky, dark curly hair graying at the temples, short salt-and-pepper beard, mustard shirt and BLUE work apron; not a new recipient. Rear approach is ordinary workshop geography, no new permit. Rusk is present, so agreed return contingency is not triggered. Humans and cart supported.'
p['N7-35']['current_state']='Daro owns this prospective PICKUP/collection request and notebook. It is not accepted on Aren’s behalf and is not sealed private correspondence. East washhouse is a future place, no new recurring person appears in7. No route access, pickup door or collection time has been agreed; cargo kind and volume remain unagreed until8.'
p['N7-36']['copy'][1]['text']='And I have not walked the collection door they marked.'
p['N7-36']['camera']='Two independent limits: existing duty and unknown actual pickup approach.'
p['N7-36']['current_state']='Aren will not cancel Lower Post or promise simultaneous jobs. Unknown PICKUP door is an honest lack of observation, not a declared unsafe/closed district or a delivery destination. Existing registered Ilen/Kiva routes remain valid. Cargo kind and volume remain unagreed. No urgent deadline or manufactured disaster.'
p['N7-37']['copy'][0]['text']='We speak to the person handing goods over before either of us promises.'
p['N7-37']['current_state']='Concrete Chapter8 task agreed by BOTH men: meet here after Aren’s tenth morning round, then visit the person handing goods over at the washhouse to negotiate the PICKUP door and collection time. Cargo kind and volume remain unagreed until8. No qualification granted, inspection completed or new job accepted yet. Daro takes his own empty cart along the ramp; all entrusted Kiva cargo/board/receipt already settled.'
p['N7-40']['copy'][1]['text']='Yes. With the person handing the goods over.'
p['N7-40']['current_state']='A request for an on-site PICKUP conversation, not an approved new route or qualification. Tomorrow is tenth morning, still within paid week; visit AFTER Lower Post, before accepting first-bell collection. They will speak to the person handing goods over; cargo kind and volume remain unagreed until8. Daro and Aren already agreed the lower-landing meeting in37. Sera keeps her own ledger; LIGHTBLUE remains Office, GREEN Toma. No new danger or erased reward.'
d['status']='complete-provisional-v4-40-panel-draft-awaiting-lead-review-no-art'
(r/'chapter-7-draft-v4.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
lines=['# Chapter7 — A Place on the Round','','Complete provisional v4,40 story panels. V1, v2 and v3 preserved. V4 only clarifies existing Rusk identity and the prospective washhouse pickup. This manuscript is not an artwork, budget or owner-approval gate.','']
for q in d['panels']:
 lines += ['## '+q['id'],'',q['action'],'']
 lines += ['- **'+c['speaker']+'**: '+c['text'] for c in q['copy']] or ['*Silent.*']
 lines += ['', '**Camera:** '+q['camera'],'','**Current state:** '+q['current_state'],'']
(r/'chapter-7-draft-v4.md').write_text('\n'.join(lines))
state=(r/'STATE-AND-ROUTE-v3.md').read_text()
state=state.replace('# Chapter7 v3 —','# Chapter7 v4 —').replace('chapter-7-draft-v3.json/.md','chapter-7-draft-v4.json/.md')
state=state.replace('V1(43panels) and v2(40panels) remain unchanged; both revision maps explain the edits.','V1(43panels), v2(40panels) and v3(40panels) remain unchanged; revision receipts explain each bounded change.')
state=state.replace('V3\'s shorthand “gray hair/stubble/dark apron” in22 means this existing actor, not a new all-gray-haired design.','V4 places this exact established identity directly in panel22; no shorthand override is needed.')
state=state.replace('not an already certified contiguous cart route.','not an already certified contiguous cart route.')
state=state.replace('specific unaccepted washhouse request, agreed visit after next round','specific unaccepted washhouse PICKUP request, agreed visit after next round')
state=state.replace('Chapter8 uncertainty is whether the actual washhouse user/door/time can fit first-bell request and Aren\'s morning obligation; visit accepted, collection NOT accepted.','Chapter8 uncertainty concerns a prospective PICKUP/collection door and time, not a delivery or receiving destination. The visit speaks to the person handing goods over; cargo kind and volume remain unagreed until8. The requested first-bell timing must be considered alongside Aren\'s existing morning obligation. Visit accepted, collection NOT accepted.')
(r/'STATE-AND-ROUTE-v4.md').write_text(state)
diff=[]
for a,b in zip(before['panels'],d['panels']):
 for k in a:
  if a[k]!=b[k]:diff.append({'panel':a['id'],'field':k,'before':a[k],'after':b[k]})
assert {x['panel'] for x in diff}=={'N7-22','N7-35','N7-36','N7-37','N7-40'}
assert all(a['action']==b['action'] for a,b in zip(before['panels'],d['panels']))
assert len(d['panels'])==40
md=(r/'chapter-7-draft-v4.md').read_text()
assert all(q['action'] in md and q['camera'] in md and q['current_state'] in md for q in d['panels'])
assert all(c['text'] in md for q in d['panels'] for c in q['copy'])
assert [q['id'] for q in d['panels']]==[f'N7-{i:02d}' for i in range(1,41)]
receipt={'reason':'Requested exact existing Rusk identity and prospective washhouse pickup clarity only.','story_panel_count':40,'unchanged_actions':True,'unchanged_panels':35,'metadata_change':'status v3 to v4 only','changes':diff,'json_md_exact_action_copy_camera_state_pass':True,'image_calls':0,'included_source_mutations':False,'hashes':{n:hashlib.sha256((r/n).read_bytes()).hexdigest() for n in ['chapter-7-draft-v3.json','chapter-7-draft-v3.md','chapter-7-draft-v4.json','chapter-7-draft-v4.md','STATE-AND-ROUTE-v3.md','STATE-AND-ROUTE-v4.md']}}
(r/'REVISION-v3-v4.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'panel_count':40,'changed_fields':[(x['panel'],x['field']) for x in diff],'hashes':receipt['hashes'],'validation':'PASS'},indent=2))
