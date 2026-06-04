#!/usr/bin/env python3
"""Demo: a Japanese sales/pitch deck built with the Presentation God engine.

Structure follows the widely-used pitch-deck playbook (Sequoia Capital /
Guy Kawasaki 10-slide): Title → Problem → Solution → Why now → Market →
Product → Business model → Traction → Comparison → The ask.
"""
import os

from engine import Deck

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")


def build():
    d = Deck(theme="consulting")

    d.title(
        "AI プレゼン自動生成サービス",
        "Hono Deck",
        "リサーチからデザインまで、プレゼン資料を10分で。",
        "事業提案資料  •  2026年6月",
        icon="idea",
    )

    d.bullets(
        "課題 / PROBLEM", "資料作成に時間が溶けている",
        [
            "営業担当が提案資料の作成に費やす時間は週あたり平均5〜8時間と言われる。",
            "デザインの巧拙が受注率を左右するのに、現場には専任デザイナーがいない。",
            "リサーチ・構成・デザインが分断され、品質が担当者の力量に依存する。",
        ],
        key="「中身は良いのに、資料で損をしている」——これが現場の本音。",
        bold_lead=False, icon="doc",
    )

    d.split(
        "解決策 / SOLUTION", "調べる・書く・整えるを一気通貫で",
        [
            "リサーチ: 最新情報をWebから収集し、出典付きで裏取り。",
            "構成: 受注実績の高い型に沿って自動でストーリーを設計。",
            "デザイン: プロ品質のスライドを自動レンダリング(pptx/PDF)。",
        ],
        side_title="ひとことで言うと",
        side_body="「テーマを入れるだけで、根拠のある美しい提案資料が完成する」。人は判断と仕上げに集中できる。",
        key="作業時間を1/10に、品質を全社で標準化する。",
        bold_lead=True, icon="idea",
    )

    d.bullets(
        "なぜ今 / WHY NOW", "技術と市場が同時に成熟した",
        [
            "生成AIの精度が実用水準に到達: 文章・要約・構成が任せられる段階に。",
            "リモート商談の定着で、資料そのものが営業の主役になった。",
            "ノーコード/自動化への投資意欲が中小企業まで広がっている。",
        ],
        key="3年前には作れなかった。1年後には当たり前になる。",
        icon="chart",
    )

    d.compare(
        "市場 / MARKET", "狙う市場と立ち上がり方",
        "TAM — 全体市場",
        ["国内の営業・企画職 約900万人", "資料作成ツール市場は年率二桁成長", "横展開: 教育・行政・採用資料"],
        "SOM — 初期の獲得層",
        ["BtoB SaaS/IT営業チーム", "提案頻度が高く品質要求が厳しい", "ROIを数字で説明できる層"],
        key="「資料で受注率が上がる」と最も実感しやすい層から取る。",
    )

    d.bullets(
        "製品 / PRODUCT", "3ステップで完成する",
        [
            "入力: テーマ・聞き手・ゴールを指定するだけ。",
            "生成: リサーチ→構成→デザインを自動実行し、出典も添付。",
            "編集: pptxで開いて微調整。テーマ配色は3種から選択可能。",
        ],
        key="専門知識ゼロでも、プロのアウトプットが出せる。",
        bold_lead=True, icon="idea",
    )

    d.takeaways(
        "提案 / THE ASK", "次の一歩",
        [
            ("01", "パイロット導入", "営業チーム1部門で4週間の無償トライアル。"),
            ("02", "効果測定", "作成時間と受注率を導入前後で比較・可視化。"),
            ("03", "全社展開", "効果が出た型をテンプレート化し横展開。"),
        ],
        sources="Sequoia Capital『Writing a Business Plan』/ Guy Kawasaki『The 10/20/30 Rule』/ 各社公開IR・調査レポート（デモ用の例示数値を含む）",
    )

    res = d.build(OUT, "hono_deck_demo")
    print(f"built {res['n']} slides")
    print("pptx:", res.get("pptx"))
    print("pdf :", res.get("pdf"))
    print("sheet:", res.get("contact"))


if __name__ == "__main__":
    build()
