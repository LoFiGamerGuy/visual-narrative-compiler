"""Register completed tool outputs; original tool files remain in place."""
from pathlib import Path
import json,shutil
from sequence_pilot.cli import Workspace,locked
P=Path(__file__).resolve().parent
rows=json.loads((P/'returned-calls.json').read_text())
for r in rows:
    with locked(P):
        w=Workspace(P)
        if any(c['attempt_id']==r['attempt_id'] for c in w.records('registered')):continue
        incoming=P/'.scratch/incoming'/f"{r['attempt_id']}.png"
        incoming.parent.mkdir(parents=True,exist_ok=True)
        if not incoming.exists():shutil.copyfile(r['source_path'],incoming)
        c=w.register(r['attempt_id'],str(incoming))
        w.select(r['panel'],c['id'])
        print(json.dumps({'panel':r['panel'],'candidate_id':c['id'],'sha256':c['sha256'],'path':c['path']}),flush=True)
