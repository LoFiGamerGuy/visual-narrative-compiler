// Local, read-only smoke checks. Uses the existing Chromium and Node CDP client.
import {spawn} from 'node:child_process';
import {readFileSync,writeFileSync,mkdirSync,mkdtempSync,rmSync} from 'node:fs';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {tmpdir} from 'node:os';
const here=dirname(fileURLToPath(import.meta.url)), root=resolve(here,'../..');
const pause=ms=>new Promise(r=>setTimeout(r,ms));
const profile=mkdtempSync(resolve(tmpdir(),'anime-library-browser-'));
const server=spawn('python',[resolve(root,'scripts/serve_library.py'),'--port','8766'],{cwd:root,stdio:['ignore','ignore','ignore']});
const chrome=spawn('/home/gosnerp/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome',[
 '--headless','--no-sandbox','--disable-dev-shm-usage','--disable-gpu','--no-first-run',
 '--disable-background-networking','--disable-component-update','--remote-debugging-port=9341',
 `--user-data-dir=${profile}`,'about:blank'],{stdio:['ignore','ignore','ignore'],env:{...process.env,LD_LIBRARY_PATH:resolve(root,'research/anime-pipeline-total-review/.scratch/browser-comparables/lib/usr/lib/x86_64-linux-gnu')}});
let ws;
const result={routes:[],failures:[]};
try{
 for(let n=0;n<80;n++){
  await pause(250);
  try{if((await fetch('http://127.0.0.1:8766/START-HERE.html',{method:'HEAD'})).ok && (await fetch('http://127.0.0.1:9341/json/version')).ok)break;}catch{}
  if(n===79)throw new Error('Local server or browser did not start');
 }
 const tabs=await(await fetch('http://127.0.0.1:9341/json/list')).json();
 ws=new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);
 await new Promise((r,j)=>{ws.onopen=r;ws.onerror=j;});
 let id=0,errors=[],requests=new Map(),pending=new Map();
 ws.onmessage=e=>{
  const m=JSON.parse(e.data);
  if(pending.has(m.id)){const [r,j]=pending.get(m.id);pending.delete(m.id);m.error?j(new Error(JSON.stringify(m.error))):r(m.result);}
  if(m.method==='Network.requestWillBeSent')requests.set(m.params.requestId,m.params.request.url);
  if(m.method==='Network.responseReceived'&&m.params.response.status>=400)errors.push({type:'http',status:m.params.response.status,url:m.params.response.url});
  if(m.method==='Runtime.exceptionThrown')errors.push({type:'javascript',detail:m.params.exceptionDetails.text,description:m.params.exceptionDetails.exception?.description});
  if(m.method==='Network.loadingFailed'&&m.params.errorText!=='net::ERR_ABORTED')errors.push({type:'network',url:requests.get(m.params.requestId),detail:m.params.errorText});
 };
 const send=(method,params={})=>new Promise((r,j)=>{pending.set(++id,[r,j]);ws.send(JSON.stringify({id,method,params}));});
 await send('Page.enable');await send('Network.enable');await send('Runtime.enable');
 await send('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:true});
 const catalog=JSON.parse(readFileSync(resolve(here,'catalog.json'),'utf8'));
 const routes=['START-HERE.html',...new Set(catalog.filter(x=>x.title!=='Legacy baseline').map(x=>x.path)),...catalog.map(x=>x.url)];
 const portable='production/nightglass-longform/package/output/Nightglass-NineChapters-v1/docs/nightglass-longform/index.html';
 for(let n=1;n<=9;n++)routes.push(portable+'#chapter-'+n);
 for(const route of routes){
  await send('Page.stopLoading');await pause(50);errors=[];requests.clear();
  await send('Page.navigate',{url:'http://127.0.0.1:8766/'+route});
  await pause(900);
  const fullChapter=route.startsWith(portable+'#');
  const expression=`(async()=>{
    ${fullChapter?"for(const i of document.images)i.loading='eager';":''}
    const images=[...document.images].filter(i=>i.loading!=='lazy');
    await Promise.race([Promise.all(images.map(i=>i.complete?Promise.resolve():new Promise(r=>{i.addEventListener('load',r,{once:true});i.addEventListener('error',r,{once:true})}))),new Promise(r=>setTimeout(r,12000))]);
    return {title:document.title,imageCount:document.images.length,brokenImages:images.filter(i=>!i.complete||!i.naturalWidth).map(i=>i.src),bodyText:document.body.innerText.slice(0,180)};
  })()`;
  const evaluated=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});
  const page={route,...evaluated.result.value,errors:errors.filter(e=>!e.url?.endsWith('/favicon.ico'))};
  result.routes.push(page);
  if(page.errors.length||page.brokenImages.length||evaluated.exceptionDetails)result.failures.push(page);
  console.log(JSON.stringify({route,images:page.imageCount,failures:page.errors.length+page.brokenImages.length}));
 }
 result.checkedRoutes=result.routes.length;result.failedRoutes=result.failures.length;
 writeFileSync(resolve(here,'browser-check.json'),JSON.stringify(result,null,2)+'\n');
 await send('Browser.close');
 if(result.failures.length)process.exitCode=1;
}finally{
 ws?.close();server.kill();chrome.kill();await pause(300);rmSync(profile,{recursive:true,force:true});
}
