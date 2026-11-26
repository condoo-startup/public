const {chromium}=require('playwright');const {spawn}=require('child_process');const path=require('path');
const mode=process.argv[2];
(async()=>{const b=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const p=await b.newPage({viewport:{width:540,height:960},deviceScaleFactor:2});
await p.goto('file://'+path.resolve('scene.html'));await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(300);
if(mode==='stills'){for(const t of process.argv.slice(3).map(Number)){await p.evaluate(t=>render(t),t);await p.screenshot({path:`st_${t}.jpg`,type:'jpeg',quality:85});}}
else{const D=Number(process.argv[3]||21),FPS=30;
 const ff=spawn('ffmpeg',['-y','-loglevel','error','-f','image2pipe','-framerate',String(FPS),'-c:v','mjpeg','-i','-','-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','v3d_tmp.mp4']);
 const t0=Date.now();
 for(let i=0;i<D*FPS;i++){await p.evaluate(t=>render(t),i/FPS);const buf=await p.screenshot({type:'jpeg',quality:92});if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));if(i%60==0)console.log(i,(Date.now()-t0)/1000);}
 ff.stdin.end();await new Promise(r=>ff.on('close',r));}
await b.close();})();
