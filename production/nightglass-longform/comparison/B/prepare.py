from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,sys
root=Path(__file__).resolve().parents[4];d=root/'production/nightglass-longform/comparison/B'
for n in range(31,37):
 im=Image.new('RGB',(1000,650),'#e9e9df');draw=ImageDraw.Draw(im);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',22)
 draw.text((20,18),f'N1-{n} CURRENT STATE / geography only; not drawing style',fill='black',font=font)
 if n<=32:
  draw.rectangle((50,540,950,600),fill='#555c66');draw.ellipse((220,120,310,210),outline='#75571e',width=6);draw.line([(265,210),(265,420),(220,535)],fill='#75571e',width=12);draw.line([(265,420),(315,535)],fill='#75571e',width=12)
  draw.ellipse((620,110,710,200),outline='#273f62',width=6);draw.rectangle((600,210,740,420),outline='#273f62',width=6);draw.line([(625,420),(605,535)],fill='#273f62',width=12);draw.line([(715,420),(755,535)],fill='#273f62',width=12)
  if n==31:
   draw.line([(265,250),(405,330)],fill='#75571e',width=10);draw.rectangle((415,300,510,350),fill='#151522');draw.line([(465,355),(600,285)],fill='#273f62',width=10);draw.text((350,375),'BLACK envelope -> Aren LEFT',fill='black',font=font)
  else:
   draw.rectangle((650,250,700,285),outline='#111111',width=3);draw.text((300,450),'Envelope hidden CHEST. Sword RIGHT.',fill='black',font=font)
 else:
  draw.rectangle((30,230,270,270),fill='#555c66');draw.rectangle((540,540,960,590),fill='#555c66');draw.rectangle((845,370,875,540),fill='#151522');draw.text((735,590),'fixed metal post',fill='black',font=font)
  x,y=(440,260) if n==33 else (675,340)
  draw.ellipse((x-35,y-85,x+35,y-15),outline='#273f62',width=5);draw.line([(x,y),(x,y+120),(x-40,y+195)],fill='#273f62',width=10);draw.line([(x,y+120),(x+40,y+195)],fill='#273f62',width=10)
  draw.line([(x,y+25),(x+60,y+55)],fill='#273f62',width=10);draw.ellipse((x+55,y+45,x+75,y+65),outline='#00aabc',width=4);draw.line([(x+50,y+45),(x-35,y+95)],fill='#555555',width=9)
  if n<=34:draw.line([(x+65,y+55),(860,395)],fill='#00aabc',width=4)
  if n>=34:draw.line([(x-30,y+25),(x-55,y+75)],fill='#273f62',width=10);draw.line([(x-40,y+40),(x-55,y+50)],fill='#b04c26',width=7)
  draw.text((35,60),'RIGHT sword / pommel behind fist; blade separate.',fill='black',font=font);draw.text((35,90),'Envelope: LEFT hand' if n==36 else 'Envelope: hidden CHEST',fill='black',font=font);draw.text((35,120),'Line OFF; LEFT sleeve tear persists' if n>=35 else ('New LEFT sleeve tear at iron tooth' if n==34 else 'Sleeves intact; hem already torn'),fill='black',font=font)
 im.save(d/f'controls/N1-{n}.png')
n=int(sys.argv[1]) if len(sys.argv)>1 else 31
b=json.loads((root/'production/nightglass-longform/scripts/chapter-1.json').read_text())['panels'][n-1]
refs=[root/'production/pilot-chapters/references/anchor-01.png',root/'production/pilot-chapters/candidates/NG-SHEET-P.png',d/f'controls/N1-{n}.png']
if n>31:refs.append(d/f'candidates/B{n-1}-R1.png' if (d/f'candidates/B{n-1}-R1.png').exists() else d/f'candidates/B{n-1}-P.png')
prompt="""Use case: illustration-story. Generate ONE new Nightglass comic panel, square composition, no text, no lettering, no balloons. Reference 1 supplies original thin controlled anime drawing, elegant face proportions, inhabited navy/cyan city with selective amber windows. Reference 2 supplies stable cast construction ONLY: Aren is slim adult dark-haired man in long-sleeved ivory waist jacket, black high-neck shirt/trousers/gloves, red courier cord; Pell older gray-haired stubbled man in mustard work jacket. Exclude the sheet's tall rig, spear, ray and extra people. Reference 3 is CURRENT STATE/geography control only, not visual style. Reference 4 if supplied is the preceding selected panel: preserve its identities and current physical geography, but advance exactly the new action/state below. Use expressive attractive acting, clear hands, broad quiet surface shapes, matte stone, no microtexture everywhere. Scene: old postal stair, blue night, warm windows distant. """+b['action']+'\nCurrent state authoritative: '+b['current_state']+'\nCamera: '+b['camera']+'. Keep quiet dark upper 20 percent for later dialogue. One black envelope only, in the stated location; cream wallet concealed; do not add objects from sheet. No future damage or characters. One frozen moment. Make visible causal hand/contact/endpoint information clear.'
args=dict(prompt=prompt,referenced_image_paths=[str(x) for x in refs]);record=dict(id=f'B{n}-P',status='prepared',args=args,references=[dict(path=str(x.relative_to(root)),sha256=hashlib.sha256(x.read_bytes()).hexdigest()) for x in refs],tool='built-in image_gen',model=None,cost=None)
(d/f'calls/B{n}-P.json').write_text(json.dumps(record,indent=2));print(json.dumps(args))
