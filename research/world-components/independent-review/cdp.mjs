/** No dependency CDP client. Local screenshots only; use `shot-memory` for public research.
 * Start: node cdp.mjs start [port]
 * Commands: node cdp.mjs [--port 9333] navigate URL | viewport W H | eval JS | shot PATH | shot-memory | close
 * Profile, logs and library extraction are isolated in this checkout's .scratch.
 */
import { spawn } from 'node:child_process';
import { mkdirSync, openSync, writeFileSync, readFileSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
const root=dirname(fileURLToPath(import.meta.url));
const scratch=resolve(root,'.scratch/browser');
const args=process.argv.slice(2);
let port=9333;
if(args[0]==='--port'){args.shift();port=Number(args.shift());}
const op=args.shift();
const pause=ms=>new Promise(r=>setTimeout(r,ms));
async function connect(url){
  const ws=new WebSocket(url);await new Promise((r,j)=>{ws.onopen=r;ws.onerror=j});
  let id=0;const pending=new Map();
  ws.onmessage=e=>{const m=JSON.parse(e.data);if(pending.has(m.id)){const [r,j]=pending.get(m.id);pending.delete(m.id);m.error?j(new Error(JSON.stringify(m.error))):r(m.result)}};
  return {ws,send(method,params={}){return new Promise((r,j)=>{pending.set(++id,[r,j]);ws.send(JSON.stringify({id,method,params}))})}};
}
if(op==='start'){
  port=Number(args[0]||port);mkdirSync(scratch,{recursive:true});
  const log=openSync(resolve(scratch,`chromium-${port}.log`),'a');
  const browser=spawn('/home/gosnerp/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome',[
    '--headless','--no-sandbox','--disable-dev-shm-usage','--disable-gpu','--no-first-run',
    '--disable-background-networking','--disable-component-update',`--remote-debugging-port=${port}`,
    `--user-data-dir=${resolve(scratch,`profile-${port}`)}`,'about:blank'],
    {detached:true,stdio:['ignore',log,log],env:{...process.env,LD_LIBRARY_PATH:'/mnt/c/AgentWorkspaces/anime-pipeline-total-review-20260907-014149/research/anime-pipeline-total-review/.scratch/browser-comparables/lib/usr/lib/x86_64-linux-gnu'}});
  browser.unref();
  for(let i=0;i<40;i++){await pause(250);try{const x=await fetch(`http://127.0.0.1:${port}/json/version`);if(x.ok){console.log(JSON.stringify({port,pid:browser.pid,ready:true}));process.exit(0)}}catch{}}
  throw new Error('Chromium not ready; inspect isolated log');
}
const tabs=await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
const tab=tabs.find(x=>x.type==='page');if(!tab)throw new Error('No page tab');
const c=await connect(tab.webSocketDebuggerUrl);
try{
  await c.send('Page.enable');
  let display={width:390,height:844,mobile:true};
  const displayPath=resolve(scratch,`display-${port}.json`);
  try{display=JSON.parse(readFileSync(displayPath,'utf8'));}catch{}
  if(op==='viewport'||op==='mobile'){
    display={width:Number(args[0]||390),height:Number(args[1]||844),mobile:op==='mobile'||Number(args[0]||390)<=600};
    writeFileSync(displayPath,JSON.stringify(display));
  }
  // Reapply mobile semantics for old saved narrow-viewport configurations too.
  display.mobile=display.mobile||display.width<=600;
  await c.send('Emulation.setDeviceMetricsOverride',{...display,deviceScaleFactor:1});
  if(display.mobile)await c.send('Network.setUserAgentOverride',{userAgent:'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1'});
  if(op==='navigate'){
    const r=await c.send('Page.navigate',{url:args[0]});await pause(1500);
    console.log(JSON.stringify(r));
  }else if(op==='mobile'){
    console.log('{"mobile":true}');
  }else if(op==='viewport'){
    console.log(JSON.stringify({width:Number(args[0]),height:Number(args[1])}));
  }else if(op==='eval'){
    const r=await c.send('Runtime.evaluate',{expression:args[0],returnByValue:true,awaitPromise:true});
    if(r.exceptionDetails)throw new Error(JSON.stringify(r.exceptionDetails));
    console.log(JSON.stringify(r.result.value??null));
  }else if(op==='shot'||op==='shot-memory'){
    const r=await c.send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});
    if(op==='shot-memory')console.log(JSON.stringify({image:'data:image/png;base64,'+r.data}));
    else{const p=resolve(args[0]);if(!p.startsWith(root+'/'))throw new Error('Screenshot destination must be inside isolated checkout');writeFileSync(p,Buffer.from(r.data,'base64'));console.log(JSON.stringify({path:p}));}
  }else if(op==='close'){await c.send('Browser.close');console.log('{"closed":true}');}
  else throw new Error('Unknown command '+op);
}finally{c.ws.close();}
