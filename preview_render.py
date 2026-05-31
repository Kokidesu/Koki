#!/usr/bin/env python3
"""Render the deck slides to PNG previews (1280x720), mirroring the pptx layout."""
from PIL import Image, ImageDraw, ImageFont

PX = 96  # px per inch -> 13.333x7.5in = 1280x720
def I(v): return int(round(v * PX))

NAVY=(0x0F,0x2A,0x43); SLATE=(0x33,0x44,0x55); ACCENT=(0xC0,0x8A,0x2B)
LIGHT=(0xF2,0xF4,0xF7); WHITE=(0xFF,0xFF,0xFF); GREY=(0x6B,0x76,0x82)

# Liberation Serif is metrically compatible with Times New Roman
FONT="/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
FONTB="/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
FONTI="/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
FONTBI="/usr/share/fonts/truetype/liberation/LiberationSerif-BoldItalic.ttf"

_cache={}
def font(sz, bold=False, italic=False):
    path = FONTBI if (bold and italic) else FONTB if bold else FONTI if italic else FONT
    key=(path,sz)
    if key not in _cache: _cache[key]=ImageFont.truetype(path, sz)
    return _cache[key]

def pt(p): return int(round(p*PX/72.0))  # points -> px

def wrap(draw, text, fnt, maxw):
    words=text.split(); lines=[]; cur=""
    for w in words:
        t=(cur+" "+w).strip()
        if draw.textlength(t, font=fnt)<=maxw: cur=t
        else:
            if cur: lines.append(cur)
            cur=w
    if cur: lines.append(cur)
    return lines or [""]

class Slide:
    def __init__(self, bgc=WHITE):
        self.img=Image.new("RGB",(1280,720),bgc); self.d=ImageDraw.Draw(self.img)
    def rect(self,x,y,w,h,c): self.d.rectangle([I(x),I(y),I(x+w),I(y+h)],fill=c)
    def text(self,x,y,w,s,sz,c=SLATE,bold=False,italic=False,align="l",ls=1.0,anchor_mid=False):
        fnt=font(pt(sz),bold,italic); maxw=I(w); lh=int(pt(sz)*1.2*ls); yy=I(y)
        for raw in s.split("\n"):
            for line in wrap(self.d, raw, fnt, maxw):
                tw=self.d.textlength(line,font=fnt)
                if align=="c": xx=I(x)+(maxw-tw)//2
                elif align=="r": xx=I(x)+maxw-tw
                else: xx=I(x)
                self.d.text((xx,yy),line,font=fnt,fill=c); yy+=lh
        return yy
    def bullets(self,x,y,w,items,sz,c=SLATE,gap=6,bold_lead=False):
        fnt=font(pt(sz)); fb=font(pt(sz),bold=True); maxw=I(w); lh=int(pt(sz)*1.18); yy=I(y)
        for it in items:
            indent=I(x)+self.d.textlength("•  ",font=fnt)
            # first line gets bullet
            if bold_lead and ": " in it:
                lead,rest=it.split(": ",1)
                segs=[("•  "+lead+": ",fb),(rest,fnt)]
            else:
                segs=[("•  "+it,fnt)]
            # build word list with fonts
            words=[]
            for txt_,f in segs:
                for j,wd in enumerate(txt_.split(" ")):
                    if wd=="" : continue
                    words.append((wd,f))
            # wrap manually
            line=[]; lw=0; first=True; xx=I(x)
            def flush(line, yy, firstline):
                xpos=I(x) if firstline else indent
                for wd,f in line:
                    self.d.text((xpos,yy),wd+" ",font=f,fill=(NAVY if f==fb else c))
                    xpos+=self.d.textlength(wd+" ",font=f)
            firstline=True
            for wd,f in words:
                ww=self.d.textlength(wd+" ",font=f)
                avail=maxw-(0 if firstline else (indent-I(x)))
                if lw+ww>avail and line:
                    flush(line,yy,firstline); yy+=lh; line=[]; lw=0; firstline=False
                line.append((wd,f)); lw+=ww
            if line: flush(line,yy,firstline); yy+=lh
            yy+=int(gap*PX/72.0)
        return yy
    def save(self,p): self.img.save(p)

def header(s,kicker,title):
    s.rect(0,0,13.333,1.25,NAVY); s.rect(0,1.25,13.333,0.06,ACCENT)
    s.text(0.6,0.18,11,kicker,13,ACCENT,bold=True)
    s.text(0.6,0.5,12,title,26,WHITE,bold=True)

slides=[]

# 1 TITLE
s=Slide(NAVY)
s.rect(0,3.05,13.333,0.06,ACCENT)
s.text(1.0,1.5,11.3,"TRANSNATIONAL CRIME & THE LIMITS OF INTERNATIONAL JUSTICE",16,ACCENT,bold=True,align="c")
s.text(1.0,2.0,11.3,"What the Epstein Case Reveals",40,WHITE,bold=True,align="c")
s.text(1.0,3.35,11.3,"A case study in cross-border exploitation, jurisdiction, and accountability",18,LIGHT,italic=True,align="c")
s.text(1.0,6.4,11.3,"Group Presentation  •  Faculty of Law  •  2026",13,GREY,align="c")
slides.append(s)

# 2 OVERVIEW
s=Slide(); header(s,"OVERVIEW","Our Central Question & Roadmap")
s.rect(0.6,1.6,12.1,1.25,LIGHT)
s.text(0.9,1.82,11.5,"Why is transnational sexual exploitation so hard to prosecute — and what do international law and cross-border cooperation need in order to work?",19,NAVY,bold=True,italic=True,ls=1.1)
s.bullets(0.7,3.2,12,[
 "Part 1 — Framing & the international scope of the case",
 "Part 2 — The international legal framework (Palermo Protocol, UNTOC, jurisdiction & extradition)",
 "Part 3 — Wealth, mobility, and the problem of \"elite impunity\"",
 "Part 4 — Accountability, transparency & lessons (incl. a Japan comparison)",
],19,SLATE,gap=14)
s.text(0.7,6.7,12,"Note: This presentation centres victims and legal systems — not sensational detail.",13,GREY,italic=True)
slides.append(s)

# 3 PART 1
s=Slide(); header(s,"PART 1  •  FRAMING","Why This Is an International Story")
s.bullets(0.7,1.6,7.4,[
 "Who: Jeffrey Epstein, a financier whose network spanned multiple countries.",
 "2008: A lenient Florida plea deal — state charges, limited accountability.",
 "2019: Federal sex-trafficking charges in New York; Epstein died in custody.",
 "Cross-border recruitment of victims, including minors and foreign nationals.",
 "Offshore wealth and properties across the US, US Virgin Islands and Paris.",
 "A globe-spanning social network of internationally prominent figures.",
],18,gap=14,bold_lead=True)
s.rect(8.4,1.7,4.3,4.9,LIGHT)
s.text(8.7,1.95,3.8,"WHY IT'S \"INTERNATIONAL\"",14,ACCENT,bold=True)
s.bullets(8.7,2.5,3.8,[
 "Victims moved across borders","Money held offshore","Multiple jurisdictions involved",
 "Foreign & quasi-diplomatic figures","→ A test for international justice",
],16,SLATE,gap=12)
slides.append(s)

# 4 PART 2
s=Slide(); header(s,"PART 2  •  LEGAL FRAMEWORK","Trafficking as a Transnational Crime")
s.bullets(0.7,1.6,12,[
 "UN Palermo Protocol (2000): Defines trafficking in persons and obliges states to criminalise it.",
 "UN Convention against Transnational Organized Crime (UNTOC): The parent framework for cooperation.",
 "Jurisdiction: Which state may prosecute when conduct spans several countries?",
 "Extradition & MLATs: Mutual Legal Assistance Treaties enable evidence-sharing across borders.",
 "Foreign nationals: Ghislaine Maxwell (UK) — convicted 2021 of sex-trafficking conspiracy.",
 "Quasi-diplomatic complications: Prince Andrew settled a US civil case (2022) and later lost titles.",
],18,gap=14,bold_lead=True)
s.text(0.7,6.7,12,"Takeaway: The law exists — the difficulty is coordinating sovereign systems.",14,NAVY,bold=True,italic=True)
slides.append(s)

# 5 PART 3
s=Slide(); header(s,"PART 3  •  WEALTH & MOBILITY","How Wealth Enabled \"Elite Impunity\"")
s.bullets(0.7,1.6,7.4,[
 "Offshore structures and private wealth obscured assets and ownership.",
 "Property in several jurisdictions enabled mobility and evasion.",
 "Identity documents: an expired passport bore Epstein's photo, a false name, and listed Saudi Arabia as residence.",
 "Contrast: the lenient 2008 outcome vs. the 2019 federal prosecution.",
 "Maxwell's 2021 conviction showed accountability is possible — but slow.",
],18,gap=13,bold_lead=True)
s.rect(8.4,1.7,4.3,4.9,LIGHT)
s.text(8.7,1.95,3.8,"COMPARATIVE QUESTION",14,ACCENT,bold=True)
s.text(8.7,2.6,3.8,"Would other legal systems — the UK, France, or Japan — have acted faster, or slower, against a defendant of comparable wealth and mobility?",17,SLATE,italic=True,ls=1.15)
slides.append(s)

# 6 PART 4
s=Slide(); header(s,"PART 4  •  ACCOUNTABILITY","Transparency, Survivors & Lessons")
s.bullets(0.7,1.6,12,[
 "2025 document-release wave under US transparency legislation brought new scrutiny.",
 "Survivors' concern: disclosures made it easy to identify victims — but not the enablers.",
 "Lesson: transparency must be designed to protect victims while exposing accountability.",
 "Reform: stronger MLATs, faster extradition, victim-centred disclosure, asset tracing.",
 "Japan comparison: anti-trafficking framework & US State Dept. TIP assessments offer a benchmark.",
],18,gap=15,bold_lead=True)
s.rect(0.6,6.35,12.1,0.75,NAVY)
s.text(0.9,6.52,11.5,"Closing: Justice across borders depends less on new laws than on the will to cooperate.",16,WHITE,bold=True,italic=True)
slides.append(s)

# 7 TAKEAWAYS
s=Slide(); header(s,"CONCLUSION","Four Takeaways")
items=[("01","Crime crosses borders — justice often doesn't.","Networks are global; enforcement is national."),
 ("02","The legal tools exist.","Palermo & UNTOC provide the framework; coordination is the gap."),
 ("03","Wealth buys time, not immunity.","Mobility delayed — but did not prevent — accountability."),
 ("04","Transparency must protect victims.","Disclosure should expose enablers, not endanger survivors.")]
y=1.65
for num,head_,sub in items:
    s.rect(0.7,y,0.85,1.05,ACCENT)
    s.text(0.7,y+0.22,0.85,num,26,WHITE,bold=True,align="c")
    s.text(1.75,y+0.05,10.8,head_,19,NAVY,bold=True)
    s.text(1.75,y+0.52,10.8,sub,15,SLATE,italic=True)
    y+=1.25
slides.append(s)

# 8 THANKS
s=Slide(NAVY)
s.rect(0,2.0,13.333,0.06,ACCENT)
s.text(1.0,0.9,11.3,"Thank You",40,WHITE,bold=True,align="c")
s.text(1.0,2.2,11.3,"Questions & Discussion",18,LIGHT,italic=True,align="c")
s.text(1.0,3.3,11.3,"SELECTED SOURCES & INSTRUMENTS",13,ACCENT,bold=True,align="c")
s.bullets(3.3,3.85,7,[
 "UN Protocol to Prevent, Suppress and Punish Trafficking in Persons (Palermo Protocol, 2000)",
 "UN Convention against Transnational Organized Crime (UNTOC)",
 "US Dept. of Justice filings: US v. Epstein (2019); US v. Maxwell (2021)",
 "US State Department Trafficking in Persons (TIP) Reports",
 "Contemporary news reporting on 2025 document disclosures",
],14,LIGHT,gap=8)
slides.append(s)

# save individual + contact sheet
paths=[]
for i,s in enumerate(slides,1):
    p=f"/home/user/Koki/preview_slide_{i}.png"; s.save(p); paths.append(p)

# contact sheet: 2 cols x 4 rows with margins
cols,rows=2,4; tw,th=640,360; pad=16
sheet=Image.new("RGB",(cols*tw+pad*(cols+1), rows*th+pad*(rows+1)),(220,224,228))
for idx,s in enumerate(slides):
    r,c=divmod(idx,cols)
    thumb=s.img.resize((tw,th))
    sheet.paste(thumb,(pad+c*(tw+pad), pad+r*(th+pad)))
sheet.save("/home/user/Koki/preview_all.png")
print("rendered", len(paths), "slides + contact sheet")
