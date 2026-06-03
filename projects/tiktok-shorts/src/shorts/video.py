"""ffmpeg で縦型MP4を合成（背景＋音声＋字幕焼き込み、任意でBGM）。"""
from __future__ import annotations

import os
import random
import shutil
import subprocess
from pathlib import Path

_VIDEO_EXT = {".mp4", ".mov", ".webm", ".mkv"}
_AUDIO_EXT = {".mp3", ".m4a", ".wav", ".aac"}


def _ensure_paths() -> None:
    """システムに ffmpeg/ffprobe が無ければ pip の静的バイナリをPATHに追加。"""
    if shutil.which("ffmpeg") and shutil.which("ffprobe"):
        return
    try:
        import static_ffmpeg
        static_ffmpeg.add_paths()  # 初回はGitHubからDL、以降キャッシュ
    except Exception:  # noqa: BLE001
        pass


def _require(bin_name: str) -> str:
    path = shutil.which(bin_name)
    if not path:
        _ensure_paths()
        path = shutil.which(bin_name)
    if not path:
        raise RuntimeError(
            f"{bin_name} が見つかりません。`pip install static-ffmpeg` か、"
            "システムに ffmpeg を入れてください。")
    return path


def probe_duration(path: str) -> float:
    out = subprocess.run(
        [_require("ffprobe"), "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True, check=True,
    )
    return float(out.stdout.strip())


def _pick(directory: str, exts: set[str]) -> str | None:
    d = Path(directory)
    if not d.is_dir():
        return None
    files = [p for p in d.iterdir() if p.suffix.lower() in exts]
    return str(random.choice(files).resolve()) if files else None


def assemble(audio_path: str, ass_path: str, out_path: str,
             resolution=(1080, 1920), fps: int = 30,
             backgrounds_dir: str = "assets/backgrounds",
             music_dir: str = "assets/music", music_volume: float = 0.12,
             fonts_dir: str | None = None) -> str:
    ffmpeg = _require("ffmpeg")
    w, h = resolution
    dur = probe_duration(audio_path)
    audio_abs = str(Path(audio_path).resolve())
    bg = _pick(backgrounds_dir, _VIDEO_EXT)
    music = _pick(music_dir, _AUDIO_EXT)

    # 字幕は cwd 相対のファイル名で渡し、パス内のコロン等によるフィルタ崩れを回避する
    workdir = str(Path(out_path).resolve().parent)
    ass_name = Path(ass_path).name
    out_abs = str(Path(out_path).resolve())

    cmd = [ffmpeg, "-y"]
    if bg:
        cmd += ["-stream_loop", "-1", "-i", bg]
    else:
        # 素材が無くてもベタ塗りにならないよう、ゆっくり動くグラデを生成
        grad = (f"gradients=s={w}x{h}:c0=0x0b1224:c1=0x223a66:c2=0x0b1224:"
                f"x0=0:y0=0:x1={w}:y1={h}:speed=0.008:r={fps}")
        cmd += ["-f", "lavfi", "-i", grad]
    cmd += ["-i", audio_abs]            # input 1 = voice
    if music:
        cmd += ["-stream_loop", "-1", "-i", music]  # input 2 = bgm

    subs = f"subtitles={ass_name}"
    if fonts_dir and Path(fonts_dir).is_dir() and any(Path(fonts_dir).iterdir()):
        subs += f":fontsdir={Path(fonts_dir).resolve()}"
    vchain = (
        f"[0:v]scale={w}:{h}:force_original_aspect_ratio=increase,"
        f"crop={w}:{h},{subs}[v]"
    )
    if music:
        fc = (
            f"{vchain};[1:a]volume=1.7[a1];[2:a]volume={music_volume}[a2];"
            f"[a1][a2]amix=inputs=2:duration=first:dropout_transition=0[a]"
        )
        amap = "[a]"
    else:
        fc = f"{vchain};[1:a]volume=1.7[a]"
        amap = "[a]"

    cmd += [
        "-filter_complex", fc,
        "-map", "[v]", "-map", amap,
        "-t", f"{dur:.3f}",
        "-r", str(fps),
        "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        "-shortest",
        out_abs,
    ]

    subprocess.run(cmd, cwd=workdir, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    return out_path
