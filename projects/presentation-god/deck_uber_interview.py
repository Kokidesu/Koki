#!/usr/bin/env python3
"""Uber interview preparation deck (Japanese) — Modern engine.

Content based on Uber's Software Engineer interview process (recruiter screen →
technical phone screen → onsite loop → decision), sourced from Glassdoor,
Exponent, Interviewing.io-style guides and recent candidate write-ups.
"""
import os

from engine_modern import ModernDeck

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")


def build(theme="slate"):
    d = ModernDeck(theme=theme)

    d.title("Uber 面接対策",
            "Uberの選考を、\n戦略的に突破する。",
            "選考プロセスの全体像と、ラウンド別の準備ポイント。",
            "Interview Preparation", "ソフトウェアエンジニア向け  •  2026年6月")

    d.flow("全体像 / PROCESS", "選考は4ステップで進む",
           [("リクルーター", "経歴・志望・レベル感を確認 (30〜45分)"),
            ("技術スクリーン", "ライブコーディング1問 (45〜60分)"),
            ("オンサイト", "4〜6ラウンドの集中面接"),
            ("最終判断", "通常3〜6週間で結果")],
           lead="まず流れを把握する。各段階で見られる観点が違う。",
           next_="評価される3つの軸")

    d.cards("評価軸 / WHAT THEY ASSESS", "Uberが見る3つの能力",
            [("ソフトウェア工学",
              ["データ構造・アルゴリズム", "テストと可読性", "設計パターンの理解"],
              "“動く”だけでなく“良い”コード"),
             ("設計・アーキテクチャ",
              ["システム/プロダクト設計", "トレードオフの判断", "拡張性・将来要件"],
              "制約を踏まえた現実的な設計"),
             ("協働・リーダーシップ",
              ["他チームとの連携", "巻き込みと支援", "影響範囲の広さ"],
              "一人で速いより、チームで強い")],
            lead="技術力・設計力・人間力の3点で総合評価される。",
            next_="ラウンド別の準備")

    d.kpis("数字で把握 / BY THE NUMBERS", "準備の目安となる数字",
           [("45〜60分", "1ラウンドの所要時間"),
            ("4〜6", "オンサイトの\nラウンド数"),
            ("30〜40分", "コーディング1問に\nかける目安"),
            ("3〜6週", "応募から結果までの\n標準的な期間")],
           lead="時間配分を体に染み込ませておく。",
           next_="コーディング対策")

    d.points("ラウンド対策① / CODING", "コーディングは「過程」を見せる",
             ["まず要件と制約を口頭で確認し、入出力と例を固めてから書き始める。",
              "素直な解 → 計算量を述べる → 改善、の順で思考を声に出す。",
              "境界値・エラー処理・簡単なテストまでやり切る（中レベルが中心）。",
              "30〜40分で1問を解く感覚を、本番形式で時間を計って練習する。"],
             lead="正解より、考え方・コミュニケーション・詰めの丁寧さ。",
             next_="システム設計と行動面接")

    d.cards("ラウンド対策② / DESIGN & BEHAVIORAL", "設計と行動面接の型を持つ",
            [("システム設計",
              ["要件→規模→API→データ", "ボトルネックとスケール", "一貫性とのトレードオフ"],
              "“なぜその選択か”を語る"),
             ("行動面接 (STAR)",
              ["Situation / Task", "Action / Result", "数字で成果を示す"],
              "具体エピソードを5本用意"),
             ("逆質問",
              ["チーム・技術スタック", "成功の定義", "入社後90日の期待"],
              "意欲と相性を示す場")],
            lead="設計は手順を固定化し、行動はエピソードを在庫化する。",
            next_="当日までの3つ")

    d.takeaways("まとめ / ACTION", "本番までにやる3つ",
                [("01", "型を固定する", "コーディングと設計の進め方を“いつも同じ手順”にする。"),
                 ("02", "エピソードを5本", "STARで語れる実績を、数字付きで準備しておく。"),
                 ("03", "時間を計って模擬", "本番形式で時間を計り、声に出して反復練習する。")],
                sources="Glassdoor / Exponent / Prepfully / InterviewBit ほか Uber SWE 選考ガイド・体験記（2024–2026）")
    return d.build(OUT, "uber_interview_prep_ja")


if __name__ == "__main__":
    r = build()
    print(r["pdf"], r["n"], "slides")
