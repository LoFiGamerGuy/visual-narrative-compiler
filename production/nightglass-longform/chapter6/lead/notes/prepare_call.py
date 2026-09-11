import json,hashlib,datetime,sys
from pathlib import Path
b=Path(__file__).resolve().parents[5]
r=b/'production/nightglass-longform/chapter6/lead'
aid=sys.argv[1]; refs=sys.argv[2:]; prompt=(r/'requests'/f'{aid}.txt').read_text()
args={'prompt':prompt,'referenced_image_paths':[str(b/p) for p in refs]}
p=r/'calls'/f'{aid}.json';assert not p.exists()
(r/'requests'/f'{aid}.json').write_text(json.dumps(args,indent=2)+'\n')
rec={'id':aid,'tool':'image_gen.imagegen','status':'submitted','phase':'repair' if 'R1' in aid else 'primary','panels':[aid.split('-')[0]+'-'+part for part in aid.split('-')[1:-1] if part.isdigit()], 'args':args,'arguments_path':str(r/'requests'/f'{aid}.json'),'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),'references':[{'path':v,'sha256':hashlib.sha256((b/v).read_bytes()).hexdigest()} for v in refs],'before_art_dependency':'Complete47 script independently reviewed SHAaeea4046b2f138dcebad3e27b0cc5cf4d4b241c3a02fcc27337977e80d6f3204. Fresh FiveChapters portable artifact verified and all55actualcaptures reviewed. Chapter6 finite65 within104 remaining original320; oneP/maxoneR1, no cap reset. Lead actually viewed current references; visible custody/gear only.','model_snapshot':None,'seed':None,'billing':None,'owner_approval':None,'invoked':True,'submitted_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
p.write_text(json.dumps(rec,indent=2)+'\n'); print(aid, 'submitted provenance recorded')
