"""Preserve v1; create the first full pass set with a brighter exterior field."""
import json
from pathlib import Path
root=Path(__file__).resolve().parent
data=json.loads((root/'v1'/'scene.json').read_text())
data['revision']='v2: ivory exterior and full layered exports; no generated art'
(root/'v2').mkdir(exist_ok=True)
(root/'v2'/'scene.json').write_text(json.dumps(data,indent=2)+'\n')
