"""Author the original, explicitly posed SC-20260907-01 geometry specification.

This is agent-authored staging, not motion capture, a human drawing or final art.
Run with stdlib Python; only writes beside this script into the requested version.
"""
import copy, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def adult(x, y, height=1.78):
    h=height/1.78
    joints={
      'hip':[x,y,.90*h], 'chest':[x,y,1.36*h], 'neck':[x,y,1.55*h], 'head':[x,y,1.72*h],
      'right_shoulder':[x,y-.20,1.42*h], 'right_elbow':[x+.08,y-.26,1.13*h], 'right_hand':[x+.16,y-.28,.96*h],
      'left_shoulder':[x,y+.20,1.42*h], 'left_elbow':[x+.08,y+.24,1.13*h], 'left_hand':[x+.17,y+.25,.96*h],
      'right_hip':[x,y-.12,.9*h], 'right_knee':[x+.08,y-.13,.51*h], 'right_ankle':[x+.08,y-.13,.17],
      'left_hip':[x,y+.12,.9*h], 'left_knee':[x-.13,y+.13,.50*h], 'left_ankle':[x-.18,y+.13,.17],
    }
    return {'joints':joints,'gaze':[x+1,y,1.5*h], 'facing':[1,0,0]}

def pose(actor, **updates):
    actor=copy.deepcopy(actor)
    for key,value in updates.items():
        if key in ['gaze','facing']: actor[key]=value
        else: actor['joints'][key]=value
    return actor

contact=[3.9,0,.26]
nera8=pose(adult(3.10,-.42),
 hip=[2.95,-.48,.79],chest=[3.14,-.47,1.23],neck=[3.28,-.46,1.42],head=[3.37,-.45,1.59],
 right_shoulder=[3.13,-.68,1.29],right_elbow=[3.30,-.68,.96],right_hand=[3.50,-.15,.64],
 left_shoulder=[3.13,-.25,1.29],left_elbow=[3.16,-.15,.96],left_hand=[3.25,-.25,.90],
 right_hip=[2.95,-.63,.79],right_knee=[3.29,-.65,.47],right_ankle=[3.48,-.59,.17],
 left_hip=[2.95,-.33,.79],left_knee=[2.60,-.25,.46],left_ankle=[2.41,-.18,.17],gaze=[4.55,.1,1.6])
odo8=pose(adult(1.05,.23,1.89),left_elbow=[.88,.50,1.58],left_hand=[.85,.50,1.82],gaze=[4.1,.2,1.7])
limbs8={'foreleg':[[4.63,.20,1.90],[4.25,.08,1.14],contact],
        'sweep_leg':[[5.10,-.30,1.92],[5.75,-.76,.96],[5.8,-.77,.17]],
        'support_leg':[[5.26,.55,1.88],[5.9,1.04,.9],[6.05,1.18,.17]]}
base={'resolution':[1170,1020],'camera':{'location':[3.75,-8.6,3.35],'target':[3.85,.05,1.18],'ortho':4.8},
      'nera':nera8,'odo':odo8,'sentinel':{'center':[5,.22,2.2],'yaw':0,'limbs':limbs8},
      'staff':{'state':'intact','segments':[[[2.96,-.37,1.20],contact]],'holder':'nera'},
      'flask':{'holder':'nera','location':[3.24,-.67,1.13]}, 'shutter_bottom':.05,
      'cable_hand':'odo.left_hand','charges':2,'injury':None,'effects':[],
      'contact':{'kind':'staff-tip restrained forefoot','point':contact},'foot_anchor':contact,
      'spatial_mode':'grounded','note':'P08 counter; named forefoot and staff share endpoint.'}
panels={'P08':base}
p=copy.deepcopy(base)
p.update(resolution=[1170,900],camera={'location':[3.5,-11,4.1],'target':[3.5,0,1.28],'ortho':7.6},
  note='P09 pivot around the unchanged forefoot. Side limb sweeps toward Odo at west release.')
p['sentinel']={'center':[4.80,.78,2.16],'yaw':-28,'limbs':{
 'foreleg':[[4.46,.47,1.89],[4.13,.25,1.10],contact],
 'sweep_leg':[[4.62,.16,1.88],[3.16,.13,1.23],[1.62,.10,.98]],
 'support_leg':[[5.16,1.02,1.86],[5.57,1.28,.96],[5.89,1.25,.17]]}}
p['effects']=[{'id':'ongoing_sweep','color':'violet','points':[[4.85,-.48,.48],[3.6,-.70,.60],[2.42,-.25,.84],[1.62,.10,.98]]}]
panels['P09']=p
p=copy.deepcopy(p)
p.update(resolution=[1170,1080],camera={'location':[2.5,-8.6,2.9],'target':[2.5,-.1,1.15],'ortho':4.5}, note='P10 one flask between throwing and receiving hands.')
p['nera']=pose(nera8,right_elbow=[2.89,-.6,1.36],right_hand=[2.65,-.55,1.57],gaze=[1.05,.23,1.79])
p['odo']=pose(odo8,right_elbow=[1.28,-.2,1.38],right_hand=[1.55,-.22,1.51],gaze=[2.1,-.42,1.77])
p['flask']={'holder':'in_transit','location':[2.07,-.36,1.84]}
p['effects']=[{'id':'flask_arc','color':'ivory','points':[[2.65,-.55,1.6],[2.30,-.42,1.93],[1.94,-.34,1.88],[1.55,-.22,1.51]]}]
panels['P10']=p
p=copy.deepcopy(base)
p.update(resolution=[1170,1500],camera={'location':[4.15,-11.7,4.55],'target':[4.15,.1,1.83],'ortho':8.0},shutter_bottom=2.65,charges=1,
 note='P11 one airborne adult above an ongoing side sweep; Air Brake accent redirects motion east. Odo pulls trailing west-linked cord while running east.')
p['nera']=pose(adult(4.00,-.58),hip=[3.84,-.58,2.58],chest=[4.10,-.59,2.98],neck=[4.24,-.59,3.14],head=[4.37,-.59,3.29],
 right_shoulder=[4.08,-.79,3.03],right_elbow=[4.49,-.77,2.87],right_hand=[4.79,-.60,2.63],
 left_shoulder=[4.08,-.37,3.03],left_elbow=[4.07,-.26,2.68],left_hand=[4.45,-.48,2.88],
 right_hip=[3.84,-.73,2.58],right_knee=[4.24,-.85,2.31],right_ankle=[4.43,-.84,2.02],
 left_hip=[3.84,-.43,2.58],left_knee=[3.46,-.34,2.50],left_ankle=[3.23,-.32,2.09],gaze=[5.3,.12,1.0])
p['odo']=pose(adult(2.52,.64,1.89),hip=[2.54,.64,.99],chest=[2.77,.64,1.46],neck=[2.90,.64,1.65],head=[2.98,.64,1.81],
 right_shoulder=[2.74,.44,1.49],right_elbow=[3.03,.38,1.23],right_hand=[3.18,.39,1.44],
 left_shoulder=[2.74,.85,1.49],left_elbow=[2.33,1.0,1.51],left_hand=[2.05,1.03,1.76],
 right_hip=[2.54,.50,.99],right_knee=[2.93,.39,.58],right_ankle=[3.14,.34,.17],
 left_hip=[2.54,.78,.99],left_knee=[2.19,.86,.54],left_ankle=[1.94,.86,.29],gaze=[6.7,0,1.6])
p['sentinel']={'center':[4.85,.71,1.95],'yaw':-12,'limbs':{
 'foreleg':[[4.47,.36,1.69],[4.2,.14,.97],contact],
 'sweep_leg':[[4.76,-.03,1.70],[3.7,-.32,1.02],[2.14,-.29,.92]],
 'support_leg':[[5.17,1.05,1.66],[5.68,1.27,.82],[5.87,1.33,.17]]}}
p['staff']={'state':'intact','segments':[[[4.27,-.37,3.03],[5.43,-.76,2.07]]],'holder':'nera'}
p['flask']={'holder':'odo','location':[3.18,.39,1.54]}
p['effects']=[{'id':'ongoing_sweep','color':'violet','points':[[4.5,-.68,.65],[3.6,-.7,.72],[2.9,-.48,.85],[2.14,-.29,.92]]},
 {'id':'air_brake_arrival','color':'cyan','points':[[2.7,-.55,1.25],[2.86,-.55,2.22],[3.48,-.6,3.0]]},
 {'id':'east_redirect','color':'cyan','points':[[4.11,-.50,3.6],[4.72,-.45,3.43],[5.28,-.40,2.68],[5.60,-.3,1.9]]}]
p['contact']={'kind':'intended next strike joint','point':[4.2,.14,.97]}
panels['P11']=p
p=copy.deepcopy(base)
p.update(resolution=[1170,1650],camera={'location':[5.75,-8.3,3.5],'target':[5.75,.02,1.35],'ortho':5.45},shutter_bottom=2.6,charges=1,injury='nera.right_hand.dorsal',
 note='P12 backward strike during eastward motion. Staff fractures at joint; right dorsal hand scraped.')
p['nera']=pose(adult(5.98,-.57),hip=[6.06,-.57,.97],chest=[5.95,-.57,1.39],neck=[5.81,-.55,1.56],head=[5.69,-.52,1.72],
 right_shoulder=[5.93,-.79,1.43],right_elbow=[5.72,-.80,1.14],right_hand=[5.43,-.53,1.08],
 left_shoulder=[5.93,-.35,1.43],left_elbow=[6.15,-.21,1.17],left_hand=[5.83,-.40,1.21],
 right_hip=[6.06,-.73,.97],right_knee=[6.39,-.76,.52],right_ankle=[6.60,-.76,.19],
 left_hip=[6.06,-.42,.97],left_knee=[5.75,-.33,.62],left_ankle=[5.52,-.33,.34],gaze=[5.0,.02,.88])
p['odo']=pose(adult(7.19,.07,1.89),right_hand=[7.44,-.12,1.22],left_hand=[6.96,.29,1.37],gaze=[7.9,0,1.7])
p['sentinel']={'center':[4.45,.57,1.96],'yaw':14,'limbs':{
 'foreleg':[[4.67,.25,1.68],[5.11,.00,.97],[6.62,.00,.16]],
 'sweep_leg':[[4.12,-.08,1.68],[3.6,-.39,.88],[3.06,-.55,.17]],
 'support_leg':[[4.32,.99,1.66],[4.7,1.30,.82],[4.99,1.36,.17]]}}
p['staff']={'state':'broken','holder':'nera','segments':[[[6.22,-.26,1.38],[5.16,-.02,.99]],[[5.08,.01,.96],[4.69,.17,.80]]]}
p['flask']={'holder':'odo','location':[7.44,-.12,1.32]}
p['effects']=[]
p['contact']={'kind':'staff fracture at forelimb joint','point':[5.11,0,.97]}
panels['P12']=p
p=copy.deepcopy(p)
p.update(resolution=[1170,1080],camera={'location':[6.5,-12.0,4.95],'target':[6.5,.05,1.16],'ortho':7.0},shutter_bottom=.20,
 note='P13 south-side cutaway: adults east of X=6.7; live sentinel west. Closed shutter physically bears on foreleg at ground contact.')
p['nera']=pose(adult(7.37,-.42),head=[7.43,-.42,1.68],right_elbow=[7.6,-.69,1.21],right_hand=[7.83,-.70,1.18],
 left_elbow=[7.25,-.16,1.17],left_hand=[7.09,-.13,.97],gaze=[7.85,-.65,1.18])
p['odo']=pose(adult(8.30,.05,1.89),left_elbow=[8.00,.10,1.3],left_hand=[7.84,-.63,1.13],right_hand=[8.42,-.21,1.04],gaze=[7.8,-.65,1.17],facing=[-1,0,0])
p['staff']={'state':'broken','holder':'nera.left_hand','segments':[[[7.30,-.13,1.29],[6.91,-.13,.70]],[[5.57,-.49,.16],[5.23,-.35,.16]]]}
p['flask']={'holder':'odo.right_hand','location':[8.42,-.21,1.14]}
p['sentinel']['limbs']['foreleg'][-1]=[6.74,0,.16]
p['contact']={'kind':'shutter bottom on extended foreleg','point':[6.7,0,.20]}
p['cable_hand']=None
panels['P13']=p
p=copy.deepcopy(p)
p.update(resolution=[1170,1320],camera={'location':[7.84,-8.6,2.78],'target':[7.84,-.17,1.34],'ortho':2.60},
 note='P14 Nera presents injured RIGHT dorsal hand, LEFT hand retains broken staff. Odo supports injury with left hand and holds upright flask in right.')
p['nera']['gaze']=[8.18,0,1.80]
p['odo']['gaze']=[7.75,-.66,1.17]
panels['P14']=p

spec={'schema':'OriginalSceneControl/1','experiment':'SC-20260907-01','authored_utc':'2026-09-07T05:47:46Z',
 'status':'EDITABLE_STRUCTURAL_GUIDES_NOT_FINISHED_ART','units':'meters; X east; Y north; Z up',
 'source':'Original plan plus original agent-authored geometry; no third-party art inputs',
 'gallery':{'shutter_x':6.7,'ridge_y':0,'release':[.85,.5,1.82],'overhead_cable_z':3.33,'south_cutaway':True},
 'anatomy':'Actor right shoulder is south-facing/near Y-negative in these side views; names are anatomical, not viewer labels.',
 'panels':panels}
(ROOT/'v1'/'scene.json').write_text(json.dumps(spec,indent=2)+'\n')
