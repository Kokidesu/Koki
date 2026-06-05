#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fpdf import FPDF

FONT = "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf"
SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
BG = (11, 11, 12)
CARD = (22, 22, 24)
FG = (245, 245, 247)
SUB = (161, 161, 166)
ACC = (6, 193, 103)
WARN = (245, 166, 35)
LINE = (42, 42, 46)

W, H = 297, 167  # 16:9 landscape (mm)

pdf = FPDF(orientation="L", unit="mm", format=(H, W))
pdf.set_auto_page_break(False)
pdf.set_line_width(0.3)
# Latin/English = Times New Roman相当 (Liberation Serif), 日本語 = ゴシックでフォールバック
pdf.add_font("serif", "", SERIF)
pdf.add_font("serif", "B", SERIF_B)
pdf.add_font("jp", "", FONT)
pdf.add_font("jp", "B", FONT)
pdf.set_fallback_fonts(["jp"])

def bg():
    pdf.set_fill_color(*BG)
    pdf.rect(0, 0, W, H, "F")

def progress(i, n):
    pdf.set_fill_color(*ACC)
    pdf.rect(0, 0, W * (i + 1) / n, 1.6, "F")

def footer(i, n, label=""):
    pdf.set_draw_color(*LINE)
    pdf.line(MX, H - 12, W - MX, H - 12)
    text(MX, H - 9.5, "Uber Eats Japan — AE 面接デッキ", 8, SUB)
    pdf.set_xy(W - MX - 30, H - 9.5)
    pdf.set_font("serif", "B", 8)
    pdf.set_text_color(*ACC)
    pdf.cell(30, 4, f"{i+1:02d}", align="R")
    pdf.set_text_color(*SUB)
    pdf.set_font("serif", "", 8)
    pdf.cell(0, 4, f" / {n:02d}")

def text(x, y, s, size, color=FG, bold=False, w=0, align="L", lh=1.3):
    pdf.set_xy(x, y)
    pdf.set_font("serif", "B" if bold else "", size)
    pdf.set_text_color(*color)
    if w:
        pdf.multi_cell(w, size * 0.42 * lh, s, align=align)
    else:
        pdf.cell(0, size * 0.5, s, align=align)

def kicker(x, y, s):
    text(x, y, s, 11, ACC, True)

def bullet(x, y, s, size=13, color=FG, w=230):
    pdf.set_fill_color(*ACC)
    pdf.rect(x, y + 2.4, 2.4, 2.4, "F")
    text(x + 6, y, s, size, color, w=w, lh=1.25)

def card(x, y, cw, ch, title, value, sub, vcolor=FG):
    pdf.set_fill_color(*CARD)
    pdf.set_draw_color(*LINE)
    pdf.rect(x, y, cw, ch, "DF")
    text(x + 6, y + 6, title, 10.5, ACC, True)
    text(x + 6, y + 15, value, 20, vcolor, True)
    text(x + 6, y + 30, sub, 9.5, SUB, w=cw - 12, lh=1.15)

MX = 26  # left margin

# ---- Slide 1: Title ----
def s1():
    bg()
    pdf.set_fill_color(13, 40, 26)
    pdf.set_draw_color(*ACC)
    pdf.rect(MX, 44, 120, 11, "DF")
    text(MX + 6, 47, "AE / BPS 面接対策 — 2025〜2026 最新版", 10.5, ACC, True)
    text(MX, 64, "Uber Eats Japan", 40, FG, True)
    text(MX, 86, "市場・事業 データブリーフ", 30, FG, True)
    text(MX, 112, "なぜ今、Uber Eats の AE なのか —", 15, SUB)
    text(MX, 122, "市場・競合・事業戦略を数字で読む", 15, SUB)

# ---- Slide HOOK ----
def hook(i, n):
    bg(); progress(i, n)
    text(MX, 40, "つかみ", 11, ACC, True)
    text(MX, 52, "日本のフードデリバリーは", 22, FG)
    text(MX, 66, "「2強 → 1強」へ。", 34, FG, True)
    pdf.set_text_color(*ACC); pdf.set_font("serif", "B", 70)
    pdf.set_xy(MX, 86); pdf.cell(0, 30, "約6割")
    text(MX, 122, "Uber Eatsの利用率シェア。Wolt撤退・出前館赤字の中、唯一黒字で独走。", 13, SUB)
    footer(i, n)

# ---- Slide 2: Agenda ----
def s2(i, n):
    bg(); progress(i, n)
    kicker(MX, 22, "AGENDA — 現状から「なぜ自分か」まで")
    text(MX, 30, "本日の構成", 28, FG, True)
    items = [
        "① 市場 — 成熟・微成長局面と「2強」【現状】",
        "② 競合 — Wolt撤退で鮮明になった構図【現状】",
        "③ 事業 — Uberの成長性と日本の地方拡大【強み】",
        "④ 商品 — AEが売る加盟店ソリューション【手段】",
        "⑤ 論点 — 地方拡大の鍵は「配達供給」【課題】",
        "⑥ 結論 — なぜUberのAEなのか【自分】",
    ]
    y = 50
    for it in items:
        bullet(MX, y, it, 13)
        y += 14
    footer(i, n)

# ---- table helper ----
def table(x, y, rows, colw, header=True):
    ry = y
    for ri, row in enumerate(rows):
        pdf.set_draw_color(*LINE)
        pdf.line(x, ry + 11, x + sum(colw), ry + 11)
        cx = x
        for ci, cell in enumerate(row):
            col = ACC if (header and ri == 0) else FG
            align = "L" if ci == 0 else "R"
            pdf.set_xy(cx, ry + 1)
            pdf.set_font("serif", "B" if (ri == 0 or ci > 0) else "", 12.5 if not (header and ri==0) else 11)
            pdf.set_text_color(*col)
            pdf.cell(colw[ci], 9, cell, align=align)
            cx += colw[ci]
        ry += 13

# ---- Slide 3: Market ----
def s3(i, n):
    bg(); progress(i, n)
    kicker(MX, 22, "① 市場")
    text(MX, 30, "市場は「成熟・微成長」局面へ", 26, FG, True)
    rows = [
        ["年（外食デリバリー / Circana基準）", "市場規模", "前年比"],
        ["2023年（ピーク）", "8,622億円", "+11%"],
        ["2024年（調整）", "7,967億円", "−7.6%"],
        ["2025年（見込み）", "8,240億円", "+2.0%"],
    ]
    table(MX, 52, rows, [150, 50, 40])
    text(MX, 112, "爆発的成長は終了。コロナ前の約2倍水準で定着し、再び微増へ。", 12, SUB)
    text(MX, 120, "→ だからこそ「新領域の開拓」が成長のカギ。", 12, SUB)
    text(MX, 132, "出典: Circana Japan (2024–2025)", 9, SUB)
    footer(i, n)

# ---- Slide 4: Competition ----
def s4(i, n):
    bg(); progress(i, n)
    kicker(MX, 22, "② 競合")
    text(MX, 30, "2強構造 ＋ Wolt撤退", 26, FG, True)
    cw, ch, gap = 113, 38, 11
    x2 = MX + cw + gap
    card(MX, 50, cw, ch, "Uber Eats", "利用率 約6割", "独走首位・黒字化済み")
    card(x2, 50, cw, ch, "出前館", "約3割", "2位 / 2025年8月期 約49.7億円の赤字")
    card(MX, 50 + ch + gap, cw, ch, "Wolt", "2026年3月 撤退", "値下げ競争+物価高で収益化できず", vcolor=WARN)
    card(x2, 50 + ch + gap, cw, ch, "menu (KDDI系)", "数%", "ニッチ / au経済圏連携")
    text(MX, 144, "出典: S.E.ネットワーク調査, 日経 (2025–2026)", 9, SUB)
    footer(i, n)

# ---- Slide 5: Uber growth ----
def s5(i, n):
    bg(); progress(i, n)
    kicker(MX, 22, "③ 事業 — 成長性")
    text(MX, 30, "成長し、かつ黒字の事業", 26, FG, True)
    cw, ch, gap = 113, 38, 11
    x2 = MX + cw + gap
    card(MX, 50, cw, ch, "総取扱高 (2025通年)", "$193.5B", "前年比 +19%")
    card(x2, 50, cw, ch, "調整後EBITDA", "$8.73B", "+35% / 過去最高")
    card(MX, 50 + ch + gap, cw, ch, "Delivery部門EBITDA", "$3.6B", "前年比 +$1.1B", vcolor=ACC)
    card(x2, 50 + ch + gap, cw, ch, "月間利用者", "2.02億人", "+18%")
    text(MX, 144, "出典: Uber SEC 8-K / IR (FY2025)", 9, SUB)
    footer(i, n)

# ---- Slide 6: Japan expansion ----
def s6(i, n):
    bg(); progress(i, n)
    kicker(MX, 22, "③ 事業 — 日本の拡大")
    text(MX, 30, "地方へ。「100都市」を達成", 26, FG, True)
    items = [
        ("2025年3月：「年内100都市以上」拡大を公表", FG),
        ("4〜9月：毎月6県前後を追加し続ける", FG),
        ("2025年10月：100都市計画を達成", ACC),
        ("2026年5月：新潟・長野・山梨の観光地12市町村へ", FG),
    ]
    y = 52
    for s, c in items:
        bullet(MX, y, s, 14, c)
        y += 15
    text(MX, 122, "戦略フレーム「3つのA」: Anything（小売、売上前年比2倍） /", 11.5, SUB, w=245)
    text(MX, 130, "Anywhere（地方・観光地） / Affordable（手頃さ）", 11.5, SUB)
    text(MX, 144, "出典: Uberニュースルーム, ダイヤモンド・チェーンストア (2025–2026)", 9, SUB)
    footer(i, n)

# ---- Slide 7: Merchant solutions ----
def s7(i, n):
    bg(); progress(i, n)
    kicker(MX, 22, "④ 商品 — AEが売るもの")
    text(MX, 30, "加盟店ソリューション", 26, FG, True)
    rows = [
        ["プラン", "手数料（税抜）"],
        ["配達あり（Uber配達網）", "35%"],
        ["自前配達（店が配達）", "15%"],
        ["テイクアウト（ピックアップ）", "12%"],
    ]
    table(MX, 50, rows, [150, 50])
    y = 106
    for s in [
        "広告（リテールメディア）：Uber Ads年間$1.5B規模・前年比+60%",
        "Uber Direct：自社サイト注文をUber配達網で（スシロー等）",
        "グローサリー/リテール：ローソン7,000店超、ロボ配達も",
    ]:
        bullet(MX, y, s, 12.5)
        y += 13
    text(MX, 146, "出典: 加盟店支援各社, Uber公式, MarkeZine (2025–2026)", 9, SUB)
    footer(i, n)

# ---- Slide 8: Key issue ----
def node(cx, cy, label, sub):
    r = 19
    pdf.set_fill_color(*CARD); pdf.set_draw_color(*ACC)
    pdf.set_line_width(0.5)
    pdf.ellipse(cx - r, cy - r, 2 * r, 2 * r, "DF")
    pdf.set_xy(cx - r, cy - 5); pdf.set_font("serif", "B", 11); pdf.set_text_color(*FG)
    pdf.cell(2 * r, 5, label, align="C")
    pdf.set_xy(cx - r, cy + 1); pdf.set_font("serif", "", 8); pdf.set_text_color(*SUB)
    pdf.cell(2 * r, 4, sub, align="C")

def s8(i, n):
    bg(); progress(i, n)
    kicker(MX, 22, "⑤ 論点 — AEの視点")
    text(MX, 30, "地方拡大の鍵は「配達供給」", 26, FG, True)
    # left: bullets
    y = 56
    for s in [
        "3者が揃って 初めて回るマーケットプレイス",
        "地方ほど配達距離が長く、供給確保が難しい",
        "需給バランスが崩れると配達遅延が発生",
    ]:
        bullet(MX, y, s, 12.5, w=135)
        y += 18
    # right: triangle diagram
    cx, cy = 215, 78
    pdf.set_draw_color(*LINE); pdf.set_line_width(0.4)
    pdf.line(cx, cy - 26, cx - 32, cy + 24)
    pdf.line(cx, cy - 26, cx + 32, cy + 24)
    pdf.line(cx - 32, cy + 24, cx + 32, cy + 24)
    node(cx, cy - 26, "加盟店", "Merchant")
    node(cx - 32, cy + 24, "注文者", "Eater")
    node(cx + 32, cy + 24, "配達PT", "Courier")
    # bottom takeaway
    pdf.set_fill_color(*ACC)
    pdf.rect(MX, 122, 1.8, 24, "F")
    text(MX + 7, 124, "AEは店を開拓するだけでなく、需要を作り、配達ネットワーク", 13.5, (232,232,234), w=240, lh=1.3)
    text(MX + 7, 135, "全体が回る状態まで意識して優先順位をつけるべき。", 13.5, (232,232,234))
    footer(i, n)

# ---- Slide 9: Conclusion ----
def s9(i, n):
    bg(); progress(i, n)
    kicker(MX, 22, "⑥ 結論")
    text(MX, 30, "なぜ Uber の AE なのか", 26, FG, True)
    y = 52
    for s in [
        "成長市場でパイを取りに行ける — 唯一黒字で独走する勝ち組",
        "End to Endの営業 — 開拓〜交渉〜クロージングを一気通貫で担える",
        "様々な規模の店に提案 — 個人店〜チェーンで営業スキルの幅が育つ",
    ]:
        bullet(MX, y, s, 13.5, w=240)
        y += 15
    pdf.set_fill_color(*ACC)
    pdf.rect(MX, 112, 1.8, 30, "F")
    text(MX + 7, 114, "市場の成長に、自分の手で貢献しながら成長したい。", 15, (232,232,234), w=235, lh=1.3)
    text(MX + 7, 127, "その全部が揃っているのが Uber Eats の AE です。", 15, (232,232,234))
    footer(i, n)

# ---- Slide 10: Closing ----
def s10(i, n):
    bg(); progress(i, n)
    pdf.set_fill_color(13, 40, 26)
    pdf.set_draw_color(*ACC)
    pdf.rect(MX, 50, 40, 11, "DF")
    text(MX + 6, 53, "Thank you", 10.5, ACC, True)
    text(MX, 70, "ご質問をお待ちしています", 32, FG, True)
    text(MX, 100, "※ 数字は2025〜2026年公開情報ベース。", 13, SUB)
    text(MX, 110, "一部は「私の理解では」と前置き推奨。", 13, SUB)

slides = [s1, hook, s2, s3, s4, s5, s6, s7, s8, s9, s10]
N = len(slides)
for idx, fn in enumerate(slides):
    pdf.add_page()
    if idx == 0:
        fn()
    else:
        fn(idx, N)

pdf.output("/home/user/Koki/uber_interview_deck.pdf")
print("OK")
