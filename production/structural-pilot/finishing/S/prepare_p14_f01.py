"""P14 conventional pair matte and explicit prop-hand corrections; no generation."""
import json,hashlib,datetime
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[4];OUT=ROOT/'production/structural-pilot/finishing/S/P14/F01'
RAW=ROOT/'production/structural-pilot/candidates/C00007-05e9227e2675c85a.png'
if (OUT/'pair-matte.png').exists():raise SystemExit('Preserve previous composite')
im=Image.open(RAW).convert('RGB');w,h=im.size
mask=Image.new('L',im.size);values=[]
for r,g,b in im.getdata():
 spread=max(r,g,b)-min(r,g,b);light=min(r,g,b)
 alpha=0 if spread<23 and light>220 else 255
 if spread<23 and 204<light<=220:alpha=round(255*(220-light)/16)
 values.append(alpha)
mask.putdata(values);draw=ImageDraw.Draw(mask)
erasures={
 'nera_old_left_forearm_hand_staff':[(454,886),(517,881),(553,1020),(617,1168),(576,1186),(479,1073),(459,1036)],
 'odo_old_right_cuff_hand_flask':[(970,790),(1100,798),(1069,889),(1032,1038),(909,1075),(893,875),(940,851)],
}
for poly in erasures.values():draw.polygon(poly,fill=0)
mask.save(OUT/'pair-mask.png');rgba=im.convert('RGBA');rgba.putalpha(mask);rgba.save(OUT/'pair-matte.png')
props=Image.open(ROOT/'production/structural-pilot/control/v8/P14-props.png').convert('RGBA')
# Keep the original drawn three-streak injury on its visibly correct right hand;
# avoid doubling it with the guide's schematic scrape while keeping rigid props.
pixels=[]
for r,g,b,a in props.getdata():pixels.append((r,g,b,0 if r>1.5*g and r>1.5*b and r>80 else a))
props.putdata(pixels);props.save(OUT/'fixed-props-without-double-wound.png')
matrix=[1,0,0,1.05,-38.67,87.95]
nera_arm='''<path d="M423 1008 Q440 994 458 1013 L594 1128 L574 1172 Q548 1169 531 1150 L430 1070 Z" fill="#303239" stroke="#17191e" stroke-width="3.4"/>
<path d="M442 1017 Q456 1040 473 1053 L557 1121 L543 1130 L446 1050" fill="#44474f"/>
<path d="M546 1120 L594 1134 L585 1160 L538 1141 Z" fill="#24262d" stroke="#16181d" stroke-width="3"/>
<path d="M556 1141 Q573 1127 587 1135 L609 1151 Q620 1162 615 1178 L601 1191 Q584 1201 568 1186 L552 1171 Q544 1157 556 1141 Z" fill="#aa733f" stroke="#2c221b" stroke-width="3"/>
<path d="M558 1146 Q564 1134 575 1141 L588 1154 Q596 1163 588 1170 Q581 1174 572 1164 Z" fill="#c18b51" stroke="#49301f" stroke-width="2.2"/>
<path d="M601 1151 Q612 1161 605 1172 M593 1164 Q603 1174 596 1184 M581 1173 Q589 1183 584 1188" fill="none" stroke="#573a26" stroke-width="2.1" stroke-linecap="round"/>
<path d="M454 1062 L465 1079 M482 1088 L497 1108 M520 1120 L530 1128" stroke="#1b1d23" stroke-width="2.1" fill="none"/>'''
odo_arm='''<path d="M1022 816 Q1053 838 1045 862 L1025 923 L977 917 L988 866 Z" fill="#214986" stroke="#172331" stroke-width="3.5"/>
<path d="M1012 850 L1035 847 L1019 900 L1003 905 Z" fill="#315d9e"/>
<path d="M977 902 L1027 915 L1020 944 L971 932 Z" fill="#d8c8a5" stroke="#2c2b28" stroke-width="3"/>
<path d="M976 924 Q987 916 997 923 L1012 936 Q1019 950 1008 968 Q995 977 981 966 L965 950 Q961 935 976 924 Z" fill="#aa7746" stroke="#34281d" stroke-width="3"/>
<path d="M977 920 Q988 912 998 918 L1004 931 Q1008 941 1000 944 Q993 946 985 936 L974 931 Z" fill="#bd8a54" stroke="#4f3622" stroke-width="2.2"/>
<path d="M967 940 Q981 947 994 942 M970 951 Q985 958 1000 951 M981 964 Q994 966 1006 958" fill="none" stroke="#61432b" stroke-width="2.1" stroke-linecap="round"/>'''
prefix='production/structural-pilot/control/v8/'
spec={'id':'SC-20260907-01-S-P14-F01','width':1170,'height':1320,'output_svg':str((OUT/'P14-F01.svg').relative_to(ROOT)),
 'description':'Original adult pair retained together to preserve right-hand support; checkerboard/foreign props removed; rigid v8 staff/flask plus explicit conventional far-arm/hand corrections. Unaccepted candidate.',
 'layers':[{'id':'fixed-architecture','path':prefix+'P14-background.png','kind':'fixed-original-geometry'},
 {'id':'fixed-partition','path':prefix+'P14-foreground.png','kind':'fixed-original-geometry'},
 {'id':'fixed-staff-and-flask','path':str((OUT/'fixed-props-without-double-wound.png').relative_to(ROOT)),'kind':'fixed-v8-props-with-duplicate-schematic-injury-removed'},
 {'id':'connected-adult-pair','path':str((OUT/'pair-matte.png').relative_to(ROOT)),'width':w,'height':h,'transform':'matrix(1 0 0 1.05 -38.67 87.95)','kind':'source-bound-color-key-and-explicit-prop-region-mask'},
 {'id':'nera-anatomical-left-forearm-and-grip','svg':nera_arm,'kind':'explicit-conventional-vector-drawing'},
 {'id':'odo-right-forearm-and-flask-grip','svg':odo_arm,'kind':'explicit-conventional-vector-drawing'}]}
(OUT/'P14-F01.spec.json').write_text(json.dumps(spec,indent=2)+'\n')
(OUT/'matte-receipt.json').write_text(json.dumps({'schema':'ExplicitMatteReceipt/1','raw':str(RAW.relative_to(ROOT)),'raw_sha256':hashlib.sha256(RAW.read_bytes()).hexdigest(),'raw_contract_failures':['RGB painted checkerboard instead of alpha','Unwanted rendered remnant and flask','Far prop-hand positions differ from fixed geometry'],
 'preserved':'Connected drawn adult pair, facial relationship and anatomically right dorsal wound/support','transform':matrix,'anchor_used':{'raw_nera_right_hand':[631,755],'v8_nera_right_hand':[592.33,880.7]},
 'erasures_source_px':erasures,'explicit_vector_corrections':['Nera anatomical LEFT forearm/hand to fixed remnant grip [583.83,1160.15]','Odo right sleeve/hand to fixed flask grip [988.58,931.03]'],
 'fixed_geometry_changed':False,'generation_calls':0,'paid_spend_usd':0,'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'limits':'Only one actor-pair anchor is exact. Added hands/sleeves are AI-agent-authored vector drawings, not skilled human drawing; contact, overlap and appeal require actual review.'},indent=2)+'\n')
print('P14_PRIMARY_COMPOSITION_PREPARED')
