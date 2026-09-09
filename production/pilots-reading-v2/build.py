"""Build the reading edition from preserved v1 copy and explicit v2 decisions."""
import json,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def read(p):return json.loads((ROOT/p).read_text())
plan=read('production/pilot-chapters/plan.json');selected=read('production/pilot-chapters/selected.json')['selected'];candidates={c['attempt_id']:c for c in read('production/pilot-chapters/candidates.json')['candidates']}
overrides=read('production/pilot-chapters/lettering-overrides.json')['entries']
# Normalized mouth/face positions observed from selected natives, in dialogue order.
targets={
'NG02':[[.59,.58],[.33,.46]],'NG04':[[.23,.66],[-.1,.45]],'NG05':[[.3,.37],[.76,.42]],'NG06':[[.42,.41],[.42,.41]],'NG07':[[.5,.74],[.45,.35]],'NG09':[[.62,.61]],'NG10':[[.2,.45]],'NG11':[[.34,.61],[.64,.36]],'NG13':[[.58,.47],[.31,.42]],'NG14':[[.29,.48],[.7,.34]],'NG15':[[.25,.34],[.7,.4]],'NG16':[[.4,.57]],
'BP02':[[-.1,.1],[.38,.42]],'BP03':[[.17,.45],[.58,.41]],'BP04':[[.86,.33],[.38,.27]],'BP05':[[1.1,.3],[.19,.37]],'BP07':[[.67,.29],[.27,.55]],'BP08':[[.85,.3]],'BP09':[[.42,.45],[.42,.45]],'BP11':[[1.1,.4]],'BP12':[[.56,.29],[.87,.34]],'BP14':[[.29,.43],[.66,.43]],'BP15':[[.35,.42],[.67,.41]],'BP16':[[.17,.52]],
'ST02':[[.64,.42],[.34,.42]],'ST03':[[.24,.4]],'ST04':[[.37,.33]],'ST06':[[.44,.41],[.44,.41]],'ST07':[[.21,.52]],'ST09':[[.27,.31],[.27,.31]],'ST11':[[.29,.49],[.29,.49]],'ST12':[[.31,.43]],'ST13':[[.18,.39],[.76,.39]],'ST14':[[.49,.24],[.19,.5]],'ST15':[[.2,.38],[.61,.24]],'ST16':[[.4,.48]],
'RC02':[[.28,.18],[.68,.43]],'RC03':[[.32,.45],[.67,.44]],'RC05':[[.23,.53]],'RC06':[[.24,.46]],'RC07':[[.34,.25],[.7,.39]],'RC09':[[.33,.26]],'RC11':[[-.1,.4]],'RC12':[[.34,.34],[.78,.46]],'RC14':[[.36,.42],[.73,.48]],'RC15':[[.84,.57],[.3,.47]],'RC16':[[.35,.31]],
'FL02':[[.28,.36],[.7,.4]],'FL03':[[.34,.22],[.56,.45]],'FL04':[[.54,.41],[.23,.11]],'FL06':[[.58,.33],[.28,.25]],'FL08':[[.22,.16],[.22,.16]],'FL09':[[.43,.35],[.25,.24]],'FL11':[[.19,.26],[-.1,.5]],'FL12':[[.15,.16]],'FL14':[[.2,.62],[.72,.43]],'FL15':[[1.1,.68],[.38,.36]],'FL16':[[.49,.65]]}
# Panels with close faces, reversed speaker geography or no safe text band use
# added lettering space, preserving every pixel of the native composition.
framed={'NG02','NG04','NG07','NG11','NG13','BP02','BP04','BP05','BP07','BP08','BP09','BP11','BP12','BP14','BP15','ST02','ST03','ST14','ST15','RC02','RC07','RC15','FL02','FL03','FL04','FL06','FL08','FL09','FL11','FL12','FL14','FL15'}
revisions={
'BP12': [('The root is clear. Come through.','Replace deflective joke with escape instruction supported by the freed doorway.'),('I thought I would never see this side.','Give Neris relief after confinement instead of a second joke.')],
'FL12':[('Keep pulling.','Preserve urgency while Ada extracts Lio; remove rescue-time quip.')]
}
changes=[];panels=[]
for e in plan['entries']:
 id=e['id'];c=candidates[selected[id]];original=copy.deepcopy(e['copy']);letters=copy.deepcopy(overrides.get(id,{}).get('lettering',e['lettering']))
 for i,l in enumerate(letters):
  l['speaker']=original[i]['speaker'].split(',')[0];l['text']=original[i]['text'];l['target']=targets[id][i];l['offscreen']=l['target'][0]<0 or l['target'][0]>1;l['voice']=l['speaker']=='Voice'
  l.pop('attribution',None);l.pop('show_speaker',None);l.pop('tail',None)
  if id in revisions:
   text,reason=revisions[id][i];changes.append({'panel':id,'line':i+1,'speaker':l['speaker'],'original':l['text'],'revised':text,'reason':reason});l['text']=text
  if id in framed:
   l['position']='above' if i==0 else 'below';l['w']=.84 if len(l['text'])>70 else .73;l['x']=max(.025,min(.975-l['w'],l['target'][0]-l['w']/2));l['y']=0
  else:
   l['position']='overlay'
  if id in {'NG07','NG11'} or (id=='ST15' and i==1):l['name_cue']=True;l['no_tail']=True
  # Repeated speech has one continuous speaker, not two competing pointers.
  if i and l['speaker']==letters[i-1]['speaker'] and l['position']==letters[i-1]['position']:l['linked']=True
 panels.append({'id':id,'chapter_id':e['chapter_id'],'source':c['path'],'attempt_id':c['attempt_id'],'sha256':c['sha256'],'width':c['width'],'height':c['height'],'alt':e['action'],'original_copy':original,'lettering':letters,'gap_after': e.get('gap_after',24),'reading_note':'Native composition preserved; lettering decisions are provisional AI editorial work.'})
premises={
 'NG':"Tonight is Aren Vale’s chance to qualify for the upper courier routes. In a city built over darkness, even a short delivery can ask too much.",
 'BP':"Ilyra’s missing brother is calling from a condemned glasshouse. She knows that voice. She needs to know why it is here.",
 'ST':"Tavi needs a seat on the departing sky-caravan. Its signal bell is hanging from a very large, very uncooperative ram.",
 'RC':"Clear the trial bridge. Earn the upper-ring key. Ren has borrowed gauntlets that can return a monster’s blow—and has barely read the terms.",
 'FL':"Ada’s brother has vanished into the flood city. His coat came home without him. Corin has a notebook, a ward-pole, and one very worried client."
}
for c in plan['chapters']:c['reading_premise']=premises[c['id']]
data={'schema':'PilotReadingEdition/2','version':'2026-09-09-v2','owner_approval':None,'chapters':plan['chapters'],'panels':panels,'copy_revisions':changes}
(ROOT/'production/pilots-reading-v2/edition.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
(ROOT/'production/pilots-reading-v2/copy-revisions.json').write_text(json.dumps({'source':'production/pilot-chapters/plan.json','version':'v2','revisions':changes},ensure_ascii=False,indent=2)+'\n')
(ROOT/'docs/pilots-reading-v2/data.js').write_text('window.PILOT_EDITION = '+json.dumps(data,ensure_ascii=False)+';\n')
print('Built',len(panels),'panels;',len(changes),'explicit copy revisions')
