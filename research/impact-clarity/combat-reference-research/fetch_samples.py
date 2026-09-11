import requests,re,json,html,concurrent.futures
from pathlib import Path
from PIL import Image,ImageDraw
D=Path(__file__).parent/'local';D.mkdir(exist_ok=True)
S=[('doom','https://www.webtoons.com/en/action/doom-breaker/episode-1/viewer?title_no=3197&episode_no=1',list(range(0,36))),('goh','https://www.webtoons.com/en/action/the-god-of-high-school/ep-1/viewer?title_no=66&episode_no=1',list(range(0,50))),('tower','https://www.webtoons.com/en/fantasy/tower-of-god/season-2-ep-40/viewer?title_no=95&episode_no=120',list(range(0,45))),('gosu','https://www.webtoons.com/en/action/gosu/ep-14-the-rosy-cheeked-sword-devil-so-hong-4/viewer?title_no=1099&episode_no=15',list(range(0,35))),('orv','https://www.webtoons.com/en/action/omniscient-reader/episode-0-prologue/viewer?title_no=2154&episode_no=1',list(range(0,35))),('jungle','https://www.webtoons.com/en/action/jungle-juice/episode-1/viewer?title_no=2480&episode_no=1',list(range(0,45)))]
def run(s):
 key,u,indices=s;h=requests.get(u,timeout=30).text
 imgs=[html.unescape(re.search('data-url="([^"]+)"',x).group(1)) for x in re.findall('<img[^>]+>',h) if 'class="_images"' in x]
 (D/(key+'-source.json')).write_text(json.dumps({'url':u,'title':re.findall('<title>(.*?)</title>',h,re.S),'images':imgs},indent=2))
 print(key,len(imgs),flush=True)
 for i in indices:
  if i>=len(imgs):break
  p=D/f'{key}-{i+1:03}.jpg'
  if not p.exists():
   r=requests.get(imgs[i],headers={'Referer':u},timeout=30);r.raise_for_status();p.write_bytes(r.content)
 for batch in range(0,len(indices),20):
  canvas=Image.new('RGB',(1000,1400),'#ddd');dr=ImageDraw.Draw(canvas)
  for j,i in enumerate(indices[batch:batch+20]):
   p=D/f'{key}-{i+1:03}.jpg'
   if not p.exists():continue
   im=Image.open(p).convert('RGB');im.thumbnail((196,320));x=(j%5)*200;y=(j//5)*350;canvas.paste(im,(x,y+24));dr.text((x+4,y+4),f'{key} image {i+1}',fill='black')
  canvas.save(D/f'{key}-sheet-{batch//20}.jpg')
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as e:list(e.map(run,S))
