"""Build original schematic storyboard proof from the frozen v2 pilot. No raster inputs."""
import json,html
from pathlib import Path
root=Path(__file__).resolve().parents[3]
plan=json.loads((root/'research/anime-pipeline-total-review/next-pilot-plan.json').read_text())
assert plan['schema']=='NeutralPilotPlan/2'
esc=html.escape
INK='#29343a'; PAPER='#f7f3e9'; BLUE='#375baf'; YELLOW='#e3c565'; VIOLET='#8b54aa'; CORD='#936c39'
def line(x1,y1,x2,y2,c=INK,w=3,extra=''):return f'<path d="M{x1} {y1} L{x2} {y2}" stroke="{c}" stroke-width="{w}" fill="none" {extra}/>'
def path(d,c=INK,w=3,fill='none',extra=''):return f'<path d="{d}" stroke="{c}" stroke-width="{w}" fill="{fill}" {extra}/>'
def rect(x,y,w,h,f,s=INK):return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{f}" stroke="{s}" stroke-width="2"/>'
def ellipse(x,y,rx,ry,f,s=INK):return f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{f}" stroke="{s}" stroke-width="2"/>'
def note(x,y,t):return f'<text class="guide" x="{x}" y="{y}" font-size="11" font-family="sans-serif" fill="#506777">{esc(t)}</text>'
def arrow(d,c=INK):return path(d,c,2,extra='stroke-dasharray="6 4" marker-end="url(#arrow)" class="guide"')
def flask(x,y,s=1):return f'<g transform="translate({x} {y}) scale({s})">'+rect(-6,0,12,22,'#f4efe0')+rect(-4,-5,8,5,CORD)+line(-4,14,4,14,BLUE,2)+'</g>'
def person(x,y,s=1,who='n',pose='stand',fl=False,scrape=False):
 n=who=='n'; color=YELLOW if n else BLUE; skin='#bea48b' if n else '#ad927e'; shoulder=21 if n else 28
 arms={'stand':[(-31,70,-26,98),(31,72,29,97)],'give':[(-28,71,-24,96),(42,65,60,64)],'catch':[(-35,64,-58,64),(31,77,30,95)],'plant':[(-43,66,-55,89),(24,64,2,72)],'brace':[(-38,60,-55,79),(28,60,12,76)],'run':[(-28,63,-49,49),(33,62,45,83)],'vault':[(-37,41,-48,15),(39,47,55,40)],'strike':[(-33,39,-48,20),(28,43,48,27)],'comfort':[(-35,69,-52,81),(38,68,56,80)]}.get(pose,[(0,0,0,0)]*2)
 legs={'plant':[(-35,121,-53,162),(31,126,57,162)],'brace':[(-37,117,-55,151),(39,123,57,151)],'run':[(-19,117,-52,143),(42,115,55,95)],'vault':[(-34,112,-53,122),(29,108,47,90)],'strike':[(-35,112,-45,155),(35,115,65,129)]}.get(pose,[(-13,125,-16,165),(15,125,19,165)])
 a=f'<g transform="translate({x} {y}) scale({s})">'
 for kx,ky,fx,fy in legs:a+=path(f'M{(-10 if kx<0 else 10)} 83 L{kx} {ky} L{fx} {fy}',INK,12)+line(fx-3,fy,fx+10,fy,INK,7)
 if n:a+=path('M-17 31 L24 35 L30 97 L-35 84 Z',INK,2,color)
 else:a+=path('M-28 34 L28 34 L24 88 L-24 88 Z',INK,2,color)+line(-18,78,18,78,PAPER,4)
 for side,(ex,ey,hx,hy) in zip([-1,1],arms):a+=path(f'M{side*shoulder} 38 L{ex} {ey} L{hx} {hy}',color,11)+ellipse(hx,hy,5,6,skin)
 a+=ellipse(0,13,11,16,skin)
 a+=path('M-11 10 Q-14 -7 1 -5 Q13 -5 12 7',INK,4,INK if n else '#c8c8bf')
 a+=line(-7,11,-2,10,INK,1.4)+line(3,10,8,11,INK,1.4)+path('M1 12 L3 19 L0 19',INK,1)+line(-3,24,5,24,INK,1)
 if fl:a+=line(-13,34,17,76,CORD,3)+flask(5,48,.7)
 if scrape:
  hx,hy=arms[1][2:];a+=line(hx-4,hy-2,hx+4,hy+4,'#a95644',2)
 return a+'</g>'
def beast(x,y,s=1,legs=None):
 legs=legs or [(-37,65,-69,110,-80,160),(28,66,56,106,77,152),(3,84,7,136,-4,167)]
 a=f'<g transform="translate({x} {y}) scale({s})">'
 for sx,sy,kx,ky,fx,fy in legs:a+=path(f'M{sx} {sy} L{kx} {ky} L{fx} {fy}',INK,9)+ellipse(kx,ky,6,6,'#9b9fa0')
 a+=path('M0 0 L62 33 L31 94 L-24 94 L-62 33 Z',INK,3,'#747f85')+line(-21,47,25,47,VIOLET,7)
 return a+'</g>'
def room(h,door='closed',tail=None):
 floor=h-30;top=max(25,floor-180)
 a=rect(0,floor-12,390,42,'#d4e0df','#d4e0df')+path(f'M0 {floor-4} L350 {floor-4} L390 {floor+15} L0 {floor+15}',INK,1,'#cec6b4')
 a+=line(24,15,24,floor,INK,5)+line(342,15,342,floor,INK,5)+line(374,15,374,floor,INK,5)
 if door=='closed':a+=rect(345,top,26,floor-top,'#8e999b')+path(' '.join(f'M345 {q}h26' for q in range(int(top+12),int(floor),16)),INK,1)
 elif door=='open':a+=rect(345,top,26,30,'#8e999b')
 else:a+=rect(345,top,26,floor-top-13,'#8e999b')
 # Load cable runs from WEST release fairlead, across overhead pulleys, to EAST shutter.
 a+=path(f'M32 95 V25 H357 V{top}',CORD,3)+ellipse(32,25,6,6,PAPER)+ellipse(357,25,6,6,PAPER)+ellipse(32,95,5,5,PAPER)
 if tail:a+=path(f'M32 95 Q35 {floor-60} {tail[0]} {tail[1]}',CORD,3)
 else:a+=path(f'M32 95 V{floor-15} q22 -15 18 0 q-20 15 -18 0 q15 -12 20 0',CORD,2)
 a+=note(8,14,'WEST')+note(345,14,'EAST')
 return a

def art(i,h):
 a=rect(0,0,390,h,PAPER,PAPER)
 if i==1:
  a+=path('M160 320 L178 234 L305 219 L377 320',INK,3,YELLOW)+ellipse(258,157,52,78,'#bea48b')+path('M204 145 Q186 64 254 65 Q315 63 311 128',INK,6,INK)+path('M214 147 L235 143 M265 141 L285 146 M252 146 L264 177 L253 183 M239 205 L266 201',INK,3)+arrow('M289 161 L364 126')+path('M283 218 Q317 214 321 230 M289 228 Q308 227 312 238','#7f8d90',2)+note(14,35,'NERA · 31 · looking EAST')+note(20,285,'Trembling breath; one adult face.')
 elif i==2:
  a+=room(h);a+=person(130,140,.95,'o','give')+person(255,140,.95,'n','catch');a+=flask(194,196)+arrow('M150 195 L174 195')+arrow('M209 195 L228 195')+line(282,230,324,300,INK,4)+note(102,110,'ONE sealed flask · handoff')
 elif i==3:
  a+=room(h);a+=rect(190,27,75,25,INK)+person(72,112,.5,'o')+person(138,112,.5,'n',fl=True)+line(156,135,167,197,INK,3)+note(158,228,'DRY RIDGE →')+note(47,78,'WEST release + stored travel cord')+note(227,64,'overhead recess')+arrow('M63 213 L320 213')
 elif i==4:
  a+=path('M39 110 L128 68 L300 106 L284 153 L141 108 L61 151',INK,3,'#bea48b')+rect(126,62,59,41,INK)+line(133,76,177,76,YELLOW,3)+line(133,87,161,87,YELLOW,3)+flask(327,52,1.4)+line(347,39,367,153,INK,5)+note(12,24,'Wrist display · no activation')
 elif i==5:
  a+=room(h);a+=rect(152,18,124,80,INK)+path('M163 76 L174 197 M259 79 L258 187',INK,7)+beast(230,183,1.7)+arrow('M310 108 Q346 272 297 422')+person(74,692,.58,'o')+person(130,692,.58,'n',fl=True)+line(140,729,173,802,INK,4)+note(16,534,'Slate kite body; one violet gill; three legs.')+note(19,590,'Threat occupies the EAST route.')+path('M280 440 L293 632 L302 778',INK,11)
 elif i==6:
  a+=room(h,tail=(72,122))+person(87,51,.75,'o','catch')+person(167,70,.85,'n','plant',True)+line(125,145,263,184,INK,5)+beast(312,57,.65)+note(96,29,'PLANTED · no attack yet')+arrow('M97 172 L97 204')
 elif i==7:
  a+=room(h,tail=(65,130))+person(72,102,.8,'o','catch')+person(173,117,.8,'n','brace',True)+beast(285,70,1.05,[(-37,65,-65,114,-121,160),(28,66,56,106,77,152),(3,84,7,136,-4,167)])+line(128,183,201,232,INK,5)+arrow('M326 86 Q267 98 194 215')+path('M152 250 l-17 -9 m17 9 l-5 -20 m5 20 l20 -5','#668c92',3)
 elif i==8:
  a+=room(h,tail=(51,171))+person(193,154,.85,'n','brace',True)+beast(315,76,1.1,[(-37,65,-81,115,-139,157),(28,66,56,106,55,180),(3,84,7,136,-4,195)])+path('M125 212 L162 249 L209 265',INK,6)+ellipse(162,249,11,11,'none')+arrow('M125 259 L155 251')+arrow('M193 236 L167 248')+note(14,48,'CONTACT: forefoot ↔ staff')+note(16,74,'One pulse spent. Second verified counter.')
 elif i==9:
  a+=room(h,tail=(50,126))+person(78,103,.85,'o','catch')+person(207,130,.82,'n','brace',True)+beast(301,78,.95,[(-37,65,-84,111,-151,166),(28,66,-31,38,-191,67),(3,84,15,151,40,185)])+path('M160 191 L157 236 L219 249',INK,5)+ellipse(157,236,12,8,'none')+arrow('M310 47 Q194 33 97 142')+note(105,279,'Pivot about blocked foot; side limb sweeps WEST.')
 elif i==10:
  a+=room(h,tail=(64,247))+person(86,161,.9,'o','give')+person(266,157,.9,'n','give')+flask(141,219)+arrow('M320 215 Q213 61 141 219')+line(282,247,330,310,INK,5)+note(93,58,'One flask · one arc · reciprocal eyelines')+arrow('M252 172 L101 173')+note(48,328,'Odo keeps cord in his other hand.')
 elif i==11:
  a+=room(h,'open',tail=(48,318))+person(91,275,.88,'o','run')+flask(131,348)+person(235,153,1.02,'n','vault')+beast(249,311,.73,[(-37,65,-67,97,-101,116),(28,66,-51,42,-177,56),(3,84,17,136,46,159)])+line(279,195,328,269,INK,5)+arrow('M154 352 Q148 118 239 116 Q287 125 301 297')+path('M206 131 H265 M211 121 H258',INK,4)+arrow('M361 239 L361 94')+note(14,64,'AIR BRAKE: visible stop, then redirected arc')+note(14,87,'Odo pulls WEST release; EAST shutter rises.')+note(14,107,'Free cord travels with him; flask stays upright.')
 elif i==12:
  a+=room(h,'open',tail=(319,356))+beast(257,230,1.14,[(-37,65,0,125,48,215),(28,66,39,99,52,181),(3,84,-43,150,-78,201)])+person(349,326,.62,'o','run')+flask(377,378,.8)+person(205,299,1.12,'n','strike')
  a+=path('M151 321 L250 369',INK,6)+path('M263 376 L307 403',INK,6)+path('M249 365 l-6 -6 10 2 -1 8 10 1',INK,2)+ellipse(257,373,13,13,'none')+line(249,362,242,350,'#a95644',3)+arrow('M169 296 L242 358')+arrow('M296 402 L271 382')+note(14,65,'ONE contact · staff breaks at joint')+note(14,88,'Scraped hand begins here; no obscuring effect cloud.')+note(14,116,'Odo crosses EAST, carrying the long return cord.')+arrow('M337 462 L383 462')
 elif i==13:
  # Re-establishing wide frame shifts shutter leftward to show safe EAST side, preserving axis.
  floor=h-35;a+=rect(0,floor,390,35,'#d4e0df')+rect(188,30,26,floor-44,'#8e999b')+line(186,14,186,floor,INK,5)+line(217,14,217,floor,INK,5)+beast(97,121,.73,[(-37,65,-70,132,-77,208),(28,66,100,267,157,269),(3,84,4,149,4,218)])+person(254,184,.73,'n','stand',False,True)+person(332,181,.76,'o','comfort')+flask(375,242)+line(231,249,258,277,INK,5)+line(162,300,190,316,INK,5)+path('M7 24 H202 V45 M7 24 V298 Q87 340 319 313',CORD,3)+arrow('M312 279 L319 310')+note(10,14,'WEST: threat alive')+note(224,14,'EAST: both adults safe')+note(9,347,'Released cord falls slack. Shutter pins foreleg.')
 elif i==14:
  a+=rect(0,0,21,h,'#8e999b')+person(142,144,1.45,'n','comfort',False,True)+person(298,134,1.45,'o','comfort')+flask(379,252,1.1)+line(67,263,91,302,INK,6)+path('M216 260 Q228 241 249 257',INK,3,'#ad927e')+line(217,260,225,265,'#a95644',3)+note(33,52,'Beyond the shutter · consequence held')+note(33,80,'ONE charge remains · staff stays broken')+arrow('M310 97 L369 97')
 return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 390 {h}" role="img" aria-label="{esc(plan["panels"][i-1]["beat"])}"><defs><marker id="arrow" markerWidth="7" markerHeight="7" refX="6" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6" fill="{INK}"/></marker></defs>{a}</svg>'.replace('id="arrow"',f'id="arrow-{i}"').replace('url(#arrow)',f'url(#arrow-{i})')

cards=[]
for p in plan['panels']:
 i=p['panel'];copy=[]
 for raw in p['copy']:
  speaker,body=(raw.split(': ',1) if ': ' in raw else ('SYSTEM',raw));kind='system' if speaker=='SYSTEM' else 'sfx' if speaker=='SFX' else 'speech'
  copy.append(f'<div class="utterance {kind}" data-speaker="{speaker}"><span class="speaker">{speaker}</span><span class="words" data-base="{esc(body,quote=True)}">{esc(body)}</span></div>')
 text=f'<div class="lettering">{"".join(copy)}</div>' if copy else ''
 cards.append(f'<section class="panel" id="p{i:02}" aria-labelledby="t{i}"><h2 id="t{i}"><span>P{i:02}</span> {esc(p["function"])} <small>{p["target_css_height_at390"]} px art at 390</small></h2>{text}<div class="art" style="aspect-ratio:390/{p["target_css_height_at390"]}">{art(i,p["target_css_height_at390"])}</div><details class="intent"><summary>Intent and continuity contract</summary><p>{esc(p["beat"])}</p><p>{esc(p["continuity_contract"])}</p></details></section>')
transcript=''.join(f'<li><strong>P{p["panel"]:02} · {esc(p["function"])}</strong><p>{esc(p["beat"])}</p><p>{esc(" / ".join(p["copy"]) or "Silent.")}</p></li>' for p in plan['panels'])
page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Three Charges, One Dose — rough proof</title><style>
*{box-sizing:border-box}body{margin:0;background:#172126;color:#f4efe5;font:16px/1.45 system-ui,sans-serif}a{color:#e7cf86}header,footer,.controls,.transcript{max-width:760px;padding:18px 16px;margin:auto}h1{font-size:30px;line-height:1.08;margin:8px 0}header p{margin:10px 0}.status{font-size:13px;color:#e7cf86}.controls{display:flex;gap:10px;flex-wrap:wrap;align-items:center;border-block:1px solid #607076}button,select{font:inherit;padding:7px;background:#f7f3e9;color:#25323a;border:1px solid #a9adb0;border-radius:4px}button:focus-visible,a:focus-visible,summary:focus-visible{outline:3px solid #ddb94f;outline-offset:3px}nav{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px}nav a{padding:3px}.reader{width:100%;max-width:720px;margin:auto}.panel{margin:14px 0 0;background:#f7f3e9;color:#26343b;scroll-margin-top:10px}.panel h2{font:600 13px/1.3 system-ui;margin:0;padding:8px 12px;background:#e1e5e3;display:flex;gap:9px;flex-wrap:wrap}.panel h2 small{font-size:11px;font-weight:400;margin-left:auto}.art{width:100%;overflow:hidden}.art svg{display:block;width:100%;height:100%}.lettering{display:flex;gap:10px;padding:10px 14px 12px;align-items:flex-start;background:#f7f3e9}.utterance{background:#fffefa;border:1.7px solid #29343a;border-radius:17px;padding:8px 11px;flex:1;min-width:0;font-size:16px;line-height:1.25;overflow-wrap:anywhere}.speaker{display:block;font-size:10px;letter-spacing:.08em;font-weight:650;margin-bottom:3px}.system{background:#29343a;color:#f7f3e9;border-radius:3px;font-size:14px}.sfx{border:0;border-radius:0;font-size:24px;font-weight:800;letter-spacing:.05em;background:transparent}.intent{display:none;padding:5px 12px;font-size:12px;border-top:1px solid #c3cbc7}.show-contracts .intent{display:block}.intent summary{cursor:pointer;color:#50616b}.intent p{margin:8px 0}.no-guides .guide{display:none}.gray .art{filter:grayscale(1)}.transcript{border-top:1px solid #607076;margin-top:24px}.transcript ol{padding-left:23px}.transcript li{margin-bottom:22px}.transcript p{margin:5px 0}.readout{font-size:12px;width:100%;color:#cad6d6}footer{font-size:13px}#expansion-note{color:#e7cf86;font-size:13px} @media(min-width:800px){.utterance{font-size:18px}.system{font-size:16px}}@media(prefers-reduced-motion:no-preference){html{scroll-behavior:smooth}}
</style><body><header><a href="index.html">← Review hub</a><h1>Three Charges,<br>One Dose</h1><p class="status">V2 rough vector storyboard · unaccepted · owner-review-pending · commercially uncleared</p><p>Fourteen original rough panels test staging and live lettering. This is not finished art, a production comparison, or evidence of a winning route.</p><details style="font-size:13px"><summary>Adult cast and cord routing</summary><p>Adult cast: Nera, 31; Odo, 38. The west release has a long free return cord: Odo carries it east while holding the shutter open, then lets it fall slack behind both adults.</p></details><nav aria-label="Panel navigation">NAV</nav></header><div class="controls"><label>Copy stress <select id="expansion"><option value="0">Original</option><option value=".3">+30% synthetic</option><option value=".5">+50% synthetic</option></select></label><label><input id="guides" type="checkbox" checked> Staging marks</label><label><input id="gray" type="checkbox"> Grayscale</label><label><input id="contracts" type="checkbox"> Contracts</label><span id="expansion-note">Exact frozen copy. No font shrinking.</span><output class="readout" id="readout"></output></div><main class="reader" aria-label="Continuous rough storyboard">CARDS</main><details class="transcript"><summary>Accessible transcript · all 14 panels</summary><ol>TRANSCRIPT</ol></details><footer><details><summary>Proof scope and production limits</summary><p>Art heights follow frozen V2 targets: 5,360 CSS pixels total at a 390-pixel reader width. Lettering sits in independent flowing lanes; expansion increases scroll length rather than shrinking type or covering art. These lanes are a layout proof, not finished speech-tail design.</p><p>The cord routing is an explicit rough proposal resolving the residual physical-continuity question. A skilled storyboard artist must still verify grips, travel length, joint/contact mechanics and the crossing timing. No production acceptance gates or human comprehension tests have been passed by this schematic.</p></details><p><a href="../../../research/anime-pipeline-total-review/next-pilot-plan.json">Frozen V2 machine plan</a> · <a href="../../../research/anime-pipeline-total-review/next-pilot-specification.md">Pilot specification</a></p></footer><script>
const select=document.querySelector('#expansion');function update(){const n=Number(select.value);document.querySelectorAll('.words').forEach(el=>{const base=el.dataset.base,extra=Math.ceil(base.length*n);el.textContent=base+(extra?(' test copy'.repeat(Math.ceil(extra/10)+1)).slice(0,extra):'')});document.querySelector('#expansion-note').textContent=n?'Artificial length padding only; not a translation. Original copy is preserved in the transcript.':'Exact frozen copy. No font shrinking.';requestAnimationFrame(measure)}function measure(){const reader=document.querySelector('.reader'),art=[...document.querySelectorAll('.art')].reduce((n,e)=>n+e.getBoundingClientRect().height,0);document.querySelector('#readout').textContent=`Reader width ${Math.round(reader.clientWidth)} px · art ${Math.round(art)} px · story strip ${Math.round(reader.getBoundingClientRect().height)} px · complete page ${document.documentElement.scrollHeight} px · 14 panels`;}
select.addEventListener('change',update);document.querySelector('#contracts').addEventListener('change',e=>{document.body.classList.toggle('show-contracts',e.target.checked);measure()});document.querySelector('#guides').addEventListener('change',e=>document.body.classList.toggle('no-guides',!e.target.checked));document.querySelector('#gray').addEventListener('change',e=>document.body.classList.toggle('gray',e.target.checked));addEventListener('resize',measure);update();
</script></body></html>'''
page=page.replace('NAV',''.join(f'<a href="#p{i:02}">{i:02}</a>' for i in range(1,15))).replace('CARDS',''.join(cards)).replace('TRANSCRIPT',transcript)
out=root/'docs/research/anime-pipeline-total-review/pilot-proof.html';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(page)
print(out)
