#!/usr/bin/env python3
"""Replace only the G04 flanker mace with a downward, noncontact sword."""
from pathlib import Path
import json,hashlib
HERE=Path(__file__).resolve().parent;source=HERE/'v3-contact/G04-water-foot-wedge.svg';out=HERE/'v5-sword-continuity';out.mkdir(exist_ok=False)
s=source.read_text();a=s.index('<path d="M688,490 L651,585"');b=s.index('<circle cx="688" cy="490"',a)
s=s[:a]+'''<g id="retained-sword-point-down-away"><path d="M681,513 L632,613 L628,617 L675,511 Z" fill="#c1c7c8" stroke="#293843" stroke-width="4"/><path d="M695,473 L678,512" stroke="#293843" stroke-width="11" stroke-linecap="round"/><path d="M663,505 L694,520" stroke="#293843" stroke-width="7" stroke-linecap="round"/><circle cx="695" cy="473" r="6" fill="#a49587" stroke="#293843" stroke-width="3"/></g>'''+s[b:]
p=out/'G04-sword-water-foot-wedge.svg';p.write_text(s);record={'records':[{'id':'G04-sword-water-foot-wedge','svg':str(p.relative_to(HERE)),'svg_sha256':hashlib.sha256(p.read_bytes()).hexdigest()}],'derived_from':{'path':str(source.relative_to(HERE)),'sha256':hashlib.sha256(source.read_bytes()).hexdigest()},'changes':'Only enemy weapon replaced; hilt uses unchanged hand, sword points down and away with no contact. All figure, source blade, ice, water and foot positions unchanged.'};(out/'manifest.json').write_text(json.dumps(record,indent=2)+'\n');(HERE/'render_svg_native_v5.py').write_text((HERE/'render_svg_native_v2.py').read_text().replace('v2-guides/','v5-sword-continuity/'))
