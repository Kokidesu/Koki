#!/usr/bin/env python3
"""Render the 4-section speaker script to a clean, formatted PDF."""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, HRFlowable,
                                Table, TableStyle, KeepTogether)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

NAVY=HexColor("#0F2A43"); ACCENT=HexColor("#C08A2B"); SLATE=HexColor("#333333"); GREY=HexColor("#6B7682")
SERIF="Times-Roman"; SERIFB="Times-Bold"; SERIFI="Times-Italic"

styles=getSampleStyleSheet()
H_TITLE=ParagraphStyle("t",fontName=SERIFB,fontSize=20,leading=24,textColor=NAVY,spaceAfter=4)
H_SUB  =ParagraphStyle("s",fontName=SERIFI,fontSize=12,leading=16,textColor=GREY,spaceAfter=2)
SEC    =ParagraphStyle("sec",fontName=SERIFB,fontSize=15,leading=19,textColor=NAVY,spaceBefore=14,spaceAfter=2)
SECMETA=ParagraphStyle("secm",fontName=SERIFI,fontSize=10.5,leading=14,textColor=ACCENT,spaceAfter=8)
CUE    =ParagraphStyle("cue",fontName=SERIFB,fontSize=11,leading=15,textColor=ACCENT,spaceBefore=8,spaceAfter=2)
BODY   =ParagraphStyle("b",fontName=SERIF,fontSize=11,leading=16,textColor=SLATE,alignment=TA_LEFT,spaceAfter=4)
NOTE   =ParagraphStyle("n",fontName=SERIFI,fontSize=10,leading=14,textColor=GREY,spaceAfter=4)

sections=[
 ("SECTION 1 — Speaker 1: Introduction & Framing","Slides 1–6  ·  approx. 7 minutes",[
  ("Slide 1 – Title","Good morning. Our presentation is “Transnational Crime and the Limits of International Justice: What the Epstein Case Reveals.” We use this case not as a true-crime story, but as a lens to ask a serious legal question: what happens when a crime is global, but the institutions meant to punish it are national?"),
  ("Slide 2 – Central Question & Roadmap","Our guiding question: why is transnational sexual exploitation so hard to prosecute, and what do international law and cross-border cooperation need in order to work? We’ve split this into four parts — framing, the legal framework, wealth and impunity, and accountability. Throughout, we center the victims and the legal systems, not sensational detail."),
  ("Slide 3 – Part 1 Divider","Let me start with the framing — who Epstein was, and why this case crosses borders."),
  ("Slide 4 – Who Was Jeffrey Epstein?","Jeffrey Epstein was an American financier with enormous wealth and a network of powerful international contacts. A 2005–06 Florida investigation led to a controversial 2008 state plea deal; he registered as a sex offender. In 2019 he was arrested on federal sex-trafficking charges in New York and died in custody that August. His death matters legally: accountability could no longer run through him — it had to be pursued through others, across borders."),
  ("Slide 5 – A Case That Spanned Two Decades","The timeline: 2008, the lenient Florida plea deal; 2019, federal charges and his death; 2021, Ghislaine Maxwell’s conviction; 2025, a wave of document releases. Across two decades, a local plea bargain became a global question about justice and accountability."),
  ("Slide 6 – Why This Is an International Story","It’s international on every axis: cross-border recruitment of victims, offshore wealth, properties in the US, the US Virgin Islands and Paris, and an expired passport with a false name listing Saudi residence. The core tension — and the heart of our talk — is that the network was global, but criminal enforcement is national. To explain that gap, over to Speaker 2."),
 ]),
 ("SECTION 2 — Speaker 2: The International Legal Framework","Slides 7–12  ·  approx. 8 minutes",[
  ("Slide 7 – Part 2 Divider","Thank you. I’ll show how international law addresses crime that crosses borders — and where it strains."),
  ("Slide 8 – What Makes a Crime “Transnational”?","A crime is transnational when it’s committed in more than one state, or planned or felt in another. Trafficking is the paradigm case — it moves people, money, and evidence across borders. Prosecuting it needs more than one country’s police, courts and laws to act together, which strains systems built for domestic crime. The question is institutional: can sovereign systems coordinate fast enough?"),
  ("Slide 9 – The Palermo Protocol (2000)","The main answer starts with the Palermo Protocol — the UN Protocol to Prevent, Suppress and Punish Trafficking in Persons. It gave the first agreed definition of trafficking: an act, a means, and a purpose of exploitation. For children, the “means” element isn’t required. It obliges states to criminalise trafficking domestically, and with 190+ parties, gives the world a shared vocabulary — a precondition for cooperation."),
  ("Slide 10 – UNTOC & Cross-Border Cooperation","The Protocol sits under the UN Convention against Transnational Organized Crime, or UNTOC. Together they frame the practical tools — extradition, mutual legal assistance, joint investigations — and can even ground cooperation where no bilateral treaty exists. So the machinery already exists on paper."),
  ("Slide 11 – Jurisdiction, Extradition & MLATs","Making it run is harder. States claim jurisdiction by territory or nationality, so several may have a concurrent right to prosecute. Extradition usually needs a treaty plus “dual criminality.” MLATs move evidence across borders. The friction: these are slow, can be refused, and stall when a suspect is wealthy or well-connected. The tools exist — speed and political will decide if they work."),
  ("Slide 12 – Foreign Nationals & Quasi-Diplomatic Figures","The case shows this through its people: Ghislaine Maxwell (UK) was convicted in 2021; Prince Andrew settled a US civil claim in 2022 and later lost his titles. High status confers no immunity but creates practical and diplomatic hurdles, and foreign nationality complicates arrest and evidence-gathering. We stick to what courts have decided — not speculation. Over to Speaker 3."),
 ]),
 ("SECTION 3 — Speaker 3: Wealth, Mobility & Impunity","Slides 13–16  ·  approx. 7 minutes",[
  ("Slide 13 – Part 3 Divider","Thanks. I’ll look at how resources can delay accountability — though not always defeat it."),
  ("Slide 14 – Offshore Wealth & Global Mobility","Offshore structures obscure who owns assets; property in several jurisdictions gives places to live and move between; private travel reduces scrutiny; multiple identity documents show evasion capacity. Together, wealth becomes mobility, and mobility becomes delay. And this isn’t unique to one man — it’s how illicit elite wealth tends to behave."),
  ("Slide 15 – “Elite Impunity”: 2008 vs 2019","Compare two moments. 2008 Florida: a state plea deal, ~13 months with work release, a non-prosecution agreement that shielded others, victims not properly consulted. 2019 federal New York: full trafficking charges, held without bail, treated as serious organised wrongdoing — ending only with his death. Same conduct, two very different responses, a decade apart. That’s what “elite impunity” means: not that law never catches up, but that wealth buys a softer outcome and a lot of time."),
  ("Slide 16 – Would Other Systems Have Acted Differently?","A comparative question. Adversarial vs inquisitorial systems (France’s investigating magistrates differ from US prosecutors); earlier victim participation in some systems; limitation periods; and less central plea bargaining in civil-law systems. So: would the UK, France, or Japan have acted faster — or slower? Over to Speaker 4."),
 ]),
 ("SECTION 4 — Speaker 4: Accountability, Transparency & Conclusion","Slides 17–20  ·  approx. 8 minutes",[
  ("Slide 17 – Part 4 Divider","Thank you. I’ll close on accountability — and how to design cross-border justice that protects victims."),
  ("Slide 18 – The 2025 Document-Release Wave","In 2025, US transparency legislation drove a large release of case documents, answering public demand for openness. But survivors warned the disclosures made it easy to identify those abused — yet not those who may have been involved. That’s the tension between transparency and victims’ privacy and safety. Transparency isn’t automatically just; its design decides who it protects."),
  ("Slide 19 – Reform Proposals & a Japan Comparison","Four reforms: faster MLAT and extradition channels; victim-centred disclosure that shields identities by default; stronger cross-border asset tracing and recovery; and harmonised definitions so mismatched laws don’t block cooperation. For our audience, Japan is a useful benchmark — it has an anti-trafficking framework and is assessed yearly in the US State Department’s TIP Report. Better cross-border justice is mostly an engineering problem, not a gap in principle."),
  ("Slide 20 – Conclusion: Four Takeaways","Four takeaways. One: crime crosses borders, but justice often doesn’t. Two: the legal tools already exist — the gap is coordination, not law. Three: wealth buys time, not immunity. Four: transparency must protect victims — expose enablers, not endanger survivors. Sources are on the slide. Thank you — we’re happy to take questions."),
 ]),
]

doc=SimpleDocTemplate("/home/user/Koki/Speaker_Script_4_Sections.pdf",pagesize=A4,
    topMargin=18*mm,bottomMargin=16*mm,leftMargin=20*mm,rightMargin=20*mm,
    title="Epstein Presentation — Speaker Script (4 sections)")
fl=[]
fl.append(Paragraph("Transnational Crime &amp; the Limits of International Justice",H_TITLE))
fl.append(Paragraph("What the Epstein Case Reveals — Speaker Script (4 sections, ~30 min)",H_SUB))
fl.append(Spacer(1,3))
fl.append(HRFlowable(width="100%",thickness=2,color=ACCENT,spaceAfter=6))
fl.append(Paragraph("Note: this topic involves the sexual abuse of minors. Keep the focus on victims and on how legal systems respond — stick to what courts have adjudicated.",NOTE))

for title,meta,cues in sections:
    block=[HRFlowable(width="100%",thickness=0.6,color=GREY,spaceBefore=8,spaceAfter=6),
           Paragraph(title,SEC),Paragraph(meta,SECMETA)]
    fl.append(KeepTogether(block))
    for cue,body in cues:
        fl.append(Paragraph("["+cue+"]",CUE))
        fl.append(Paragraph(body,BODY))

doc.build(fl)
print("wrote Speaker_Script_4_Sections.pdf")
