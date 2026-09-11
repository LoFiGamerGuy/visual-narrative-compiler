// New-namespace local browser QA; own Chrome profile on CDP9361. No old writes.
import {writeFileSync, readFileSync, mkdirSync, existsSync} from 'node:fs';
import {resolve, dirname} from 'node:path';
import {pathToFileURL, fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'../..');
const output=resolve(root,'research/visual-directions/.scratch/gallery-browser');mkdirSync(output,{recursive:true});
const port=Number(process.env.GALLERY_QA_PORT||9361), complete=process.argv.includes('--require-complete');
const pageURL=pathToFileURL(resolve(root,'docs/research/visual-directions/index.html')).href;
const tab=await(await fetch(`http://127.0.0.1:${port}/json/new?about:blank`,{method:'PUT'})).json();
const ws=new WebSocket(tab.webSocketDebuggerUrl);await new Promise((r,j)=>{ws.onopen=r;ws.onerror=j});
let serial=0;const pending=new Map(),errors=[];
ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails);if(m.method==='Log.entryAdded'&&m.params.entry.level==='error')errors.push(m.params.entry);if(pending.has(m.id)){const[r,j]=pending.get(m.id);pending.delete(m.id);m.error?j(Error(JSON.stringify(m.error))):r(m.result)}};
const send=(method,params={})=>new Promise((r,j)=>{pending.set(++serial,[r,j]);ws.send(JSON.stringify({id:serial,method,params}))});
const evaluate=async expression=>{const r=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value};
const pause=ms=>new Promise(r=>setTimeout(r,ms));
const screenshot=async name=>{const r=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});writeFileSync(resolve(output,name+'.png'),Buffer.from(r.data,'base64'))};
const data=JSON.parse(readFileSync(resolve(root,'docs/research/visual-directions/gallery-data.json'),'utf8'));
const results={schema:'VisualDirectionsBrowserQA/1',utc:new Date().toISOString(),dataset_sha256:data.dataset_sha256,available:data.available_count,expected:20,complete_required:complete,viewports:[],interaction:{},errors};
try{
 await send('Page.enable');await send('Runtime.enable');await send('Log.enable');
 await send('Page.navigate',{url:pageURL});await pause(250);
 const original=await evaluate('VisualDirections.exportSelection()');
 for(const[width,height]of[[390,844],[1024,768],[1440,1000]]){
  await send('Emulation.setDeviceMetricsOverride',{width,height,mobile:width<=600,deviceScaleFactor:1});
  await send('Page.navigate',{url:pageURL});await pause(200);
  await evaluate(`(async()=>{for(const image of document.querySelectorAll('#gallery img')){image.scrollIntoView({block:'center'});await image.decode();}window.scrollTo(0,0)})()`);
  const view=await evaluate(`({width:innerWidth,height:innerHeight,ready:VisualDirections.ready,dataset_sha256:VisualDirections.getState().dataset_sha256,overflow:document.documentElement.scrollWidth>innerWidth,cards:document.querySelectorAll('#gallery .card').length,pending:document.querySelectorAll('#gallery .pending-art').length,images:[...document.querySelectorAll('#gallery img')].map(i=>({id:i.closest('[data-direction]').dataset.direction,src:i.getAttribute('src'),loaded:i.complete&&i.naturalWidth>0,width:i.getBoundingClientRect().width,height:i.getBoundingClientRect().height,natural_width:i.naturalWidth,natural_height:i.naturalHeight,fit:getComputedStyle(i).objectFit,uncropped:Math.abs(i.getBoundingClientRect().width/i.getBoundingClientRect().height-i.naturalWidth/i.naturalHeight)<.01})),first_art_top:document.querySelector('.art-button,.pending-art').getBoundingClientRect().top,fonts:{title:getComputedStyle(document.querySelector('.card h2')).fontSize,component:getComputedStyle(document.querySelector('.components button')).fontSize},compare:{},zoom:{}})`);
  await screenshot('gallery-top-'+width);
  for(const id of ['02','04','10','15','20']){if(data.cards.find(c=>c.id===id)?.candidate){await evaluate(`document.getElementById('direction-${id}').scrollIntoView({block:'start'})`);await screenshot(`gallery-${id}-${width}`);}}
  const ids=data.cards.filter(c=>c.candidate).slice(0,4).map(c=>c.id);
  if(ids.length>=2){await evaluate(`(${JSON.stringify(ids)}).forEach(id=>VisualDirections.selectCompare(id));document.getElementById('open-compare').click()`);await pause(100);
   view.compare=await evaluate(`({count:document.querySelectorAll('#compare-stage .compare-card').length,dialog_open:document.getElementById('compare-dialog').open,page_overflow:document.documentElement.scrollWidth>innerWidth,horizontal_scroll:document.getElementById('compare-stage').scrollWidth>document.getElementById('compare-stage').clientWidth,images:[...document.querySelectorAll('#compare-stage img')].map(i=>({fit:getComputedStyle(i).objectFit,width:i.getBoundingClientRect().width,height:i.getBoundingClientRect().height}))})`);await screenshot('compare-'+width);
   await evaluate(`document.querySelector('#compare-stage .art-button').click()`);await pause(100);await evaluate(`document.querySelector('#zoom-stage img').decode()`);await screenshot('zoom-fit-'+width);
   view.zoom=await evaluate(`({open:document.getElementById('zoom-dialog').open,width:document.querySelector('#zoom-stage img').getBoundingClientRect().width,height:document.querySelector('#zoom-stage img').getBoundingClientRect().height,stage_width:document.getElementById('zoom-stage').clientWidth,stage_height:document.getElementById('zoom-stage').clientHeight})`);
   await evaluate(`document.getElementById('zoom-toggle').click()`);view.zoom.native=await evaluate(`({width:document.querySelector('#zoom-stage img').getBoundingClientRect().width,natural_width:document.querySelector('#zoom-stage img').naturalWidth,horizontal_scroll:document.getElementById('zoom-stage').scrollWidth>document.getElementById('zoom-stage').clientWidth})`);
   await send('Input.dispatchKeyEvent',{type:'keyDown',key:'Escape',code:'Escape',windowsVirtualKeyCode:27});await send('Input.dispatchKeyEvent',{type:'keyUp',key:'Escape',code:'Escape',windowsVirtualKeyCode:27});await pause(100);
   view.zoom.after_escape=await evaluate(`({zoom:document.getElementById('zoom-dialog').open,compare:document.getElementById('compare-dialog').open,active:document.activeElement?.id})`);view.zoom.escape_closes=await evaluate(`!document.getElementById('zoom-dialog').open&&document.getElementById('compare-dialog').open`);
   await evaluate(`document.getElementById('compare-dialog').close()`);
  }
  results.viewports.push(view);
 }
 results.interaction=await evaluate(`(()=>{
 const app=VisualDirections, original=app.exportSelection(), id=window.VISUAL_DIRECTIONS_DATA.cards.find(c=>c.candidate).id;
 const fav=document.querySelector('[data-favorite="'+id+'"]');fav.click();
 document.querySelector('[data-id="'+id+'"][data-facet="character"]').click();
 const note=document.querySelector('[data-notes="'+id+'"]');note.value='QA: keep the character; explore another world.';note.dispatchEvent(new Event('input',{bubbles:true}));
 const exported=app.exportSelection();
 const independentlyLiked=exported.preferences[id].likes.character!==original.preferences[id].likes.character&&exported.preferences[id].likes.world===original.preferences[id].likes.world;
 const favoriteChanged=exported.preferences[id].favorite!==original.preferences[id].favorite;
 const noteRetained=exported.preferences[id].notes===note.value;
 const rejected={};
 for(const mode of ['stale_dataset','source_id','source_hash','copy_missing_binding','acceptance_assertion','wrong_boolean','overlong_note','unexpected_facet']){const bad=structuredClone(exported);if(mode==='stale_dataset')bad.dataset_sha256='0'.repeat(64);if(mode==='source_id')bad.source_bindings[0].attempt_id='fake';if(mode==='source_hash')bad.source_bindings[0].sha256='0'.repeat(64);if(mode==='copy_missing_binding')bad.source_bindings.pop();if(mode==='acceptance_assertion')bad.production_accepted=true;if(mode==='wrong_boolean')bad.preferences[id].favorite='yes';if(mode==='overlong_note')bad.preferences[id].notes='x'.repeat(4001);if(mode==='unexpected_facet')bad.preferences[id].likes.production=true;try{app.importSelection(bad);rejected[mode]=false}catch{rejected[mode]=true}}
 const unchangedAfterReject=JSON.stringify(app.exportSelection().preferences)===JSON.stringify(exported.preferences);
 app.importSelection(exported);const roundtrip=JSON.stringify(app.exportSelection().preferences)===JSON.stringify(exported.preferences);
 document.getElementById('family').value='Paint & wash';document.getElementById('family').dispatchEvent(new Event('change'));const familyCount=document.querySelectorAll('#gallery .card').length;
 document.getElementById('family').value='';document.getElementById('family').dispatchEvent(new Event('change'));
 document.getElementById('shortlist-filter').click();const shortlistCount=document.querySelectorAll('#gallery .card').length,expectedShortlist=Object.values(exported.preferences).filter(p=>p.favorite).length;document.getElementById('shortlist-filter').click();
 const available=window.VISUAL_DIRECTIONS_DATA.cards.filter(c=>c.candidate);const cap=available.length>4?!app.selectCompare(available[4].id):null;
 const storageSet=Storage.prototype.setItem;let storageFallback=false;try{Storage.prototype.setItem=function(){throw Error('QA unavailable storage')};app.toggleFavorite(id);storageFallback=!app.getState().storage_available&&document.getElementById('save-status').textContent.includes('export to keep')&&!!app.exportSelection().preferences[id]}finally{Storage.prototype.setItem=storageSet}
 app.importSelection(original);return {storageFallback,independentlyLiked,favoriteChanged,noteRetained,rejected,unchangedAfterReject,roundtrip,familyCount,shortlistCount,expectedShortlist,compareCap:cap,exportSchema:exported.schema,sourceBindings:exported.source_bindings.length};})()`);
 // Actual browser export → downloaded JSON → file-input import, bound to current pixels.
 const downloadDir=resolve(output,'downloads',new Date().toISOString().replace(/[:.]/g,'-'));mkdirSync(downloadDir,{recursive:true});
 await send('Browser.setDownloadBehavior',{behavior:'allow',downloadPath:downloadDir,eventsEnabled:true});
 await evaluate(`document.querySelector('.selection-menu').open=true;document.getElementById('export').click()`);await pause(250);
 const download=resolve(downloadDir,`visual-directions-selection-${data.dataset_sha256.slice(0,10)}.json`);
 results.interaction.actual_export_file=existsSync(download);results.interaction.download_path=download;
 if(existsSync(download)){
  const exported=JSON.parse(readFileSync(download,'utf8'));const id=data.cards.find(c=>c.candidate).id;exported.preferences[id].notes='Actual file import QA note.';
  const importPath=resolve(downloadDir,'actual-file-import.json');writeFileSync(importPath,JSON.stringify(exported,null,2));
  const {root:doc}=await send('DOM.getDocument');const {nodeId}=await send('DOM.querySelector',{nodeId:doc.nodeId,selector:'#import-file'});await send('DOM.setFileInputFiles',{nodeId,files:[importPath]});await pause(150);
  results.interaction.actual_file_import=await evaluate(`VisualDirections.exportSelection().preferences['${id}'].notes==='Actual file import QA note.'`);
  await send('Page.reload');await pause(200);results.interaction.persisted_after_reload=await evaluate(`VisualDirections.exportSelection().preferences['${id}'].notes==='Actual file import QA note.'`);
 }
 await evaluate(`VisualDirections.importSelection(${JSON.stringify(original)})`);
 results.interaction.original_restored=await evaluate(`JSON.stringify(VisualDirections.exportSelection().preferences)===JSON.stringify(${JSON.stringify(original.preferences)})`);
 results.source_links=data.cards.filter(c=>c.candidate).map(c=>({id:c.id,path:c.candidate.path,sha256:c.candidate.sha256,exists:existsSync(resolve(root,c.candidate.path)),hash_matches:createHash('sha256').update(readFileSync(resolve(root,c.candidate.path))).digest('hex')===c.candidate.sha256}));
 results.local_links=(await evaluate(`[...document.querySelectorAll('a[href]')].map(a=>a.href)`)).filter(href=>href.startsWith('file:')).map(href=>({href,exists:existsSync(decodeURIComponent(new URL(href).pathname))}));
 results.bindings=['index.html','style.css','app.js','gallery-data.json','gallery-data.js'].map(f=>({path:'docs/research/visual-directions/'+f,sha256:createHash('sha256').update(readFileSync(resolve(root,'docs/research/visual-directions',f))).digest('hex')}));
 const i=results.interaction;
 results.pass=(!complete||data.available_count===20)&&errors.length===0&&results.viewports.every(v=>v.ready&&v.dataset_sha256===data.dataset_sha256&&!v.overflow&&v.cards===20&&v.pending+v.images.length===20&&v.images.every(x=>x.loaded&&x.uncropped&&x.fit==='contain'&&data.cards.find(c=>c.id===x.id)?.candidate?.src===x.src)&&v.compare.count===Math.min(4,data.available_count)&&v.compare.dialog_open&&!v.compare.page_overflow&&v.zoom.open&&v.zoom.width<=v.zoom.stage_width+1&&v.zoom.height<=v.zoom.stage_height+1&&v.zoom.native.width===v.zoom.native.natural_width&&v.zoom.escape_closes)&&i.storageFallback&&i.independentlyLiked&&i.favoriteChanged&&i.noteRetained&&Object.values(i.rejected).every(Boolean)&&i.unchangedAfterReject&&i.roundtrip&&i.familyCount===data.cards.filter(c=>c.family==='Paint & wash').length&&i.shortlistCount===i.expectedShortlist&&(i.compareCap===null||i.compareCap)&&i.actual_export_file&&i.actual_file_import&&i.persisted_after_reload&&i.original_restored&&results.local_links.every(l=>l.exists)&&results.source_links.every(l=>l.exists&&l.hash_matches);
 writeFileSync(resolve(root,'research/visual-directions/gallery-browser-qa.json'),JSON.stringify(results,null,2)+'\n');console.log(JSON.stringify({pass:results.pass,available:data.available_count,viewports:results.viewports.map(v=>({width:v.width,cards:v.cards,images:v.images.length,pending:v.pending,overflow:v.overflow,first_art_top:v.first_art_top})),interaction:i,errors},null,2));if(!results.pass)process.exitCode=1;
}finally{ws.close();await fetch(`http://127.0.0.1:${port}/json/close/${tab.id}`)}
