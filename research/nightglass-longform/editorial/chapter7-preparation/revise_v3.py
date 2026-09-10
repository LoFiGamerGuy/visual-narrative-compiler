from pathlib import Path
import json,hashlib
r=Path(__file__).parent
d=json.loads((r/'chapter-7-draft-v2.json').read_text());p={x['id']:x for x in d['panels']}
p['N7-30']['action']='Daro returns ON FOOT up the ordinary market steps to Kiva’s awning, holding the small signed slip in his LEFT hand. His EMPTY cart remains parked on the fixed LOWER landing where it began. Aren rises beside the public bench, and Kiva looks up from her supported work.'
p['N7-30']['camera']='Wide return up the same pedestrian steps, peer and small receipt visible; lower cart can remain outside frame.'
p['N7-30']['current_state']='Actual result reaches Kiva after ordinary travel. Daro parked the empty cart below before climbing; it never climbs the market steps. ONE signed slip with Daro, box/hinges remain Rusk. Cart pad and strap stay on his lower-landing cart, not new cargo. No instant message or inferred success.'
p['N7-32']['action']='Kiva’s small coin pouch is already open on her bench. She places Daro’s agreed cart share into his waiting LEFT palm; his RIGHT hand is empty beside his coat.'
p['N7-34']['action']='After payment, Aren and Daro have walked down the ordinary market steps to the fixed LOWER landing beside Daro’s parked EMPTY cart. Aren turns to him before they part; the blue awning remains on the upper terrace behind them.'
p['N7-34']['current_state'] += ' Kiva already stored her signed receipt and kept working above. The cart remains below the steps throughout; no wheel ascent or relocation to the awning.'
p['N7-37']['action']='Aren and Daro stand beside the empty cart on the lower public landing before parting. Daro gestures toward this same meeting place; Kiva’s blue awning is visible above the ordinary steps.'
p['N7-37']['copy']=[{'speaker':'Aren','text':'We speak to the person there before either of us promises.'},{'speaker':'Daro','text':'Tomorrow after your round. Meet here.'}]
p['N7-37']['current_state']='Concrete Chapter8 task agreed by BOTH men: meet here after Aren’s tenth morning round, then visit the washhouse user to negotiate actual door and collection time. No qualification granted, inspection completed or new job accepted yet. Daro takes his own empty cart along the ramp; all entrusted Kiva cargo/board/receipt already settled.'
p['N7-40']['copy'][1]['text']='Yes. With the person who uses that door.'
p['N7-40']['current_state']='A request for an on-site conversation, not an approved new route or qualification. Tomorrow is tenth morning, still within paid week; visit AFTER Lower Post, before accepting first-bell collection. Daro and Aren already agreed the lower-landing meeting in37. Sera keeps her own ledger; LIGHTBLUE remains Office, GREEN Toma. No new danger or erased reward.'
d['status']='complete-provisional-v3-40-panel-draft-awaiting-lead-review-no-art'
(r/'chapter-7-draft-v3.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
lines=['# Chapter7 — A Place on the Round','','Complete provisional v3,40 story panels. V1 and v2 preserved. This manuscript is not an artwork, budget or owner-approval gate.','']
for q in d['panels']:
 lines += ['## '+q['id'],'',q['action'],'']
 lines += ['- **'+c['speaker']+'**: '+c['text'] for c in q['copy']] or ['*Silent.*']
 lines += ['', '**Camera:** '+q['camera'],'','**Current state:** '+q['current_state'],'']
(r/'chapter-7-draft-v3.md').write_text('\n'.join(lines))
rev={'reason':'Author self-review caught cart at upper awning on return despite step exclusion. Correct the actual route before independent lead review. Also explicitly agree peer availability before the closing proposed visit.','changed_panels':{'30':'Daro returns ON FOOT; cart stays lower landing','32':'No impossible upper-awning cart handle contact during pay','34':'Post-payment conversation at lower landing reached by ordinary steps','37':'Same lower landing; both men agree tomorrow after round','40':'Sera clearly agrees; prior Daro meeting authorization reflected'},'panel_count':40,'art_calls':0}
(r/'REVISION-v2-v3.json').write_text(json.dumps(rev,indent=2)+'\n')
for n in ['chapter-7-draft-v3.json','chapter-7-draft-v3.md']:
 f=r/n;print(n,hashlib.sha256(f.read_bytes()).hexdigest())
