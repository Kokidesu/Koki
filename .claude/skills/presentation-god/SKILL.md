---
name: presentation-god
description: Generate beautiful presentation/pitch/slide decks (.pptx + .pdf + PNG previews) from a topic. Use whenever the user says "ほのちゃんプレゼン", or asks to make slides, a deck, a pitch, 営業資料, プレゼン資料, ピッチ, 提案資料, or "presentation for X". Researches the topic on the web first when facts/numbers matter (Hono-chan style), then renders a clean modern deck (white canvas, gothic JP / Times New Roman EN, single accent colour, big readable type). Bilingual JA/EN, switchable theme colours.
---

# Presentation God — beautiful decks from a topic

A reusable engine that turns a topic into a polished deck: a clean, modern
Japanese-SaaS / pitch aesthetic (white background, gothic Japanese font / Times
New Roman for English, ONE vivid accent colour, generous whitespace, big
"jump-ratio" headings, card rows, big KPI numbers, arrow process flows).

## When to use
- The user says **「ほのちゃんプレゼン」** (the activation phrase), e.g.
  "ほのちゃんプレゼン、Xのスライド作って".
- Any request to create slides / a deck / pitch / 営業資料・プレゼン・ピッチ・提案資料,
  or "make a presentation about X" / "Xのスライド作って".

When invoked, act as **Hono-chan**: research the topic properly (see the hono-chan
skill's rules) before composing the deck, so every figure is real and cited.

## Workflow (do this every time)
1. **Research if it matters.** If the deck needs real facts, numbers, dates, or
   market data, use WebSearch / WebFetch first and verify key figures across
   sources. Put concrete numbers on a KPI slide and list sources on the last slide.
   (This is "Hono-chan" doing the research — be specific, cite, don't bluff.)
2. **Pick structure.** A strong default pitch order: Title → Problem → Solution →
   Why now → Market → Traction (KPIs) → How it works (flow) → The ask (takeaways).
   For non-pitch topics, adapt (overview → key points → comparison → summary).
3. **Write a build script** next to `engine_modern.py` that imports `ModernDeck`,
   composes slides, and calls `.build(outdir, name)`.
4. **Run it**, then **review the generated `<name>_contact.png`** with the Read
   tool to check layout/overflow before delivering. Fix and re-run if needed.
5. **Deliver**: send the `.pdf` (viewing), `.pptx` (editing) AND the
   `<name>_contact.png` (so the user can see it inline without downloading).

## Setup
Requires `python-pptx` and `pillow`. Japanese needs Noto Sans/Serif CJK and the
engine falls back to IPA Gothic. Install if missing:
```bash
pip install python-pptx pillow
apt-get install -y fonts-noto-cjk poppler-utils   # CJK fonts + pdf preview (if available)
```
Run a build script from the folder that contains `engine_modern.py`.

## API — `engine_modern.ModernDeck`
```python
from engine_modern import ModernDeck
d = ModernDeck(theme="blue")   # themes below; colour switches the whole deck

# Title (gradient accent background)
d.title(kicker, headline, subline="", company="", note="")
#   headline may contain "\n" for line breaks.

# Section divider (full-bleed accent)
d.section(no, total, title, lead="")

# A single clean bullet list (1 slide = 1 message)
d.points(section, title, items, lead="", next_="")

# Card row (2–4 cards). Each card = (heading, [bullets], summary_strip_text)
d.cards(section, title, cards, lead="", next_="")

# Big KPI numbers (2–4). Each = (number, label).  number auto-shrinks to fit.
d.kpis(section, title, stats, lead="", next_="")

# Process flow with arrows (2–6). Each step = (name, sub). 4 → 2x2 grid.
d.flow(section, title, steps, lead="", next_="")

# Numbered takeaways + optional sources strip. Each = (num, head, sub)
d.takeaways(section, title, items, sources="", next_="")

out = d.build(OUTDIR, "my_deck")   # writes .pptx, .pdf, per-slide PNGs, _contact.png
# out = {"pptx":..., "pdf":..., "contact":..., "n": n}
```
- `section` is the small top-left label (e.g. "課題 / PROBLEM").
- `lead` is the one-line description under the big heading.
- `next_` shows a quiet "NEXT ▶ …" footer hinting the next slide.

## Themes (accent colour — shades auto-derived)
`blue` (default), `indigo`, `teal`, `green`, `purple`, `orange`, `rose`, `slate`.
Switch with `ModernDeck(theme="purple")`. "色を変えて/紫で/オレンジで" → change theme.

## Fonts (fixed)
Japanese → Noto Sans CJK gothic (游ゴシック / "Yu Gothic" in the .pptx).
English → Times New Roman. Keep this unless the user asks otherwise.

## Design rules to honour
1 slide = 1 message · plenty of whitespace · 2–3 colours (dark grey + one accent) ·
high jump ratio (big bold heading, small calm body) · minimal decoration · text
big enough to read from the back of a room.

## There is also `engine.py`
An alternate dark "consulting" theme (navy + serif). The modern engine above is
the default; prefer it unless the user wants a formal navy/serif look.
