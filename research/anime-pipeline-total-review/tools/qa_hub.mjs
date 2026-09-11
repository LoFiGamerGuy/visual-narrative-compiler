/** Browser exercise of all built reports and interactive routes at three sizes. */
import {readFileSync,writeFileSync,readdirSync,mkdirSync} from 'node:fs';
import {resolve,dirname} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const out=resolve(dirname(fileURLToPath(import.meta.url)),'..'),wt=resolve(out,'../..'),doc=resolve(wt,'docs/research/anime-pipeline-total-review');
const port=Number(process.argv[2]||9333),pause=ms=>new Promise(r=>setTimeout(r,ms));
const version=await(await fetch(`http://127.0.0.1:${port}/json/version`)).json();
const tabs=await(await fetch(`http://127.0.0.1:${port}/json/list`)).json();const tab=tabs.find(x=>x.type==='page');
const ws=new WebSocket(tab.webSocketDebuggerUrl);await new Promise((r,j)=>{ws.onopen=r;ws.onerror=j});let id=0;const pending=new Map(),events=[];
ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){const pair=pending.get(m.id);if(pair){pending.delete(m.id);m.error?pair[1](m.error):pair[0](m.result)}}else if(m.method==='Runtime.exceptionThrown'||m.method==='Log.entryAdded'&&['warning','error'].includes(m.params.entry.level)||m.method==='Runtime.consoleAPICalled'&&['warning','error'].includes(m.params.type))events.push(m)};
const send=(method,params={})=>new Promise((r,j)=>{pending.set(++id,[r,j]);ws.send(JSON.stringify({id,method,params}))});
async function ev(expression){const x=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(x.exceptionDetails)throw Error(JSON.stringify(x.exceptionDetails));return x.result.value}
await send('Page.enable');await send('Runtime.enable');await send('Log.enable');
const pages=readdirSync(doc,{recursive:true}).filter(x=>x.endsWith('.html')).sort();const results=[];const scratch=resolve(out,'.scratch/final-qa');mkdirSync(scratch,{recursive:true});
async function shot(name){const r=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});const p=resolve(scratch,name+'.png');writeFileSync(p,Buffer.from(r.data,'base64'));return p}
const metrics=`(()=>({width:innerWidth,height:innerHeight,scrollWidth:document.documentElement.scrollWidth,scrollHeight:document.documentElement.scrollHeight,title:document.title,bodyText:document.body.innerText.length,brokenImages:[...document.images].filter(i=>!i.complete||!i.naturalWidth).map(i=>i.src),minBodyFont:Math.min(...[...document.querySelectorAll('p,li,label,td,th')].filter(x=>x.getBoundingClientRect().width>0).map(x=>parseFloat(getComputedStyle(x).fontSize))),externalRuntimeDependencies:[...document.querySelectorAll('script[src],link[rel=stylesheet],img[src]')].map(x=>x.src||x.href).filter(x=>/^https?:/.test(x)),horizontalOffenders:[...document.querySelectorAll('body *')].filter(x=>{const r=x.getBoundingClientRect();return r.right>innerWidth+1&&!x.closest('.table-wrap')&&r.width>0}).slice(0,12).map(x=>x.tagName+'.'+x.className)}))()`;
try{
 for(const [width,height] of [[390,844],[1024,768],[1440,1000]]){
  await send('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:width===390});
  for(const page of pages){
   const start=events.length;await send('Page.navigate',{url:pathToFileURL(resolve(doc,page)).href});await pause(120);
   await ev(`new Promise(r=>document.readyState==='complete'?r():window.addEventListener('load',r,{once:true}))`);
   await ev(`(async()=>{for(const i of document.images){i.scrollIntoView();try{await i.decode()}catch{}}scrollTo(0,0)})()`);
   const row={page,requestedWidth:width,requestedHeight:height,...await ev(metrics)};
   if(page==='index.html'){
    row.navigation=await ev(`(()=>{document.documentElement.style.scrollBehavior='auto';return [...document.querySelectorAll('nav[aria-label="Hub sections"] a')].map(a=>{a.click();const t=document.querySelector(a.hash);return {hash:a.hash,exists:!!t,visibleTop:t?.getBoundingClientRect().top}})})()`);
    row.scoreViews=await ev(`(()=>{const p=document.querySelector('#pipeline-select'),c=document.querySelector('#category-select'),r=[];for(const a of p.options){p.value=a.value;for(const b of c.options){c.value=b.value;c.dispatchEvent(new Event('change'));r.push({pipeline:a.value,category:b.value,rows:document.querySelectorAll('#score-output tbody tr').length,hasReason:document.querySelector('#score-output').textContent.includes('Reasons')})}}return r})()`);
    row.strategyViews=await ev(`(()=>{const s=document.querySelector('#strategy-select');return [...s.options].map(o=>{s.value=o.value;s.dispatchEvent(new Event('change'));return {id:o.value,text:document.querySelector('#strategy-output').textContent.length}})})()`);
    await ev(`document.querySelector('#pipeline-select').value='editorial52';document.querySelector('#category-select').value='sequential_storytelling';document.querySelector('#category-select').dispatchEvent(new Event('change'));document.querySelector('#strategy-select').value='B';document.querySelector('#strategy-select').dispatchEvent(new Event('change'));scrollTo(0,0);document.activeElement.blur();document.querySelector('.skip').focus();scrollTo(0,0)`);
    await send('Input.dispatchKeyEvent',{type:'keyDown',key:'Tab',code:'Tab',windowsVirtualKeyCode:9});await send('Input.dispatchKeyEvent',{type:'keyUp',key:'Tab',code:'Tab',windowsVirtualKeyCode:9});row.keyboardFocus=await ev(`({tag:document.activeElement.tagName,text:document.activeElement.textContent,visible:document.activeElement.getBoundingClientRect().width>0})`);
    await ev(`document.activeElement.blur();scrollTo(0,0)`);await pause(50);row.screenshot=await shot(`hub-${width}`);
    await ev(`document.querySelector('#scores').scrollIntoView()`);row.scoreScreenshot=await shot(`scores-${width}`);
   }
   if(page==='pilot-proof.html'){
    row.proofControls=await ev(`[...document.querySelectorAll('select,button,input')].map(x=>({tag:x.tagName,id:x.id,text:x.textContent,type:x.type,options:x.options?[...x.options].map(o=>({value:o.value,text:o.textContent})):null}))`);
    row.proofStress=await ev(`(async()=>{const sel=document.querySelector('#expansion'),r=[];for(const value of ['0','.3','.5']){sel.value=value;sel.dispatchEvent(new Event('change'));await new Promise(x=>requestAnimationFrame(()=>requestAnimationFrame(x)));r.push({expansion:value,scrollWidth:document.documentElement.scrollWidth,pageHeight:document.documentElement.scrollHeight,stripHeight:document.querySelector('.reader').getBoundingClientRect().height,artHeight:[...document.querySelectorAll('.art')].reduce((n,x)=>n+x.getBoundingClientRect().height,0),panelCount:document.querySelectorAll('.panel').length,dialogueFonts:[...new Set([...document.querySelectorAll('.speech')].map(x=>getComputedStyle(x).fontSize))],uiFonts:[...new Set([...document.querySelectorAll('.system')].map(x=>getComputedStyle(x).fontSize))],textOverflow:[...document.querySelectorAll('.utterance')].filter(x=>x.scrollWidth>x.clientWidth+2).length})}sel.value='0';sel.dispatchEvent(new Event('change'));return r})()`);
    row.proofToggles=await ev(`(()=>{return ['guides','gray','contracts'].map(id=>{const e=document.getElementById(id);e.click();const on=e.checked;e.click();return{id,toggled:on!==e.checked}})})()`);
    row.proofNavigation=await ev(`(()=>{document.documentElement.style.scrollBehavior='auto';return [...document.querySelectorAll('nav a')].map(a=>{a.click();return {target:a.hash,exists:!!document.querySelector(a.hash)}})})()`);
    await ev(`scrollTo(0,0)`);await pause(50);row.screenshot=await shot(`pilot-${width}`);
    for(const panel of ['p03','p08','p11','p12','p13','p14']){await ev(`document.getElementById('${panel}').scrollIntoView()`);await shot(`pilot-${width}-${panel}`)}
   }
   row.events=events.slice(start);row.pass=(!row.proofStress||row.proofStress.every(x=>x.scrollWidth<=width&&x.textOverflow===0&&x.panelCount===14))&&row.scrollWidth<=width&&row.brokenImages.length===0&&row.events.length===0&&row.externalRuntimeDependencies.length===0&&row.bodyText>30;results.push(row);
  }
  console.log(JSON.stringify({width,pages:pages.length,failures:results.filter(x=>x.requestedWidth===width&&!x.pass).map(x=>x.page)}));
 }
 const result={schema:'FinalBrowserQA/1',checked_utc:new Date().toISOString(),browser:version.Browser,userAgent:version['User-Agent'],mode:'Chromium CDP, local file URLs;390 mobile metrics, desktop1024/1440;not Safari/device/network validation',pages:pages.length,results,pass:results.every(x=>x.pass)};
 writeFileSync(resolve(out,'evidence/final-browser-qa.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({pass:result.pass,checks:results.length}));
}finally{ws.close()}
