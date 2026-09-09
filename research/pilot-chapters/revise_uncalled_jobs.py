"""Version unsubmitted inputs after observed first-panel continuity failures.
Original frozen plan and every v1 prompt/job remain untouched.
"""
from pathlib import Path
import hashlib,json,re
R=Path(__file__).resolve().parents[2];P=R/'production/pilot-chapters'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
dump=lambda p,x:p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
afile=R/'research/pilot-chapters/editorial/production-review/uncalled-state-amendments.json'
a=json.loads(afile.read_text());plan=json.loads((P/'plan.json').read_text());assert sha(P/'plan.json')==a['plan_sha256']
entries={e['id']:e for e in plan['entries']};chapters={c['id']:c for c in plan['chapters']}
(P/'job-revisions').mkdir(exist_ok=True);out=[];history=[]
for amendment in a['amendments']:
 ident=amendment['id'];aid=ident+'-P';old=P/'jobs'/(aid+'.json');j=json.loads(old.read_text());e=entries[ident];ch=chapters[e['chapter_id']]
 assert not (P/'calls'/(aid+'.json')).exists(),aid+' was called'
 assert sha(old)==amendment['original_job_sha256']
 assert sha(R/j['prompt_path'])==amendment['original_prompt_sha256']
 prompt=j['prompt'];cast={c['id']:c for c in ch['cast']}
 for cid,equipment in amendment['replace_visible_equipment_prose'].items():
  assert cid in e['cast_in_frame']
  pattern=r'('+re.escape(cast[cid]['name'])+r': [^\n]* Equipment: )[^\n]*'
  prompt,n=re.subn(pattern,lambda m:m[1]+equipment,prompt)
  assert n==1,(ident,cid,n)
 visible=', '.join(cast[c]['name'] for c in e['cast_in_frame']) or 'No principal character'
 absent=', '.join(c['name'] for c in ch['cast'] if c['id'] not in e['cast_in_frame'])
 guard=f'INVENTORY CONTINUITY — This is state information, not a request to add people. Only {visible} may appear physically, with the stated crop. '
 if absent:guard+=f'Keep {absent} physically OUTSIDE this frame even if named in possession history. '
 guard+='The existing action, camera and explicit nonphysical special elements control what is visible.\n'
 inventory=amendment['append_authoritative_current_inventory']
 ending='\n'+guard+inventory+'\nCOMPOSITION FOR EDITABLE DIALOGUE: '+amendment['speaker_blocking_recommendation']+'\nFINAL SHOT PRIORITY: '+e['camera']+' Depict only this instant: '+e['action']+' No added text or panel division.\n'
 prompt=prompt.rstrip()+ending
 pp=P/'prompts'/(aid+'-input-v2.txt');jp=P/'job-revisions'/(aid+'-v2.json');assert not pp.exists() and not jp.exists();pp.write_text(prompt)
 jj={**j,'prompt':prompt,'prompt_path':str(pp.relative_to(R)),'prompt_sha256':sha(pp),'input_revision':2,'supersedes_unsubmitted_job_path':str(old.relative_to(R)),'supersedes_unsubmitted_job_sha256':sha(old),'amendments_path':str(afile.relative_to(R)),'amendments_sha256':sha(afile)}
 dump(jp,jj);out.append(jj);history.append({'id':ident,'attempt_id':aid,'original_job_path':str(old.relative_to(R)),'original_job_sha256':sha(old),'submitted_job_path':str(jp.relative_to(R)),'submitted_job_sha256':sha(jp),'reason':'Six actual test panels exposed recurring inventory/prop-state conflicts. No extra artwork called; revise only unsubmitted input.'})
assert len(out)==74
op=P/'jobs-remaining-v2.json';assert not op.exists();dump(op,out)
dump(P/'input-revisions.json',{'schema':'PilotInputRevisions/1','entries':history,'original_plan_unchanged':sha(P/'plan.json'),'artwork_regenerations_for_revision':0})
print(json.dumps({'jobs':len(out),'path':str(op.relative_to(R)),'amendments_sha256':sha(afile)}))
