// Focused final observations integration: no art or owner-choice mutation.
import{readFileSync,writeFileSync,existsSync,mkdirSync}from'node:fs';
import{resolve,dirname}from'node:path';
import{fileURLToPath,pathToFileURL}from'node:url';
import{createHash}from'node:crypto';
const here=dirname(fileURLToPath(import.meta.url)),root=resolve(here,'../../..'),docs=resolve(root,'docs/research/visual-refinement'),out=resolve(here,'.scratch/browser');mkdirSync(out,{recursive:true});
const data=JSON.parse(readFileSync(resolve(docs,'sequence-data.json'),'utf8'));
if(!data.review_notes_sha256||data.route_observations.length!==3)throw Error('Final source-bound route observations are not ready.');
const tab=await(await fetch('http://127.0.0.1:9367/json/new?about:blank',{method:'PUT'})).json(),ws=new WebSocket(tab.webSocketDebuggerUrl);await new Promise(r=>ws.onopen=r);let serial=0;const pending=new Map(),errors=[];
ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails);if(pending.has(m.id)){const[r,j]=pending.get(m.id);pending.delete(m.id);m.error?j(Error(JSON.stringify(m.error))):r(m.result)}};
const send=(method,params={})=>new Promise((r,j)=>{pending.set(++serial,[r,j]);ws.send(JSON.stringify({id:serial,method,params}))});
const evaluate=async expression=>{const r=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value};
const pause=ms=>new Promise(r=>setTimeout(r,ms));
const shot=async name=>{const s=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});writeFileSync(resolve(out,name+'.png'),Buffer.from(s.data,'base64'))};
const receipt={schema:'VisualRefinementNotesQA/1',utc:new Date().toISOString(),sequence_dataset_sha256:data.dataset_sha256,notes_sha256:data.review_notes_sha256,viewports:[],errors};
try{
 await send('Page.enable');await send('Runtime.enable');
 for(const[width,height]of[[390,844],[1024,768],[1440,1000]]){
  await send('Emulation.setDeviceMetricsOverride',{width,height,mobile:width<650,deviceScaleFactor:1});await send('Page.navigate',{url:pathToFileURL(resolve(docs,'sequence.html')).href});await pause(250);
  const original=await evaluate('JSON.stringify(RefinementApp.exportChoices().choices)'),view={width,height,routes:[]};
  for(const style of data.styles){
   await evaluate(`RefinementApp.setSequenceStyle('${style.id}')`);
   const row=await evaluate(`({style:'${style.id}',default_reading:!RefinementApp.getState().sequence_review,route_collapsed:[...document.querySelectorAll('#route-observations details')].every(n=>!n.open),route_notes:[...document.querySelectorAll('#route-observations li')].map(n=>n.textContent),panel_notes_hidden:[...document.querySelectorAll('.review-tools .ai-observations')].every(n=>n.closest('.review-tools').hidden)})`);
   await evaluate(`(async()=>{for(const image of document.querySelectorAll('#stage img')){image.scrollIntoView({block:'center'});await image.decode();}document.querySelector('#route-observations details').open=true;document.getElementById('route-observations').scrollIntoView({block:'start'});})()`);await shot(`route-notes-${style.id}-${width}`);
   await evaluate(`document.getElementById('review-panels').click()`);
   row.panel_notes=await evaluate(`[...document.querySelectorAll('#stage [data-entry]')].map(card=>({id:card.dataset.entry,visible:!card.querySelector('.review-tools').hidden,notes:[...card.querySelectorAll('.ai-observations li')].map(n=>n.textContent)}))`);
   row.overflow=await evaluate('document.documentElement.scrollWidth>innerWidth');await evaluate(`document.getElementById('read-story').click()`);
   row.choices_unchanged=await evaluate(`JSON.stringify(RefinementApp.exportChoices().choices)===${JSON.stringify(original)}`);view.routes.push(row);
  }
  await evaluate('RefinementApp.setSequenceCompare(true)');view.compare_routes=await evaluate('document.querySelectorAll("#route-observations details").length');
  receipt.viewports.push(view);
 }
 receipt.links=[];
 for(const name of ['index.html','sequence.html']){
  await send('Page.navigate',{url:pathToFileURL(resolve(docs,name)).href});await pause(150);
  const links=await evaluate(`[...document.querySelectorAll('footer a')].map(a=>({label:a.textContent,href:a.href,visible:!a.hidden}))`);
  receipt.links.push({page:name,links:links.map(l=>({...l,exists:l.href.startsWith('file:')&&existsSync(fileURLToPath(l.href))}))});
 }
 const sha=p=>createHash('sha256').update(readFileSync(p)).digest('hex');
 receipt.bindings=['index.html','sequence.html','app.js','style.css','preferences.js','comparison-data.json','sequence-data.json'].map(name=>({path:'docs/research/visual-refinement/'+name,sha256:sha(resolve(docs,name))}));
 receipt.source_notes_hash_matches=sha(resolve(root,'production/visual-refinement/sequence-review-notes.json'))===data.review_notes_sha256;
 receipt.pass=errors.length===0&&receipt.source_notes_hash_matches&&receipt.links.every(p=>p.links.length===2&&p.links.every(l=>l.visible&&l.exists))&&receipt.viewports.every(v=>v.compare_routes===3&&v.routes.every(r=>r.default_reading&&r.route_collapsed&&r.panel_notes_hidden&&!r.overflow&&r.choices_unchanged&&JSON.stringify(r.route_notes)===JSON.stringify(data.route_observations.find(n=>n.style_id===r.style).observations)&&r.panel_notes.every(p=>p.visible&&JSON.stringify(p.notes)===JSON.stringify(data.entries.find(e=>e.id===p.id).ai_observations||[]))));
 writeFileSync(resolve(here,'notes-browser-qa.json'),JSON.stringify(receipt,null,2)+'\n');console.log(JSON.stringify({pass:receipt.pass,errors},null,2));if(!receipt.pass)process.exitCode=1;
}finally{ws.close();await fetch('http://127.0.0.1:9367/json/close/'+tab.id)}
