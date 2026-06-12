#!/usr/bin/env python3
"""
make_figures.py — generates the deck's infographics and flag chips as
transparent PNGs in assets/figures/. Everything is drawn from primitives
in the deck's navy/gold palette so the visuals match the slides exactly.

Each figure is drawn supersampled (SS x) and downsampled with LANCZOS for
clean edges. Coordinates below are in *final* pixels; helpers scale by SS.
"""
import os, math
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(HERE, "assets", "figures")
os.makedirs(OUT, exist_ok=True)

NAVY=(0x0F,0x2A,0x43,255); SLATE=(0x33,0x44,0x55,255); ACCENT=(0xC0,0x8A,0x2B,255)
LIGHT=(0xF2,0xF4,0xF7,255); WHITE=(0xFF,0xFF,0xFF,255); GREY=(0x6B,0x76,0x82,255)
PANEL=(0xE8,0xEC,0xF1,255); RED=(0xB3,0x3A,0x3A,255); MUTE=(0xA9,0xB3,0xBE,255)
SS=3
FB="/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
FR="/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
FI="/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
_fc={}
def fnt(px,b=True,i=False):
    p=FB if b and not i else FI if i else FR
    k=(p,int(px*SS))
    if k not in _fc: _fc[k]=ImageFont.truetype(p,int(px*SS))
    return _fc[k]

class Fig:
    def __init__(self,w,h):
        self.w,self.h=w,h
        self.im=Image.new("RGBA",(w*SS,h*SS),(0,0,0,0))
        self.d=ImageDraw.Draw(self.im)
    def box(self,x,y,w,h,fill=None,outline=None,width=2,r=10):
        self.d.rounded_rectangle([x*SS,y*SS,(x+w)*SS,(y+h)*SS],radius=r*SS,
                                 fill=fill,outline=outline,width=int(width*SS))
    def line(self,x0,y0,x1,y1,fill=ACCENT,width=3,dash=None):
        if dash:
            seg,gap=dash; L=math.hypot(x1-x0,y1-y0); n=max(1,int(L/(seg+gap)))
            for k in range(n+1):
                a=k*(seg+gap)/L; b=min(1,(k*(seg+gap)+seg)/L)
                self.d.line([(x0+(x1-x0)*a)*SS,(y0+(y1-y0)*a)*SS,
                             (x0+(x1-x0)*b)*SS,(y0+(y1-y0)*b)*SS],fill=fill,width=int(width*SS))
        else:
            self.d.line([x0*SS,y0*SS,x1*SS,y1*SS],fill=fill,width=int(width*SS))
    def arrow(self,x0,y0,x1,y1,fill=ACCENT,width=4,head=14):
        self.line(x0,y0,x1,y1,fill,width)
        ang=math.atan2(y1-y0,x1-x0)
        for s in (+1,-1):
            a=ang+s*math.radians(26)
            self.d.line([x1*SS,y1*SS,(x1-head*math.cos(a))*SS,(y1-head*math.sin(a))*SS],
                        fill=fill,width=int(width*SS))
    def dot(self,x,y,r,fill=ACCENT,outline=None,width=2):
        self.d.ellipse([(x-r)*SS,(y-r)*SS,(x+r)*SS,(y+r)*SS],fill=fill,
                       outline=outline,width=int(width*SS))
    def text(self,x,y,s,px=20,fill=NAVY,b=True,i=False,anchor="mm",spacing=4):
        self.d.multiline_text((x*SS,y*SS),s,font=fnt(px,b,i),fill=fill,
                              anchor=anchor,align="center",spacing=spacing*SS)
    def save(self,name):
        out=self.im.resize((self.w,self.h),Image.LANCZOS)
        out.save(os.path.join(OUT,name+".png"))
        return out

# ----------------------------------------------------------------------
# Slide 8 — domestic crime vs transnational crime
def fig_transnational():
    f=Fig(1000,1000)
    # top: one state contains the whole case
    f.text(500,70,"DOMESTIC CRIME",30,ACCENT)
    f.box(250,120,500,210,fill=NAVY,r=18)
    f.text(500,175,"ONE STATE",26,WHITE)
    f.dot(420,250,16,fill=ACCENT); f.dot(500,250,16,fill=ACCENT); f.dot(580,250,16,fill=ACCENT)
    f.text(500,300,"one system investigates,\ncharges & tries the case",19,SLATE,b=False,i=True)
    # divider
    f.line(120,400,880,400,fill=MUTE,width=2,dash=(16,12))
    # bottom: case spread across three states
    f.text(500,470,"TRANSNATIONAL CRIME",30,ACCENT)
    cx=[250,500,750]; cy=620; bw=200; bh=150
    for i,x in enumerate(cx):
        f.box(x-bw/2,cy-bh/2,bw,bh,fill=NAVY,r=16)
        f.text(x,cy,"STATE\n"+chr(65+i),24,WHITE,spacing=2)
    f.arrow(250+bw/2,cy-30,500-bw/2,cy-30); f.arrow(500+bw/2,cy-30,750-bw/2,cy-30)
    f.arrow(750-bw/2,cy+34,500+bw/2,cy+34); f.arrow(500-bw/2,cy+34,250+bw/2,cy+34)
    for x in (375,625):
        f.line(x,cy-bh/2-26,x,cy+bh/2+26,fill=MUTE,width=2,dash=(12,10))
    f.text(500,790,"people · money · evidence cross borders",20,SLATE,b=False,i=True)
    f.text(500,855,"no single system can reach all of it",20,NAVY,b=True)
    f.save("fig_transnational")

# Slide 9 — Palermo's three elements
def fig_palermo():
    f=Fig(1000,1000)
    rows=[("ACT","recruit · transport · harbour"),
          ("MEANS","force · fraud · coercion"),
          ("PURPOSE","exploitation")]
    y=80; bh=150; gap=70
    for i,(t,sub) in enumerate(rows):
        f.box(150,y,700,bh,fill=LIGHT,outline=ACCENT,width=4,r=18)
        f.text(280,y+bh/2,t,30,NAVY)
        f.line(430,y+34,430,y+bh-34,fill=MUTE,width=2)
        f.text(645,y+bh/2,sub,20,SLATE,b=False)
        if i<2: f.text(500,y+bh+gap/2,"+",40,ACCENT)
        y+=bh+gap
    f.arrow(500,y-6,500,y+58,width=5,head=20)
    f.box(220,y+70,560,150,fill=NAVY,r=18)
    f.text(500,y+145,"= HUMAN TRAFFICKING",27,WHITE)
    f.save("fig_palermo")

# Slide 10 — UNTOC parent treaty + supplementing protocols + tools
def fig_untoc():
    f=Fig(1000,1000)
    f.box(180,70,640,150,fill=NAVY,r=18)
    f.text(500,130,"UNTOC  (2000)",30,WHITE)
    f.text(500,182,"UN Convention against Transnational Organized Crime",15,LIGHT,b=False,i=True)
    f.line(500,220,500,290,fill=ACCENT,width=4)
    xs=[235,500,765]
    f.line(235,290,765,290,fill=ACCENT,width=4)
    for x in xs: f.line(x,290,x,330,fill=ACCENT,width=4)
    labels=[("Migrant\nSmuggling",MUTE,WHITE),("PALERMO\nPROTOCOL",ACCENT,NAVY),("Firearms",MUTE,WHITE)]
    for x,(t,fill,tc) in zip(xs,labels):
        f.box(x-150,330,300,150,fill=fill,r=16)
        f.text(x,405,t,21,tc,spacing=2)
    f.text(500,520,"trafficking protocol",15,SLATE,b=False,i=True)
    # tools bar
    f.box(150,600,700,300,fill=LIGHT,outline=ACCENT,width=4,r=18)
    f.text(500,650,"SHARED MACHINERY",22,ACCENT)
    tools=["Extradition","Mutual legal assistance","Joint investigations","Asset confiscation"]
    yy=705
    for t in tools:
        f.dot(285,yy,9,fill=ACCENT); f.text(320,yy,t,20,SLATE,b=False,anchor="lm"); yy+=50
    f.save("fig_untoc")

# Slide 11 — cross-border enforcement between two states
def fig_enforcement():
    f=Fig(1000,1000)
    bw=300; bh=240; ay=130; ax=80; bx=620
    f.box(ax,ay,bw,bh,fill=NAVY,r=18)
    f.text(ax+bw/2,ay+95,"STATE A",26,WHITE); f.text(ax+bw/2,ay+145,"requesting",17,LIGHT,b=False,i=True)
    f.box(bx,ay,bw,bh,fill=NAVY,r=18)
    f.text(bx+bw/2,ay+95,"STATE B",26,WHITE); f.text(bx+bw/2,ay+145,"requested",17,LIGHT,b=False,i=True)
    midL,midR=ax+bw,bx           # 380 .. 620 central channel
    # extradition (top) A -> B
    f.text(500,ay+30,"EXTRADITION",18,NAVY)
    f.arrow(midL+10,ay+72,midR-10,ay+72,width=5,head=16)
    f.text(500,ay+112,"treaty +\n“dual criminality”",15,SLATE,b=False,i=True,spacing=2)
    # MLAT (bottom) B -> A
    f.arrow(midR-10,ay+185,midL+10,ay+185,width=5,head=16)
    f.text(500,ay+218,"evidence (MLAT)",16,NAVY)
    f.line(120,470,880,470,fill=MUTE,width=2,dash=(16,12))
    f.text(500,535,"THE FRICTION",24,ACCENT)
    for i,t in enumerate(["requests are slow","can be refused",
                          "stall for wealthy, well-connected suspects"]):
        f.dot(250,610+i*82,9,fill=ACCENT); f.text(285,610+i*82,t,19,SLATE,b=False,anchor="lm")
    f.save("fig_enforcement")

# Slide 14 — offshore layering hides the owner
def fig_layering():
    f=Fig(1000,1000)
    f.box(230,70,540,150,fill=NAVY,r=18)
    f.text(500,130,"BENEFICIAL OWNER",26,WHITE)
    f.text(500,180,"who really controls the wealth",16,LIGHT,b=False,i=True)
    f.line(160,300,840,300,fill=ACCENT,width=3,dash=(20,14))
    f.text(500,275,"ownership obscured",18,ACCENT,i=True)
    layers=["Trust","Shell company","Nominee director"]
    y=350; bh=120; gap=40
    prevy=220
    for t in layers:
        f.arrow(500,prevy+4,500,y-6,width=4,head=14)
        f.box(260,y,480,bh,fill=LIGHT,outline=ACCENT,width=4,r=14)
        f.text(500,y+bh/2,t,23,NAVY)
        prevy=y+bh; y+=bh+gap
    f.arrow(500,prevy+4,500,y-6,width=4,head=14)
    f.box(210,y,580,150,fill=NAVY,r=18)
    f.text(500,y+58,"ASSETS",24,WHITE)
    f.text(500,y+105,"property · accounts · aircraft",17,LIGHT,b=False,i=True)
    f.save("fig_layering")

# Slide 18 — transparency vs victim safety
def fig_redaction():
    f=Fig(1000,1000)
    # a document
    f.box(210,70,580,860,fill=WHITE,outline=GREY,width=3,r=16)
    f.text(500,140,"CASE FILE  ·  2025 RELEASE",22,NAVY)
    f.line(260,185,740,185,fill=MUTE,width=2)
    # ordinary lines
    for yy in (235,275,315):
        f.line(280,yy,720,yy,fill=MUTE,width=10)
    # survivor line — exposed
    f.box(260,365,480,86,fill=(0xF6,0xE4,0xD8,255),outline=RED,width=3,r=10)
    f.text(500,392,"survivor identity",18,RED)
    f.text(500,425,"easy to identify",17,RED,b=False,i=True)
    for yy in (505,545,585):
        f.line(280,yy,720,yy,fill=MUTE,width=10)
    # enabler line — redacted
    f.box(260,640,480,86,fill=NAVY,r=10)
    f.text(500,667,"possible enabler",18,WHITE)
    f.text(500,700,"redacted / unknown",17,LIGHT,b=False,i=True)
    for yy in (780,820,860):
        f.line(280,yy,720,yy,fill=MUTE,width=10)
    f.save("fig_redaction")

# ----------------------------------------------------------------------
# Flags (2:1), thin grey frame so they read as flags on a light panel
def _flag(w=300):
    h=w//2; im=Image.new("RGBA",(w*SS,h*SS),(0,0,0,0)); return im,ImageDraw.Draw(im),w*SS,h*SS
def _finish(im,name):
    w=im.size[0]//SS; out=im.resize((w,w//2),Image.LANCZOS)
    d=ImageDraw.Draw(out); d.rectangle([0,0,out.size[0]-1,out.size[1]-1],outline=(0x6B,0x76,0x82,255),width=2)
    out.save(os.path.join(OUT,name+".png"))

def flag_jp():
    im,d,W,H=_flag(); d.rectangle([0,0,W,H],fill=WHITE)
    r=int(H*0.30); d.ellipse([W/2-r,H/2-r,W/2+r,H/2+r],fill=(0xBC,0x00,0x2D,255))
    _finish(im,"flag_jp")
def flag_fr():
    im,d,W,H=_flag()
    d.rectangle([0,0,W/3,H],fill=(0x00,0x35,0x80,255))
    d.rectangle([W/3,0,2*W/3,H],fill=WHITE)
    d.rectangle([2*W/3,0,W,H],fill=(0xED,0x29,0x39,255))
    _finish(im,"flag_fr")
def flag_us():
    im,d,W,H=_flag(); red=(0xB2,0x22,0x34,255); blue=(0x3C,0x3B,0x6E,255)
    for i in range(13):
        if i%2==0: d.rectangle([0,H*i/13,W,H*(i+1)/13],fill=red)
        else: d.rectangle([0,H*i/13,W,H*(i+1)/13],fill=WHITE)
    d.rectangle([0,0,W*0.40,H*7/13],fill=blue)
    for r in range(5):
        for c in range(6):
            cx=W*0.40*(c+0.7)/6; cy=H*7/13*(r+0.7)/5
            rr=H*0.018; d.ellipse([cx-rr,cy-rr,cx+rr,cy+rr],fill=WHITE)
    _finish(im,"flag_us")
def flag_uk():
    im,d,W,H=_flag(); blue=(0x01,0x20,0x69,255); red=(0xC8,0x10,0x2E,255)
    d.rectangle([0,0,W,H],fill=blue)
    # white diagonals then red diagonals (counterchanged, approximate)
    d.line([0,0,W,H],fill=WHITE,width=int(H*0.22)); d.line([W,0,0,H],fill=WHITE,width=int(H*0.22))
    d.line([0,0,W,H],fill=red,width=int(H*0.10)); d.line([W,0,0,H],fill=red,width=int(H*0.10))
    # white cross then red cross
    d.rectangle([W/2-H*0.17,0,W/2+H*0.17,H],fill=WHITE)
    d.rectangle([0,H/2-H*0.17,W,H/2+H*0.17],fill=WHITE)
    d.rectangle([W/2-H*0.10,0,W/2+H*0.10,H],fill=red)
    d.rectangle([0,H/2-H*0.10,W,H/2+H*0.10],fill=red)
    _finish(im,"flag_uk")

if __name__=="__main__":
    fig_transnational(); fig_palermo(); fig_untoc()
    fig_enforcement(); fig_layering(); fig_redaction()
    flag_jp(); flag_fr(); flag_us(); flag_uk()
    print("figures + flags written to", OUT)
