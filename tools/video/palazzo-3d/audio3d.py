import numpy as np, wave
SR=44100; DUR=22.0
buf=np.zeros(int(SR*(DUR+1)))
def nf(m): return 440*2**((m-69)/12)
def add(t,s):
    i=int(t*SR); j=min(len(buf),i+len(s))
    if j>i: buf[i:j]+=s[:j-i]
def pad(m,dur,vol=.035):
    t=np.arange(int(SR*dur))/SR; f=nf(m)
    w=sum(np.sin(2*np.pi*f*k*t*(1+0.0015*(k-1)))/k**1.6 for k in (1,2,3))
    env=np.minimum(1,t/0.8)*np.minimum(1,(dur-t)/0.8); return w*env*vol
def pluck(m,vol=.10,dur=1.2):
    t=np.arange(int(SR*dur))/SR; f=nf(m)
    return (np.sin(2*np.pi*f*t)+.3*np.sin(4*np.pi*f*t))*np.exp(-t*4)*vol
def whoosh(dur=1.0,vol=.05):
    n=int(SR*dur); x=np.random.randn(n); k=np.ones(60)/60; x=np.convolve(x,k,'same')
    t=np.arange(n)/n; return x*np.sin(np.pi*t)**2*vol*4
def pop(m=84,vol=.12):
    t=np.arange(int(SR*.25))/SR; f=nf(m)*(1+.5*np.exp(-t*40)); return np.sin(2*np.pi*f*t)*np.exp(-t*18)*vol
chords=[[48,55,59,64],[45,52,55,60],[41,48,52,57],[43,50,55,59]]
bar=60/88*4
t=0;c=0
while t<DUR:
    ch=chords[c%4]
    for m in ch: add(t,pad(m+12,bar+0.6))
    add(t,pad(ch[0]-12,bar+0.4,.05))
    arp=[ch[1]+24,ch[2]+24,ch[3]+24,ch[2]+24]
    for k in range(8): add(t+k*bar/8,pluck(arp[k%4],.045,.9))
    t+=bar;c+=1
for tt in (2.8,4.6,9.4,13.0,16.0,19.0): add(tt-0.3,whoosh(1.0))
for tt in (4.7,9.3,12.9,15.9): add(tt,pop())
add(10.2,pop(88,.1)); add(11.1,pop(91,.1)); add(11.25,pop(96,.08))
for k,m in enumerate([72,76,79,84]): add(19.1+k*0.12,pluck(m,.12,1.6))
n=int(SR*DUR); x=buf[:n]
fade=np.ones(n); fl=int(SR*1.5); fade[-fl:]=np.linspace(1,0,fl); x=x*fade
x=x/np.max(np.abs(x))*0.85
with wave.open('a3d.wav','wb') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x*32767).astype(np.int16).tobytes())
print('ok')
