"""A tiny, dependency-free Markdown -> HTML converter.

Supports just what the article generator emits: headings, paragraphs,
bullet/numbered lists, pipe tables, inline bold/links/code, and pass-through
of raw HTML blocks (used for the CTA).
"""

from __future__ import annotations

import re
from typing import List


def _inline(text: str) -> str:
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    return text


def _cells(line: str) -> List[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def _table(header: List[str], rows: List[List[str]]) -> str:
    th = "".join(f"<th>{_inline(c)}</th>" for c in header)
    body = ""
    for row in rows:
        tds = "".join(f"<td>{_inline(c)}</td>" for c in row)
        body += f"<tr>{tds}</tr>"
    return f"<table><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table>"


def to_html(md: str) -> str:
    lines = md.split("\n")
    n = len(lines)
    out: List[str] = []
    para: List[str] = []

    def flush() -> None:
        if para:
            text = " ".join(para).strip()
            if text:
                out.append("<p>" + _inline(text) + "</p>")
            para.clear()

    i = 0
    while i < n:
        raw = lines[i]
        s = raw.strip()

        if not s:
            flush()
            i += 1
            continue

        # Raw HTML block (e.g. the CTA): pass through verbatim.
        if s.startswith("<"):
            flush()
            block = []
            while i < n and lines[i].strip():
                block.append(lines[i])
                i += 1
            out.append("\n".join(block))
            continue

        # Heading
        m = re.match(r"(#{1,6})\s+(.*)", s)
        if m:
            flush()
            level = len(m.group(1))
            out.append(f"<h{level}>{_inline(m.group(2).strip())}</h{level}>")
            i += 1
            continue

        # Table (header row followed by a |---|---| separator)
        nxt = lines[i + 1].strip() if i + 1 < n else ""
        if s.startswith("|") and nxt and set(nxt) <= set("|-: ") and "-" in nxt:
            flush()
            header = _cells(s)
            i += 2
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append(_cells(lines[i]))
                i += 1
            out.append(_table(header, rows))
            continue

        # Unordered list
        if re.match(r"[-*]\s+", s):
            flush()
            items = []
            while i < n and re.match(r"[-*]\s+", lines[i].strip()):
                items.append(re.sub(r"^[-*]\s+", "", lines[i].strip()))
                i += 1
            out.append("<ul>" + "".join(f"<li>{_inline(x)}</li>" for x in items) + "</ul>")
            continue

        # Ordered list
        if re.match(r"\d+\.\s+", s):
            flush()
            items = []
            while i < n and re.match(r"\d+\.\s+", lines[i].strip()):
                items.append(re.sub(r"^\d+\.\s+", "", lines[i].strip()))
                i += 1
            out.append("<ol>" + "".join(f"<li>{_inline(x)}</li>" for x in items) + "</ol>")
            continue

        para.append(s)
        i += 1

    flush()
    return "\n".join(out)
