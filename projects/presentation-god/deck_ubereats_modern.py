#!/usr/bin/env python3
"""Uber Eats pitch — Modern (MusePass-style) engine, Japanese & English.

Figures from Uber FY2024 results + reputable trackers (see closing slide).
"""
import os

from engine_modern import ModernDeck

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")


def build_ja(theme="green"):
    d = ModernDeck(theme=theme)
    d.title("5分でわかる Uber Eats の事業",
            "「あらゆるモノを、\n数分で。」",
            "フードデリバリーから“ローカル・コマースのOS”へ。",
            "Uber Technologies, Inc.", "投資家向け資料  •  2026年6月")

    d.points("なぜ今、課題なのか / PROBLEM", "外食と日常の買い物は、まだ不便だ",
             ["飲食店は来店客しか取り込めず、空席や余剰在庫が機会損失になっている。",
              "消費者は「今すぐ・近くで」を求めるが、店ごとの注文導線はバラバラ。",
              "個人商店や中小店舗には、需要を取り込むデジタル基盤がない。"],
             lead="リアル店舗の在庫と、目の前の需要が、つながっていない。",
             next_="解決策：需要と供給を数分でつなぐ")

    d.cards("解決策 / SOLUTION", "需要と供給を、数分でつなぐ",
            [("集客", ["1.4億人の利用者基盤", "店舗を即オンライン化"], "来店を待たず需要を取り込む"),
             ("配送", ["ドライバー網", "ラストワンマイルを担う"], "店は配達網を持たなくていい"),
             ("拡張", ["食料品・小売・酒類へ", "品揃えを横展開"], "フードは入口にすぎない")],
            lead="フードデリバリーを入口に、地域コマース全体を取りに行く。",
            next_="なぜ今このタイミングなのか")

    d.points("なぜ今 / WHY NOW", "行動変容が、不可逆に定着した",
             ["コロナ後もデリバリー利用は高止まりし、日常インフラ化した。",
              "配送オペレーションの効率化で、ユニットエコノミクスが黒字転換。",
              "広告やサブスク(Uber One)など高粗利の収益源が育ってきた。"],
             lead="“使われるか”の段階は終わり、“儲かるか”の段階に入った。",
             next_="市場の数字で実力を見る")

    d.kpis("実績 / TRACTION", "規模と収益性を、同時に実現",
           [("1.4億人", "2024年にUber Eatsで\n注文した利用者"),
            ("$20.1B", "四半期のデリバリー総取扱高\n(2024 Q4・前年比 +18%)"),
            ("1.71億人", "Uber全体の\n月間利用者数"),
            ("45カ国", "展開国数\n(11,000都市超)")],
           lead="「成長」と「利益」を両立できるフェーズに入った。",
           next_="次に取りに行くもの")

    d.flow("仕組み / HOW IT WORKS", "注文から配達まで、数分で完結する",
           [("注文", "アプリで近くの店を選ぶ"),
            ("調理", "店舗に即時通知"),
            ("配達", "ドライバーが受け取り運ぶ"),
            ("到着", "数分〜数十分で受け取り")],
           next_="提案：次の打ち手")

    d.takeaways("提案 / THE ASK", "次に取りに行くもの",
                [("01", "品揃えの拡張", "食料品・小売・酒類のカテゴリを各都市で広げる。"),
                 ("02", "高粗利の収益化", "広告とUber Oneの普及で利益率をさらに引き上げる。"),
                 ("03", "ローカルOS化", "地域コマースの基盤（注文・配送・決済）を押さえる。")],
                sources="Uber FY2024決算 (Q4 & 通期, SEC 8-K) / Business of Apps・Statista 各統計（一部は公開情報に基づく概算）")
    return d.build(OUT, "ubereats_modern_ja")


def build_en(theme="blue"):
    d = ModernDeck(theme=theme)
    d.title("Uber Eats in 5 minutes",
            "\"Anything,\nin minutes.\"",
            "From food delivery to the operating system for local commerce.",
            "Uber Technologies, Inc.", "Investor deck  •  June 2026")

    d.points("PROBLEM", "Eating out and everyday shopping are still clunky",
             ["Restaurants only serve who walks in — empty seats and waste are lost revenue.",
              "Consumers want \"now, nearby\" — but every store's ordering flow differs.",
              "Small local merchants lack the digital rails to capture nearby demand."],
             lead="Local inventory and immediate demand simply aren't connected.",
             next_="Solution: connect supply and demand in minutes")

    d.cards("SOLUTION", "Linking supply and demand in minutes",
            [("Demand", ["140M consumer base", "Stores online instantly"], "Capture demand beyond walk-ins"),
             ("Delivery", ["Driver network", "Owns the last mile"], "Stores need no fleet"),
             ("Expansion", ["Grocery, retail, alcohol", "Widen the shelf"], "Food is only the front door")],
            lead="Food delivery is the entry point to all of local commerce.",
            next_="Why this moment")

    d.points("WHY NOW", "Behaviour has shifted — irreversibly",
             ["Post-pandemic delivery demand stayed high and became everyday infrastructure.",
              "Operational efficiency flipped unit economics into profit.",
              "High-margin revenue (ads, Uber One) is now scaling."],
             lead="The \"will they use it\" phase is over; the \"is it profitable\" phase has begun.",
             next_="The numbers behind the business")

    d.kpis("TRACTION", "Scale and profitability, at the same time",
           [("140M", "consumers ordered on\nUber Eats in 2024"),
            ("$20.1B", "quarterly Delivery Gross\nBookings (Q4 2024, +18%)"),
            ("171M", "monthly active consumers\nacross Uber"),
            ("45", "countries\n(11,000+ cities)")],
           lead="We have entered the phase of growing and earning at once.",
           next_="What we go after next")

    d.flow("HOW IT WORKS", "From order to doorstep, in minutes",
           [("Order", "Pick a nearby store"),
            ("Cook", "Store notified instantly"),
            ("Deliver", "A driver picks it up"),
            ("Arrive", "Delivered in minutes")],
           next_="The ask")

    d.takeaways("THE ASK", "What we go after next",
                [("01", "Widen the shelf", "Expand grocery, retail and alcohol categories city by city."),
                 ("02", "Monetise at high margin", "Scale advertising and Uber One to lift profitability."),
                 ("03", "Own local commerce", "Control the rails: ordering, delivery and payments.")],
                sources="Uber FY2024 results (Q4 & full year, SEC 8-K) / Business of Apps & Statista trackers (some figures are estimates from public data)")
    return d.build(OUT, "ubereats_modern_en")


if __name__ == "__main__":
    ja = build_ja()
    en = build_en()
    print("JA:", ja["pdf"], ja["n"], "slides")
    print("EN:", en["pdf"], en["n"], "slides")
