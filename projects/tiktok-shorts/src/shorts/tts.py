"""TTS（既定: edge-tts / キー不要）。単語タイムスタンプも返す。

別プロバイダ（ElevenLabs等）に差し替えたい場合は synthesize() を実装し直すだけ。
ただし字幕の自動タイミングには単語境界（word boundary）が必要です。
"""
from __future__ import annotations

import asyncio


def synthesize(text: str, out_path: str, voice: str = "ja-JP-NanamiNeural",
               rate: str = "+0%") -> list[dict]:
    """text を読み上げて out_path(mp3) に保存し、単語境界のリストを返す。

    返り値: [{"text": str, "start": float秒, "end": float秒}, ...]
    """
    try:
        import edge_tts
    except ImportError as e:  # pragma: no cover
        raise RuntimeError("edge-tts が未インストールです: pip install edge-tts") from e

    async def _run() -> list[dict]:
        communicate = edge_tts.Communicate(text, voice, rate=rate)
        boundaries: list[dict] = []
        with open(out_path, "wb") as f:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    f.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    start = chunk["offset"] / 1e7  # 100ns 単位 → 秒
                    dur = chunk["duration"] / 1e7
                    boundaries.append({"text": chunk["text"], "start": start, "end": start + dur})
        return boundaries

    return asyncio.run(_run())
