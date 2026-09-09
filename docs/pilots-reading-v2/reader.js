/* Editable HTML text and SVG tails; native image files remain unmodified.
   The small renderer is reusable: renderPanel(panel, assetPrefix) returns a figure.
   Normalized x/y/w and target coordinates refer to the complete source image. */
(function(){
'use strict';
const data=window.PILOT_EDITION, ns='http://www.w3.org/2000/svg';
const el=(tag,cls,text)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(text)n.textContent=text;return n;};
function renderPanel(p,prefix='../../'){
 const figure=el('figure');figure.id=p.id;figure.dataset.panel=p.id;figure.style.setProperty('--gap',Math.max(18,Math.min(90,p.gap_after||24))+'px');
 const top=el('div','rail above'),art=el('div','art'),bottom=el('div','rail below');const img=el('img');img.src=prefix+p.source;img.alt=p.alt;img.width=p.width;img.height=p.height;img.decoding='async';art.append(img);
 const svg=document.createElementNS(ns,'svg');svg.setAttribute('class','tails');svg.setAttribute('aria-hidden','true');figure.append(top,art,bottom,svg);const nodes=[];
 for(const l of p.lettering){const b=el('p','balloon '+l.position+(l.voice?' voice':''));b.dataset.speaker=l.speaker;b.setAttribute('aria-label',l.speaker+': '+l.text);
  if((l.offscreen||l.name_cue)&&!l.voice)b.append(el('span','voice-id',l.speaker));b.append(document.createTextNode(l.text));b.style.left=(l.x*100)+'%';b.style.width=(l.w*100)+'%';if(l.position==='overlay')b.style.top=(l.y*100)+'%';(l.position==='above'?top:l.position==='below'?bottom:art).append(b);nodes.push([b,l]);
 }
 if(!top.childElementCount)top.remove();if(!bottom.childElementCount)bottom.remove();
 function tails(){svg.replaceChildren();const fr=figure.getBoundingClientRect(),ar=art.getBoundingClientRect();svg.setAttribute('viewBox',`0 0 ${fr.width} ${fr.height}`);
  for(const [b,l] of nodes){if(l.linked||l.no_tail)continue;const br=b.getBoundingClientRect();const tx=ar.left-fr.left+l.target[0]*ar.width,ty=ar.top-fr.top+l.target[1]*ar.height;let cx=br.left-fr.left+br.width/2,cy=br.top-fr.top+br.height/2;
   if(l.offscreen){const right=l.target[0]>1,sx=right?br.right-fr.left-3:br.left-fr.left+3,tip=right?fr.width:0;const path=document.createElementNS(ns,'path');path.setAttribute('class','tail'+(l.voice?' voice':''));path.setAttribute('d',`M ${sx} ${cy-7} L ${tip} ${cy} L ${sx} ${cy+7} Z`);svg.append(path);continue;}
   let dx=tx-cx,dy=ty-cy;const scale=1/Math.max(Math.abs(dx)/(br.width/2-9),Math.abs(dy)/(br.height/2-5));const sx=cx+dx*scale,sy=cy+dy*scale;dx=tx-sx;dy=ty-sy;const distance=Math.hypot(dx,dy);if(distance<10)continue;
   const ux=dx/distance,uy=dy/distance,limit=l.offscreen?Math.min(distance,55):Math.min(Math.max(distance-35,12),l.position==='overlay'?65:42);const tipx=sx+ux*limit,tipy=sy+uy*limit;
   const path=document.createElementNS(ns,'path');path.setAttribute('class','tail'+(l.voice?' voice':''));path.setAttribute('d',`M ${sx-uy*7} ${sy+ux*7} L ${tipx} ${tipy} L ${sx+uy*7} ${sy-ux*7} Z`);svg.append(path);
  }
 }
 img.addEventListener('load',tails);new ResizeObserver(tails).observe(figure);figure._drawTails=tails;return figure;
}
window.ComicReading={renderPanel};
function show(){let id=location.hash.slice(1);if(!data.chapters.some(c=>c.id===id))id='NG';const c=data.chapters.find(c=>c.id===id);document.body.dataset.series=id;document.title=c.title+' · '+c.chapter_title;document.getElementById('title').textContent=c.title;document.getElementById('subtitle').textContent=c.chapter_title;document.getElementById('premise').textContent=c.reading_premise||c.logline||c.premise;
 const nav=document.getElementById('stories');nav.replaceChildren();for(const item of data.chapters){const a=el('a','',item.title);a.href='#'+item.id;if(item.id===id)a.setAttribute('aria-current','page');nav.append(a);}
 const comic=document.getElementById('comic');comic.replaceChildren(...data.panels.filter(p=>p.chapter_id===id).map(p=>renderPanel(p)));document.getElementById('ending').textContent='End of '+c.chapter_title;const next=document.getElementById('next');next.replaceChildren();for(const item of data.chapters.filter(c=>c.id!==id)){const a=el('a','',item.title+' →');a.href='#'+item.id;next.append(a);}requestAnimationFrame(()=>document.querySelectorAll('figure').forEach(f=>f._drawTails()));
}
window.addEventListener('hashchange',()=>{if(data.chapters.some(c=>c.id===location.hash.slice(1))){show();scrollTo(0,0);}});show();
})();
