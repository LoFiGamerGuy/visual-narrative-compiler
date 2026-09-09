from pathlib import Path
import json,hashlib,datetime
R=Path(__file__).resolve().parents[4];O=Path(__file__).parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
plan=json.loads((R/'production/pilot-chapters/plan.json').read_text());am=json.loads((O/'uncalled-state-amendments.json').read_text());rows=[]
for a in am['amendments']:
 i=a['id'];edits=[]
 if i in ['FL04','FL06']:
  edits.append({'find':'Ada and Lio remain outside this assigned close framing; no extra people or silhouettes.','replace':'Ada remains physically present as the current medium-shot action specifies. No Lio body, eel or additional people.'})
  edits.append({'find':'LEFT bare fingertips perform memory touch.','replace':'LEFT glove has just been removed; no water touch or memory imprint yet.' if i=='FL04' else 'Bare LEFT hand is withdrawing from the fully erased pool; black-gloved RIGHT hand catches Ada’s elbow.'})
 if i in ['NG15','NG16']:edits.append({'find':'both hands free unless handling wallet.','replace':'hand use follows the current action; the black envelope is distinct from the cream wallet.'})
 e=next(e for e in plan['entries'] if e['id']==i)
 if e['chapter_id']=='FL' and e['sequence_order']>=3 and 'ada' in e['cast_in_frame']:
  edits.append({'find':'Equipment: Her missing brother’s dark work coat folded over one arm.','replace':'Equipment: The wet dark work coat is discarded on the ledge, not draped on Ada’s arm. Her hands follow the present action and are free for the rescue. Do not duplicate this coat.'})
 if edits:
  p=R/f'production/pilot-chapters/prompts/{i}-P-input-v3.txt';t=p.read_text()
  for z in edits:assert t.count(z['find'])==1,(i,z['find'],t.count(z['find']))
  rows.append({'id':i,'original_prompt_path':str(p.relative_to(R)),'original_prompt_sha256':sha(p),'exact_replacements':edits})
obj={'schema':'PilotEditorialPromptCorrections/1','created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'frozen_plan_sha256':sha(R/'production/pilot-chapters/plan.json'),'original_amendment_sha256':sha(O/'uncalled-state-amendments.json'),'scope':'Preserve v1/v2/v3 and original amendment. Apply by new input revision only when primary has not been called. No script/copy/story changes. Exact replacements each occur once in bound v3 prompt.','corrections':rows}
p=O/'state-corrections-v1.json';p.write_text(json.dumps(obj,indent=2)+'\n');print('corrections',len(rows),'sha',sha(p))
# Every record makes coverage and cast/action review explicit without claiming source generation correctness.
audit=[]
for a in am['amendments']:
 e=next(e for e in plan['entries'] if e['id']==a['id']);p=R/f"production/pilot-chapters/prompts/{a['id']}-P-input-v3.txt"
 audit.append({'id':a['id'],'cast_in_frame':e['cast_in_frame'],'cast_visibility':e.get('cast_visibility',{}),'action':e['action'],'current_state':e['current_state'],'v3_prompt_sha256':sha(p),'amendment_inventory_sha256':hashlib.sha256(a['append_authoritative_current_inventory'].encode()).hexdigest(),'review_result':'correction identified; see exact corrections' if any(r['id']==a['id'] for r in rows) else 'No additional material inventory/cast/action contradiction identified in this editorial pass; actual artwork still requires review.'})
x={'schema':'PilotEditorialAllPanelStateAudit/1','created_at':obj['created_at'],'plan_sha256':obj['frozen_plan_sha256'],'amendment_sha256':obj['original_amendment_sha256'],'corrections_path':str(p),'corrections_sha256':sha(O/'state-corrections-v1.json'),'reviewed_ids':len(audit),'scope':'All 74 uncalled-template cast/current-state/action combinations reviewed; original amendment retained unchanged. This is implementation review, not art approval.','panels':audit}
x['corrections_path']='research/pilot-chapters/editorial/production-review/state-corrections-v1.json'
p=O/'all-74-state-audit.json';p.write_text(json.dumps(x,indent=2)+'\n');print('audit',sha(p))
