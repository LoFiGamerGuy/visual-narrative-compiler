from build_controls import *

def bloom(cx,cy,scale=1,planted=False,floor=640,closed=False,tilt=0,cut=False,fallen=False):
 s='';foot=(cx+25,floor);root_top=(cx+15,cy+90*scale);root_end=(cx+25,floor if planted else min(floor-65,cy+255*scale))
 if fallen:
  s+=path(f'M {cx-20} {cy+65} Q {cx-70} {floor-20} {cx-115} {floor-70}',stroke='#776b80',w=42*scale)
 elif cut:
  s+=path(f'M {root_top[0]} {root_top[1]} Q {cx+100} {cy+150} {cx+95} {floor-90}',stroke='#776b80',w=44*scale)
  s+=path(f'M {cx+25} {floor-40} L {cx+25} {floor}',stroke='#776b80',w=48*scale)
 else:s+=path(f'M {root_top[0]} {root_top[1]} Q {cx+75} {cy+165*scale} {root_end[0]} {root_end[1]}',stroke='#776b80',w=44*scale)
 if (planted or cut) and not fallen:
  s+=poly([(foot[0]-65*scale,floor),(foot[0]-30*scale,floor-23*scale),(foot[0]+5*scale,floor-9*scale),(foot[0]+53*scale,floor-19*scale),(foot[0]+70*scale,floor)],'#776b80',C['ink'],3)
 pet=''
 if closed:
  pet+=path(f'M {cx-145*scale} {cy+80*scale} Q {cx-200*scale} {cy-20*scale} {cx-55*scale} {cy-165*scale} Q {cx+170*scale} {cy-125*scale} {cx+135*scale} {cy+130*scale} Q {cx} {cy+180*scale} {cx-145*scale} {cy+80*scale} Z','#746c7f',C['ink'],3)
  pet+=path(f'M {cx-145*scale} {cy+80*scale} Q {cx-25*scale} {cy+25*scale} {cx-55*scale} {cy-165*scale}',stroke='#d8d4de',w=3)
 else:
  for ang,rx,ry in [(-75,75,177),(-22,90,184),(32,89,174),(83,73,160),(142,78,180)]:
   pet+=f'<g transform="rotate({ang} {cx} {cy})">'+ellipse(cx,cy-105*scale,rx*scale,ry*scale,'#ada4b5','#70687c',3)+'</g>'
  pet+=ellipse(cx,cy,65*scale,86*scale,'#f5f4ed','#70687c',4)
 s+=f'<g transform="rotate({tilt} {cx} {cy})">'+pet+'</g>'
 return '<g id="single-root-bloom">'+s+'</g>',foot,root_end

def bp(n):
 s=bg('BP',n==1);supports=[];contact_points=[];rootinfo={};p=None
 if n==1:
  p=standing(296,642,.42);s+=human(p,'I',fill='#bcb6c2',scale=.42,coat=True);sw,_=sword(p['rw'],(358,607));s+=sw;b,foot,end=bloom(805,322,1,False);s+=b;supports=[p['rf'],p['lf']];rootinfo={'state':'hanging','end':end,'floor_y':640}
 elif n==2:
  p=pose((442,334),(410,371),(451,383),(470,407),(389,417),(540,429),(355,450),(378,467),(422,483),(282,545),(501,549),(216,639),(546,647));s+=human(p,'I',fill='#bcb6c2',coat=True);b,foot,end=bloom(840,348,1.08,False,closed=True);s+=b;sw,_=sword(p['rw'],(697,425));s+=sw+contact((684,430))+arrow((268,393),(378,387));supports=[p['rf'],p['lf']];contact_points=[(684,430)];rootinfo={'state':'hanging; petals closed','end':end}
 elif n==3:
  p=pose((322,385),(298,422),(338,423),(293,464),(373,462),(325,503),(402,475),(296,511),(337,514),(247,574),(397,576),(223,643),(429,643));s+=human(p,'I',fill='#bcb6c2',coat=True);sw,_=sword(p['rw'],(451,475));s+=sw;b,foot,end=bloom(823,321,.85,True);s+=b+support(foot)+arrow((715,233),(590,280),C['muted'],3);supports=[p['rf'],p['lf'],foot];rootinfo={'state':'planted, no turn until lifted','foot':foot}
 elif n==4:
  p=pose((408,375),(378,414),(423,411),(446,463),(440,363),(510,513),(480,336),(475,517),(518,535),(404,596),(584,596),(352,658),(645,648));b,foot,end=bloom(915,296,.67,True);s+=b
  s+=path('M 904 274 Q 704 349 500 548 L 496 598 Q 765 449 1000 327 Z','#a99fb0','#71667e',3)
  s+=human(p,'I',fill='#bcb6c2',coat=True,tear=(493,596));sw,_=sword(p['rw'],(626,584));s+=sw+contact((500,587))+arrow((773,391),(589,514));supports=[p['rf'],p['lf'],foot];contact_points=[(500,587)];rootinfo={'state':'planted','foot':foot};s=s
 elif n==5:
  p=pose((383,354),(363,390),(405,387),(383,437),(439,424),(423,465),(468,440),(371,477),(415,480),(322,552),(477,532),(284,594),(516,571));s+=human(p,'I',fill='#bcb6c2',coat=True,tear=(386,552));sw,_=sword(p['rw'],(536,451));s+=sw;b,foot,end=bloom(807,320,.69,True,closed=True,tilt=-40);s+=b+support(foot)+arrow((870,440),(977,515),C['muted'],4)+arrow((533,536),(745,584),C['force'],4);supports=[p['rf'],p['lf'],foot];rootinfo={'state':'planted; front faces former lower-right position','foot':foot};s=s
 elif n==6:
  p=pose((463,448),(423,478),(468,489),(519,511),(454,530),(607,535),(481,544),(383,556),(435,573),(296,612),(527,617),(236,654),(582,654));s+=human(p,'I',fill='#bcb6c2',coat=True,tear=(405,642));b,foot,end=bloom(835,299,.79,True,closed=True,tilt=-35);s+=b;sw,_=sword(p['rw'],(810,593));s+=sw+arrow((345,497),(455,499));supports=[p['rf'],p['lf'],foot];rootinfo={'state':'intact, exposed; blade tip stops before root','foot':foot,'blade_tip':(810,593)}
 elif n==7:
  p=pose((499,427),(465,460),(508,473),(551,492),(490,515),(637,531),(523,534),(418,537),(470,554),(306,597),(587,605),(249,650),(640,649));b,foot,end=bloom(803,319,.78,True,tilt=25,cut=True);s+=b;s+=human(p,'I',fill='#bcb6c2',coat=True,tear=(439,622));sw,_=sword(p['rw'],(981,592));s+=sw+contact((853,578))+arrow((605,500),(750,554))+arrow((921,350),(993,471));supports=[p['rf'],p['lf'],foot];contact_points=[(853,578)];rootinfo={'state':'severed','stump_top':(828,600),'upper_end':(898,550),'gap_visible':True}
 else:
  p=pose((363,459),(337,496),(379,497),(365,553),(410,538),(433,595),(436,567),(326,588),(369,591),(325,659),(440,625),(396,695),(491,664));s+=human(p,'I',fill='#bcb6c2',coat=True,tear=(341,672));sw,_=sword(p['rw'],(549,684));s+=sw;b,foot,end=bloom(877,548,.52,True,tilt=80,fallen=True);s+=b+path('M 676 601 L 676 650',stroke='#776b80',w=39)+poly([(620,655),(653,637),(678,645),(710,633),(733,655)],'#776b80',C['ink'],2);supports=[p['rk'],p['lf'],(877,690),(676,655)];rootinfo={'state':'fallen mass; separate stump','stump':(676,655)}
 for x in supports:s+=support(x)
 if n in [1,2]:s+=ellipse(rootinfo['end'][0],650,45,6,'#c3b8c5','#c3b8c5',1)
 if n==4:s='<g transform="translate(-235,-100) scale(1.35)">'+s+'</g>'
 if n==5:s='<g transform="translate(95,90) skewX(-8) scale(1,.84)">'+s+'</g>'
 return s,{'support_points':supports,'contact_points':contact_points,'anatomical_hands':{'ILYRA_RIGHT':p['rw'],'ILYRA_LEFT':p['lw']},'creature':{'construction':'single flower body, oval empty center when open, exactly one thick root and one thorn foot',**rootinfo},'limitations':'Botanical blocking volumes only, not final petal design; camera is schematic.'}

def ram(cx,cy,scale=1,feet=None,inhale=False,hit=False,sit=False):
 s='';sc=scale;fill='#9bbacb';feet=feet or [(cx-110*sc,cy+295*sc),(cx-52*sc,cy+270*sc),(cx+150*sc,cy+295*sc),(cx+208*sc,cy+270*sc)]
 hips=[(cx-120*sc,cy+78*sc),(cx-62*sc,cy+53*sc),(cx+115*sc,cy+76*sc),(cx+170*sc,cy+48*sc)]
 if sit:
  knees=[(cx-140*sc,cy+145*sc),(cx-68*sc,cy+125*sc),(cx+110*sc,cy+165*sc),(cx+179*sc,cy+130*sc)]
 else:knees=[((h[0]+f[0])/2,cy+200*sc) for h,f in zip(hips,feet)]
 for i in [1,3,0,2]:
  s+=line([hips[i],knees[i],feet[i]],C['ink'],36*sc)+line([hips[i],knees[i],feet[i]],'#7797af' if i in [1,3] else fill,30*sc)
  x,y=feet[i];s+=line([(x-13*sc,y),(x+15*sc,y)],C['ink'],9*sc)
 s+=ellipse(cx,cy,207*sc,(152 if inhale else 134)*sc,fill,C['ink'],3)
 s+=path(f'M {cx+184*sc} {cy+5*sc} Q {cx+260*sc} {cy-75*sc} {cx+257*sc} {cy+4*sc} Q {cx+228*sc} {cy+35*sc} {cx+201*sc} {cy+21*sc}',fill,C['ink'],3)
 hx,hy=cx-181*sc,cy+16*sc
 s+=ellipse(hx,hy,89*sc,91*sc,fill,C['ink'],3)
 for ox,oy in [(-18,-62),(57,-42)]:
  s+=ellipse(hx+ox*sc,hy+oy*sc,40*sc,43*sc,'#729aaf',C['ink'],3)
  s+=path(f'M {hx+(ox+18)*sc} {hy+(oy-7)*sc} A {23*sc} {23*sc} 0 1 0 {hx+(ox-8)*sc} {hy+(oy+19)*sc}',stroke='#c2d6df',w=6*sc)
 s+=ellipse(hx-48*sc,hy+42*sc,63*sc,46*sc,'#e9e0c9',C['ink'],3)
 cheek=(hx+27*sc,hy+35*sc);s+=ellipse(*cheek,(34 if inhale else 24)*sc,(31 if inhale else 22)*sc,'#d38b65',C['ink'],2)
 s+=line([(hx-36*sc,hy-12*sc),(hx+2*sc,hy-20*sc)],C['ink'],6*sc)+ellipse(hx-14*sc,hy+1*sc,(7 if hit else 4)*sc,(10 if hit else 6)*sc,'#f5f4ed',C['ink'],2)
 mouth=(hx-91*sc,hy+47*sc);s+=path(f'M {hx-81*sc} {hy+40*sc} Q {hx-48*sc} {hy+54*sc} {hx-21*sc} {hy+49*sc}',stroke=C['ink'],w=3)
 if hit:s+=path(f'M {hx-43*sc} {hy+62*sc} Q {hx-4*sc} {hy+47*sc} {hx+26*sc} {hy+56*sc}',stroke=C['force'],w=4)
 return '<g id="four-legged-gale-ram">'+s+'</g>',feet,mouth,cheek

def wind(a,b,width=85):
 dx=b[0]-a[0];dy=b[1]-a[1];n=math.hypot(dx,dy);nx,ny=-dy/n,dx/n
 return poly([a,(b[0]+nx*width,b[1]+ny*width),(b[0]-nx*width,b[1]-ny*width)],'#fbfcf2','#99b9c7',3)+arrow((a[0]*.8+b[0]*.2,a[1]*.8+b[1]*.2),(a[0]*.3+b[0]*.7,a[1]*.3+b[1]*.7),'#99b9c7',3)

def st(n):
 s=bg('ST',n in [1,8]);supports=[];contact_points=[];p=None;feet=[];ramstate={};frame=None
 if n==1:
  p=standing(296,652,.55);p['rw']=(292,579);p['lw']=(334,578);s+=human(p,'T',fill='#bdd8d4',scale=.55,gauntlet=True);r,feet,mouth,ch=ram(870,401,.73);s+=r;supports=[p['rf'],p['lf']]+feet;ramstate={'legs':4,'charge':'none','mouth':mouth}
 elif n==2:
  p=pose((391,309),(361,351),(408,351),(330,418),(465,351),(377,443),(457,305),(361,467),(411,470),(293,548),(480,545),(259,650),(520,650));r,feet,mouth,ch=ram(943,460,.57,inhale=True);s+=r+human(p,'T',fill='#bdd8d4',gauntlet=True,charged=True);supports=[p['rf'],p['lf']]+feet;ramstate={'legs':4,'cheeks':'inflated','mouth':mouth}
 elif n==3:
  p=pose((309,277),(313,322),(353,308),(263,353),(426,310),(230,319),(472,269),(341,411),(379,396),(250,429),(435,407),(269,501),(460,465));r,feet,mouth,ch=ram(900,338,.95,inhale=True);s+=r+wind(mouth,(371,357),93)+human(p,'T',fill='#bdd8d4',gauntlet=True);s+=arrow((389,257),(274,235));supports=feet;ramstate={'legs':4,'mouth':mouth,'wind_target':(371,357),'Tavi':'airborne; no charge halo'}
 elif n==4:
  p=pose((470,449),(435,480),(477,486),(447,526),(525,557),(484,528),(523,633),(367,489),(411,512),(425,564),(302,576),(486,652),(260,635));r,feet,mouth,ch=ram(959,466,.48);s+=r+path('M 490 655 Q 646 702 770 675',stroke='#d9cba6',w=22)+human(p,'T',fill='#bdd8d4',gauntlet=True,chip=True);s+=contact(p['lw'],ringonly=True);supports=[p['rf'],p['lw']];contact_points=[p['lw']];ramstate={'legs':4,'mouth':mouth,'hero_support':'right boot and left palm'};frame='translate(-160,-95) scale(1.3)'
 elif n==5:
  p=pose((416,471),(385,508),(429,507),(363,550),(462,491),(411,576),(472,460),(384,603),(430,604),(328,665),(490,659),(297,703),(524,697));r,feet,mouth,ch=ram(838,390,.8);s+=r+wind(mouth,(223,328),54)+human(p,'T',fill='#bdd8d4',gauntlet=True,chip=True,charged=True);supports=[p['rf'],p['lf']]+feet;ramstate={'legs':4,'mouth':mouth,'missed_wind_lane_end':(223,328),'cheeks':'deflated'};frame='translate(88,67) skewX(-7) scale(1,.87)'
 elif n==6:
  p=pose((558,366),(523,399),(564,422),(613,401),(547,465),(694,412),(581,486),(491,510),(543,526),(401,586),(657,576),(357,656),(712,656));feet=[(851,558),(806,623),(1112,655),(1154,620)];r,feet,mouth,ch=ram(953,362,.97,feet=feet,hit=True);s+=r+human(p,'T',fill='#bdd8d4',gauntlet=True,chip=True)+wind((700,412),(757,412),31)+contact((710,412),ringonly=True);s+=arrow((318,445),(398,417));supports=[p['rf'],p['lf'],feet[1],feet[2],feet[3]];contact_points=[(710,412)];ramstate={'legs':4,'mouth':mouth,'near_front_hoof':'lifted','fist_contact':(710,412)};frame='translate(-85,-55) scale(1.11)'
 elif n==7:
  p=pose((349,373),(331,415),(372,411),(309,452),(257,441),(340,484),(207,402),(337,517),(381,516),(270,574),(438,577),(235,641),(481,646));feet=[(813,631),(750,608),(1034,650),(1103,610)];r,feet,mouth,ch=ram(913,365,.9,feet=feet);s+=r+human(p,'T',fill='#bdd8d4',gauntlet=True,chip=True);s+=arrow((455,667),(290,680))+arrow((925,559),(1065,588));supports=[p['rf'],p['lf'],feet[2],feet[3]];ramstate={'legs':4,'mouth':mouth,'front_legs':'crossing, separate dark far chain and pale near chain'}
 else:
  p=pose((367,437),(340,479),(384,477),(354,523),(413,499),(404,534),(440,503),(330,606),(378,609),(362,647),(471,639),(444,675),(557,657));feet=[(785,660),(815,620),(1024,667),(1057,632)];r,feet,mouth,ch=ram(917,560,.67,feet=feet,sit=True);s+=r+human(p,'T',fill='#bdd8d4',gauntlet=True,chip=True);supports=[p['rh'],p['rf'],p['lf']]+feet;ramstate={'legs':4,'mouth':mouth,'resting':'all four limbs folded; no effects'}
 for pt in supports:s+=support(pt)
 if frame:s='<g transform="'+frame+'">'+s+'</g>'
 return s,{'support_points':supports,'contact_points':contact_points,'anatomical_hands':{'TAVI_RIGHT':p['rw'],'TAVI_LEFT':p['lw']},'gauntlets':{'RIGHT':'cream circular pressure plate; intact','LEFT':'cream crescent; chipped only from04 onward','charge':n in [2,5]},'creature':{'construction':'one blue ram body, two curled horns, exactly four continuous leg chains, one tuft tail',**ramstate},'limitations':'Schematic staging volumes; final anatomy and foreshortening require native artwork inspection.'}
