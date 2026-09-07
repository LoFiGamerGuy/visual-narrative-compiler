// Bounded local browser QA. Start isolated Chromium on port 9351 before running.
import {writeFileSync, mkdirSync, readFileSync} from 'node:fs';
import {resolve, dirname} from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';
const here=dirname(fileURLToPath(import.meta.url));
const root=resolve(here,'../../../..');
const correction=process.argv.includes('--correction');
const reader=correction?resolve(here,'../correction-reader'):here;
const bundle=JSON.parse(readFileSync(resolve(reader,'routes.json'),'utf8'));
const routeIDs=bundle.routes.map(r=>r.id);
const prefix=correction?'CF-':'';
const output=resolve(root,'research/structural-pilot/.scratch/reader-browser');
mkdirSync(output,{recursive:true});
const port=Number(process.env.READER_QA_PORT || 9351);
const tabs=await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
const ws=new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);
await new Promise((r,j)=>{ws.onopen=r;ws.onerror=j});
let serial=0;const pending=new Map(),errors=[];
ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails);if(pending.has(m.id)){const [r,j]=pending.get(m.id);pending.delete(m.id);m.error?j(Error(JSON.stringify(m.error))):r(m.result)}};
const send=(method,params={})=>new Promise((r,j)=>{pending.set(++serial,[r,j]);ws.send(JSON.stringify({id:serial,method,params}))});
const evaluate=async expression=>{const r=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value};
const pause=ms=>new Promise(r=>setTimeout(r,ms));
const results={schema:'StructuralReaderBrowserQA/1',utc:new Date().toISOString(),scope:'Actual available candidate art; missing test candidates reported explicitly. Layout checks do not judge art semantics or acceptance.',viewports:[],interaction:{},errors};
try{
 await send('Runtime.enable');await send('Page.enable');
 for(const [width,height] of [[390,844],[1024,768],[1440,1000]]){
  await send('Emulation.setDeviceMetricsOverride',{width,height,mobile:width<=600,deviceScaleFactor:1});
  await send('Page.navigate',{url:pathToFileURL(resolve(reader,'index.html')).href});await pause(500);
  const view={width,height,default_route:await evaluate('SequenceReviewApp.getState().route_id'),routes:[],comparison:null};
  for(const route of routeIDs){
   await evaluate(`SequenceReviewApp.switchRoute(${JSON.stringify(route)});SequenceReviewApp.setView('reader');window.scrollTo(0,0)`);
   await evaluate(`Promise.all([...document.querySelectorAll('#reader-stage img')].map(i=>i.decode().catch(()=>null)))`);
   view.routes.push(await evaluate(`(()=>{const s=SequenceReviewApp.getState(),canvas=document.querySelector('#reader-stage .art-canvas');return {route:s.route_id,ready:SequenceReviewApp.ready,view:s.view,neutral:s.neutral,panels:document.querySelectorAll('#reader-stage .reader-panel').length,images:[...document.querySelectorAll('#reader-stage img')].filter(i=>i.complete&&i.naturalWidth>0).length,missing:s.data.panels.filter(p=>!p.candidate).map(p=>p.id),overflow:document.documentElement.scrollWidth>innerWidth,first_art_top:canvas.getBoundingClientRect().top,first_art_width:canvas.getBoundingClientRect().width,visible_provenance:[...document.querySelectorAll('.provenance-only')].some(n=>n.getClientRects().length>0)}})()`));
   if(['G','CF','S'].includes(route)){
    const lettering=[];
    for(const panel of ['P11','P14']){
     await evaluate(`document.getElementById('reader-${panel}').scrollIntoView({block:'start'})`);
     const shot=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});writeFileSync(resolve(output,`${prefix}${route}-${panel}-${width}.png`),Buffer.from(shot.data,'base64'));
     lettering.push(await evaluate(`(()=>{const frame=document.querySelector('#reader-${panel} .art-canvas');return {panel:'${panel}',glyphs:[...frame.querySelectorAll('text[data-glyph-text]')].map(t=>({text:t.getAttribute('aria-label'),css_font_px:Number(t.getAttribute('font-size'))*frame.getBoundingClientRect().width/390})),glyphs_outside_canvas:[...frame.querySelectorAll('tspan')].filter(t=>{const b=t.getBBox(),h=Number(frame.querySelector('svg').getAttribute('height'));return b.x<0||b.y<0||b.x+b.width>390||b.y+b.height>h}).length}})()`));
     await evaluate(`SequenceReviewApp.setView('review');SequenceReviewApp.selectPanel(${Number(panel.slice(1))-1})`);
     await pause(30);
     lettering.at(-1).editor_geometry=await evaluate('SequenceReviewApp.geometryReport()');
     await evaluate(`SequenceReviewApp.setView('reader')`);
    }
    view.routes.at(-1).lettering=lettering;
   }
  }
  await evaluate(`SequenceReviewApp.setView('compare');window.scrollTo(0,0)`);await pause(60);
  view.comparison=await evaluate(`({groups:document.querySelectorAll('.comparison-group').length,canvases:document.querySelectorAll('.comparison-cell .art-canvas').length,overflow:document.documentElement.scrollWidth>innerWidth,widths:[...new Set([...document.querySelectorAll('.comparison-cell .art-canvas')].map(x=>Math.round(x.getBoundingClientRect().width)))]})`);
  const shot=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});writeFileSync(resolve(output,`${prefix}comparison-${width}.png`),Buffer.from(shot.data,'base64'));
  await evaluate(`SequenceReviewApp.switchRoute('${correction?'CF':'B'}');SequenceReviewApp.setView('reader');window.scrollTo(0,0)`);
  const top=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});writeFileSync(resolve(output,`${prefix}reader-${width}.png`),Buffer.from(top.data,'base64'));
  results.viewports.push(view);
 }
 results.interaction=await evaluate(`(()=>{const app=SequenceReviewApp;app.switchRoute('G');app.setView('review');app.selectPanel(13);const original=app.exportDraft();let staleRejected=false;try{const bad=structuredClone(original);bad.panels[0].candidate_sha256='0'.repeat(64);app.importDraft(bad)}catch{staleRejected=true}const edit=structuredClone(original);edit.panels[13].lettering[0].x+=.01;app.importDraft(edit);app.switchRoute('${correction?'CF':'B'}');app.switchRoute('G');const routeEditRetained=app.exportDraft().panels[13].lettering[0].x===edit.panels[13].lettering[0].x;app.importDraft(original);app.setNeutral(false);const provenanceVisible=[...document.querySelectorAll('.provenance-only')].some(n=>n.getClientRects().length>0);app.setNeutral(true);return {staleRejected,routeEditRetained,provenanceVisible,exportSchema:original.schema,routeBinding:original.route_id,planBinding:original.plan_sha256}})()`);
 results.plan_sha256=bundle.plan_sha256;results.input_sha256=bundle.input_sha256;
 results.pass=errors.length===0&&results.viewports.every(v=>v.default_route===(bundle.default_route||routeIDs[0])&&v.routes.every(r=>r.ready&&r.panels===14&&!r.overflow&&r.visible_provenance===correction&&r.first_art_top<(correction?450:320)&&r.images+r.missing.length===14&&(!r.lettering||r.lettering.every(l=>l.glyphs_outside_canvas===0&&l.editor_geometry.every(g=>g.level!=='fail'))))&&v.comparison.groups===4&&v.comparison.canvases===4*routeIDs.length&&!v.comparison.overflow)&&results.interaction.staleRejected&&results.interaction.routeEditRetained&&results.interaction.provenanceVisible;
 writeFileSync(resolve(output,`${prefix}browser-qa.json`),JSON.stringify(results,null,2)+'\n');console.log(JSON.stringify(results,null,2));
 if(!results.pass)process.exitCode=1;
}finally{ws.close()}
