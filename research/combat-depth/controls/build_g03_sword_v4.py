#!/usr/bin/env python3
"""Preserve prior controls; replace only G03 mace with existing sword pommel strike."""
from pathlib import Path
import re,json,hashlib
HERE=Path(__file__).resolve().parent
source=HERE/'v2-guides/G03-brace-break.svg';target=HERE/'v4-sword-continuity';target.mkdir(exist_ok=False)
s=source.read_text()
s=s.replace('M920,412 L855,370 L775,375','M920,412 L795,355 L646,319')
s=s.replace('<circle cx="775" cy="375" r="12" fill="#ded2bf" stroke="#293843" stroke-width="3"/>','')
a=s.index('<path d="M775,375 L636,349"');b=s.index('<path d="M703,402',a)
s=s[:a]+'''<g id="existing-sword-pommel-strike"><path d="M670,291 L852,69 L858,74 L679,298 Z" fill="#c1c7c8" stroke="#293843" stroke-width="4"/><path d="M624,343 L674,291" fill="none" stroke="#293843" stroke-width="13" stroke-linecap="round"/><path d="M655,278 L690,310" fill="none" stroke="#293843" stroke-width="8" stroke-linecap="round"/><circle cx="624" cy="343" r="10" fill="#a49587" stroke="#293843" stroke-width="4"/><circle cx="646" cy="319" r="12" fill="#ded2bf" stroke="#293843" stroke-width="3"/></g>'''+s[b:]
p=target/'G03-sword-pommel.svg';p.write_text(s)
manifest={'records':[{'id':'G03-sword-pommel','svg':str(p.relative_to(HERE)),'svg_sha256':hashlib.sha256(p.read_bytes()).hexdigest()}],'derived_from':{'path':str(source.relative_to(HERE)),'sha256':hashlib.sha256(source.read_bytes()).hexdigest()},'changes':'Only striking forearm endpoint and weapon changed: retained sword pommel contacts shoulder; blade points upward and away. Actors, shield, pressure-spill vector, pier, stone trajectory and floor unchanged.'}
(target/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
renderer=(HERE/'render_svg_native_v2.py').read_text().replace('v2-guides/','v4-sword-continuity/')
(HERE/'render_svg_native_v4.py').write_text(renderer)
