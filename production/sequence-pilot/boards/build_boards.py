"""Original editable layout diagrams. Standard library only; never final art."""
from pathlib import Path
import hashlib
import html
import json

HERE = Path(__file__).resolve().parent
PLAN = HERE.parent / "plan.json"
INK = "#25303b"
YELLOW = "#dfc969"
BLUE = "#3d65af"
SKIN = "#b58467"


def path(d, stroke=INK, width=3, fill="none", extra=""):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round" {extra}/>'


def line(x1, y1, x2, y2, color=INK, width=3, extra=""):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}" stroke-linecap="round" {extra}/>'


def rect(x,y,w,h,fill,stroke="none",radius=0):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}"/>'


def ellipse(x,y,rx,ry,fill,stroke=INK):
    return f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'


def group(name, content):
    return f'<g id="{name}" data-editable-layer="true">{content}</g>'


def flask(x,y,scale=1):
    return f'<g transform="translate({x} {y}) scale({scale})">'+rect(-6,-11,12,23,"#ad7433",INK,3)+rect(-5,-15,10,5,"#ddd7c7",INK)+line(-2,-7,-2,7,"#f4ce89",2)+"</g>"


def adult(name,x,y,s=1,pose="stand",angle=0,flask_here=False,injury=False):
    """x,y are the crown; 114 units crown-to-sole, adult ~7.5-head proportions."""
    color=YELLOW if name=="nera" else BLUE
    width=13 if name=="nera" else 17
    poses={
        "stand": ((-21,48),(24,49),(-12,110),(15,110),(-10,80),(12,80)),
        "offer": ((-20,45),(43,45),(-12,110),(15,110),(-10,80),(12,80)),
        "receive": ((-38,46),(25,52),(-12,110),(15,110),(-10,80),(12,80)),
        "plant": ((19,50),(39,61),(-29,108),(32,108),(-23,82),(22,85)),
        "release": ((-31,24),(21,49),(-12,110),(15,110),(-10,80),(12,80)),
        "crouch": ((24,43),(41,50),(-31,91),(35,97),(-20,63),(25,71)),
        "toss": ((-43,33),(18,48),(-19,109),(21,109),(-12,81),(16,82)),
        "catch": ((-22,37),(41,37),(-12,110),(15,110),(-10,80),(12,80)),
        "vault": ((-31,7),(40,21),(-30,79),(34,70),(-27,52),(20,60)),
        "strike": ((27,37),(43,49),(-29,97),(25,102),(-24,71),(18,76)),
        "run": ((-30,32),(30,47),(-30,98),(35,100),(-20,71),(20,85)),
        "hurt": ((-24,43),(18,40),(-12,110),(15,110),(-10,80),(12,80)),
    }
    lh,rh,lf,rf,lk,rk=poses[pose]
    c=ellipse(0,10,6.5,9,SKIN)
    c+=path("M-7 9 Q-10 -3 0 0 Q9 -2 7 9",width=2,fill="#252730" if name=="nera" else "#bec3ca")
    c+=line(1,10,5,10,INK,1)+line(2,15,5,15,INK,1)
    c+=path(f"M-5 20 L{-width} 26 L{-width+3} 59 L{width-2} 59 L{width} 26 L5 20 Z",fill=color)
    if name=="nera":
        c+=path("M-7 21 L-20 45 L-7 40 L13 49 L14 26 Z",width=2,fill=color)
    c+=path(f"M{-width} 29 L{lh[0]} {lh[1]} M{width} 29 L{rh[0]} {rh[1]}",stroke=color,width=9)
    c+=ellipse(*lh,3.5,4,SKIN)+ellipse(*rh,3.5,4,SKIN)
    c+=path(f"M-7 59 L{lk[0]} {lk[1]} L{lf[0]} {lf[1]} M7 59 L{rk[0]} {rk[1]} L{rf[0]} {rf[1]}",width=10)
    c+=line(lf[0]-2,lf[1],lf[0]+6,lf[1],INK,6)+line(rf[0]-2,rf[1],rf[0]+6,rf[1],INK,6)
    if flask_here:
        c+=flask(0,41,.65)
    if injury:
        c+=path(f"M{rh[0]-3} {rh[1]-2} l5 3 m-5 0 l4 3",stroke="#a93c43",width=1.7)
    return f'<g id="actor-{name}" transform="translate({x} {y}) rotate({angle}) scale({s})">{c}</g>'


def sentinel(body,legs):
    """Three separate articulated paths always, including occluded/cropped legs."""
    x,y,s=body
    c="".join(path(d,"#657181",10) + path(d,INK,2) for d in legs)
    c+=path(f"M{x-48*s} {y} L{x+9*s} {y-26*s} L{x+51*s} {y+2*s} L{x-2*s} {y+30*s} Z",fill="#667481")
    c+=line(x-15*s,y+4*s,x+17*s,y+4*s,"#b585d4",4)
    return c


def room(h,shutter="closed",wide=False):
    floor=h*.86
    c=rect(0,0,390,h,"#e8ece9")
    c+=path(f"M0 {h*.32} H390 M0 {floor} H390",stroke="#c4cdce",width=2)
    c+=rect(0,floor,390,h-floor,"#9cadb4")
    c+=path(f"M0 {floor-8} H390 V{floor+10} H0 Z",fill="#a49c87",stroke="#788185",width=1)
    c+=rect(22,25,17,max(20,floor-25),"#8f9da1")
    c+=rect(242,22,76,30,"#424d59")
    doorx=341
    c+=rect(doorx,45,44,max(20,floor-45),"#dfe4dd",INK)
    bottom=floor if shutter=="closed" else floor-91 if shutter=="open" else floor-9
    c+=rect(doorx,45,44,max(5,bottom-45),"#7b8790",INK)
    for yy in range(57,int(bottom),13):
        c+=line(doorx+2,yy,383,yy,"#53616b",1)
    c+=path(f"M30 {floor-65} V35 H364 V45",stroke="#424b54",width=2)
    c+=ellipse(30,floor-65,6,6,"#d3c6a2")
    return c


def arrow(d,color="#517588"):
    return path(d,color,2.6,extra='stroke-dasharray="6 5" marker-end="url(#arrow)"')


def burst(x,y,r=20):
    return ''.join(line(x+dx*.55,y+dy*.55,x+dx,y+dy,"#e69c44",3) for dx,dy in [(-r,0),(r,0),(0,-r),(0,r),(-r*.7,-r*.7),(r*.7,r*.7),(-r*.7,r*.7),(r*.7,-r*.7)])


def normalized(rectangle,h):
    x,y,w,hh=rectangle
    return [round(x/390,4),round(y/h,4),round(w/390,4),round(hh/h,4)]


def build(panel):
    n=panel["panel"]; h=panel["target_css_height_at390"]
    bg=room(h); actors=""; props=""; threat=""; fx=""
    zones=[]; positions={}; protected=[]; offscreen=[]; notes=[]
    def person(name,x,y,s=1,pose="stand",angle=0,**kwargs):
        nonlocal actors
        actors+=adult(name,x,y,s,pose,angle,**kwargs)
        positions[name]={"crown":[round(x/390,4),round(y/h,4)],"scale":s,"pose":pose,"rotation_degrees":angle}
        if angle==0:
            protected.append({"kind":"face","actor":name,"rect":normalized((x-10*s,y-2*s,20*s,23*s),h)})
    def protect(kind,r):
        protected.append({"kind":kind,"rect":normalized(r,h)})
    def staff(x1,y1,x2,y2,broken=False):
        nonlocal props
        if broken:
            props+=line(x1,y1,x2,y2,"#574b3c",5)
        else:
            props+=line(x1,y1,x2,y2,"#574b3c",5)
    if n==1:
        bg=rect(0,0,390,h,"#d9e1df")+path("M302 0 V320",stroke="#f7f4d9",width=56)
        person("nera",210,114,4.1)
        zones=[(18,18,170,72)]
        offscreen=["Odo with sealed flask","Nera intact staff","wrist charge display","closed east shutter"]
        notes=["Mature face and cape close-up; lower body deliberately cropped. Exit light is screen-right."]
    elif n==2:
        person("odo",118,150,1.65,"offer")
        person("nera",265,150,1.65,"receive")
        props+=flask(196,224,1.05); staff(306,235,327,348)
        protect("flask handoff",(167,196,77,66));zones=[(17,18,181,91),(211,47,165,76)]
        notes=["One flask at the shared handoff; Odo left, Nera right. Both west of closed exit."]
    elif n==3:
        person("odo",73,135,.62,"release");person("nera",132,132,.65,flask_here=True)
        staff(151,159,166,205);props+=path("M30 141 Q52 167 52 202",stroke="#7e6651",width=2)
        notes=["No visible monster. Left pillar release connects overhead to right shutter. Long free cord hangs at west pillar."]
    elif n==4:
        bg=rect(0,0,390,h,"#e7e7db")
        actors=path("M-20 116 L135 101 L220 126 L240 163 L129 143 L-20 161 Z",fill=SKIN)
        props+=rect(135,98,42,42,"#293642",INK,5)+rect(143,106,26,21,"#92c2c5",INK,2)
        props+=flask(294,131,1.1);staff(340,95,371,174)
        protect("wrist hand and inert display",(111,94,126,75));zones=[(17,15,353,63)]
        offscreen=["adult faces","Odo","whole gallery"]
        notes=["Display is blank for live UI overlay in reserved upper margin. Flask and intact staff are insert detail, not duplicated in another hand."]
    elif n==5:
        bg=room(h)+rect(129,44,204,179,"#414c58")
        threat=sentinel((268,291,1.7),["M242 321 L188 428 L220 576","M277 329 L336 466 L305 690","M313 310 L355 399 L371 540"])
        person("odo",67,652,.8,"release");person("nera",127,651,.9,flask_here=True)
        staff(147,697,164,755)
        fx=arrow("M261 186 Q265 207 265 227")
        notes=["Long visual descent: dark overhead recess, kite body, exactly three unfurling legs, small west-side adults. Sentinel blocks east route; no attack contact yet."]
    elif n==6:
        person("odo",61,99,.86,"release");person("nera",151,100,.91,"plant",flask_here=True)
        staff(154,141,228,194)
        threat=sentinel((322,106,.65),["M300 119 L273 157 L277 196","M326 125 L346 159 L335 199","M342 114 L371 145 L376 188"])
        props+=path("M30 141 L34 122",stroke="#7e6651",width=2)
        zones=[(90,15,224,62)]
        notes=["Staff lowers across the forefoot path without touching yet. Odo reaches west release."]
    elif n==7:
        person("odo",55,146,.85,"release");person("nera",143,154,.93,"crouch",flask_here=True)
        staff(163,193,219,251)
        threat=sentinel((306,160,.9),["M277 178 L239 195 L216 237","M309 185 L342 220 L336 256","M334 169 L369 204 L375 244"])
        fx=arrow("M308 125 Q263 126 221 168")+path("M208 263 l-14 -9 m21 10 l7 -13 m-1 18 l22 -4",stroke="#eef4ec",width=3)
        zones=[(249,22,125,48)];protect("forefoot approach",(191,212,46,47))
        notes=["Right-to-left lunge. Forefoot still separated from staff by a small visible gap; contact is next panel."]
    elif n==8:
        person("nera",107,161,1.3,"crouch",flask_here=True)
        props+=path("M138 217 L160 226 L190 254 L209 272",stroke="#574b3c",width=5)
        threat=sentinel((327,190,1.0),["M291 207 L249 231 L190 254","M331 212 L353 261 L338 298","M356 190 L385 222 L405 281"])
        fx=burst(190,254,22)+path("M60 291 l-15 7 m27 -1 l-12 9",stroke="#819a9e",width=2)
        zones=[(15,16,357,91)];protect("staff forefoot contact",(168,231,47,46))
        offscreen=["Odo remains at west release","full third sentinel leg cropped right"]
        notes=["Staff/forefoot contact center is (190,254). Bent knees oppose leftward force; violet gill remains active. UI overlay must show 3 to 2 and second-counter unlock."]
    elif n==9:
        person("odo",60,149,.83,"release");person("nera",165,167,.81,"crouch",flask_here=True)
        staff(174,188,231,240)
        threat=sentinel((301,135,.93),["M275 149 L251 193 L220 229","M303 160 L204 167 L94 183","M334 143 L369 184 L373 241"])
        fx=arrow("M308 94 Q210 84 118 139")
        protect("new side-leg threat to Odo",(81,159,143,41))
        notes=["Pivot around still blocked forefoot; a DIFFERENT leg extends toward Odo on west pillar. A curved vector makes reversal distinct from first lunge."]
    elif n==10:
        person("odo",79,181,1.28,"catch");person("nera",280,186,1.22,"toss")
        staff(300,235,329,319)
        props+=flask(176,166,.9)
        fx=arrow("M231 219 Q197 128 136 205")
        zones=[(210,19,163,60),(20,91,122,58)];protect("single flask trajectory",(129,142,93,58))
        offscreen=["sentinel side-leg sweep outside close two-shot","flask temporarily airborne before Odo receives"]
        notes=["One flask only, cap upward on arc Nera right to Odo left. Nera sling empty. Odo left hand remains assigned release cord; right catches."]
    elif n==11:
        bg=room(h,"open")
        person("nera",219,188,1.05,"vault",angle=-18)
        person("odo",111,331,.84,"run")
        props+=flask(139,370,.62)
        props+=path("M30 365 Q34 415 68 406 L86 358",stroke="#7e6651",width=2)
        staff(244,193,294,246)
        threat=sentinel((306,323,.9),["M280 338 L260 378 L234 414","M309 346 L194 359 L92 381","M338 329 L369 365 L376 410"])
        fx=arrow("M130 355 Q155 208 218 176 Q265 179 285 279")+path("M185 195 l22 -14 m-17 27 l24 -13 m-6 36 l18 -13",stroke="#81c8d1",width=5)
        zones=[(20,18,348,68)];protect("vault body and brake accent",(171,167,107,118))
        notes=["Only one Nera body. Dashed trajectory rises from west, stalls at cyan braking bars, then redirects down-right. Odo carries upright flask and continuous release cord, starts east. Shutter visibly raised."]
    elif n==12:
        bg=room(h,"open")
        person("nera",191,279,1.34,"strike",injury=True)
        person("odo",353,380,.72,"run")
        props+=flask(375,414,.6)
        props+=path("M30 408 Q107 469 223 462 L331 403",stroke="#7e6651",width=2)
        threat=sentinel((277,262,.95),["M246 282 L256 360 L287 443","M283 288 L319 355 L322 449","M308 269 L351 316 L342 368"])
        staff(227,329,253,357,True);staff(264,367,290,408,True)
        fx=burst(257,360,27)+arrow("M198 209 Q225 250 249 314")
        zones=[(18,20,142,62)];protect("broken staff joint impact and scraped hand",(226,323,66,70))
        notes=["ONE contact at forelimb joint (257,360), exposed between two staff pieces. Small red scrape on Nera right hand; no cloud hides contact. Odo slips through screen-right opening, flask upright, cord continuous."]
    elif n==13:
        bg=rect(0,0,390,h,"#e6e9df")+rect(0,290,390,70,"#aab8bb")+path("M0 284 H390 V299 H0Z",fill="#aaa18d",width=1)
        bg+=rect(178,23,30,265,"#75828a",INK)
        for yy in range(35,278,15): bg+=line(181,yy,205,yy,"#43525b",1)
        threat=sentinel((79,195,.78),["M102 212 L145 249 L193 287","M65 214 L33 251 L19 291","M50 194 L19 219 L5 269"])
        person("nera",251,178,.97,"hurt",injury=True);person("odo",332,170,1.04,"receive")
        staff(228,220,252,250,True)
        props+=line(217,295,237,306,"#574b3c",4)+flask(357,224,.72)
        props+=path("M1 33 H191 V28 M190 291 Q244 306 298 284",stroke="#7e6651",width=2)
        fx=arrow("M219 201 V262")+path("M91 181 l9 -6 m-2 14 l11 -2",stroke="#b585d4",width=2)
        protect("shutter pinning living foreleg",(165,265,48,39))
        notes=["Camera moves east with adults while preserving west-left/east-right axis. Door is now screen center, both adults to its RIGHT. Living violet-gill sentinel remains left; foreleg pinned under bottom edge. Free cord falls slack on east floor."]
    elif n==14:
        bg=rect(0,0,390,h,"#e8e3d0")+rect(9,0,18,440,"#869296")
        person("nera",140,173,1.9,"hurt",injury=True);person("odo",275,163,1.97,"receive")
        props+=flask(325,271,.9);staff(94,255,111,314,True)
        props+=path("M175 249 Q190 261 201 254",stroke=SKIN,width=9)
        props+=path("M172 247 l6 5 m-7 -1 l6 5",stroke="#a93c43",width=2)
        zones=[(204,19,167,62),(25,92,143,56)];protect("steadied scraped hand",(162,235,62,42))
        offscreen=["second loose broken staff piece on prior-panel east floor","living sentinel west beyond closed shutter","wrist charge display"]
        notes=["Odo steadies Nera scraped hand at shared center; separate outer hand holds one sealed upright flask. Nera retains short broken staff. Final charge1 state remains recorded, not automatically inferred from cropped wrist."]
    for z in zones:
        # Deliberate blank space, boundary only; no baked story text.
        bg+=rect(*z,"#f6f4e9","#bdc8c8",8)
    markup=f'''<svg xmlns="http://www.w3.org/2000/svg" width="390" height="{h}" viewBox="0 0 390 {h}" role="img" aria-labelledby="title desc">
<title id="title">Panel {n:02d}: original {html.escape(panel['camera'])} layout diagram</title>
<desc id="desc">Editable storyboard expectation, not final illustration or observed generated art. {html.escape(' '.join(notes))}</desc>
<defs><marker id="arrow" markerWidth="7" markerHeight="7" refX="5" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6" fill="none" stroke="#517588" stroke-width="1.5"/></marker></defs>
{group('background',bg)}{group('threat',threat)}{group('actors',actors)}{group('props',props)}{group('effects',fx)}
</svg>'''
    layout={"panel":n,"file":f"p{n:02d}.svg","camera":panel["camera"],"width":390,"height":h,"coordinate_system":"normalized [x,y,width,height], origin top-left","evidence_class":"EXPECTED_STORYBOARD_LAYOUT_NOT_OBSERVED_GENERATED_ART","actor_positions":positions,"protected_zones_expected":protected,"reserved_lettering_zones":[normalized(z,h) for z in zones],"offscreen_or_cropped":offscreen,"deliberate_choices":notes,"beat":panel["beat"],"continuity_contract":panel["continuity_contract"]}
    return markup,layout


def main():
    data=json.loads(PLAN.read_text())
    layouts=[];cards=[]
    for panel in data["panels"]:
        markup,layout=build(panel)
        (HERE/layout["file"]).write_text(markup)
        layout["sha256"]=hashlib.sha256(markup.encode()).hexdigest()
        layouts.append(layout)
        cards.append(f'<article><h2>P{panel["panel"]:02d} · {html.escape(panel["function"])}</h2><a href="{layout["file"]}"><img src="{layout["file"]}" alt="Panel {panel["panel"]} editable layout diagram" width="390" height="{layout["height"]}"></a><p>{html.escape(panel["beat"])}</p><p class="note">{html.escape(" ".join(layout["deliberate_choices"]))}</p></article>')
    metadata={"schema":"PilotStoryboardLayouts/1","plan_sha256":hashlib.sha256(PLAN.read_bytes()).hexdigest(),"authorship":"Original code-native SVG authored for this pilot; no imported art or inherited board drawings.","status":"DRAFT_LAYOUT_EXPECTATIONS; NOT_HUMAN_APPROVED; NOT_FINAL_ART","diagram_conventions":{"nera":"yellow cape, long adult proportions","odo":"broad blue jacket, silver hair","sentinel":"slate kite body, exactly three leg paths, violet gill","dashed_blue_arrow":"motion expectation, not extra body","cyan_bars":"Air Brake halt accent","pale_outlined_rectangle":"reserved blank lettering margin, not final balloon","separate_group_ids":["background","threat","actors","props","effects"]},"panels":layouts}
    (HERE/"layouts.json").write_text(json.dumps(metadata,indent=2)+"\n")
    document='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Three Charges, One Dose — original editable storyboards</title><style>*{box-sizing:border-box}body{margin:0;background:#17232d;color:#edf0e9;font:16px/1.5 system-ui,sans-serif}header{max-width:1050px;padding:32px 20px;margin:auto}h1{font-size:30px;line-height:1.2}header p{max-width:780px}a{color:#eed479}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,390px),1fr));gap:24px;align-items:start;max-width:1280px;padding:20px;margin:auto}article{background:#26333e;border:1px solid #50606b;border-radius:8px;padding:14px;min-width:0}h2{font-size:18px;margin:0 0 12px}img{display:block;width:100%;max-width:390px;height:auto;margin:auto}p{margin:14px 0}.note{color:#bfcdd4;font-size:14px}a:focus-visible{outline:3px solid #efcc6c;outline-offset:5px}</style><header><h1>Three Charges, One Dose</h1><p>Fourteen original editable storyboard diagrams. These are draft composition and continuity expectations, not finished illustrations, observed generated-art annotations or a quality verdict. Pale outlined areas reserve lettering space; no story copy is baked into the art.</p><p>Yellow: Nera · Blue: Odo · Slate kite: three-legged sentinel · Dashed arrow: motion · Cyan bars: Air Brake. Each SVG exposes background, threat, actors, props and effects groups.</p><p><a href="layouts.json">Layout coordinates and state notes</a> · <a href="build_boards.py">Reproducible source</a> · <a href="../plan.json">Frozen pilot plan</a></p></header><main>'''+"\n".join(cards)+"</main></html>"
    (HERE/"index.html").write_text(document)
    print(f"Wrote {len(layouts)} original editable diagrams; plan {metadata['plan_sha256']}")


if __name__=="__main__":
    main()
