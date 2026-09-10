from pathlib import Path
import json,hashlib,sys
from PIL import Image
r=Path(__file__).resolve().parents[5];f=Path(__file__).resolve().parents[1];panel,aid,note=sys.argv[1:];s=f/'candidates'/f'{aid}.png';p=f/'notes/selected-records.json';d=json.loads(p.read_text()) if p.exists() else {'selected':{},'status':'worker recommendations; shared selections lead-owned'};d['selected'][panel]={'path':str(s.relative_to(r)),'sha256':hashlib.sha256(s.read_bytes()).hexdigest(),'attempt_id':aid,'dimensions':list(Image.open(s).size),'operation':'whole unchanged native PNG','selection_note':note};p.write_text(json.dumps(d,indent=2)+'\n')
