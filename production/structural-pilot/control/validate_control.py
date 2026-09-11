"""Check deterministic control facts; explicitly does not accept image semantics/art."""
import hashlib,json,math,struct,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
ACTIVE={f'P{p:02d}':'v8' for p in range(8,15)}
scenes={v:json.loads((ROOT/v/'scene.json').read_text()) for v in set(ACTIVE.values())}
panels={k:scenes[v]['panels'][k] for k,v in ACTIVE.items()}
checks=[]
def check(name,passed,detail=None):checks.append({'check':name,'pass':bool(passed),'detail':detail})
def dist(a,b):return math.dist(a,b)
def rod_distance(p,a,b):
 ab=[b[i]-a[i] for i in range(3)];ap=[p[i]-a[i] for i in range(3)]
 t=sum(x*y for x,y in zip(ab,ap))/sum(x*x for x in ab)
 return dist(p,[a[i]+max(0,min(1,t))*ab[i] for i in range(3)])
for k,p in panels.items():
 check(k+'.three_named_limbs',set(p['sentinel']['limbs'])=={'foreleg','sweep_leg','support_leg'})
 check(k+'.south_camera',p['camera']['location'][1]<0)
 expected='nera.right_hand.dorsal' if int(k[1:])>=12 else None
 check(k+'.injury_state',p['injury']==expected)
 anchors=json.loads((ROOT/ACTIVE[k]/(k+'-anchors.json')).read_text())
 for key in ['nera.right_hand','nera.left_hand','odo.right_hand','odo.left_hand']:
  # P08 is a Nera/contact close shot; Odo's off-frame release hand is intentionally
  # contextual, unlike the selected wide/reversal/movement/aftermath panels.
  if k=='P08' and key.startswith('odo.'):continue
  check(k+'.'+key+'.in_frame',anchors['anchors'][key]['inside_frame'])
 for name in ['full','background','sentinel','actors','props','foreground','effects']:
  file=ROOT/ACTIVE[k]/(k+'-'+name+'.png')
  raw=file.read_bytes();size=struct.unpack('>II',raw[16:24])
  check(k+'.'+name+'.dimensions',list(size)==p['resolution'])
check('P08_P09.fixed_anchor',panels['P08']['foot_anchor']==panels['P09']['foot_anchor'])
check('P08_P09.identical_staff',panels['P08']['staff']['segments']==panels['P09']['staff']['segments'])
for k in ['P08','P09']:
 p=panels[k];a,b=p['staff']['segments'][0]
 check(k+'.forefoot_staff_contact',dist(b,p['sentinel']['limbs']['foreleg'][-1])<1e-8)
 for side in ['right','left']:
  error=rod_distance(p['nera']['joints'][side+'_hand'],a,b)
  check(k+'.'+side+'_hand_on_staff',error<1e-8,error)
for k in ['P13','P14']:
 p=panels[k]
 for actor in ['nera','odo']:
  check(k+'.'+actor+'.all_joints_east',all(v[0]>6.7 for v in p[actor]['joints'].values()))
 check(k+'.sentinel_body_west',p['sentinel']['center'][0]<6.7)
 check(k+'.left_staff_holder',p['staff']['holder']=='nera.left_hand')
lengths={k:[round(dist(a,b),4) for a,b in p['staff']['segments']] for k,p in panels.items()}
asset=scenes['v8']['staff_asset']
for k,p in panels.items():
 expected=[asset['intact_length_m']] if p['staff']['state']=='intact' else [asset['held_fragment_length_m'],asset['discarded_fragment_length_m']]
 check(k+'.canonical_staff_lengths',all(abs(dist(*segment)-length)<1e-8 for segment,length in zip(p['staff']['segments'],expected)))
 for side in (['right','left'] if int(k[1:])<13 and k!='P10' else ['left']):
  error=rod_distance(p['nera']['joints'][side+'_hand'],*p['staff']['segments'][0])
  check(k+'.'+side+'_hand_on_retained_rod',error<1e-8,error)
check('P12.fracture_at_joint',dist(panels['P12']['staff']['segments'][0][1],panels['P12']['sentinel']['limbs']['foreleg'][1])<1e-8)
mesh_report=json.loads((ROOT/'mesh-alpha-verification.json').read_text())
check('P13.actual_mesh_partition_spans_floor',mesh_report['p13_actual_partition_y_union']['covers_floor_width'])
check('P11.actual_mesh_boot_clearance',mesh_report['panels']['P11']['minimum_world_vertical_clearance_m']>.4)
for k,info in mesh_report['panels'].items():
 for suffix in ['full','background']:check(k+'.'+suffix+'.opaque_alpha',info['alpha'][suffix]['min']==1)
 check(k+'.actual_mesh_three_limb_ids',len(info['limb_ids'])==3)
files=[]
for k,v in ACTIVE.items():
 for file in sorted((ROOT/v).glob(k+'-*')):
  raw=file.read_bytes();files.append({'path':str(file.relative_to(ROOT)), 'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
report={'schema':'StructuralControlVerification/1','created_epoch':time.time(),'active_versions':ACTIVE,
 'status':'DETERMINISTIC_CONTROL_CHECKS_ONLY_NOT_ART_ACCEPTANCE','checks':checks,
 'passed':sum(c['pass'] for c in checks),'failed':sum(not c['pass'] for c in checks),
 'staff_segment_lengths_m':lengths,
 'known_limitations':['PNG layers require explicit foreground occlusion order. A sentinel-only image by itself does not preserve shutter occlusion.',
 'v8 P12 fragments project almost collinearly and the fracture is partly hidden by the joint. Separate v9 P12 correction exposes the discarded fragment but does not independently establish fully clear impact.',
 'Actor shapes and facial features are pose guides. No skilled human drawing, final artistic appeal or human comprehension is established.',
 'P11 guide depicts a high vault above the window lintel; the source scene contains no roof collision simulation.'],
 'files':files,'deterministic_guide_pngs_preserved':len(list(ROOT.glob('v*/*.png'))),
 'generative_calls_by_this_agent':0,'direct_paid_spend_usd':0}
(ROOT/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
(ROOT/'active-controls.json').write_text(json.dumps({'schema':'ActiveStructuralControls/1','status':'GUIDES_FOR_BOUNDED_EXPERIMENT_NOT_ACCEPTED_FINAL_ART','panels':ACTIVE,'frozen_selected':['P09','P11','P13','P14'],'supplemental_unselected':{'P12':'v9'}},indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['passed','failed','staff_segment_lengths_m','deterministic_guide_pngs_preserved']},indent=2))
if report['failed']:raise SystemExit(1)
