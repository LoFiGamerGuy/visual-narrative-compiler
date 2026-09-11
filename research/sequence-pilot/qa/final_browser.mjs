// Integration QA of the final local artifact, using an already running isolated CDP browser.
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {resolve} from 'node:path';
import {createHash} from 'node:crypto';
const root=process.cwd(), port=Number(process.argv[2]||9336);
const pause=ms=>new Promise(r=>setTimeout(r,ms));
const tabs=await(await fetch(`http://127.0.0.1:${port}/json/list`)).json();
const ws=new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);
await new Promise((r,j)=>{ws.onopen=r;ws.onerror=j});
let id=0;const pending=new Map(),errors=[];
ws.onmessage=e=>{const m=JSON.parse(e.data);if(pending.has(m.id)){const[r,j]=pending.get(m.id);pending.delete(m.id);m.error?j(Error(JSON.stringify(m.error))):r(m.result);}else if(m.method==='Runtime.exceptionThrown'||m.method==='Log.entryAdded'&&['error','warning'].includes(m.params.entry.level))errors.push(m);};
const send=(method,params={})=>new Promise((r,j)=>{pending.set(++id,[r,j]);ws.send(JSON.stringify({id,method,params}));});
const evaluate=async expression=>{const r=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value;};
await send('Page.enable');await send('Runtime.enable');await send('Log.enable');
const result={schema:'FinalBrowserIntegration/1',at_utc:new Date().toISOString(),views:[],errors,limitations:['Geometry compares actual glyphs with authored image-observed rectangles; it does not authenticate semantics or human acceptance.','Synthetic expansion is at least the named percentage using whole words, not qualified translation.']};
const scratch=resolve('research/sequence-pilot/.scratch/final-browser');mkdirSync(scratch,{recursive:true});
for(const [width,height] of [[390,844],[1024,768],[1440,1000]]){
 await send('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:width===390});
 for(const page of ['index.html','reader/index.html','corrections/index.html']){
  await send('Page.navigate',{url:'file://'+resolve('docs/research/sequence-pilot',page)});await pause(350);
  const base=await evaluate(`(async()=>{for(const img of document.images){img.loading='eager';try{await img.decode()}catch{}}return {title:document.title,width:innerWidth,scrollWidth:document.documentElement.scrollWidth,brokenImages:[...document.images].filter(i=>!i.complete||!i.naturalWidth).map(i=>i.getAttribute('src')),images:document.images.length}})()`);
  const row={page,width,height,...base};
  if(page==='reader/index.html'){
   row.review=await evaluate(`(async()=>{const app=SequenceReviewApp;app.setView('review');const rows=[];for(let i=0;i<14;i++){app.selectPanel(i);await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));rows.push({panel:app.getState().data.panels[i].id,geometry:app.geometryReport()});}return rows})()`);
   row.stress=await evaluate(`(async()=>{const rows=[];for(const n of [30,50]){const s=document.getElementById('stress');s.value=String(n);s.dispatchEvent(new Event('change'));for(let i=0;i<14;i++){SequenceReviewApp.selectPanel(i);await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));rows.push({percent_at_least:n,panel:SequenceReviewApp.getState().data.panels[i].id,flags:SequenceReviewApp.geometryReport().filter(x=>x.level==='fail')});}}const s=document.getElementById('stress');s.value='0';s.dispatchEvent(new Event('change'));return rows})()`);
   row.reader=await evaluate(`(async()=>{SequenceReviewApp.setView('reader');await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));const rows=[];for(const f of document.querySelectorAll('#reader-stage .reader-panel')){f.scrollIntoView({block:'center'});await new Promise(r=>requestAnimationFrame(r));const img=f.querySelector('img');await img.decode();rows.push({panel:f.id,image_ok:img.naturalWidth>0,width:f.getBoundingClientRect().width,height:f.getBoundingClientRect().height});}return {panels:rows,scroll_height:document.querySelector('#reader-stage').getBoundingClientRect().height,overflow:document.documentElement.scrollWidth>innerWidth}})()`);
   if(width===390)for(const panel of ['P01','P02','P05','P08','P09','P11','P12','P13','P14']){await evaluate(`document.getElementById('reader-${panel}').scrollIntoView({block:'center'})`);await pause(80);const shot=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});writeFileSync(resolve(scratch,panel+'.png'),Buffer.from(shot.data,'base64'));}
  }
  row.pass=row.scrollWidth<=width&&row.brokenImages.length===0&&(!row.review||row.review.every(p=>p.geometry.every(g=>g.level!=='fail')))&&(!row.reader||row.reader.panels.length===14&&!row.reader.overflow&&row.reader.panels.every(p=>p.image_ok));
  result.views.push(row);
 }
}
result.hashes=Object.fromEntries(['src/sequence_pilot/web/app.js','src/sequence_pilot/web/style.css','docs/research/sequence-pilot/reader/review-data.json','production/sequence-pilot/layout-draft.json','research/sequence-pilot/report-source.md'].map(p=>[p,createHash('sha256').update(readFileSync(p)).digest('hex')]));
result.pass=result.views.every(v=>v.pass)&&errors.length===0;
writeFileSync(resolve('research/sequence-pilot/evidence/final-browser-qa.json'),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({pass:result.pass,views:result.views.map(v=>({page:v.page,width:v.width,pass:v.pass,images:v.images,original_geometry_flags:v.review?.flatMap(p=>p.geometry.filter(g=>g.level==='fail')).length,stress_flags:v.stress?.flatMap(p=>p.flags).length,scroll_height:v.reader?.scroll_height})),errors:errors.length}));ws.close();
