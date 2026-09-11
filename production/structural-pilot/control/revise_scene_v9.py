"""One P12-only structural correction: show separation while preserving lengths/contact."""
import json,math
from pathlib import Path
root=Path(__file__).resolve().parent
data=json.loads((root/'v8'/'scene.json').read_text())
data['revision']='v9: P12-only separated flying fragment and explicit small splinter strokes; frozen v8 selected panels untouched'
p=data['panels']['P12'];length=data['staff_asset']['discarded_fragment_length_m']
start=[4.96,-.29,.93];direction=[-.91,-.1,-.30];norm=math.sqrt(sum(x*x for x in direction))
end=[start[i]+length*direction[i]/norm for i in range(3)]
p['staff']['segments'][1]=[start,end]
p['fracture_splinter_lines']=[[[5.10,-.15,.94],[5.015,-.24,.985]],[[5.105,-.15,1.015],[5.025,-.22,1.065]],[[5.06,-.17,.97],[4.99,-.27,.945]]]
p['note']+=' v9 one correction: the long discarded fragment separates toward camera, exposing the break; short retained piece still ends exactly at the joint contact.'
(root/'v9').mkdir(exist_ok=True)
(root/'v9'/'scene.json').write_text(json.dumps(data,indent=2)+'\n')
