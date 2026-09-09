"""Observed source geometry for the bounded comparison, with frozen copy."""
from pathlib import Path
import json
HERE=Path(__file__).resolve().parent
snap=json.loads((HERE/'snapshot.json').read_text());p=HERE/'lettering-overrides.json';data=json.loads(p.read_text())
# All positions are source-specific. Margins are used where faces occupy the
# source's upper band; the text never covers the handoff, envelope or line.
geometry={
 'A-N1-31':[(.18,.2)],'A-N1-32':[(.45,.34)],'A-N1-34':[(.57,.29)],'A-N1-35':[(.65,.32),(-.1,.2)],'A-N1-36':[(.49,.34)],
 'B-N1-31':[(.25,.2)],'B-N1-32':[(.64,.25)],'B-N1-34':[(.6,.29)],'B-N1-35':[(.56,.3),(-.1,.2)],'B-N1-36':[(.55,.28)],
 'C-N1-31':[(.3,.28)],'C-N1-32':[(.64,.25)],'C-N1-34':[(.47,.15)],'C-N1-35':[(.55,.2),(-.1,.2)],'C-N1-36':[(.54,.25)]}
for method in snap['comparisons']:
 for panel in method['panels']:
  id=panel['id']
  if not panel['available'] or id not in geometry:continue
  letters=[]
  for i,target in enumerate(geometry[id]):
   off=target[0]<0;letters.append({'position':'above' if i==0 else 'below','x':max(.04,min(.22,target[0]-.36)),'y':0,'w':.74,'target':list(target),'offscreen':off})
  data['panels'][id]={'sha256':panel['sha256'],'reviewed':False,'reason':'Native source directly viewed; marginal composition protects face and causal equipment. Pending actual 390px lettered inspection.','lettering':letters}
p.write_text(json.dumps(data,indent=2)+'\n')
