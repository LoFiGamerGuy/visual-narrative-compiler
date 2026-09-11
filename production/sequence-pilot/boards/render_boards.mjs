/** Render code-native SVGs using an already running local Chromium CDP browser.
 * Usage: node render_boards.mjs [port, default 9337]. Creates its own isolated tab.
 * No external requests or image generation; outputs are layout controls, not art.
 */
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {dirname,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
const here=dirname(fileURLToPath(import.meta.url));
const layouts=JSON.parse(readFileSync(resolve(here,'layouts.json'),'utf8'));
const port=Number(process.argv[2]||9337);
const version=await(await fetch(`http://127.0.0.1:${port}/json/version`)).json();
const ws=new WebSocket(version.webSocketDebuggerUrl);
await new Promise((r,j)=>{ws.onopen=r;ws.onerror=j});
let id=0;const pending=new Map();
ws.onmessage=e=>{const m=JSON.parse(e.data);if(pending.has(m.id)){const[r,j]=pending.get(m.id);pending.delete(m.id);m.error?j(Error(JSON.stringify(m.error))):r(m.result)}};
const send=(method,params={},sessionId)=>new Promise((r,j)=>{pending.set(++id,[r,j]);ws.send(JSON.stringify({id,method,params,sessionId}))});
const {targetId}=await send('Target.createTarget',{url:'about:blank'});
const {sessionId}=await send('Target.attachToTarget',{targetId,flatten:true});
const pause=ms=>new Promise(r=>setTimeout(r,ms));
const results=[];mkdirSync(resolve(here,'png'),{recursive:true});
try{
  for(const p of layouts.panels){
    await send('Emulation.setDeviceMetricsOverride',{width:p.width*2,height:p.height*2,deviceScaleFactor:1,mobile:false},sessionId);
    await send('Page.navigate',{url:pathToFileURL(resolve(here,p.file)).href},sessionId);
    await pause(120);
    await send('Runtime.evaluate',{expression:`document.documentElement.setAttribute('width',${p.width*2});document.documentElement.setAttribute('height',${p.height*2});`,returnByValue:true},sessionId);
    const result=await send('Runtime.evaluate',{expression:`(()=>({width:document.documentElement.clientWidth,height:document.documentElement.clientHeight,groups:[...document.querySelectorAll('[data-editable-layer]')].map(x=>x.id),externalImages:document.querySelectorAll('image').length,storyTextNodes:document.querySelectorAll('text').length,parserError:!!document.querySelector('parsererror')}))()`,returnByValue:true},sessionId);
    const measured=result.result.value;
    if(measured.parserError||measured.width!==p.width*2||measured.height!==p.height*2||measured.externalImages||measured.storyTextNodes||measured.groups.length!==5)throw Error(`Invalid SVG board ${p.panel}: ${JSON.stringify(measured)}`);
    const shot=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false},sessionId);
    const pngName=p.file.replace('.svg','.png').toUpperCase().replace('.PNG','.png');
    const pngBytes=Buffer.from(shot.data,'base64');
    writeFileSync(resolve(here,'png',pngName),pngBytes);
    results.push({panel:p.panel,svg_sha256:p.sha256,png_file:`png/${pngName}`,png_sha256:createHash('sha256').update(pngBytes).digest('hex'),...measured});
  }
  writeFileSync(resolve(here,'render-qa.json'),JSON.stringify({schema:'StoryboardBrowserRenderQA/1',plan_sha256:layouts.plan_sha256,browser:version.Browser,device_scale_factor:1,svg_render_scale:2,scope:'Structural render checks only; not image quality or semantic acceptance',panels:results},null,2)+'\n');
  console.log(JSON.stringify({rendered:results.length,browser:version.Browser,output:resolve(here,'png')}));
}finally{await send('Target.closeTarget',{targetId});ws.close()}
