from pathlib import Path
import json,hashlib,datetime,sys
r=Path(__file__).parent
call_id,kind=sys.argv[1:]
a=json.loads((r/'requests'/f'{call_id}.json').read_text())
x={'attempt_id':call_id,'kind':kind,'status':'submitted','tool':'image_gen.imagegen','submitted_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'args':a,'references':[{'path':p,'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()} for p in a['referenced_image_paths']],'model_snapshot':None,'seed':None,'billing':None}
(r/'calls'/f'{call_id}.json').write_text(json.dumps(x,indent=2))
