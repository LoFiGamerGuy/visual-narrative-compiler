(function(){'use strict';const ns='http://www.w3.org/2000/svg';
const el=(tag,cls,text)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(text)n.textContent=text;return n;};
function renderPanel(p,prefix='../../'){
 const figure=el('figure');figure.id=p.id;figure.dataset.panel=p.id;figure.style.setProperty('--gap',Math.max(18,Math.min(90,p.gap_after||24))+'px');
 const top=el('div','rail above'),art=el('div','art'),bottom=el('div','rail below');const img=el('img');img.src=prefix+p.source;img.alt=p.alt;img.width=p.width;img.height=p.height;img.decoding='async';art.append(img);
 const svg=document.createElementNS(ns,'svg');svg.setAttribute('class','tails');svg.setAttribute('aria-hidden','true');figure.append(top,art,bottom,svg);const nodes=[];
 for(const l of p.lettering){const b=el('p','balloon '+l.position+(l.voice?' voice':'')+(l.caption?' caption':'')+(l.card?' card':''));b.dataset.speaker=l.speaker;b.setAttribute('aria-label',l.speaker+': '+l.text);
  if((l.offscreen||l.name_cue)&&!l.voice)b.append(el('span','voice-id',l.speaker));b.append(document.createTextNode(l.text));b.style.left=(l.x*100)+'%';b.style.width=(l.w*100)+'%';if(l.position==='overlay')b.style.top=(l.y*100)+'%';(l.position==='above'?top:l.position==='below'?bottom:art).append(b);nodes.push([b,l]);
 }
 if(!top.childElementCount)top.remove();if(!bottom.childElementCount)bottom.remove();
 function tails(){svg.replaceChildren();const fr=figure.getBoundingClientRect(),ar=art.getBoundingClientRect();svg.setAttribute('viewBox',`0 0 ${fr.width} ${fr.height}`);
  for(const [b,l] of nodes){if(l.linked||l.no_tail)continue;const br=b.getBoundingClientRect();const tx=ar.left-fr.left+l.target[0]*ar.width,ty=ar.top-fr.top+l.target[1]*ar.height;let cx=br.left-fr.left+br.width/2,cy=br.top-fr.top+br.height/2;
   if(l.offscreen){const right=l.target[0]>1,sx=right?br.right-fr.left-3:br.left-fr.left+3,tip=right?fr.width:0;const path=document.createElementNS(ns,'path');path.setAttribute('class','tail'+(l.voice?' voice':'')+(l.caption?' caption':'')+(l.card?' card':''));path.setAttribute('d',`M ${sx} ${cy-7} L ${tip} ${cy} L ${sx} ${cy+7} Z`);svg.append(path);continue;}
   let dx=tx-cx,dy=ty-cy;const scale=1/Math.max(Math.abs(dx)/(br.width/2-9),Math.abs(dy)/(br.height/2-5));const sx=cx+dx*scale,sy=cy+dy*scale;dx=tx-sx;dy=ty-sy;const distance=Math.hypot(dx,dy);if(distance<10)continue;
   const ux=dx/distance,uy=dy/distance,limit=l.offscreen?Math.min(distance,55):Math.min(Math.max(distance-35,12),l.position==='overlay'?65:42);const tipx=sx+ux*limit,tipy=sy+uy*limit;
   const path=document.createElementNS(ns,'path');path.setAttribute('class','tail'+(l.voice?' voice':'')+(l.caption?' caption':'')+(l.card?' card':''));path.setAttribute('d',`M ${sx-uy*7} ${sy+ux*7} L ${tipx} ${tipy} L ${sx+uy*7} ${sy-ux*7} Z`);svg.append(path);
  }
 }
 img.addEventListener('load',tails);new ResizeObserver(tails).observe(figure);figure._drawTails=tails;return figure;
}
window.ComicReading={renderPanel};
})();
