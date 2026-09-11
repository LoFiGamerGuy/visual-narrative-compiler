"""Remove the remaining P11 projected boot/kite-apex tangent. Other poses unchanged."""
import json
from pathlib import Path
root=Path(__file__).resolve().parent
data=json.loads((root/'v5'/'scene.json').read_text())
data['revision']='v6: P11-only additional 0.35 m vault clearance; other poses remain v5'
p=data['panels']['P11']
for v in p['nera']['joints'].values():v[2]+=.35
for seg in p['staff']['segments']:
 for v in seg:v[2]+=.35
for fx in p['effects']:
 if fx['id'] in ['air_brake_arrival','east_redirect']:
  for v in fx['points']:v[2]+=.35
p['air_brake_height_offset']+=.35
(root/'v6').mkdir(exist_ok=True)
(root/'v6'/'scene.json').write_text(json.dumps(data,indent=2)+'\n')
