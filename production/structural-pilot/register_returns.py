"""Preserve tool originals and register returned panel rasters; never calls a generator."""
from pathlib import Path
import json, shutil
from PIL import Image
from sequence_pilot.cli import Workspace, locked
P=Path(__file__).resolve().parent
for receipt in sorted((P/'calls').glob('A*-returned.json')):
    row=json.loads(receipt.read_text()); aid=row['attempt_id']; dest=P/'calls'/f'{aid}-registered.json'
    if dest.exists(): continue
    if row.get('error') or not row.get('source_path'): continue
    source=Path(row['source_path']); incoming=P/'incoming'/f'{aid}.png'; incoming.parent.mkdir(exist_ok=True)
    if incoming.exists():
        if incoming.read_bytes()!=source.read_bytes(): raise ValueError('Incoming bytes conflict')
    else: shutil.copyfile(source,incoming)
    with locked(P):
        w=Workspace(P)
        previous=[r for r in w.records('registered') if r['attempt_id']==aid]
        candidate=previous[0] if previous else w.register(aid,str(incoming))
    with Image.open(incoming) as im:
        alpha=im.getchannel('A') if 'A' in im.getbands() else None
        stats={'image_mode':im.mode,'alpha_extrema':alpha.getextrema() if alpha else None,'transparent_pixels':sum(v for k,v in enumerate(alpha.histogram()) if k<255) if alpha else 0,'total_pixels':im.width*im.height}
    dest.write_text(json.dumps({**row,'candidate':candidate,**stats},indent=2)+'\n')
    print(aid,candidate['id'],candidate['path'],stats)
