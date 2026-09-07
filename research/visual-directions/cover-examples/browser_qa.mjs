import {readFileSync,writeFileSync,mkdirSync,existsSync} from 'node:fs';
import {resolve,dirname} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'../../..'),dir=resolve(process.argv.find(a=>a.startsWith('--shared-dir='))?.slice(13)||resolve(root,'docs/research/visual-directions/cover-examples')),scratch=resolve(root,'research/visual-directions/cover-examples/.scratch');mkdirSync(scratch,{recursive:true});
const preview=process.argv.includes('--preview'),port=9365,tab=await(await fetch(`http://127.0.0.1:${port}/json/new?about:blank`,{method:'PUT'})).json();
const ws=new WebSocket(tab.webSocketDebuggerUrl);await new Promise((r,j)=>{ws.onopen=r;ws.onerror=j});let seq=0;const pending=new Map(),errors=[];
ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails);if(pending.has(m.id)){const[r,j]=pending.get(m.id);pending.delete(m.id);m.error?j(Error(JSON.stringify(m.error))):r(m.result)}};
const send=(method,params={})=>new Promise((r,j)=>{pending.set(++seq,[r,j]);ws.send(JSON.stringify({id:seq,method,params}))});
const ev=async expression=>{const r=await send('Runtime.evaluate',{expression,awaitPromise:true,returnByValue:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value};
const pause=ms=>new Promise(r=>setTimeout(r,ms));
const result={schema:'BlackPetalCoverBrowserQA/1',utc:new Date().toISOString(),preview,document_root:dir,viewports:[],covers:[],errors};
const hash=p=>createHash('sha256').update(readFileSync(p)).digest('hex');
async function navigate(name){await send('Page.navigate',{url:pathToFileURL(resolve(dir,name)).href});await pause(150);await ev('Promise.all([...document.images].map(i=>i.decode()))')}
async function screenshot(path,selector){const params={format:'png',captureBeyondViewport:!!selector};if(selector)params.clip=await ev(`(()=>{const b=document.querySelector(${JSON.stringify(selector)}).getBoundingClientRect();return {x:b.x+scrollX,y:b.y+scrollY,width:b.width,height:b.height,scale:1}})()`);const shot=await send('Page.captureScreenshot',params);writeFileSync(path,Buffer.from(shot.data,'base64'))}
try{
 await send('Page.enable');await send('Runtime.enable');await navigate('index.html');
 for(const[width,height]of(preview?[[390,844],[1280,900]]:[[390,844],[1024,768],[1440,1000]])){
  await send('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:width<600});
  const row=await ev(`({width:innerWidth,overflow:document.documentElement.scrollWidth>innerWidth,images:[...document.images].map(i=>({loaded:i.complete&&i.naturalWidth>0,uncropped:getComputedStyle(i).objectFit==='contain',native:[i.naturalWidth,i.naturalHeight]})),titles:[...document.querySelectorAll('.cover h2')].map(t=>{const c=t.closest('.cover').getBoundingClientRect(),b=t.getBoundingClientRect();return{fits:b.left>=c.left&&b.right<=c.right&&b.bottom<c.top+c.height*.29}})})`);result.viewports.push(row);
  await screenshot(resolve(scratch,`gallery-top-${width}.png`));
 }
 if(preview){await screenshot(resolve(scratch,'first-cover-preview.png'),'#cover-01')}
 else{
  await ev(`document.querySelector('.edit-controls').open=true`);
  await ev(`document.getElementById('author-input').focus();document.getElementById('author-input').select()`);await send('Input.insertText',{text:'Sample Writer'});
  result.author_edit=await ev(`[...document.querySelectorAll('.author')].every(x=>x.textContent==='Sample Writer')`);
  await ev(`document.querySelector('article details').open=true`);
  await ev(`document.querySelector('.title-input').focus();document.querySelector('.title-input').select()`);await send('Input.insertText',{text:'A Different Title'});result.title_edit=await ev(`document.querySelector('#cover-01 h2').textContent==='A Different Title'`);
  await ev(`document.getElementById('toggle-art').click()`);result.hide_lettering=await ev(`getComputedStyle(document.querySelector('.lettering')).display==='none'`);await ev(`document.getElementById('toggle-art').click()`);
  const downloadDir=resolve(scratch,'downloads-'+Date.now());mkdirSync(downloadDir);await send('Browser.setDownloadBehavior',{behavior:'allow',downloadPath:downloadDir,eventsEnabled:true});await ev(`document.getElementById('save-page').click()`);await pause(300);const saved=resolve(downloadDir,'my-black-petal-covers.html');result.edited_download=existsSync(saved)&&readFileSync(saved,'utf8').includes('A Different Title')&&readFileSync(saved,'utf8').includes('value="Sample Writer"');
  // Reopen the saved HTML beside its dependencies, then remove no existing user files.
  const savedCopy=resolve(dir,'edited-qa-check.html');if(existsSync(savedCopy))throw Error('QA saved-copy collision');writeFileSync(savedCopy,readFileSync(saved));
  await navigate('edited-qa-check.html');result.saved_reopens=await ev(`document.querySelector('#cover-01 h2').textContent==='A Different Title'&&document.getElementById('author-input').value==='Sample Writer'&&[...document.images].every(i=>i.complete&&i.naturalWidth)`);
  const {unlinkSync}=await import('node:fs');unlinkSync(savedCopy);
  await navigate('index.html');await send('Emulation.setDeviceMetricsOverride',{width:1120,height:1700,deviceScaleFactor:1,mobile:false});await ev(`document.body.classList.add('exporting')`);
  for(let n=1;n<=10;n++){const id=String(n).padStart(2,'0'),path=resolve(dir,`cover-${id}.png`);await screenshot(path,`#cover-${id}`);const bytes=readFileSync(path);result.covers.push({id,path:`docs/research/visual-directions/cover-examples/cover-${id}.png`,width:bytes.readUInt32BE(16),height:bytes.readUInt32BE(20),sha256:hash(path)})}
  await navigate('overview.html');await send('Emulation.setDeviceMetricsOverride',{width:1640,height:1300,deviceScaleFactor:1,mobile:false});await screenshot(resolve(dir,'overview.png'),'#overview-sheet');result.overview={path:'docs/research/visual-directions/cover-examples/overview.png',sha256:hash(resolve(dir,'overview.png'))};
  result.overview_loaded=await ev(`document.images.length===10&&[...document.images].every(i=>i.complete&&i.naturalWidth>0)&&document.documentElement.scrollWidth<=innerWidth`);
  await navigate('index.html');result.local_links=await ev(`[...document.querySelectorAll('a[href]')].map(a=>a.href)`);result.local_links=result.local_links.map(href=>({href,exists:existsSync(fileURLToPath(href))}));
 }
 result.pass=!errors.length&&result.viewports.every(v=>!v.overflow&&v.images.every(i=>i.loaded&&i.uncropped)&&v.titles.every(t=>t.fits))&&(preview||result.viewports.every(v=>v.images.length===10)&&result.author_edit&&result.title_edit&&result.hide_lettering&&result.edited_download&&result.saved_reopens&&result.overview_loaded&&result.local_links.every(l=>l.exists)&&result.covers.every(c=>c.width===1024&&c.height===1536));
 result.bindings=['index.html','overview.html','style.css','app.js'].map(name=>({path:'docs/research/visual-directions/cover-examples/'+name,sha256:hash(resolve(dir,name))}));
 writeFileSync(resolve(root,'research/visual-directions/cover-examples/'+(preview?(process.argv.some(a=>a.startsWith('--shared-dir='))?'.scratch/shared-qa.json':'.scratch/preview-qa.json'):'browser-qa.json')),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({pass:result.pass,preview,viewports:result.viewports.map(v=>({width:v.width,images:v.images.length,overflow:v.overflow,titles_fit:v.titles.every(t=>t.fits)})),covers:result.covers.length,errors:errors.length}));if(!result.pass)process.exitCode=1;
}finally{ws.close();await fetch(`http://127.0.0.1:${port}/json/close/${tab.id}`)}
