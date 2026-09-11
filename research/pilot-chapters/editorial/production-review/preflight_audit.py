from pathlib import Path
import json,hashlib,datetime
R=Path(__file__).resolve().parents[4]
OUT=Path(__file__).parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=R/'production/pilot-chapters/plan.json';plan=json.loads(p.read_text())
chapters={cid:json.loads((R/f'research/pilot-chapters/editorial/{cid}.json').read_text()) for cid in ['NG','BP','ST','RC','FL']}
records=[]
for e in plan['entries']:
 b=next(x for x in chapters[e['chapter_id']]['beats'] if x['id']==e['id'])
 mismatches=[k for k,v in b.items() if e.get(k)!=v]
 exact_copy=[(x['speaker'],x['text']) for x in e['lettering']]==[(x['speaker'],x['text']) for x in b['copy']]
 assert not mismatches and exact_copy
 records.append({'id':e['id'],'all_editorial_fields_equal':True,'lettering_speaker_and_text_exact':True})
d={'schema':'PilotEditorialProductionPreflight/1','reviewer':'editorial-author-not-blind-independent','reviewed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'plan_path':str(p.relative_to(R)),'plan_sha256':sha(p),'script_manifest_sha256':sha(R/'research/pilot-chapters/editorial/script-manifest.json'),'records':records,'specific_checks':['NG04 Sera, RC11 Vexa and FL11 Ada are explicitly lettered off panel.','BP02 public lettering attribution is Voice, inside; internal Oren/Bloom metadata is not public copy.','FL05 Lio is an explicit pool-imprint special element, not present physical cast.','FL15 includes Lio partial forearm/hand visibility in frozen data.','Panel text compiler omits whole global power_rule, preventing early RC debt-mark prose from it.'],'compiler_watchlist_at_audit':[{'severity':'material-before-panel-calls','issue':'prepare_jobs.py does not feed cast_visibility into prompts, omitting FL15 partial-hand and FL09–11 mouth-only restrictions.','reported_to_root':True},{'severity':'material-before-panel-calls','issue':'visible cast equipment descriptions carry initial-only uninjured/unmarked assertions into later states, especially RC13–16. Strip such assertions from panel cast text and retain current_state.','reported_to_root':True}],'limitations':'No panel prompts existed yet at audit; compiler watchlist is code inspection, not evidence of a generated failure. Native and actual reader checks are pending.'}
(OUT/'plan-vs-script-audit.json').write_text(json.dumps(d,indent=2)+'\n')
