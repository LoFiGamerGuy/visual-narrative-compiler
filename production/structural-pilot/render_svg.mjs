// Render one original editable composite using the task-owned CDP browser.
// node production/structural-pilot/render_svg.mjs source.svg new-output.png [9347]
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {resolve} from 'node:path';
const [svgPath,pngPath,port='9347']=process.argv.slice(2),root=process.cwd();
const input=resolve(svgPath),output=resolve(pngPath);
if(!input.startsWith(root+'/')||!output.startsWith(root+'/'))throw Error('Task-local files only');
if(existsSync(output))throw Error('Preserve previous output; choose a new version');
const svg=readFileSync(input,'utf8'),m=svg.match(/<svg[^>]*width="(\d+)"[^>]*height="(\d+)"/);
if(!m)throw Error('SVG pixel size missing');const width=+m[1],height=+m[2];
const newTab=await(await fetch(`http://127.0.0.1:${port}/json/new?about:blank`,{method:'PUT'})).json();
const ws=new WebSocket(newTab.webSocketDebuggerUrl);await new Promise((r,j)=>{ws.onopen=r;ws.onerror=j});
let id=0;const pending=new Map();ws.onmessage=e=>{const m=JSON.parse(e.data);if(pending.has(m.id)){const[r,j]=pending.get(m.id);pending.delete(m.id);m.error?j(Error(JSON.stringify(m.error))):r(m.result);}};
const send=(method,params={})=>new Promise((r,j)=>{pending.set(++id,[r,j]);ws.send(JSON.stringify({id,method,params}));});
try{await send('Page.enable');await send('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:false});await send('Page.navigate',{url:'file://'+input});await new Promise(r=>setTimeout(r,600));const shot=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});writeFileSync(output,Buffer.from(shot.data,'base64'));console.log(JSON.stringify({input,output,width,height}));}finally{ws.close();await fetch(`http://127.0.0.1:${port}/json/close/${newTab.id}`);}
