"""Source-specific initial lettering based on inspected Chapter1 natives. Does not set review approval."""
import json,copy,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
p=HERE/'lettering-overrides.json';d=json.loads(p.read_text());o=d['panels'];sel=json.loads((ROOT/'production/nightglass-longform/selected.json').read_text())['selected'];sel.update(json.loads((ROOT/'production/nightglass-longform/chapter1/stair-conversation/selected-records.json').read_text())['selected'])
def speech(x,y,pos='above',off=False):return {'position':pos,'x':max(.03,min(.23,x-.37)),'y':0,'w':.74,'target':[x,y],'offscreen':off}
def card(pos='above'):return {'position':pos,'x':.05,'y':0,'w':.9,'target':[.5,.5],'caption':True,'card':True,'no_tail':True}
layouts={
'N1-16':[speech(.45,.44)],'N1-17':[speech(.36,.31)],
'N1-24':[speech(.29,.26),speech(.68,.27,'below')],
'N1-25':[speech(.18,.28),speech(.36,.34,'below')],
'N1-26':[speech(.42,.3)],
'N1-27':[speech(.28,.24),speech(.66,.28,'below')],
'N1-28':[card(),speech(-.1,.5,'below',True)],
'N1-29':[speech(.58,.24),card('below')],
'N1-30':[speech(.23,.13),speech(.085,.14,'below')],
'N1-35':[speech(.33,.51),speech(-.1,.3,'below',True)],
'N1-36':[dict(speech(-.1,.3),offscreen=True)],
'N1-37':[speech(.34,.15)]}
for sid,ls in layouts.items():
 if sid not in sel:continue
 src=sel[sid];digest=hashlib.sha256((ROOT/src['path']).read_bytes()).hexdigest()
 if sid in o and o[sid].get('sha256')==digest and o[sid].get('reviewed'):continue
 o[sid]={'sha256':digest,'reviewed':False,'reason':'Native source directly inspected; external bands preserve face, card, envelope, sleeve tear and mechanism. Awaiting actual 390px lettered review.','lettering':ls}
for sid,key in [('N1-31','C-N1-31'),('N1-32','C-N1-32'),('N1-34','A-N1-34')]:
 if sid in sel:o[sid]=copy.deepcopy(o[key]);o[sid]['reviewed']=False;o[sid]['reason']='Same selected native as inspected comparison; awaiting final chapter context reading.'
p.write_text(json.dumps(d,indent=2)+'\n')
