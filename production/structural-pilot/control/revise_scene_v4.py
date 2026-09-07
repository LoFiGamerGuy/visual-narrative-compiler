"""Expose the staff and tighten action cameras after actual v3 inspection."""
import json
from pathlib import Path
root=Path(__file__).resolve().parent
data=json.loads((root/'v3'/'scene.json').read_text())
data['revision']='v4: exposed two-hand staff brace; tighter P11/P13; opaque ivory backgrounds'
p=data['panels']
for key in ['P08','P09','P10']:
 p[key]['staff']['segments'][0][0]=[2.48,-.40,1.05]
 a,b=p[key]['staff']['segments'][0]
 for side,t in [('left',.44),('right',.70)]:
  if key=='P10' and side=='right':continue
  p[key]['nera']['joints'][side+'_hand']=[a[i]+t*(b[i]-a[i]) for i in range(3)]
 p[key]['nera']['joints']['left_elbow']=[2.87,-.27,.93]
 if key!='P10':p[key]['nera']['joints']['right_elbow']=[3.36,-.65,.83]
p['P11']['camera']={'location':[1.3,-9.4,4.2],'target':[4.5,.10,1.95],'ortho':5.5,'type':'PERSP','lens':60}
p['P13']['camera']['lens']=54
(root/'v4').mkdir(exist_ok=True)
(root/'v4'/'scene.json').write_text(json.dumps(data,indent=2)+'\n')
