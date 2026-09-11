from pathlib import Path
import json,hashlib
r=Path(__file__).parent
d=json.loads((r/'chapter-7-draft-v1.json').read_text())
old={p['id']:p for p in d['panels']}
old['N7-04']['current_state'] += ' This modest set was already in preparation alongside the commission; the short interval does not manufacture the whole larger order from scratch.'
old['N7-06']['action']='Daro and Aren have stepped to the clear edge of Kiva’s awning to look toward the ordinary market steps; Kiva remains within conversational reach at her bench. Daro keeps the folded pad under his arm.'
old['N7-06']['copy']=[{'speaker':'Daro','text':'Rusk asked for the rear yard today. His long frame is in the front aisle.'},{'speaker':'Daro','text':'You bring the box to the landing. I take the cart leg; her board comes back with you.'}]
old['N7-06']['current_state'] += ' The returned board supports Kiva’s next pin-fitting work, as visibly demonstrated later. The old broken public span stays CLOSED; neither man uses it. This is Daro’s firsthand route knowledge, not a claim Sera inspected this new rear approach in Chapter2.'
old['N7-07']['current_state'] += ' Ramp continues by ordinary connected paving to Rusk’s rear lane; no cart wheels on stairs, no mail-only lift, no direct Kiva-to-Rusk elevator. Closed old broken span is not on this route.'
old['N7-10']['copy']=[{'speaker':'Kiva','text':'Aren collects. Daro may carry it from the landing to Rusk.'},{'speaker':'Kiva','text':'If he cannot receive it, bring it back. No doorstep drop.'}]
old['N7-12']['action']='Kiva closes the lined fitted box, with the modest hinge set already inside, and fastens its two simple catches. ONE small blank cream delivery slip is already tucked under the exterior retaining loop; the carrying board is flat beneath the box.'
old['N7-28']['action']='Rusk has signed the ONE small cream delivery slip on the supported box lid. His RIGHT hand now passes that signed slip into Daro’s LEFT hand over the bench. The open hinge box remains on Rusk’s side; the empty cart is beside Daro.'
old['N7-28']['current_state'] += ' Signature occurs ordinarily between recipient inspection and this handoff; no separate pen-insert panel or claim that the signature magically appears.'
old['N7-33']['action']='Daro has returned and parked his EMPTY cart on the public paving beside the awning. He holds the small signed slip in his LEFT hand, RIGHT hand empty at his side. Aren rises beside the bench, and Kiva looks up from her supported work; the ramp he used is visible behind him.'
old['N7-36']['current_state']=old['N7-36']['current_state'].replace('before37','before the next conversation')
removed={'N7-08','N7-09','N7-27'}
new=[];mapping=[]
for p in d['panels']:
 if p['id'] in removed:continue
 before=p['id'];p['id']=f'N7-{len(new)+1:02d}';mapping.append({'v1':before,'v2':p['id']});new.append(p)
d['panels']=new
d['status']='complete-provisional-v2-40-panel-draft-awaiting-lead-review-no-art'
assert len(new)==40
(r/'chapter-7-draft-v2.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
lines=['# Chapter7 — A Place on the Round','','Complete provisional v2,40 story panels. V1 preserved. This manuscript is not an artwork, budget or owner-approval gate.','']
for p in new:
 lines += ['## '+p['id'],'',p['action'],'']
 lines += ['- **'+c['speaker']+'**: '+c['text'] for c in p['copy']] or ['*Silent.*']
 lines += ['', '**Camera:** '+p['camera'],'','**Current state:** '+p['current_state'],'']
(r/'chapter-7-draft-v2.md').write_text('\n'.join(lines))
revision={'reason':'Reduce bench terms and repeated record inserts before lead review; preserve complete original43-panel draft.','removed_v1':['08 shape comparison (flat fitted load already apparent)','09 separate plan discussion (plan folded into actual06 geography conversation; returned board value demonstrated later)','27 pen-only receipt insert (ordinary signing happens before actual28 handoff)'],'other_changes':['06 conversation moves to awning edge looking at actual route; plan and broken-span exclusion explicit','10 consent copy tightened, same custody/contingency','12 board settled before packing moment','28 receipt already signed before single transfer','33 cart already parked before receipt display','04 modest local set already in progress; no overnight major commission'],'panel_map':mapping}
(r/'REVISION-v1-v2.json').write_text(json.dumps(revision,indent=2)+'\n')
for n in ['chapter-7-draft-v2.json','chapter-7-draft-v2.md']:
 p=r/n;print(n,hashlib.sha256(p.read_bytes()).hexdigest())
