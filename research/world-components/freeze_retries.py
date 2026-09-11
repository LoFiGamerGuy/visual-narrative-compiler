"""Freeze one targeted edit for each evidence-justified repair selection."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[2];P=R/'production/world-components'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
plan=json.loads((P/'repair-plan.json').read_text());rows=plan['repairs'];assert 0<len(rows)<=9 and len({r['id'] for r in rows})==len(rows)
assert len(list((P/'calls').glob('*.json')))==54,'Freeze repairs only after all54 primaries and before any repair call'
jobs=[]
for r in rows:
 id=r['id'];aid=id+'-R';refs=[P/'candidates'/(id+'-P.png'),P/'references'/(id[:2]+'.png')]
 if r.get('extra_reference'):refs.append(R/r['extra_reference'])
 prompt='Use case: precise-object-edit\nAsset type: targeted repair of original story-component concept art.\nInput roles: Image1 is the actual edit target. Image2 is the original drawing-treatment reference for preserving its visual language only. Do not import Image2\'s people, creatures, composition or scenery.\nRequired correction: '+r['edit']+'\nPreserve: '+r['preserve']+'\nConstraints: exactly one finished image, no before/after layout, labels, text, lettering, signature or watermark. Keep the same original design and rendering except for the named concrete correction; no new ornaments, props or scene inventory. Whole subject and essential parts remain within frame with clear outer margins.\n'
 if len(refs)==3:prompt+='Image3 is the actual G1 gear card. Use ONLY its transverse cork-headed mallet as the correct tool-geometry reference; do not add its other two tools or copy its card layout.\n'
 pp=P/'prompts'/(aid+'.txt');assert not pp.exists();pp.write_text(prompt)
 jobs.append({'id':id,'attempt_id':aid,'phase':'targeted-repairs','retry_of':id+'-P','retry_reason':r['reason'],'prompt_path':pp.relative_to(R).as_posix(),'prompt_sha256':sha(pp),'references':[{'path':p.relative_to(R).as_posix(),'sha256':sha(p)} for p in refs]})
out=P/'targeted-repairs-jobs.json';assert not out.exists();out.write_text(json.dumps({'schema':'WorldComponentJobs/1','experiment_id':'WC-20260907-01','repair_plan_sha256':sha(P/'repair-plan.json'),'jobs':jobs},indent=2)+'\n');out.with_suffix('.json.sha256').write_text(sha(out)+'  '+out.relative_to(R).as_posix()+'\n');print('Frozen'+str(len(jobs))+' targeted repair calls.')
