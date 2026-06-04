#!/usr/bin/env python3
"""Uber Eats investor/strategy pitch deck — Japanese & English.

Figures are sourced from Uber's official FY2024 results and reputable trackers
(see the closing Sources slide). Built with the Presentation God engine.
"""
import os

from engine import Deck

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")


def build_ja():
    d = Deck(theme="midnight")
    d.title("Uber Eats — 事業ピッチ", "「あらゆるモノを、数分で。」",
            "フードデリバリーから“ローカル・コマースのOS”へ。", "投資家向け資料  •  2026年6月", icon="globe")

    d.bullets("課題 / PROBLEM", "外食と日常の買い物は、まだ不便だ",
              ["飲食店は来店客しか取り込めず、空席・余剰在庫が機会損失になっている。",
               "消費者は「今すぐ・近くで」を求めるが、店ごとの注文導線はバラバラ。",
               "個人商店や中小店舗には、需要を取り込むデジタル基盤がない。"],
              key="リアル店舗の在庫と、目の前の需要が、つながっていない。", icon="doc")

    d.split("解決策 / SOLUTION", "需要と供給を、数分でつなぐプラットフォーム",
            ["集客: 140百万人の利用者基盤に店舗を即接続。",
             "配送: ドライバー網がラストワンマイルを担う。",
             "拡張: 食事→食料品→小売→酒類へ品揃えを横展開。"],
            side_title="ひとことで言うと",
            side_body="「街じゅうの在庫を、スマホから数分で届く状態にする」。フードを入口に、地域コマース全体を取りに行く。",
            key="フードデリバリーは入口にすぎない。", icon="idea")

    d.bullets("なぜ今 / WHY NOW", "行動変容が、不可逆に定着した",
              ["コロナ後もデリバリー利用は高止まりし、日常インフラ化した。",
               "配送オペレーションの効率化で、ユニットエコノミクスが黒字転換。",
               "広告・サブスク(Uber One)など高粗利の収益源が育ってきた。"],
              key="“使われる”段階は終わり、“儲かる”段階に入った。", icon="chart")

    d.compare("市場 / MARKET", "巨大かつ拡張余地のある市場",
              "コア — フードデリバリー",
              ["世界11,000都市・45カ国で展開", "加盟店150万超", "日本では最も利用される配送ブランド(2024年3月時点)"],
              "拡張 — ローカル・コマース",
              ["食料品・コンビニ・小売・酒類へ", "広告事業が高成長", "Uber One によるロイヤルティ強化"],
              key="フードの先に、地域コマースという桁違いの市場がある。")

    d.bullets("実績 / TRACTION", "数字が示す、規模と収益性の両立",
              ["2024年にUber Eatsで注文した利用者は約1億4,000万人。",
               "デリバリー総取扱高は四半期で約201億ドル(2024年Q4、前年比+18%)。",
               "デリバリー事業は調整後EBITDAで黒字化し、利益率が改善中。",
               "Uber全体の月間利用者は1億7,100万人に到達。"],
              key="「成長」と「利益」を同時に出せるフェーズに入った。", bold_lead=False, icon="chart")

    d.takeaways("提案 / THE ASK", "次に取りに行くもの",
                [("01", "品揃えの拡張", "食料品・小売・酒類のカテゴリを各都市で拡大。"),
                 ("02", "高粗利の収益化", "広告とUber Oneの普及で利益率をさらに引き上げる。"),
                 ("03", "ローカルOL化", "地域コマースの基盤(注文・配送・決済)を押さえる。")],
                sources="Uber FY2024決算(Q4&通期, SEC 8-K) / Business of Apps・Statista 各統計 / 数値は公開情報に基づく概算を含む")
    return d.build(OUT, "ubereats_pitch_ja")


def build_en():
    d = Deck(theme="midnight")
    d.title("Uber Eats — Investor Pitch", "\"Anything, in minutes.\"",
            "From food delivery to the operating system for local commerce.",
            "Investor deck  •  June 2026", icon="globe")

    d.bullets("PROBLEM", "Eating out and everyday shopping are still clunky",
              ["Restaurants can only serve who walks in — empty seats and waste are lost revenue.",
               "Consumers want \"now, nearby\" — but every store's ordering flow is different.",
               "Small local merchants lack the digital rails to capture nearby demand."],
              key="Local inventory and immediate demand simply aren't connected.", icon="doc")

    d.split("SOLUTION", "A platform that links supply and demand in minutes",
            ["Demand: instant access to a 140M-consumer base.",
             "Delivery: a driver network owns the last mile.",
             "Expansion: from meals to groceries, retail and alcohol."],
            side_title="IN ONE LINE",
            side_body="\"Make every shelf in the city deliverable in minutes.\" Food is the entry point to all of local commerce.",
            key="Food delivery is only the front door.", icon="idea")

    d.bullets("WHY NOW", "Behaviour has shifted — irreversibly",
              ["Post-pandemic delivery demand stayed high and became everyday infrastructure.",
               "Operational efficiency flipped unit economics into profit.",
               "High-margin revenue (ads, Uber One subscription) is now scaling."],
              key="The \"will they use it\" phase is over; the \"is it profitable\" phase has begun.", icon="chart")

    d.compare("MARKET", "Large today, far larger tomorrow",
              "CORE — Food delivery",
              ["11,000+ cities across 45 countries", "1.5M+ merchant partners", "#1 delivery brand in Japan (Mar 2024)"],
              "EXPANSION — Local commerce",
              ["Grocery, convenience, retail, alcohol", "Fast-growing advertising business", "Loyalty via Uber One"],
              key="Beyond food lies the far bigger prize of local commerce.")

    d.bullets("TRACTION", "Scale and profitability, at the same time",
              ["~140 million consumers ordered on Uber Eats in 2024.",
               "Delivery Gross Bookings ~$20.1B in a single quarter (Q4 2024, +18% YoY).",
               "Delivery turned Adjusted-EBITDA positive, with improving margins.",
               "Uber platform reached 171 million monthly active consumers."],
              key="We have entered the phase of growing and earning at once.", bold_lead=False, icon="chart")

    d.takeaways("THE ASK", "What we go after next",
                [("01", "Widen the shelf", "Expand grocery, retail and alcohol categories city by city."),
                 ("02", "Monetise at high margin", "Scale advertising and Uber One to lift profitability."),
                 ("03", "Own local commerce", "Control the rails: ordering, delivery and payments.")],
                sources="Uber FY2024 results (Q4 & full year, SEC 8-K) / Business of Apps & Statista trackers / figures include estimates from public data")
    return d.build(OUT, "ubereats_pitch_en")


if __name__ == "__main__":
    ja = build_ja()
    en = build_en()
    print("JA:", ja["pdf"], "|", ja["n"], "slides")
    print("EN:", en["pdf"], "|", en["n"], "slides")
