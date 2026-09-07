// Persistent CDP session: viewport, navigation, lazy-load scroll, inspection, screenshots.
// Local files only; all writes restricted to the isolated review namespace.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const out=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const config=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
const port=Number(process.argv[3]||9333);
const tabs=await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
const tab=tabs.find(t=>t.type==='page');const ws=new WebSocket(tab.webSocketDebuggerUrl);
await new Promise((r,j)=>{ws.onopen=r;ws.onerror=j});let seq=0;const pending=new Map();let events=[];
ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){const p=pending.get(m.id);if(p){pending.delete(m.id);m.error?p[1](new Error(JSON.stringify(m.error))):p[0](m.result)}}else if(['Runtime.exceptionThrown','Runtime.consoleAPICalled','Log.entryAdded','Network.loadingFailed'].includes(m.method))events.push(m)};
function send(method,params={}){return new Promise((r,j)=>{pending.set(++seq,[r,j]);ws.send(JSON.stringify({id:seq,method,params}))})}
async function ev(expression){const r=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw new Error(JSON.stringify(r.exceptionDetails));return r.result.value}
const pause=ms=>new Promise(r=>setTimeout(r,ms));
await send('Page.enable');await send('Runtime.enable');await send('Log.enable');await send('Network.enable');
const results=[];fs.mkdirSync(path.join(out,'.scratch/screenshots'),{recursive:true});
try{for(const job of config.jobs){
 if(!job.url.startsWith('file:///mnt/c/AgentWorkspaces/'))throw new Error('Only local protected/read-only or new review URLs allowed');
 const width=job.width||390,height=job.height||844;events=[];
 await send('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:width<=600});
 await send('Page.navigate',{url:'about:blank'});await pause(100);
 await send('Page.navigate',{url:job.url});await pause(1500);
 await ev('document.fonts.ready');
 await ev("(()=>{const s=document.createElement('style');s.textContent='html,*{scroll-behavior:auto!important}';document.head.append(s)})()");
 let total=await ev('document.documentElement.scrollHeight');
 for(let y=0;y<total;y+=Math.max(400,height-120)){
  await ev(`scrollTo(0,${y})`);await pause(35);
  if(y+height>total-100)total=await ev('document.documentElement.scrollHeight');
 }
 await pause(500);
 // A cold first mobile layout can grow after intrinsic image dimensions load.
 for(let pass=0;pass<3;pass++){
  const count=await ev('document.images.length');
  for(let i=0;i<count;i++){await ev(`document.images[${i}].scrollIntoView({block:'center'})`);await pause(45)}
  await pause(500);
  if(await ev('[...document.images].every(i=>i.complete)'))break;
 }
 const info=await ev(`(()=>({title:document.title,width:innerWidth,height:innerHeight,documentWidth:document.documentElement.scrollWidth,scrollHeight:document.documentElement.scrollHeight,
 images:[...document.images].map(i=>({src:i.src,alt:i.alt,complete:i.complete,naturalWidth:i.naturalWidth,naturalHeight:i.naturalHeight,width:i.getBoundingClientRect().width,height:i.getBoundingClientRect().height,top:i.getBoundingClientRect().top+scrollY})),
 figures:[...document.querySelectorAll('figure.panel,article.panel,main figure')].map((f,i)=>({index:i,id:f.id,text:f.innerText,top:f.getBoundingClientRect().top+scrollY,height:f.getBoundingClientRect().height})),
 links:[...document.querySelectorAll('a[href]')].map(a=>({text:a.innerText,href:a.href})),
 horizontalElements:[...document.querySelectorAll('main,section,table,figure,img,nav')].filter(e=>e.getBoundingClientRect().right>innerWidth+1||e.getBoundingClientRect().left< -1).map(e=>({tag:e.tagName,class:e.className,width:e.getBoundingClientRect().width}))
 }))()`);
 const shots=[];
 for(const sample of job.samples||[0,.2,.4,.6,.8,1]){
  if(typeof sample==='object'&&!info.figures[sample.figure])throw new Error('Requested panel missing: '+job.id+' '+sample.figure);
  const y=typeof sample==='object'?Math.max(0,info.figures[sample.figure].top-85):Math.max(0,(info.scrollHeight-height)*sample);
  await ev(`scrollTo(0,${y})`);await pause(80);
  const name=`${job.id}-${width}x${height}-${typeof sample==='object'?'p'+(sample.figure+1):String(sample).replace('.','_')}.png`;
  const image=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});
  fs.writeFileSync(path.join(out,'.scratch/screenshots',name),Buffer.from(image.data,'base64'));shots.push({sample,y,actualScrollY:await ev('scrollY'),path:'.scratch/screenshots/'+name});
 }
 const localLinks=info.links.filter(l=>l.href.startsWith('file:')).map(l=>{let p=fileURLToPath(l.href.split('#')[0]);return {...l,exists:fs.existsSync(p)}});
 const badImages=info.images.filter(i=>i.complete&&!i.naturalWidth);const pendingImages=info.images.filter(i=>!i.complete);
 results.push({id:job.id,url:job.url,viewport:{width,height},observed:info,brokenImages:badImages,pendingImages,localLinks,events,shots,continuousScroll:true,scrollStep:Math.max(400,height-120)});
 console.log(job.id,width,height,'images',info.images.length,'broken',badImages.length,'overflow',info.documentWidth>width,'events',events.length);
}
 const target=path.resolve(out,config.output);if(!target.startsWith(out+'/'))throw new Error('Output escaped');
 fs.writeFileSync(target,JSON.stringify({schema:'BrowserReview/1',executed_utc:new Date().toISOString(),browser:'Existing Chromium 1234 build; see browser getVersion in QA package',method:'Persistent CDP session holds exact CSS viewport; each document scrolled across all positions to activate lazy assets. Screenshots internally generated, local ignored scratch only. Machine visibility checks supplement actual reviewer image inspection.',results},null,2)+'\n');
}finally{ws.close()}
