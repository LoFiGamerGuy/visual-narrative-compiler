"""Project independently reviewed observations onto the actually displayed image."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[2];P=R/'production/world-components';V=R/'research/world-components/independent-review'
def read(p):return json.loads(p.read_text())
primary=read(V/'findings.json')['entries']
repairs=read(V/'retry-findings.json')['entries'] if (V/'retry-findings.json').exists() else {}
selected=read(P/'selected.json')['selected'];candidates={x['attempt_id']:x for x in read(P/'candidates.json')['candidates']};entries={}
for id,aid in selected.items():
 findings=repairs.get(id) if aid.endswith('-R') else primary.get(id)
 assert findings and findings['attempt_id']==aid and findings['sha256']==candidates[aid]['sha256'],'Missing or stale selected-image review: '+id
 assert findings['observations'] and all(isinstance(x,str) for x in findings['observations'])
 entries[id]={k:findings[k] for k in ['attempt_id','sha256','observations']}
assert len(entries)==54
out={'schema':'WorldComponentReviewNotes/1','experiment_id':'WC-20260907-01','owner_approval':None,'entries':entries,'source_findings_sha256':hashlib.sha256((V/'findings.json').read_bytes()).hexdigest(),'retry_findings_sha256':hashlib.sha256((V/'retry-findings.json').read_bytes()).hexdigest() if repairs else None}
(P/'review-notes.json').write_text(json.dumps(out,indent=2)+'\n');print('Bound54 displayed-image review notes.')
