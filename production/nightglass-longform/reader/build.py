"""Build an offline reading snapshot. This never selects unfinished story art."""
import json,hashlib,copy,re
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent;DOC=ROOT/'docs/nightglass-longform'
def read(p,default=None):
 p=ROOT/p
 return json.loads(p.read_text()) if p.exists() else default

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
pilot=read('production/pilots-reading-v2/edition.json');pilots={p['id']:p for p in pilot['panels']}
selection=read('production/nightglass-longform/selected.json',{'selected':{}});selected=selection.get('selected',selection);overrides=read('production/nightglass-longform/reader/lettering-overrides.json',{'panels':{}})['panels'];issues=[];crops=[]

def source_record(record,id):
 if isinstance(record,str):record={'path':record}
 path=ROOT/record['path']
 if not path.exists():issues.append({'panel':id,'issue':'selected source missing','path':record['path']});return None
 digest=sha(path)
 if record.get('sha256') and record['sha256']!=digest:issues.append({'panel':id,'issue':'selected source hash mismatch','path':record['path']});return None
 with Image.open(path) as im:w,h=im.size
 return {'source':record['path'],'sha256':digest,'width':w,'height':h,'attempt_id':record.get('attempt_id',path.stem),**({'crop':record['crop']} if record.get('crop') else {})}

def letters_for(script,pilot_panel=None,key=None,source_sha=None):
 custom=overrides.get(key or script['id']);letters=[]
 if custom and custom.get('sha256')!=source_sha:
  issues.append({'panel':key or script['id'],'issue':'lettering source changed; review required'});custom=None
 if custom:
  # Copy remains script authority: source-bound entries describe placement only.
  if len(custom['lettering'])!=len(script['copy']):raise ValueError('Lettering/copy length differs: '+script['id'])
  for c,l in zip(script['copy'],custom['lettering']):letters.append(dict(l,speaker=c['speaker'],text=c['text']))
  copy_hash=hashlib.sha256(json.dumps(script['copy'],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
  approved=custom.get('reviewed',False) and custom.get('reviewed_copy_sha256')==copy_hash
  if custom.get('reviewed') and not approved:issues.append({'panel':key or script['id'],'issue':'lettering copy changed; review required'})
  return letters,approved
 if pilot_panel and len(pilot_panel['lettering'])==len(script['copy']):
  for c,l in zip(script['copy'],pilot_panel['lettering']):letters.append(dict(l,speaker=c['speaker'],text=c['text']))
  return letters,True
 for i,c in enumerate(script['copy']):
  caption=c['speaker'] in ['Caption','Card','Letter','System'];letters.append({'speaker':c['speaker'],'text':c['text'],'position':'above' if i==0 or caption else 'below','x':.06,'y':0,'w':.88,'target':[.5,.5],'name_cue':not caption,'no_tail':True,'caption':caption,'card':c['speaker'] in ['Card','System']})
 return letters,not letters

chapters=[]
for sp in sorted((ROOT/'production/nightglass-longform/scripts').glob('chapter-*.json')):
 if not re.fullmatch(r'chapter-\d+\.json',sp.name):continue
 s=json.loads(sp.read_text());panels=[]
 for p in s['panels']:
  pp=pilots.get(p.get('reuse'));r=selected.get(p['id']);sr=source_record(r,p['id']) if r else ({k:pp[k] for k in ['source','sha256','width','height','attempt_id']} if pp else None)
  lettering,reviewed=letters_for(p,pp if not r else None,source_sha=sr['sha256'] if sr else None)
  panels.append(dict(id=p['id'],alt=re.sub(r'^(?:New storyboard:|Explicit storyboard revision \d+:)\s*', '', p['action']),copy=p['copy'],lettering=lettering,lettering_reviewed=reviewed,available=sr is not None,reuse=p.get('reuse'),gap_after=(80 if p['id'].endswith(('-01','-08','-19','-23','-30','-36','-38','-45')) else 28),**(sr or {})))
 count=sum(p['available'] for p in panels);complete=count==len(panels) and s['chapter'] in selection.get('reviewed_complete',[]) and all(p['lettering_reviewed'] for p in panels)
 chapters.append({'id':'chapter-'+str(s['chapter']),'number':s['chapter'],'title':s['title'],'premise':s.get('reading_premise','Aren Vale wants a route with a wage, a room of his own, and enough time to sit in it. Tonight, the city has other demands.'),'script_path':str(sp.relative_to(ROOT)),'script_sha256':sha(sp),'panels':panels,'available':count,'total':len(panels),'complete':complete})

# Comparison defaults show primaries only. An explicit reader record can bind
# a reviewed replacement; filename order is never treated as approval.
cs=read('production/nightglass-longform/reader/comparison-sources.json',{'methods':{}});scripts={p['id']:p for p in read('production/nightglass-longform/reader/comparison-script.json')['panels']};comparisons=[]
for method in ['A','B','C']:
 ps=[]
 for n in range(31,37):
  sid=f'N1-{n}';id=f'{method}-{sid}';s=scripts[sid];r=cs['methods'].get(method,{}).get(sid)
  if not r and method in ['A','B']:
   path=f'production/nightglass-longform/comparison/{method}/candidates/'+(f'A-N1-{n}-P.png' if method=='A' else f'B{n}-P.png')
   if (ROOT/path).exists():r={'path':path}
  sr=source_record(r,id) if r else None
  lettering,reviewed=letters_for(s,key=id,source_sha=sr['sha256'] if sr else None)
  ps.append(dict(id=id,story_id=sid,alt=s['action'],copy=s['copy'],lettering=lettering,lettering_reviewed=reviewed,available=sr is not None,gap_after=48,**(sr or {})))
 comparisons.append({'id':method,'title':{'A':'Anchor and cast references','B':'Previous panel and state control','C':'Coherent three-panel groups'}[method],'panels':ps,'available':sum(p['available'] for p in ps),'total':6})
data={'schema':'NightglassReadingSnapshot/1','chapters':chapters,'comparisons':comparisons,'source_issues':issues,'owner_approval':None}
(HERE/'snapshot.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');(DOC/'data.js').write_text('window.NIGHTGLASS_READER = '+json.dumps(data,ensure_ascii=False)+';\n')
print('Story:',[(c['number'],c['available'],c['total'],c['complete']) for c in chapters]);print('Comparison:',[(c['id'],c['available']) for c in comparisons]);print('Source issues:',issues)
