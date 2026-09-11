"""Lock one rod asset and two persistent fragments before generated art tests."""
import json,math
from pathlib import Path
root=Path(__file__).resolve().parent
data=json.loads((root/'v6'/'scene.json').read_text());p=data['panels']
def distance(a,b):return math.dist(a,b)
def unit(a,b):
 d=distance(a,b);return [(b[i]-a[i])/d for i in range(3)]
def along(a,d,length):return [a[i]+d[i]*length for i in range(3)]
length=distance(*p['P08']['staff']['segments'][0])
held=distance(*p['P13']['staff']['segments'][0]);discarded=length-held
data['revision']='v7: canonical rigid rod length and two persistent fragment lengths; all seven matching final guide/pass sets'
data['staff_asset']={'intact_length_m':length,'held_fragment_length_m':held,'discarded_fragment_length_m':discarded,
 'fracture_panel':'P12','fragment_rule':'Fragment_0 retained in left hand after P12; fragment_1 discarded west of shutter.'}
# P11 grip points stay fixed on the original axis; only the free proximal end extends.
a,b=p['P11']['staff']['segments'][0];p['P11']['staff']['segments'][0][0]=along(b,unit(b,a),length)
# P12 retained piece terminates at the exact forelimb-joint contact.
contact=p['P12']['sentinel']['limbs']['foreleg'][1]
old_a,old_b=p['P12']['staff']['segments'][0];axis=unit(old_b,old_a)
p['P12']['staff']['segments'][0]=[along(contact,axis,held),contact]
negative=[-n for n in axis];free_start=along(contact,negative,.075)
p['P12']['staff']['segments'][1]=[free_start,along(free_start,negative,discarded)]
p['P12']['contact']['point']=contact
p['P12']['nera']['joints']['right_hand']=along(contact,axis,held*.43)
p['P12']['nera']['joints']['left_hand']=along(contact,axis,held*.90)
p['P12']['nera']['joints']['right_shoulder']=[5.75,-.68,1.43]
p['P12']['nera']['joints']['right_elbow']=[5.56,-.39,1.20]
p['P12']['nera']['joints']['left_elbow']=[5.88,-.16,1.19]
for key in ['P13','P14']:
 a,b=p[key]['staff']['segments'][1]
 p[key]['staff']['segments'][1]=[a,along(a,unit(a,b),discarded)]
for key,panel in p.items():
 panel['staff']['asset_id']='plain_staff_01'
 panel['staff']['segment_asset_ids']=['staff_intact'] if panel['staff']['state']=='intact' else ['staff_retained_01','staff_discarded_01']
(root/'v7').mkdir(exist_ok=True)
(root/'v7'/'scene.json').write_text(json.dumps(data,indent=2)+'\n')
