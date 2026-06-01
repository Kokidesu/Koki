#!/usr/bin/env python3
"""Render the 4-section script to PNG page images (A4 portrait) for inline preview."""
from PIL import Image, ImageDraw, ImageFont
import textwrap, os

W,H=1240,1754; M=110
NAVY=(0x0F,0x2A,0x43); ACCENT=(0xC0,0x8A,0x2B); SLATE=(0x33,0x33,0x33); GREY=(0x6B,0x76,0x82); WHITE=(255,255,255)
R="/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
B="/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
I="/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
def F(p,s): return ImageFont.truetype(p,s)
f_title=F(B,40); f_sub=F(I,23); f_sec=F(B,29); f_meta=F(I,21); f_cue=F(B,22); f_body=F(R,22); f_note=F(I,19)

from make_script_pdf import sections  # reuse the same content

pages=[];
def new_page():
    im=Image.new("RGB",(W,H),WHITE); d=ImageDraw.Draw(im); pages.append(im); return im,d
im,d=new_page(); y=M

def space(n):
    global y
    y+=n
def newpage_if(need):
    global im,d,y
    if y+need>H-M:
        im,d=new_page(); y=M
def wrap(text,font,maxw):
    out=[];
    for para in text.split("\n"):
        words=para.split(); line=""
        for w in words:
            t=(line+" "+w).strip()
            if d.textlength(t,font=font)<=maxw: line=t
            else: out.append(line); line=w
        out.append(line)
    return out
def draw_block(text,font,color,lh,indent=0,gap=8):
    global y
    for line in wrap(text,font,W-2*M-indent):
        newpage_if(lh)
        d.text((M+indent,y),line,font=font,fill=color); y+=lh
    y+=gap

# header
d.text((M,y),"Transnational Crime & the Limits of International Justice",font=f_title,fill=NAVY); y+=52
d.text((M,y),"What the Epstein Case Reveals — Speaker Script (4 sections, ~30 min)",font=f_sub,fill=GREY); y+=40
d.rectangle([M,y,W-M,y+4],fill=ACCENT); y+=22
draw_block("Note: this topic involves the sexual abuse of minors. Keep the focus on victims and on how legal systems respond — stick to what courts have adjudicated.",f_note,GREY,26,gap=14)

for title,meta,cues in sections:
    newpage_if(120)
    d.rectangle([M,y,W-M,y+2],fill=GREY); y+=18
    draw_block(title,f_sec,NAVY,36,gap=2)
    draw_block(meta,f_meta,ACCENT,28,gap=12)
    for cue,body in cues:
        newpage_if(80)
        draw_block("[ "+cue+" ]",f_cue,ACCENT,30,gap=4)
        draw_block(body,f_body,SLATE,30,gap=16)

paths=[]
for i,p in enumerate(pages,1):
    pth=f"/home/user/Koki/script_page_{i}.png"; p.save(pth); paths.append(pth)
print("pages:",len(paths))
