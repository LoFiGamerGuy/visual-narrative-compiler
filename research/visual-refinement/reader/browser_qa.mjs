// Task-owned offline UI checks. CDP9367, fresh page, no old namespace writes.
import {readFileSync,writeFileSync,mkdirSync,existsSync} from 'node:fs';
import {resolve,dirname} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
const here=dirname(fileURLToPath(import.meta.url)),root=resolve(here,'../../..'),docs=resolve(root,'docs/research/visual-refinement'),out=resolve(here,'.scratch/browser');mkdirSync(out,{recursive:true});
const final=process.argv.includes('--require-complete'),port=Number(process.env.REFINEMENT_QA_PORT||9367);
const datasets=Object.fromEntries(['comparison','sequence'].map(mode=>[mode,JSON.parse(readFileSync(resolve(docs,mode+'-data.json'),'utf8'))]));
const tab=await(await fetch(`http://127.0.0.1:${port}/json/new?about:blank`,{method:'PUT'})).json(),ws=new WebSocket(tab.webSocketDebuggerUrl);await new Promise((r,j)=>{ws.onopen=r;ws.onerror=j});
let serial=0;const pending=new Map(),errors=[],expectedErrors=[];let expectedMissing=false;
ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails);if(m.method==='Log.entryAdded'&&m.params.entry.level==='error'){const v=m.params.entry;if(expectedMissing&&JSON.stringify(v).includes('__qa_missing_asset__'))expectedErrors.push(v);else errors.push(v)}if(pending.has(m.id)){const[r,j]=pending.get(m.id);pending.delete(m.id);m.error?j(Error(JSON.stringify(m.error))):r(m.result)}};
const send=(method,params={})=>new Promise((r,j)=>{pending.set(++serial,[r,j]);ws.send(JSON.stringify({id:serial,method,params}))});
const evaluate=async expression=>{const r=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value};
const pause=ms=>new Promise(r=>setTimeout(r,ms));
const navigate=async mode=>{await send('Page.navigate',{url:pathToFileURL(resolve(docs,mode==='comparison'?'index.html':'sequence.html')).href});await pause(200)};
const shot=async name=>{const s=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});writeFileSync(resolve(out,name+'.png'),Buffer.from(s.data,'base64'))};
const decode=()=>evaluate(`(async()=>{for(const image of document.querySelectorAll('#stage img')){image.scrollIntoView({block:'center'});await image.decode();}window.scrollTo(0,0)})()`);
const metrics=()=>evaluate(`({overflow:document.documentElement.scrollWidth>innerWidth,cards:document.querySelectorAll('#stage [data-entry]').length,pending:document.querySelectorAll('#stage [data-missing]').length,images:[...document.querySelectorAll('#stage img')].map(i=>({id:i.closest('[data-entry]').dataset.entry,src:i.getAttribute('src'),loaded:i.complete&&i.naturalWidth>0,uncropped:Math.abs(i.getBoundingClientRect().width/i.getBoundingClientRect().height-i.naturalWidth/i.naturalHeight)<.01,width:i.getBoundingClientRect().width,height:i.getBoundingClientRect().height})),first_art_top:document.querySelector('#stage .image-button,#stage .pending')?.getBoundingClientRect().top??null,copy:[...document.querySelectorAll('#stage [data-copy-id]')].map(n=>({id:n.dataset.copyId,text:[...n.childNodes].filter(x=>x.nodeType===3).map(x=>x.textContent).join('')}))})`);
const result={schema:'VisualRefinementBrowserQA/1',utc:new Date().toISOString(),phase:final?'final-complete':'progressive-ui',viewports:[],interaction:{},source_links:[],errors,expected_missing_asset_errors:expectedErrors};
try{
 await send('Page.enable');await send('Runtime.enable');await send('Log.enable');
 for(const[width,height]of[[390,844],[1024,768],[1440,1000]]){
  await send('Emulation.setDeviceMetricsOverride',{width,height,mobile:width<650,deviceScaleFactor:1});
  const view={width,height,comparison:[],sequence:[],comparison_dialog:null};
  await navigate('comparison');
  for(const character of ['A','B']){
   await evaluate(`RefinementApp.setGroup('controlled');RefinementApp.setCharacter('${character}')`);await decode();
   view.comparison.push({group:'controlled',character,...await metrics()});await evaluate('window.scrollTo(0,0)');await shot(`comparison-${character}-${width}`);
  }
  await evaluate(`RefinementApp.setGroup('exploratory')`);await decode();view.comparison.push({group:'exploratory',...await metrics()});await shot('exploratory-'+width);
  const A=datasets.comparison.entries.filter(e=>e.kind==='controlled'&&e.character_id==='A'&&e.candidate).slice(0,3).map(e=>e.id);
  if(A.length>=2){
   await evaluate(`RefinementApp.setGroup('controlled');RefinementApp.setCharacter('A');${JSON.stringify(A)}.forEach(id=>RefinementApp.selectCompare(id));document.getElementById('open-compare').click()`);
   view.comparison_dialog=await evaluate(`({open:document.getElementById('compare-dialog').open,count:document.querySelectorAll('#compare-stage .card').length,columns:getComputedStyle(document.getElementById('compare-stage')).gridTemplateColumns.split(' ').length,overflow:document.documentElement.scrollWidth>innerWidth,dialog_overflow:document.getElementById('compare-dialog').scrollWidth>document.getElementById('compare-dialog').clientWidth})`);await shot('side-by-side-'+width);
   await evaluate(`document.querySelector('#compare-stage .image-button').click();document.querySelector('#zoom-stage img').decode()`);await shot('native-fit-'+width);
   view.zoom=await evaluate(`({width:document.querySelector('#zoom-stage img').clientWidth,height:document.querySelector('#zoom-stage img').clientHeight,stage_width:document.getElementById('zoom-stage').clientWidth,stage_height:document.getElementById('zoom-stage').clientHeight})`);
   await evaluate(`document.getElementById('zoom-toggle').click()`);view.zoom.native=await evaluate(`document.querySelector('#zoom-stage img').clientWidth===document.querySelector('#zoom-stage img').naturalWidth`);
   await send('Input.dispatchKeyEvent',{type:'keyDown',key:'Escape',code:'Escape',windowsVirtualKeyCode:27});await send('Input.dispatchKeyEvent',{type:'keyUp',key:'Escape',code:'Escape',windowsVirtualKeyCode:27});await pause(30);
   view.zoom.escape=await evaluate(`!document.getElementById('zoom-dialog').open&&document.getElementById('compare-dialog').open`);await evaluate(`document.getElementById('compare-dialog').close()`);
  }
  if(A.length){
   await evaluate(`RefinementApp.openReference('${A[0]}');Promise.all([...document.querySelectorAll('#compare-stage img')].map(i=>i.decode()))`);
   view.reference_compare=await evaluate(`({count:document.querySelectorAll('#compare-stage .card').length,columns:getComputedStyle(document.getElementById('compare-stage')).gridTemplateColumns.split(' ').length,explicit_difference:document.querySelector('#compare-dialog .dialog-hint').textContent.includes('different cast and world'),images:[...document.querySelectorAll('#compare-stage img')].map(i=>({src:i.getAttribute('src'),loaded:i.complete&&i.naturalWidth>0,uncropped:Math.abs(i.clientWidth/i.clientHeight-i.naturalWidth/i.naturalHeight)<.01})),overflow:document.getElementById('compare-dialog').scrollWidth>document.getElementById('compare-dialog').clientWidth})`);await shot('reference-compare-'+width);await evaluate(`document.getElementById('compare-dialog').close()`);
  }
  const captureRepairs=async mode=>{
  for(const entry of datasets[mode].entries.filter(e=>e.repair)){
   await evaluate(`RefinementApp.openRepair('${entry.id}');Promise.all([...document.querySelectorAll('#compare-stage img')].map(i=>i.decode()))`);
   view.repairs.push(await evaluate(`({mode:'${mode}',id:'${entry.id}',columns:getComputedStyle(document.getElementById('compare-stage')).gridTemplateColumns.split(' ').length,images:[...document.querySelectorAll('#compare-stage img')].map(i=>({src:i.getAttribute('src'),loaded:i.complete&&i.naturalWidth>0,uncropped:Math.abs(i.clientWidth/i.clientHeight-i.naturalWidth/i.naturalHeight)<.01})),attempts:[...document.querySelectorAll('#compare-stage .style-caption')].map(p=>p.textContent),hashes:[...document.querySelectorAll('#compare-stage .repair-trace')].map(p=>p.textContent),owner_controls:document.querySelectorAll('#compare-stage [data-response],#compare-stage [data-shortlist],#compare-stage [data-note]').length,conditioning_notice:document.querySelector('#compare-dialog .dialog-hint').textContent.includes('not an identical-input experiment'),overflow:document.getElementById('compare-dialog').scrollWidth>document.getElementById('compare-dialog').clientWidth})`));
   await shot(`repair-${entry.id}-${width}`);
   if(width===390){await evaluate(`document.querySelector('[data-repair-side=after]').scrollIntoView({block:'start'})`);await shot(`repair-${entry.id}-after-${width}`)}
   await evaluate(`document.getElementById('compare-dialog').close()`);
  }
  };
  view.repairs=[];await captureRepairs('comparison');
  await navigate('sequence');await captureRepairs('sequence');
  view.reading_mode=await evaluate(`(()=>{const a=RefinementApp,before=JSON.stringify(a.exportChoices().choices),initial=!a.getState().sequence_review&&[...document.querySelectorAll('.review-tools')].every(n=>n.hidden);document.getElementById('review-panels').click();const review=a.getState().sequence_review&&[...document.querySelectorAll('.review-tools')].every(n=>!n.hidden);document.getElementById('read-story').click();return{initial,review,restored:!a.getState().sequence_review,unchanged:JSON.stringify(a.exportChoices().choices)===before}})()`);
  if(datasets.sequence.plan_pending||!datasets.sequence.styles.length){view.sequence_pending=await evaluate(`({ready:RefinementApp.ready,placeholder:!!document.querySelector('.plan-placeholder'),overflow:document.documentElement.scrollWidth>innerWidth})`);await shot('sequence-pending-'+width)}
  else{
   for(const style of datasets.sequence.styles){await evaluate(`RefinementApp.setSequenceStyle('${style.id}')`);await decode();view.sequence.push({style:style.id,...await metrics()});await evaluate('window.scrollTo(0,0)');await shot(`sequence-${style.id}-${width}`);}
   await evaluate('RefinementApp.setSequenceCompare(true)');await decode();view.sequence_compare=await metrics();await shot('sequence-compare-'+width);
  }
  result.viewports.push(view);
 }
 for(const mode of ['comparison','sequence']){
  const data=datasets[mode];result.interaction[mode]={pending:data.plan_pending||data.available_count===0};
  for(const entry of data.entries){if(entry.candidate){const p=resolve(root,entry.candidate.path);result.source_links.push({mode,id:entry.id,path:entry.candidate.path,exists:existsSync(p),sha256:entry.candidate.sha256,hash_matches:existsSync(p)&&createHash('sha256').update(readFileSync(p)).digest('hex')===entry.candidate.sha256})}}
  if(data.plan_pending||!data.available_count)continue;
  await navigate(mode);const original=await evaluate('RefinementApp.exportChoices()'),firstEntry=data.entries.find(e=>e.candidate),id=firstEntry.id;
  if(mode==='sequence')await evaluate(`RefinementApp.setSequenceStyle('${firstEntry.style_id}');RefinementApp.setSequenceReview(true)`);
  else await evaluate(`RefinementApp.setGroup('${firstEntry.kind}');${firstEntry.character_id?`RefinementApp.setCharacter('${firstEntry.character_id}')`:''}`);
  await evaluate(`document.querySelector('[data-entry="${id}"] .response-toggle').focus()`);
  await send('Input.dispatchKeyEvent',{type:'keyDown',text:'\r',key:'Enter',code:'Enter',windowsVirtualKeyCode:13});await send('Input.dispatchKeyEvent',{type:'keyUp',key:'Enter',code:'Enter',windowsVirtualKeyCode:13});
  const keyboardExpanded=await evaluate(`document.querySelector('[data-entry="${id}"] .response-toggle').getAttribute('aria-expanded')==='true'`);
  await evaluate(`document.querySelector('[data-entry="${id}"] [data-response=comfort][data-value=no]').focus()`);
  await send('Input.dispatchKeyEvent',{type:'keyDown',text:'\r',key:'Enter',code:'Enter',windowsVirtualKeyCode:13});await send('Input.dispatchKeyEvent',{type:'keyUp',key:'Enter',code:'Enter',windowsVirtualKeyCode:13});
  const keyboardResponse=await evaluate(`RefinementApp.exportChoices().choices['${id}'].responses.comfort==='no'`);
  await send('Input.dispatchKeyEvent',{type:'keyDown',key:'Tab',code:'Tab',windowsVirtualKeyCode:9});await send('Input.dispatchKeyEvent',{type:'keyUp',key:'Tab',code:'Tab',windowsVirtualKeyCode:9});
  const keyboardTab=await evaluate(`document.activeElement.dataset.response==='comfort'&&document.activeElement.dataset.value==='unsure'`);
  await evaluate(`RefinementApp.importChoices(${JSON.stringify(original)})`);
  result.interaction[mode]=await evaluate(`(()=>{const a=RefinementApp,id=${JSON.stringify(id)},original=a.exportChoices();a.updateChoice(id,'character','yes');a.updateChoice(id,'style','no');a.updateChoice(id,'comfort','no');a.updateChoice(id,'note','QA: keep the character, simplify the treatment.');a.updateChoice(id,'shortlist',true);const exported=a.exportChoices();const independent=exported.choices[id].responses.character==='yes'&&exported.choices[id].responses.style==='no'&&exported.choices[id].responses.comfort==='no'&&exported.choices[id].responses.readability===original.choices[id].responses.readability;const rejected={};for(const mode of ['dataset','plan','mode','attempt','hash','missing_binding','owner_approval','bad_value','unknown_facet','long_note']){const bad=structuredClone(exported);if(mode==='dataset')bad.dataset_sha256='0'.repeat(64);if(mode==='plan')bad.plan_sha256='0'.repeat(64);if(mode==='mode')bad.mode='other';if(mode==='attempt')bad.source_bindings[0].attempt_id='tampered';if(mode==='hash')bad.source_bindings[0].sha256='0'.repeat(64);if(mode==='missing_binding')bad.source_bindings.pop();if(mode==='owner_approval')bad.owner_approval=true;if(mode==='bad_value')bad.choices[id].responses.comfort=1;if(mode==='unknown_facet')bad.choices[id].responses.score=10;if(mode==='long_note')bad.choices[id].note='x'.repeat(4001);try{a.importChoices(bad);rejected[mode]=false}catch{rejected[mode]=true}}const atomic=JSON.stringify(a.exportChoices().choices)===JSON.stringify(exported.choices);a.importChoices(exported);const roundtrip=JSON.stringify(a.exportChoices().choices)===JSON.stringify(exported.choices);a.importChoices(original);return{independent,rejected,atomic,roundtrip,prior_choices_blank:Object.values(original.choices).every(c=>!c.shortlist&&!c.note&&Object.values(c.responses).every(v=>v===null))}})()`);
  result.interaction[mode].keyboard={expanded:keyboardExpanded,response:keyboardResponse,tab:keyboardTab};
  const downloadDir=resolve(out,'downloads',mode+'-'+new Date().toISOString().replace(/[:.]/g,'-'));mkdirSync(downloadDir,{recursive:true});await send('Browser.setDownloadBehavior',{behavior:'allow',downloadPath:downloadDir});
  await evaluate(`document.querySelector('.save-menu').open=true;document.getElementById('export').click()`);await pause(180);
  const exportPath=resolve(downloadDir,`refinement-${mode}-${data.dataset_sha256.slice(0,10)}.json`);result.interaction[mode].actual_download=existsSync(exportPath);
  if(existsSync(exportPath)){
   const draft=JSON.parse(readFileSync(exportPath,'utf8'));draft.choices[id].note='Actual file-input roundtrip.';const importPath=resolve(downloadDir,'import-roundtrip.json');writeFileSync(importPath,JSON.stringify(draft,null,2));
   const{root:dom}=await send('DOM.getDocument');const{nodeId}=await send('DOM.querySelector',{nodeId:dom.nodeId,selector:'#import-file'});await send('DOM.setFileInputFiles',{nodeId,files:[importPath]});await pause(100);result.interaction[mode].actual_import=await evaluate(`RefinementApp.exportChoices().choices['${id}'].note==='Actual file-input roundtrip.'`);
   await send('Page.reload');await pause(180);result.interaction[mode].reload_persisted=await evaluate(`RefinementApp.exportChoices().choices['${id}'].note==='Actual file-input roundtrip.'`);result.interaction[mode].export_path=exportPath;
  }
  await evaluate(`RefinementApp.importChoices(${JSON.stringify(original)})`);
  result.interaction[mode].restored=await evaluate(`JSON.stringify(RefinementApp.exportChoices().choices)===JSON.stringify(${JSON.stringify(original.choices)})`);
 }
 await navigate('comparison');
 result.prior_stars=await evaluate(`({ids:VR_COMPARISON_DATA.prior_star_ids,labels:[...document.querySelectorAll('.reference-label')].map(x=>x.textContent),interactive_star_labels:document.querySelectorAll('button.reference-label').length})`);
 const available=datasets.comparison.entries.filter(e=>e.kind==='controlled'&&e.character_id==='A'&&e.candidate);
 if(available.length>=2){const ids=available.slice(0,3).map(e=>e.id);await evaluate(`${JSON.stringify(ids)}.forEach(id=>RefinementApp.selectCompare(id));RefinementApp.setCharacter('B')`);result.same_style_switch=await evaluate(`RefinementApp.getState().compare_ids`);result.expected_same_style_switch=ids.map(id=>id.replace('-A','-B')).filter(id=>datasets.comparison.entries.find(e=>e.id===id)?.candidate);if(available.length>3){await evaluate(`RefinementApp.setCharacter('A')`);result.compare_cap=await evaluate(`!RefinementApp.selectCompare('${available[3].id}')`);}}
 await evaluate(`RefinementApp.setGroup('controlled');RefinementApp.setCharacter('A')`);await decode();
 const first=datasets.comparison.entries.find(e=>e.kind==='controlled'&&e.character_id==='A'&&e.candidate);
 if(first){
  const before=await evaluate('RefinementApp.exportChoices().choices');expectedMissing=true;
  await evaluate(`document.querySelector('[data-entry="${first.id}"] img').src='__qa_missing_asset__.png'`);await pause(150);
  result.missing_art=await evaluate(`({visible:!!document.querySelector('[data-entry="${first.id}"] .image-failure'),disabled:[...document.querySelectorAll('[data-entry="${first.id}"] [data-response]')].every(b=>b.disabled),update_blocked:RefinementApp.updateChoice('${first.id}','comfort','yes')===false,unchanged:JSON.stringify(RefinementApp.exportChoices().choices)===JSON.stringify(${JSON.stringify(before)})})`);await navigate('comparison');expectedMissing=false;
 }
 result.local_links=(await evaluate(`[...document.querySelectorAll('a[href]')].map(a=>a.href)`)).filter(h=>h.startsWith('file:')).map(href=>({href,exists:existsSync(decodeURIComponent(new URL(href).pathname))}));
 result.bindings=['index.html','sequence.html','style.css','preferences.js','app.js','comparison-data.json','comparison-data.js','sequence-data.json','sequence-data.js'].map(name=>({path:'docs/research/visual-refinement/'+name,sha256:createHash('sha256').update(readFileSync(resolve(docs,name))).digest('hex')}));
 result.repair_bindings=Object.entries(datasets).flatMap(([mode,data])=>data.entries.filter(e=>e.repair).map(e=>({mode,id:e.id,files:[e.repair.before,e.repair.after,{path:e.repair.record_path,sha256:e.repair.record_sha256}].map(c=>({path:c.path,sha256:c.sha256,hash_matches:createHash('sha256').update(readFileSync(resolve(root,c.path))).digest('hex')===c.sha256}))})));
 const validMetrics=m=>!m.overflow&&m.images.every(i=>i.loaded&&i.uncropped);
 result.complete=datasets.comparison.available_count===20&&datasets.sequence.available_count===18;
 result.reference_comparisons_pass=result.viewports.every(v=>!v.reference_compare||v.reference_compare.count===2&&v.reference_compare.columns===(v.width<650?1:2)&&v.reference_compare.explicit_difference&&!v.reference_compare.overflow&&v.reference_compare.images.every(i=>i.loaded&&i.uncropped));
 const copyOf=p=>(p.copy||[]).map(c=>({id:c.id,text:c.text}));
 const expectedCopy=(datasets.sequence.panels||[]).flatMap(copyOf),expectedCompareCopy=(datasets.sequence.panels||[]).flatMap(p=>(datasets.sequence.styles||[]).flatMap(()=>copyOf(p)));
 result.sequence_copy_pass=result.viewports.every(v=>v.sequence.every(s=>JSON.stringify(s.copy)===JSON.stringify(expectedCopy))&&(!v.sequence_compare||JSON.stringify(v.sequence_compare.copy)===JSON.stringify(expectedCompareCopy)));
 result.repairs_pass=result.viewports.every(v=>v.repairs.every(r=>{const expected=datasets[r.mode].entries.find(e=>e.id===r.id).repair;return r.owner_controls===0&&r.conditioning_notice&&!r.overflow&&r.columns===(v.width<650?1:2)&&r.images.length===2&&r.images.every(i=>i.loaded&&i.uncropped)&&JSON.stringify(r.attempts)===JSON.stringify([expected.before.attempt_id,expected.after.attempt_id])&&r.hashes.some(h=>h.includes(expected.before.sha256))&&r.hashes.some(h=>h.includes(expected.after.sha256))}))&&result.repair_bindings.every(r=>r.files.every(f=>f.hash_matches));
 result.pass=(!final||result.complete)&&errors.length===0&&result.viewports.every(v=>v.comparison.every(m=>validMetrics(m)&&m.cards===(m.group==='controlled'?9:2)&&m.pending+m.images.length===m.cards)&&(!v.comparison_dialog||v.comparison_dialog.open&&!v.comparison_dialog.overflow&&!v.comparison_dialog.dialog_overflow&&v.comparison_dialog.columns===(v.width<650?1:v.comparison_dialog.count)&&v.zoom.native&&v.zoom.escape&&v.zoom.width<=v.zoom.stage_width+1&&v.zoom.height<=v.zoom.stage_height+1)&&v.sequence.every(m=>validMetrics(m)&&m.cards===6&&m.pending+m.images.length===6)&&(!v.sequence_pending||v.sequence_pending.ready&&v.sequence_pending.placeholder&&!v.sequence_pending.overflow)&&(!v.sequence_compare||validMetrics(v.sequence_compare)&&v.sequence_compare.cards===18))&&Object.values(result.interaction).every(i=>i.pending||Object.values(i.keyboard).every(Boolean)&&i.independent&&Object.values(i.rejected).every(Boolean)&&i.atomic&&i.roundtrip&&i.actual_download&&i.actual_import&&i.reload_persisted&&i.restored)&&result.source_links.every(l=>l.exists&&l.hash_matches)&&result.local_links.every(l=>l.exists)&&(!result.missing_art||Object.values(result.missing_art).every(Boolean))&&(!result.same_style_switch||JSON.stringify(result.same_style_switch)===JSON.stringify(result.expected_same_style_switch))&&(result.compare_cap===undefined||result.compare_cap)&&result.prior_stars.interactive_star_labels===0;
 result.pass=result.pass&&result.viewports.every(v=>Object.values(v.reading_mode).every(Boolean))&&result.reference_comparisons_pass&&result.sequence_copy_pass&&result.repairs_pass;
 writeFileSync(resolve(here,'browser-qa.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({pass:result.pass,complete:result.complete,counts:Object.fromEntries(Object.entries(datasets).map(([m,d])=>[m,d.available_count])),errors,missing_art:result.missing_art},null,2));if(!result.pass)process.exitCode=1;
}finally{ws.close();await fetch(`http://127.0.0.1:${port}/json/close/${tab.id}`)}
