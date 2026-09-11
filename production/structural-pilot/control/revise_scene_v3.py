"""Camera/value correction after actual v1/v2 image inspection. Preserve both."""
import json
from pathlib import Path
root=Path(__file__).resolve().parent
data=json.loads((root/'v2'/'scene.json').read_text())
data['revision']='v3: south-west perspectives, flat high-key values, longer locked staff, exact hand grips, closer P14'
p=data['panels']
for key in ['P08','P09','P10']:
 p[key]['staff']['segments'][0][0]=[2.72,-.47,1.45]
 a,b=p[key]['staff']['segments'][0]
 for side,t in [('left',.45),('right',.67)]:
  if key=='P10' and side=='right':continue
  p[key]['nera']['joints'][side+'_hand']=[a[i]+t*(b[i]-a[i]) for i in range(3)]
p['P08']['camera']={'location':[1.9,-7.5,3.2],'target':[3.70,.15,1.18],'ortho':4.5,'type':'PERSP','lens':49}
p['P09']['camera']={'location':[-.70,-8.6,3.9],'target':[3.55,.05,1.38],'ortho':7.6,'type':'PERSP','lens':43}
p['P11']['camera']={'location':[.80,-10.2,4.40],'target':[4.0,.08,1.78],'ortho':7.1,'type':'PERSP','lens':37}
a,b=p['P11']['staff']['segments'][0]
for side,t in [('left',.16),('right',.45)]:p['P11']['nera']['joints'][side+'_hand']=[a[i]+t*(b[i]-a[i]) for i in range(3)]
p['P12']['staff']['segments'][0][0]=[6.22,-.70,1.38]
a,b=p['P12']['staff']['segments'][0]
for side,t in [('left',.37),('right',.745)]:p['P12']['nera']['joints'][side+'_hand']=[a[i]+t*(b[i]-a[i]) for i in range(3)]
p['P12']['nera']['joints']['right_elbow']=[5.60,-.63,1.17]
# P13 slightly west offset shows the shutter's plane while leaving east adults clear.
p['P13']['camera']={'location':[4.85,-11.0,4.0],'target':[6.4,.0,1.18],'ortho':7.6,'type':'PERSP','lens':42}
p['P14']['camera']={'location':[7.65,-8.6,2.54],'target':[7.83,-.20,1.44],'ortho':1.93,'type':'ORTHO'}
(root/'v3').mkdir(exist_ok=True)
(root/'v3'/'scene.json').write_text(json.dumps(data,indent=2)+'\n')
