"""Free, dependency-free eyecatch images as SVG.

No external image services, no API key, no copyright concerns — each article
gets a generated 1200x630 (OGP-sized) card with its title and the site name.
"""

from __future__ import annotations

import html
from typing import List, Tuple

# A few gradient palettes; articles rotate through them for visual variety.
_PALETTES: List[Tuple[str, str]] = [
    ("#2563eb", "#1e3a8a"),
    ("#0ea5e9", "#0c4a6e"),
    ("#7c3aed", "#4c1d95"),
    ("#059669", "#064e3b"),
    ("#db2777", "#831843"),
    ("#ea580c", "#7c2d12"),
]


def _wrap(text: str, per_line: int, max_lines: int) -> List[str]:
    lines = [text[i : i + per_line] for i in range(0, len(text), per_line)]
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1][: per_line - 1] + "…"
    return lines


def eyecatch_svg(title: str, site_title: str, *, seed: int = 0) -> str:
    c1, c2 = _PALETTES[seed % len(_PALETTES)]
    lines = _wrap(title, 15, 3)
    start_y = 315 - (len(lines) - 1) * 45
    tspans = "".join(
        f'<tspan x="80" y="{start_y + i * 90}">{html.escape(line)}</tspan>'
        for i, line in enumerate(lines)
    )
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" '
        'viewBox="0 0 1200 630" role="img">'
        '<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{c1}"/>'
        f'<stop offset="1" stop-color="{c2}"/>'
        "</linearGradient></defs>"
        '<rect width="1200" height="630" fill="url(#g)"/>'
        '<rect x="40" y="40" width="1120" height="550" fill="none" '
        'stroke="rgba(255,255,255,.35)" stroke-width="2"/>'
        '<text font-family="\'Hiragino Kaku Gothic ProN\',\'Noto Sans JP\',sans-serif" '
        f'font-size="60" font-weight="700" fill="#ffffff">{tspans}</text>'
        '<text x="80" y="560" font-family="sans-serif" font-size="30" '
        f'fill="rgba(255,255,255,.85)">{html.escape(site_title)}</text>'
        "</svg>"
    )
