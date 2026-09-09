from pathlib import Path
import json,hashlib,sys
R=Path(__file__).resolve().parents[2];P=R/'production/anchor-return';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
spec=json.loads(Path(sys.argv[1]).read_text());cs={x['attempt_id']:x for x in json.loads((P/'candidates.json').read_text())['candidates']};plan=json.loads((P/'plan.json').read_text());jobs=[]
for e in spec:
 c=cs[e['source_attempt_id']];ident=c['id'];aid=e['attempt_id'];phase=e['phase'];assert phase in ['repair','texture'];assert not (P/'jobs'/(aid+'.json')).exists()
 pp=P/'prompts'/(aid+'.txt');pp.write_text(e['prompt'].rstrip()+'\n')
 j=dict(id=ident,attempt_id=aid,phase=phase,category=next(x['category'] for x in plan['entries']+plan['support_entries'] if x['id']==ident),retry_of=c['attempt_id'],retry_reason=e['reason'],evidence_path=sys.argv[1],evidence_sha256=sha(Path(sys.argv[1])),prompt=pp.read_text(),prompt_path=str(pp.relative_to(R)),prompt_sha256=sha(pp),plan_sha256=sha(P/'plan.json'),references=[dict(path=c['path'],sha256=c['sha256'],role='Sole source edit target; preserve all protected features named in prompt.')])
 (P/'jobs'/(aid+'.json')).write_text(json.dumps(j,indent=2)+'\n');jobs.append(j)
print(json.dumps(jobs))
