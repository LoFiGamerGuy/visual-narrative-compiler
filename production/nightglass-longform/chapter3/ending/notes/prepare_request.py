import datetime,hashlib,json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[5]
folder=Path(__file__).resolve().parents[1]
aid=sys.argv[1];refs=sys.argv[2:]
prompt=(folder/'requests'/f'{aid}.txt').read_text()
args={'prompt':prompt,'referenced_image_paths':[str(root/r) for r in refs]}
(folder/'requests'/f'{aid}.json').write_text(json.dumps(args,indent=2)+'\n')
record={'id':aid,'tool':'image_gen.imagegen','status':'prepared','prepared_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'arguments_path':str(folder/'requests'/f'{aid}.json'),'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),'references':[{'path':r,'sha256':hashlib.sha256((root/r).read_bytes()).hexdigest()} for r in refs],'model_snapshot':None,'seed':None,'billing':None}
(folder/'calls'/f'{aid}.json').write_text(json.dumps(record,indent=2)+'\n')
