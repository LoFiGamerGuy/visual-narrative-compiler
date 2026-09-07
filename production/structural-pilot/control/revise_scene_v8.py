"""Close cross-gallery partition returns; retain length-locked v7 poses."""
import json
from pathlib import Path
root=Path(__file__).resolve().parent
data=json.loads((root/'v7'/'scene.json').read_text())
data['revision']='v8: opaque cross-gallery partition returns close the floor-width bypass; all v7 lengths and poses retained'
data['gallery']['partition_coverage_y']=[-1.9,1.9]
data['gallery']['floor_coverage_y']=[-1.9,1.9]
data['gallery']['partition_solid_intervals_y']=[[-1.9,-1.1],[-1.205,-.995],[-1.0,1.54],[1.49,1.81],[1.66,1.9]]
data['gallery']['cutaway_note']='Only south longitudinal wall is omitted. Cross-gallery partition is continuous across the floor, with a working shutter opening.'
(root/'v8').mkdir(exist_ok=True)
(root/'v8'/'scene.json').write_text(json.dumps(data,indent=2)+'\n')
