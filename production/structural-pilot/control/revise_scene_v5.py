"""Final source-control correction before the lead's first generated layer tests."""
import json
from pathlib import Path
root=Path(__file__).resolve().parent
data=json.loads((root/'v4'/'scene.json').read_text())
data['revision']='v5: exposed ridge-edge anchor/grips; airborne negative space; visible east-side remnant; complete P11 Odo silhouette'
p=data['panels'];anchor=[3.9,-.45,.26]
for key in ['P08','P09','P10','P11']:
 p[key]['foot_anchor']=anchor
 p[key]['sentinel']['limbs']['foreleg'][-1]=anchor
for key in ['P08','P09','P10']:
 p[key]['staff']['segments'][0]=[[2.5,-.95,1.05],anchor]
 p[key]['contact']['point']=anchor
 a,b=p[key]['staff']['segments'][0]
 for side,t in [('left',.30),('right',.70)]:
  if key=='P10' and side=='right':continue
  p[key]['nera']['joints'][side+'_hand']=[a[i]+t*(b[i]-a[i]) for i in range(3)]
 p[key]['nera']['joints']['left_elbow']=[2.84,-.45,1.05]
 if key!='P10':p[key]['nera']['joints']['right_elbow']=[3.36,-.85,.83]
for v in p['P11']['nera']['joints'].values():v[2]+=.8
for seg in p['P11']['staff']['segments']:
 for v in seg:v[2]+=.8
for fx in p['P11']['effects']:
 if fx['id'] in ['air_brake_arrival','east_redirect']:
  for v in fx['points']:v[2]+=.8
p['P11']['air_brake_height_offset']=.8
p['P11']['camera']={'location':[1.3,-9.4,4.2],'target':[4.00,.10,2.20],'ortho':5.5,'type':'PERSP','lens':48}
for key in ['P13','P14']:
 p[key]['nera']['joints']['left_elbow']=[7.61,-.12,1.08]
 p[key]['nera']['joints']['left_hand']=[7.83,-.12,.692]
 p[key]['staff']['segments'][0]=[[7.65,-.12,.35],[7.95,-.12,.92]]
(root/'v5').mkdir(exist_ok=True)
(root/'v5'/'scene.json').write_text(json.dumps(data,indent=2)+'\n')
