from pathlib import Path

from koki.memory import HonoMemory


def test_add_and_recall(tmp_path: Path):
    mem = HonoMemory(tmp_path / "mem.jsonl")
    mem.add("日本の人口は？", "約1.24億人です。", ["https://example.com/jp"])
    mem.add("フランスの首都は？", "パリです。", ["https://example.com/fr"])

    hits = mem.recall("日本の人口について教えて", limit=2)
    assert hits, "expected at least one relevant memory"
    assert "人口" in hits[0]["question"]


def test_as_context_empty_when_no_overlap(tmp_path: Path):
    mem = HonoMemory(tmp_path / "mem.jsonl")
    assert mem.as_context("anything") == ""
    mem.add("photosynthesis basics", "Calvin cycle fixes CO2.", [])
    ctx = mem.as_context("explain the calvin cycle of photosynthesis")
    assert "Past research notes" in ctx
    assert "Calvin" in ctx


def test_persistence_across_instances(tmp_path: Path):
    p = tmp_path / "mem.jsonl"
    HonoMemory(p).add("q1", "a1", [])
    assert HonoMemory(p).recall("q1")
