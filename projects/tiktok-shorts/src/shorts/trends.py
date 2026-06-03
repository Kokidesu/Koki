"""トレンド調査: いま伸びやすい雑学ネタを出す。

注: ここはモデルの知識ベースでネタ出しします（擬似トレンド）。
リアルタイムの急上昇を厳密に取りたい場合は、検索/トレンドAPIを
fetch_trending() の中に差し込んでください（README参照）。
"""
from __future__ import annotations

from . import llm

# モデルが使えない/失敗した時のフォールバック種ネタ
SEED = [
    {"topic": "バナナは放射性物質を含む", "angle": "カリウム40。実は身近な放射線", "hook_idea": "あなたが毎朝食べてるアレ、実は放射性です"},
    {"topic": "ハチミツは腐らない", "angle": "古代エジプトの墓から食べられる蜂蜜", "hook_idea": "3000年前の食べ物、まだ食べられます"},
    {"topic": "カンガルーは後ろに歩けない", "angle": "だから国章に採用された", "hook_idea": "ある国がカンガルーを国章に選んだ意外な理由"},
    {"topic": "タコの心臓は3つある", "angle": "血も青い（ヘモシアニン）", "hook_idea": "血が青い生き物、実在します"},
    {"topic": "人間の骨は鉄より強い", "angle": "単位重量あたりの強度", "hook_idea": "あなたの骨、鉄筋コンクリートより強いです"},
    {"topic": "宇宙には燃える氷の惑星がある", "angle": "高温なのに固体の水", "hook_idea": "熱いのに凍ってる、矛盾の惑星"},
    {"topic": "エッフェル塔は夏に15cm伸びる", "angle": "金属の熱膨張", "hook_idea": "パリの塔、季節で身長が変わります"},
    {"topic": "ラッコは手をつないで眠る", "angle": "流されないため", "hook_idea": "寝てる間に離れ離れにならない工夫"},
]

_SYSTEM = (
    "あなたはTikTokショートの敏腕コンテンツ戦略家です。"
    "視聴維持率が高く、保存・シェアされやすい『雑学・豆知識』ネタを設計します。"
    "扱うのは、意外性があり・短く説明でき・事実確認が可能なネタに限ります。"
)


def fetch_trending(niche: str = "雑学・豆知識", n: int = 10, language: str = "ja") -> list[dict]:
    prompt = (
        f"ジャンル『{niche}』で、いまショート動画で伸びやすい切り口の鉄板ネタを{n}個出してください。\n"
        "各ネタは次のJSON配列で返してください（説明文は不要、JSONのみ）:\n"
        '[{"topic":"一言の事実","angle":"なぜ面白いか/切り口","hook_idea":"最初の2秒で言う掴みの一文"}]\n'
        "条件: 誰でも検証できる事実ベース / 過度に専門的でない / 似たネタを重複させない。"
    )
    try:
        data = llm.complete_json(_SYSTEM, prompt, max_tokens=1800, temperature=0.9)
        if isinstance(data, dict):
            data = data.get("topics") or data.get("items") or []
        topics = [t for t in data if isinstance(t, dict) and t.get("topic")]
        if topics:
            return topics[:n]
    except Exception as e:  # noqa: BLE001 — フォールバックして続行
        print(f"[trends] モデル呼び出し失敗のためSEEDを使用: {e}")
    return SEED[:n]
