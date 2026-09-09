from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[2];P=R/'production/pilot-chapters';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();cf=R/'research/pilot-chapters/editorial/production-review/state-corrections-v1.json';corr=json.loads(cf.read_text());jobs={j['id']:j for j in json.loads((P/'jobs-remaining-v3.json').read_text())};out=[]
for e in corr['corrections']:
 j=jobs[e['id']];call=P/'calls'/(j['attempt_id']+'.json')
 if call.exists():assert json.loads(call.read_text()).get('tool_invoked') is False,e['id']+' already invoked'
 assert sha(R/e['original_prompt_path'])==e['original_prompt_sha256'];prompt=j['prompt']
 for rep in e['exact_replacements']:assert prompt.count(rep['find'])==1;prompt=prompt.replace(rep['find'],rep['replace'])
 pp=P/'prompts'/(j['attempt_id']+'-input-v4.txt');jp=P/'job-revisions'/(j['attempt_id']+'-v4.json');assert not pp.exists() and not jp.exists();pp.write_text(prompt)
 old=P/'job-revisions'/(j['attempt_id']+'-v3.json');z={**j,'prompt':prompt,'prompt_path':str(pp.relative_to(R)),'prompt_sha256':sha(pp),'input_revision':4,'supersedes_unsubmitted_job_path':str(old.relative_to(R)),'supersedes_unsubmitted_job_sha256':sha(old),'state_correction_path':str(cf.relative_to(R)),'state_correction_sha256':sha(cf)};jp.write_text(json.dumps(z,indent=2)+'\n');jobs[e['id']]=z;out.append(z)
(P/'jobs-corrected-v4.json').write_text(json.dumps(out,indent=2)+'\n');(P/'jobs-remaining-current.json').write_text(json.dumps(list(jobs.values()),indent=2)+'\n');print(json.dumps({'corrected':len(out),'total_current':len(jobs)}))
