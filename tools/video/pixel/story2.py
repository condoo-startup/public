import math, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw
from reel import txt, sprite, F8, F16, K, W, NAVY, BLUE, LBLUE, AMB, GRN, GREY, SKIN, PANTS, sq, tri, add, note_f, SR

FPS=30; DUR=22.0
SKY_N=(14,20,44); SKY_D=(150,196,240)
WALLB=(58,70,104); SLAB=(36,44,70)
HAIRS=[(96,48,24),(30,30,36),(200,160,80),(150,60,40),(70,40,20),(230,220,200)]
SHIRTS=[(47,111,229),(31,157,99),(232,163,61),(200,80,90),(120,90,200),(240,240,240)]
PPL=[sprite(HAIRS[i%6],SHIRTS[(i*2+1)%6]) for i in range(10)]
ADM=sprite((176,176,184),AMB)

def cap(img,lines,y=8,col=W):
    for i,l in enumerate(lines):
        x=(180-len(l)*8)//2
        for dx,dy in ((1,1),(1,0),(0,1)): txt(img,(x+dx,y+i*12+dy),l,K)
        txt(img,(x,y+i*12),l,col)

def seat(g,spr,x,y):  # draw only top 12 rows (seated, legs hidden)
    s=spr.crop((0,0,16,12)); g.paste(s,(int(x),int(y)),s)
def stand(g,spr,x,y,bob=0): g.paste(spr,(int(x),int(y)-bob),spr)

ROOMC=[(244,226,170),(214,226,244),(236,214,190),(222,236,214),(240,220,200),(46,54,80),(226,232,206),(232,214,236)]
def room(g,i,x0,y0,t,env=False):
    d=ImageDraw.Draw(g); w=76; h=50
    d.rectangle([x0,y0,x0+w,y0+h],fill=ROOMC[i])
    d.rectangle([x0,y0+h-6,x0+w,y0+h],fill=(150,100,60) if i!=5 else (60,50,50))
    fl=y0+h-6
    if i==0:
        d.rectangle([x0+50,fl-18,x0+70,fl],fill=(150,156,170)); d.rectangle([x0+54,fl-24,x0+64,fl-18],fill=K)
        for k in range(3):
            ph=(t*1.5+k*.33)%1; d.point((x0+58+int(math.sin(ph*6+k)*2),fl-26-int(ph*10)),fill=W)
        stand(g,PPL[0],x0+30,fl-16)
    elif i==1:
        d.rectangle([x0+6,fl-12,x0+40,fl],fill=(47,111,229)); d.rectangle([x0+6,fl-18,x0+12,fl],fill=(32,80,180))
        d.rectangle([x0+26,fl-16,x0+34,fl-12],fill=AMB); d.point((x0+33,fl-17),fill=AMB)
        tvc=[(120,200,250),(200,230,255),(90,160,230)][int(t*6)%3]
        d.rectangle([x0+52,fl-26,x0+70,fl-12],fill=K); d.rectangle([x0+54,fl-24,x0+68,fl-14],fill=tvc)
        seat(g,PPL[1],x0+12,fl-22)
    elif i==2:
        d.rectangle([x0+14,fl-14,x0+36,fl],fill=(200,80,90)); d.line([x0+50,fl,x0+50,fl-26],fill=K); d.polygon([(x0+44,fl-26),(x0+56,fl-26),(x0+52,fl-32),(x0+48,fl-32)],fill=AMB)
        seat(g,PPL[2],x0+18,fl-22); d.rectangle([x0+22,fl-14,x0+30,fl-10],fill=W)
    elif i==3:
        d.rectangle([x0+30,fl-16,x0+66,fl-14],fill=(120,80,50)); d.line([x0+32,fl-14,x0+32,fl],fill=(120,80,50)); d.line([x0+64,fl-14,x0+64,fl],fill=(120,80,50))
        d.rectangle([x0+44,fl-24,x0+58,fl-16],fill=K); d.rectangle([x0+45,fl-23,x0+57,fl-17],fill=(170,210,250))
        seat(g,PPL[3],x0+46,fl-26)
    elif i==4:
        d.rectangle([x0+4,fl-12,x0+44,fl],fill=(31,157,99))
        seat(g,PPL[4],x0+8,fl-22); seat(g,PPL[5],x0+26,fl-22)
        tvc=[(120,200,250),(250,230,160)][int(t*4)%2]
        d.rectangle([x0+54,fl-26,x0+72,fl-12],fill=K); d.rectangle([x0+56,fl-24,x0+70,fl-14],fill=tvc)
    elif i==5:
        d.rectangle([x0+10,fl-10,x0+60,fl],fill=(90,100,140)); d.rectangle([x0+10,fl-16,x0+16,fl],fill=(70,80,120))
        d.rectangle([x0+18,fl-14,x0+26,fl-8],fill=SKIN); d.rectangle([x0+18,fl-15,x0+26,fl-13],fill=(70,40,20))
        txt(g,(x0+34,fl-30),"z",(150,160,200))
        if env: d.rectangle([x0+62,fl-10,x0+68,fl-6],fill=(200,230,255))
    elif i==6:
        for (px,py) in [(x0+56,fl-20),(x0+62,fl-26),(x0+68,fl-18),(x0+60,fl-14)]: d.ellipse([px-5,py-5,px+5,py+5],fill=GRN,outline=K)
        d.rectangle([x0+56,fl-10,x0+68,fl],fill=(168,104,56))
        stand(g,PPL[6],x0+30,fl-16)
        if int(t*4)%2: d.point((x0+48,fl-8),fill=(88,168,240))
    elif i==7:
        px=x0+10+int((math.sin(t*1.4)+1)*24)
        stand(g,PPL[7],px,fl-16,bob=int(t*6)%2)
    # window frame of room (front cut) — light spill
    if env and i!=5:
        ex,ey=x0+w-14,y0+6
        d.rectangle([ex,ey,ex+10,ey+7],fill=K); d.rectangle([ex+1,ey+1,ex+9,ey+6],fill=W); d.line([ex+1,ey+1,ex+5,ey+4],fill=BLUE); d.line([ex+9,ey+1,ex+5,ey+4],fill=BLUE)

def envelope(d,x,y):
    d.rectangle([x,y,x+10,y+7],fill=K); d.rectangle([x+1,y+1,x+9,y+6],fill=W); d.line([x+1,y+1,x+5,y+4],fill=BLUE); d.line([x+9,y+1,x+5,y+4],fill=BLUE)

ROOMS=[(f,a,12+79*a,52+50*f) for f in range(4) for a in range(2)]
def building(t,envs=0.0,office_lit=False):
    g=Image.new('RGB',(180,320),SKY_N); d=ImageDraw.Draw(g)
    for k in range(30):
        x=(k*41)%180; y=(k*23)%44
        if (k+int(t*3))%7: d.point((x,y),fill=(120,130,170))

    d.rectangle([6,46,174,302],fill=WALLB); d.rectangle([2,42,178,48],fill=SLAB)
    for idx,(f,a,x0,y0) in enumerate(ROOMS):
        got = envs>0 and t>=ENV_T0+idx*0.25+0.6
        room(g,idx,x0,y0+2,t,env=got)
    for f in range(5): d.rectangle([6,50+50*f,174,51+50*f],fill=SLAB)
    d.rectangle([89,50,90,252],fill=SLAB)
    # ground floor
    gy=252
    d.rectangle([12,gy+2,88,gy+48],fill=(244,226,170) if office_lit else (46,54,80))
    txt(g,(16,gy+5),"Ufficio",K if office_lit else (90,100,130))
    d.rectangle([40,gy+32,80,gy+34],fill=(120,80,50)); d.line([42,gy+34,42,gy+48],fill=(120,80,50)); d.line([78,gy+34,78,gy+48],fill=(120,80,50))
    if office_lit:
        d.rectangle([52,gy+24,66,gy+32],fill=K); d.rectangle([53,gy+25,65,gy+31],fill=(170,210,250))
        seat(g,ADM,54,gy+20)
    d.rectangle([91,gy+2,168,gy+48],fill=(46,54,80)); txt(g,(95,gy+5),"Sala",(90,100,130))
    for c in range(4): d.rectangle([100+c*16,gy+38,108+c*16,gy+48],fill=(70,80,110))
    d.rectangle([2,302,178,320],fill=(70,70,84)); d.rectangle([2,302,178,304],fill=(110,110,126))
    # flying envelopes
    if envs>0:
        for idx,(f,a,x0,y0) in enumerate(ROOMS):
            st=ENV_T0+idx*0.25; p=(t-st)/0.6
            if 0<=p<1:
                sx,sy=60,gy+20; ex,ey=x0+62,y0+8
                x=sx+(ex-sx)*p; y=sy+(ey-sy)*p-math.sin(p*math.pi)*20
                envelope(d,int(x),int(y))
    return g

ENV_T0=7.0
def sala(t):
    g=Image.new('RGB',(180,320),(234,240,250)); d=ImageDraw.Draw(g)
    d.rectangle([0,0,179,48],fill=NAVY)
    d.rectangle([0,260,179,319],fill=(170,120,72)); d.rectangle([0,258,179,260],fill=(120,80,50))
    for x in range(0,180,20): d.line([x,262,x,319],fill=(150,104,62))
    d.rectangle([126,80,166,120],fill=K); d.rectangle([128,82,164,118],fill=SKY_D); d.line([146,82,146,118],fill=K)
    d.rectangle([14,70,110,126],fill=K); d.rectangle([16,72,108,124],fill=W)
    txt(g,(22,80),"ASSEMBLEA",BLUE); txt(g,(22,96),"ordine",K); txt(g,(22,108),"del giorno",K)
    d.rectangle([150,186,176,258],fill=(168,104,56)); d.rectangle([170,222,172,224],fill=AMB)
    stand(g,ADM,20,242)
    chairs=[(52+c*24,236) for c in range(4)]+[(40+c*24,256) for c in range(5)]
    for i,(cx,cy) in enumerate(chairs):
        d.rectangle([cx,cy-10,cx+2,cy+2],fill=(60,70,100)); d.rectangle([cx,cy-2,cx+14,cy],fill=(60,70,100)); d.line([cx+13,cy,cx+13,cy+2],fill=(60,70,100))
    for i,(cx,cy) in enumerate(chairs):
        st=0.6+i*0.38; p=(t-st)/0.7
        spr=PPL[i%10]
        if p<0: continue
        if p<1:
            x=158+(cx+2-158)*p; stand(g,spr,x,cy-16 if cy==256 else cy-16,bob=int(t*8)%2)
        else:
            seat(g,spr,cx+2,cy-14)
            d.rectangle([cx,cy-2,cx+14,cy],fill=(60,70,100))
    return g

def phone(t):
    g=Image.new('RGB',(180,320),NAVY); d=ImageDraw.Draw(g)
    for k in range(40):
        d.point(((k*53)%180,(k*97)%320),fill=(60,84,124))
    d.rounded_rectangle([24,60,156,300],radius=12,fill=K); d.rectangle([30,74,150,288],fill=(234,242,251))
    d.rectangle([76,64,104,66],fill=(60,70,90))
    txt(g,(36,80),"Calendario",K)
    for r in range(5):
        for c in range(7):
            n=r*7+c+1
            if n>30: continue
            x=36+c*16; y=98+r*16
            hl=(n==18)
            d.rectangle([x,y,x+13,y+13],fill=BLUE if hl else W)
            if n in (6,25): d.rectangle([x+2,y+10,x+11,y+11],fill=AMB)
            if n==12: d.rectangle([x+2,y+10,x+11,y+11],fill=GRN)
            if hl: d.rectangle([x+4,y+4,x+9,y+9],fill=W)
    d.rectangle([36,184,144,214],fill=W,outline=(200,210,225)); d.rectangle([36,184,39,214],fill=BLUE)
    txt(g,(44,190),"Assemblea",K); txt(g,(44,202),"ordinaria",GREY)
    blink=int(t*3)%2
    d.rectangle([36,222,144,244],fill=(234,241,254));
    bx,by=42,226
    d.polygon([(bx+4,by),(bx+8,by),(bx+11,by+10),(bx+1,by+10)],fill=AMB if blink else BLUE); d.rectangle([bx+5,by+11,bx+7,by+13],fill=AMB if blink else BLUE)
    txt(g,(58,230),"Promemoria",BLUE)
    txt(g,(36,262),"Esempio",GREY)
    return g

def endcard(t):
    g=Image.new('RGB',(180,320),NAVY); d=ImageDraw.Draw(g)
    for k in range(60):
        if (k+int(t*4))%5: d.point(((k*37)%180,(k*71)%320),fill=(60,84,124))
    txt(g,(30,120),"Cond",W,F16)
    for cx in (106,126):
        d.ellipse([cx-8,120,cx+8,136],fill=LBLUE); d.ellipse([cx-4,124,cx+4,132],fill=NAVY)
    txt(g,(22,160),"Registrati",W); txt(g,(22,174),"gratis su",W)
    if int(t*2.5)%2==0 or t<0.6: txt(g,(22,196),"condoo.eu",AMB,F16)
    return g

def fade(g,col,a): return Image.blend(g,Image.new('RGB',g.size,col),max(0,min(1,a)))

def frame(t):
    if t<4.5:
        g=building(t)
        cap(g,["Sera. Domani c'è","l'assemblea."] if t<2.6 else ["Lo sa qualcuno?"])
        return fade(g,K,1-t/0.4) if t<0.4 else g
    if t<10.0:
        g=building(t,envs=1.0 if t>=ENV_T0 else 0,office_lit=t>=4.9)
        cap(g,["L'amministratore la","mette in calendario."] if t<ENV_T0 else ["Il promemoria","arriva via email."])
        return fade(g,K,(t-9.6)/0.4) if t>9.6 else g
    if t<15.0:
        g=sala(t-10.0)
        cap(g,["Il giorno dopo,","alle 18."] if t<12.6 else ["In sala,","l'assemblea."])
        g=fade(g,K,1-(t-10.0)/0.4) if t<10.4 else g
        return fade(g,K,(t-14.6)/0.4) if t>14.6 else g
    if t<18.5:
        g=phone(t)
        cap(g,["L'assemblea è nel","calendario di Condoo."],y=20)
        g=fade(g,K,1-(t-15.0)/0.4) if t<15.4 else g
        return fade(g,K,(t-18.1)/0.4) if t>18.1 else g
    g=endcard(t-18.5)
    return fade(g,K,1-(t-18.5)/0.4) if t<18.9 else g

def audio(out):
    buf=np.zeros(int(SR*DUR)+SR)
    bpm=96; e=60/bpm/2
    lead="E5 - G5 - A5 G5 E5 - D5 - E5 - C5 - - - C5 - D5 - E5 G5 A5 - G5 - E5 - D5 - - -".split()
    bass="C3 G2 A2 E2 F2 C3 G2 G2".split()
    t=0.0;i=0
    while t<18.5:
        n=lead[i%len(lead)]
        if n!='-': add(buf,t,sq(note_f(n),e*1.6,0.05,0.125))
        if i%4==0: add(buf,t,tri(note_f(bass[(i//4)%len(bass)]),e*3.6,0.14))
        if i%2==1: add(buf,t,sq(note_f("C7"),0.01,0.012))
        t+=e;i+=1
    for idx in range(8):
        tt=ENV_T0+idx*0.25+0.6; add(buf,tt,sq(note_f("E6"),0.05,0.07)); add(buf,tt+0.05,sq(note_f("A6"),0.07,0.06))
    for k,n in enumerate(["C5","E5","G5"]): add(buf,4.9+k*0.06,sq(note_f(n),0.06,0.06))
    for k,n in enumerate(["G5","C6","E6","G6"]): add(buf,15.2+k*0.09,sq(note_f(n),0.09,0.08,.25))
    for k,n in enumerate(["C5","E5","G5","C6","G5","C6"]): add(buf,18.7+k*0.12,sq(note_f(n),0.11,0.1,.25))
    add(buf,18.7,tri(note_f("C3"),1.4,.18))
    buf=np.clip(buf,-1,1); pcm=(buf*32767*.9).astype(np.int16)
    with wave.open(out,'wb') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())

if __name__=="__main__":
    if sys.argv[1]=="stills":
        ts=[2.0,5.5,8.4,11.5,13.8,16.5,20.0]
        m=Image.new('RGB',(7*365,650),'white')
        for i,t in enumerate(ts): m.paste(frame(t).resize((360,640),Image.NEAREST),(i*365,0))
        m.save('sheet2.png')
    else:
        audio('a2.wav')
        p=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r',str(FPS),'-i','-','-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','s2_v.mp4'],stdin=subprocess.PIPE)
        for i in range(int(DUR*FPS)): p.stdin.write(frame(i/FPS).resize((1080,1920),Image.NEAREST).tobytes())
        p.stdin.close(); p.wait()
        subprocess.run(['ffmpeg','-y','-loglevel','error','-i','s2_v.mp4','-i','a2.wav','-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','160k','-shortest','condoo-reel-pixel-assemblea.mp4'],check=True)
        print("done")
