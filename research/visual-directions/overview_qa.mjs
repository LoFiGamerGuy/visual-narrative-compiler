// Actual-browser overview sheets, local art only. New CDP9361 page/profile.
import {readFileSync,writeFileSync,mkdirSync,existsSync} from 'node:fs';
import {resolve,dirname} from 'node:path';
import {pathToFileURL,fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'../..'),dir=resolve(root,'docs/research/visual-directions'),out=resolve(root,'research/visual-directions/.scratch/gallery-browser');mkdirSync(out,{recursive:true});
const data=JSON.parse(readFileSync(resolve(dir,'gallery-data.json'),'utf8'));
if(data.available_count!==20)throw Error('Overview sheet publication requires all20 actual selected boards.');
const port=Number(process.env.GALLERY_QA_PORT||9361),tab=await(await fetch(`http://127.0.0.1:${port}/json/new?about:blank`,{method:'PUT'})).json();
const ws=new WebSocket(tab.webSocketDebuggerUrl);await new Promise((r,j)=>{ws.onopen=r;ws.onerror=j});let serial=0;const pending=new Map(),errors=[];
ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails);if(m.method==='Log.entryAdded'&&m.params.entry.level==='error')errors.push(m.params.entry);if(pending.has(m.id)){const[r,j]=pending.get(m.id);pending.delete(m.id);m.error?j(Error(JSON.stringify(m.error))):r(m.result)}};
const send=(method,params={})=>new Promise((r,j)=>{pending.set(++serial,[r,j]);ws.send(JSON.stringify({id:serial,method,params}))});
const evaluate=async expression=>{const r=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value};
const pause=ms=>new Promise(r=>setTimeout(r,ms));
const result={schema:'VisualDirectionsOverviewQA/1',utc:new Date().toISOString(),dataset_sha256:data.dataset_sha256,viewports:[],sheets:[],errors};
try{
 await send('Page.enable');await send('Runtime.enable');await send('Log.enable');
 await send('Page.navigate',{url:pathToFileURL(resolve(dir,'overview.html')).href});await pause(150);await evaluate('Promise.all([...document.images].map(i=>i.decode()))');
 for(const[width,height]of[[390,844],[1024,768],[1440,1000]]){
  await send('Emulation.setDeviceMetricsOverride',{width,height,mobile:width<=600,deviceScaleFactor:1});
  result.viewports.push(await evaluate(`({width:innerWidth,height:innerHeight,overflow:document.documentElement.scrollWidth>innerWidth,images:[...document.images].map(i=>({loaded:i.complete&&i.naturalWidth>0,uncropped:getComputedStyle(i).objectFit==='contain'&&Math.abs(i.clientWidth/i.clientHeight-i.naturalWidth/i.naturalHeight)<.02})),links:[...document.querySelectorAll('a')].map(a=>a.href)})`));
  const shot=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});writeFileSync(resolve(out,`overview-top-${width}.png`),Buffer.from(shot.data,'base64'));
 }
 for(const suffix of ['01-10','11-20']){
  const clip=await evaluate(`(()=>{const b=document.getElementById('sheet-${suffix}').getBoundingClientRect();return{x:b.x+scrollX,y:b.y+scrollY,width:b.width,height:b.height,scale:1}})()`);
  const shot=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:true,clip});const path=resolve(dir,`overview-${suffix}.png`);writeFileSync(path,Buffer.from(shot.data,'base64'));
  result.sheets.push({path:'docs/research/visual-directions/overview-'+suffix+'.png',sha256:createHash('sha256').update(readFileSync(path)).digest('hex'),clip});
 }
 await send('Emulation.setEmulatedMedia',{media:'print'});await send('Emulation.setDeviceMetricsOverride',{width:1123,height:1587,mobile:false,deviceScaleFactor:1});
 result.print=await evaluate(`({paper:'A3 portrait',content_height_limit_px:(420-16)*96/25.4,sheets:[...document.querySelectorAll('.sheet')].map(s=>({width:s.getBoundingClientRect().width,height:s.getBoundingClientRect().height,break_after:getComputedStyle(s).breakAfter}))})`);
 await send('Emulation.setEmulatedMedia',{media:''});
 await evaluate(`document.querySelector('a[href="index.html#direction-12"]').click()`);await pause(200);result.gallery_link=await evaluate(`({hash:location.hash,ready:window.VisualDirections?.ready,card_exists:!!document.getElementById('direction-12')})`);
 result.local_links=[...new Set(result.viewports.flatMap(v=>v.links))].filter(l=>l.startsWith('file:')).map(href=>({href,exists:existsSync(decodeURIComponent(new URL(href).pathname))}));
 result.html_sha256=createHash('sha256').update(readFileSync(resolve(dir,'overview.html'))).digest('hex');
 result.pass=errors.length===0&&result.viewports.every(v=>!v.overflow&&v.images.length===20&&v.images.every(i=>i.loaded&&i.uncropped))&&result.local_links.every(l=>l.exists)&&result.print.sheets.every(s=>s.height<=result.print.content_height_limit_px)&&result.gallery_link.hash==='#direction-12'&&result.gallery_link.ready&&result.gallery_link.card_exists;
 writeFileSync(resolve(root,'research/visual-directions/overview-browser-qa.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));if(!result.pass)process.exitCode=1;
}finally{ws.close();await fetch(`http://127.0.0.1:${port}/json/close/${tab.id}`)}
