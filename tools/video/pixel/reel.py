import math, os, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FPS=30
F8=ImageFont.truetype(os.path.join(os.path.dirname(os.path.abspath(__file__)),'ps2p.woff'),8)
F16=ImageFont.truetype(os.path.join(os.path.dirname(os.path.abspath(__file__)),'ps2p.woff'),16)
K=(24,24,40); W=(248,248,240); NAVY=(31,47,74); BLUE=(47,111,229); LBLUE=(111,160,242)
AMB=(232,163,61); GRN=(31,157,99); GREY=(140,150,170)
FL1=(240,224,176); FL2=(224,200,144); WALL=(88,120,200); WALLD=(48,72,128); WIN=(168,208,248)
SKIN=(248,192,152); HAIR=(96,48,24); PANTS=(48,64,96); WATER=(88,168,240); WATERD=(40,88,184)
DOOR=(168,104,56)
EVENTS=[]  # (time, kind)

def txt(img,xy,s,col,font=F8):
    m=Image.new('L',img.size,0); ImageDraw.Draw(m).text(xy,s,font=font,fill=255)
    m=m.point(lambda v:255 if v>=128 else 0)
    img.paste(Image.new('RGB',img.size,col),(0,0),m)

P_HALF=["......kk","....kkhh","...khhhh","..khhhhh","..khhsss","..khssss","..ksskss","..ksssss",
        "...kssss","..kkbbbb",".kbbbbbb",".ksbbbbb","..kbbbbb","..kppppp","...kppk.","..kkkkk."]
def sprite(hair,shirt):
    rows=[h+h[::-1] for h in P_HALF]
    pal={'k':K,'h':hair,'s':SKIN,'b':shirt,'p':PANTS}
    im=Image.new('RGBA',(16,16),(0,0,0,0)); px=im.load()
    for y,r in enumerate(rows):
        for x,c in enumerate(r):
            if c in pal: px[x,y]=pal[c]+(255,)
    return im
PLAYER=sprite(HAIR,BLUE); ADMIN=sprite((176,176,184),AMB); ADMIN2=ADMIN.resize((32,32),Image.NEAREST)

def room(puddle=0.0,drip_t=None,sparkle_t=None):
    g=Image.new('RGB',(180,225),FL1); d=ImageDraw.Draw(g)
    for ty in range(40,225,16):
        for tx in range(0,180,16):
            if ((tx//16)+(ty//16))%2: d.rectangle([tx,ty,tx+15,ty+15],fill=FL2)
    d.rectangle([0,0,179,39],fill=WALL); d.rectangle([0,36,179,40],fill=WALLD)
    for wx in (14,136):
        d.rectangle([wx,8,wx+29,27],fill=K); d.rectangle([wx+2,10,wx+27,25],fill=WIN); d.line([wx+15,10,wx+15,25],fill=K); d.line([wx+2,17,wx+27,17],fill=K)
    d.rectangle([76,10,103,40],fill=K); d.rectangle([78,12,101,40],fill=DOOR); d.rectangle([97,26,99,28],fill=AMB)
    txt(g,(80,2),"WC",W)
    # rug
    d.rectangle([40,120,140,160],fill=K); d.rectangle([42,122,138,158],fill=LBLUE); d.rectangle([48,128,132,152],outline=W)
    # plant
    d.rectangle([156,58,168,70],fill=K); d.rectangle([158,60,166,70],fill=DOOR)
    for (x,y) in [(156,48),(162,44),(168,50),(160,52),(166,56)]: d.ellipse([x-4,y-4,x+4,y+4],fill=GRN,outline=K)
    # puddle
    if puddle>0:
        rx=int(6+14*puddle); ry=int(3+6*puddle)
        d.ellipse([90-rx,62-ry,90+rx,62+ry],fill=WATERD); d.ellipse([90-rx+2,62-ry+1,90+rx-2,62+ry-1],fill=WATER)
        d.rectangle([84,60,86,61],fill=W)
    if drip_t is not None:
        ph=(drip_t*1.6)%1.0; y=42+int(ph*18)
        d.rectangle([89,y,91,y+3],fill=WATER); d.point((90,y-1),fill=WATER)
    if sparkle_t is not None:
        for i,(sx,sy) in enumerate([(80,58),(100,66),(90,50),(110,56),(72,68)]):
            if int(sparkle_t*8+i)%3==0:
                d.line([sx-3,sy,sx+3,sy],fill=AMB); d.line([sx,sy-3,sx,sy+3],fill=AMB); d.point((sx,sy),fill=W)
    return g

def textbox(g,lines,t0,t,cps=30,arrow=True):
    d=ImageDraw.Draw(g)
    d.rectangle([3,165,176,222],fill=K); d.rectangle([5,167,174,220],fill=W); d.rectangle([7,169,172,218],outline=BLUE)
    n=int(max(0,t-t0)*cps); total=sum(len(l) for l in lines)
    shown=n; y=176
    for l in lines:
        s=l[:max(0,shown)]; shown-=len(l)
        txt(g,(12,y),s,K); y+=14
    if arrow and n>=total and int(t*3)%2==0:
        d.polygon([(162,208),(170,208),(166,212)],fill=K)
    return n,total

def menu(g,sel):
    d=ImageDraw.Draw(g)
    d.rectangle([91,103,176,162],fill=K); d.rectangle([93,105,174,160],fill=W); d.rectangle([95,107,172,158],outline=BLUE)
    for i,s in enumerate(["CHAT","CITOFONO","SEGNALA"]):
        txt(g,(108,114+i*15),s,K)
        if i==sel: d.polygon([(99,114+i*15),(99,121+i*15),(103,117+i*15)],fill=K)

def put(g,spr,x,y,bob=0):
    g.paste(spr,(int(x),int(y)-bob),spr)
def bubble(g,x,y):
    d=ImageDraw.Draw(g); d.rectangle([x,y,x+10,y+12],fill=K); d.rectangle([x+1,y+1,x+9,y+11],fill=W); d.rectangle([x+4,y+3,x+6,y+7],fill=(220,40,40)); d.rectangle([x+4,y+9,x+6,y+10],fill=(220,40,40))

def phone(g,stage,t):
    d=ImageDraw.Draw(g)
    d.rectangle([0,0,179,224],fill=NAVY)
    for i in range(40):
        x=(i*53)%180; y=(i*97)%225
        d.point((x,y),fill=(60,84,124))
    d.rounded_rectangle([12,4,128,160],radius=10,fill=K); d.rectangle([18,16,122,150],fill=(234,242,251))
    d.rectangle([58,8,82,10],fill=(60,70,90))
    txt(g,(22,20),"SEGNALAZ.",BLUE)
    d.rectangle([22,32,118,120],fill=W,outline=(200,210,225))
    txt(g,(26,37),"Perdita",K); txt(g,(26,48),"in bagno",K)
    d.rectangle([26,60,70,84],fill=(220,214,200)); d.ellipse([36,64,58,80],fill=(150,136,110)); d.ellipse([42,68,52,76],fill=(120,105,80))
    d.rectangle([74,60,114,84],fill=(214,222,236)); d.ellipse([84,64,104,80],fill=(170,186,214))
    # level pips
    cols=[BLUE,AMB,GRN]
    for i in range(3):
        x=26+i*31
        d.rectangle([x,94,x+27,104],fill=K)
        d.rectangle([x+1,95,x+26,103],fill=cols[i] if i<stage else (226,230,238))
    txt(g,(26,108),"Esempio",GREY)
    d.rectangle([60,152,80,154],fill=(60,70,90))
    # floor strip
    d.rectangle([128,146,179,160],fill=WALLD)

def endcard(t):
    g=Image.new('RGB',(180,225),NAVY); d=ImageDraw.Draw(g)
    for i in range(50):
        x=(i*37)%180; y=(i*71)%225
        if (i+int(t*4))%5: d.point((x,y),fill=(60,84,124))
    txt(g,(30,70),"Cond",W,F16)
    for cx in (106,126):
        d.ellipse([cx-8,70,cx+8,86],fill=LBLUE); d.ellipse([cx-4,74,cx+4,82],fill=NAVY)
    txt(g,(22,110),"Registrati",W); txt(g,(22,124),"gratis su",W)
    if int(t*2.5)%2==0 or t<0.6: txt(g,(22,146),"condoo.eu",AMB,F16)
    return g

def mark(t,kind):
    EVENTS.append((round(t,3),kind))

def frame(t):
    # S1 0-5
    if t<5.0:
        pud=min(1,t/3.0)
        g=room(pud,drip_t=t)
        if t<1.6:
            y=150-(t/1.6)*62; put(g,PLAYER,62,y,bob=(int(t*8)%2))
        else:
            put(g,PLAYER,62,88)
            if t>=1.6: bubble(g,64,72)
        if t>=2.0: textbox(g,["Oh no! Il soffitto","del bagno gocciola."],2.0,t)
        return g
    if t<10.0:
        g=room(1.0,drip_t=t); put(g,PLAYER,62,88)
        if t<6.2:
            textbox(g,["Cosa fai?"],5.0,t,arrow=False); menu(g,0)
        elif t<8.4:
            textbox(g,["Nel gruppo tutti","leggono. Nessuno","risponde..."],6.3,t)
        elif t<9.3:
            textbox(g,["Cosa fai?"],0,t,arrow=False); menu(g,0 if t<8.6 else (1 if t<8.95 else 2))
        else:
            textbox(g,["Usi SEGNALA!"],9.3,t)
        if t>9.8:
            a=(t-9.8)/0.2; g=Image.blend(g,Image.new('RGB',g.size,W),min(1,a))
        return g
    if t<17.0:
        stage=1 if t<13.5 else (2 if t<14.4 else 3)
        g=Image.new('RGB',(180,225)); phone(g,stage,t)
        if t>=11.8:
            ax=180-min(1,(t-11.8)/0.6)*44; put(g,ADMIN2,ax,115,bob=(int(t*8)%2 if t<12.4 else 0))
        put(g,PLAYER,140 if t>=11.8 else 150,130) if False else None
        if t<11.8: textbox(g,["Segnalazione","inviata!","Stato: APERTA"],10.1,t)
        elif t<13.5: textbox(g,["AMMINISTRATORE:","Idraulico in","arrivo!"],12.4,t)
        elif t<14.4: textbox(g,["Stato:","IN LAVORAZIONE"],13.5,t)
        elif t<15.6: textbox(g,["Stato:","RISOLTA!"],14.4,t)
        else: textbox(g,["La vedete solo tu","e l'amministratore."],15.6,t)
        if t<10.2:
            g=Image.blend(g,Image.new('RGB',g.size,W),max(0,1-(t-10.0)/0.2))
        return g
    if t<20.0:
        g=room(0,sparkle_t=t); put(g,PLAYER,62,88,bob=(2 if int(t*4)%2 else 0))
        textbox(g,["Missione","compiuta!"],17.3,t)
        if t>19.8:
            g=Image.blend(g,Image.new('RGB',g.size,K),min(1,(t-19.8)/0.2))
        return g
    return endcard(t-20.0)

def reel_canvas(g,t):
    c=Image.new('RGB',(180,320),NAVY); d=ImageDraw.Draw(c)
    txt(c,(10,12),"MISSIONE:",AMB); txt(c,(10,28),"PERDITA IN BAGNO",W)
    d.rectangle([0,52,179,53],fill=K); c.paste(g,(0,54)); d.rectangle([0,279,179,280],fill=K)
    txt(c,(10,292),"Esempio",GREY)
    return c

DUR=23.0
def render(kind,out):
    W_,H_=(1080,1920) if kind=="reel" else (1080,1350)
    p=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W_}x{H_}','-r',str(FPS),'-i','-',
                        '-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p',out],stdin=subprocess.PIPE)
    for i in range(int(DUR*FPS)):
        t=i/FPS; g=frame(t)
        im=reel_canvas(g,t) if kind=="reel" else g
        p.stdin.write(im.resize((W_,H_),Image.NEAREST).tobytes())
    p.stdin.close(); p.wait()

# ---------- audio ----------
SR=44100
def note_f(n):
    names={'C':-9,'D':-7,'E':-5,'F':-4,'G':-2,'A':0,'B':2}
    return 440*2**((names[n[0]]+12*(int(n[-1])-4))/12)
def sq(f,dur,vol=.2,duty=.5):
    t=np.arange(int(SR*dur))/SR; w=np.where((t*f)%1<duty,1.0,-1.0)*vol
    env=np.minimum(1,np.minimum(t/0.005,(dur-t)/0.02)); return w*np.clip(env,0,1)
def tri(f,dur,vol=.25):
    t=np.arange(int(SR*dur))/SR; w=(2*np.abs(2*((t*f)%1)-1)-1)*vol
    env=np.minimum(1,np.minimum(t/0.005,(dur-t)/0.02)); return w*np.clip(env,0,1)
def add(buf,t,s):
    i=int(t*SR); j=min(len(buf),i+len(s)); buf[i:j]+=s[:j-i]
def audio(out):
    buf=np.zeros(int(SR*DUR)+SR)
    bpm=132; e=60/bpm/2
    lead="E5 G5 A5 G5 E5 D5 C5 D5 E5 E5 G5 E5 D5 C5 A4 C5 F5 A5 C6 A5 G5 F5 E5 D5 E5 D5 C5 D5 C5 - - -".split()
    bass="C3 C3 G2 G2 A2 A2 E2 E2 F2 F2 C3 C3 G2 G2 C3 C3".split()
    t=0.0; i=0
    while t<20.0:
        n=lead[i%len(lead)]
        if n!='-': add(buf,t,sq(note_f(n),e*0.9,0.07,0.25))
        if i%2==0:
            b=bass[(i//2)%len(bass)]; add(buf,t,tri(note_f(b),e*1.8,0.16))
        t+=e; i+=1
    # typing blips: derive from textboxes by sampling text progress
    for (tt,k) in EVENTS: pass
    def blips(t0,nchars,cps=30):
        for c in range(0,nchars,2): add(buf,t0+c/cps,sq(1200,0.018,0.05))
    for t0,s in [(2.0,37),(5.0,9),(6.3,43),(9.3,12),(10.1,34),(12.4,34),(13.5,20),(14.4,14),(15.6,37),(17.3,17)]: blips(t0,s)
    def seq(t0,notes,d=0.07,vol=.12,duty=.5):
        for k,n in enumerate(notes): add(buf,t0+k*d,sq(note_f(n),d*0.95,vol,duty))
    seq(1.6,["C6","G6"],0.06)               # !
    for tc in (5.6,8.6,8.95): add(buf,tc,sq(880,0.03,0.08))  # cursor
    seq(6.2,["E6","A6"],0.05); seq(9.3,["E6","A6"],0.05)  # select
    seq(10.1,["C5","E5","G5","C6"],0.08,.12)  # aperta
    seq(13.5,["D5","F5","A5","D6"],0.08,.12)
    seq(14.4,["C5","E5","G5","C6","E6","G6","C7"],0.07,.13)
    seq(17.3,["G5","G5","G5","C6","-","G5","C6"] if False else ["G5","C6","E6","G6","E6","G6"],0.11,.12,.25)
    seq(20.2,["C5","E5","G5","C6","G5","C6"],0.12,.11,.25)
    add(buf,20.2,tri(note_f("C3"),1.2,.2))
    buf=np.clip(buf,-1,1); pcm=(buf*32767*.9).astype(np.int16)
    with wave.open(out,'wb') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())

if __name__=="__main__":
    if sys.argv[1]=="stills":
        for t in [0.8,3.5,5.8,7.5,9.1,11.0,13.0,14.8,16.2,18.5,21.0]:
            reel_canvas(frame(t),t).resize((540,960),Image.NEAREST).save(f'st_{t}.png')
    else:
        audio('a.wav')
        render("reel","reel_v.mp4"); render("feed","feed_v.mp4")
        for v,o in [("reel_v.mp4","condoo-reel-pixel-9x16.mp4"),("feed_v.mp4","condoo-video-pixel-4x5.mp4")]:
            subprocess.run(['ffmpeg','-y','-loglevel','error','-i',v,'-i','a.wav','-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','160k','-shortest',o],check=True)
        print("done")
