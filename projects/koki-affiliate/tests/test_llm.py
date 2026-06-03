"""Verify provider selection and both production code paths (Anthropic + Ollama)
by mocking, so they work the moment a real backend is present."""

import json
import os
import unittest
from unittest import mock

from affiliate import generate, keywords, llm
from affiliate.config import Config


class TestProvider(unittest.TestCase):
    def test_forced_none(self):
        with mock.patch.dict(os.environ, {"KOKI_LLM": "none"}):
            self.assertEqual(llm.provider(), "none")
            self.assertFalse(llm.have_llm())

    def test_forced_ollama(self):
        with mock.patch.dict(os.environ, {"KOKI_LLM": "ollama"}):
            self.assertEqual(llm.provider(), "ollama")
            self.assertTrue(llm.have_llm())

    def test_forced_anthropic(self):
        with mock.patch.dict(os.environ, {"KOKI_LLM": "anthropic"}):
            self.assertEqual(llm.provider(), "anthropic")

    def test_auto_falls_back_to_none(self):
        with mock.patch.dict(os.environ, {"KOKI_LLM": "auto"}), mock.patch(
            "affiliate.llm._anthropic_ready", return_value=False
        ), mock.patch("affiliate.llm._ollama_up", return_value=False):
            self.assertEqual(llm.provider(), "none")

    def test_auto_prefers_anthropic(self):
        with mock.patch.dict(os.environ, {"KOKI_LLM": "auto"}), mock.patch(
            "affiliate.llm._anthropic_ready", return_value=True
        ):
            self.assertEqual(llm.provider(), "anthropic")

    def test_auto_uses_ollama_when_up(self):
        with mock.patch.dict(os.environ, {"KOKI_LLM": "auto"}), mock.patch(
            "affiliate.llm._anthropic_ready", return_value=False
        ), mock.patch("affiliate.llm._ollama_up", return_value=True):
            self.assertEqual(llm.provider(), "ollama")


class TestOllamaComplete(unittest.TestCase):
    def test_ollama_complete_parses_message(self):
        body = json.dumps({"message": {"content": "生成された本文"}}).encode("utf-8")

        class FakeResp:
            status = 200

            def read(self):
                return body

            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

        with mock.patch.dict(os.environ, {"KOKI_LLM": "ollama"}), mock.patch(
            "affiliate.llm.urllib.request.urlopen", return_value=FakeResp()
        ):
            out = llm.complete("プロンプト", system="システム", model="ignored")
        self.assertEqual(out, "生成された本文")


class TestClaudePaths(unittest.TestCase):
    def test_generate_parses_claude_json(self):
        fake = (
            '{"title":"タイトルX","description":"説明X",'
            '"body_markdown":"## 見出し\\n\\n本文。{AFFILIATE_CTA}"}'
        )
        with mock.patch("affiliate.generate.llm.have_llm", return_value=True), mock.patch(
            "affiliate.generate.llm.complete", return_value=fake
        ):
            art = generate.generate("空気清浄機", Config())
        self.assertEqual(art.generator, "claude")
        self.assertEqual(art.title, "タイトルX")
        self.assertIn("{AFFILIATE_CTA}", art.body_md)

    def test_generate_strips_code_fence(self):
        fake = '```json\n{"title":"T","description":"D","body_markdown":"本文だけ"}\n```'
        with mock.patch("affiliate.generate.llm.have_llm", return_value=True), mock.patch(
            "affiliate.generate.llm.complete", return_value=fake
        ):
            art = generate.generate("掃除機", Config())
        self.assertEqual(art.title, "T")
        self.assertIn("{AFFILIATE_CTA}", art.body_md)

    def test_generate_falls_back_on_bad_json(self):
        with mock.patch("affiliate.generate.llm.have_llm", return_value=True), mock.patch(
            "affiliate.generate.llm.complete", return_value="これはJSONではない"
        ):
            art = generate.generate("加湿器", Config())
        self.assertEqual(art.generator, "claude")
        self.assertIn("{AFFILIATE_CTA}", art.body_md)

    def test_keywords_uses_claude_lines(self):
        fake = "掃除機 おすすめ\n2. 掃除機 比較\n- 掃除機 安い"
        with mock.patch("affiliate.keywords.llm.have_llm", return_value=True), mock.patch(
            "affiliate.keywords.llm.complete", return_value=fake
        ):
            kws = keywords.expand("掃除機", 3, Config())
        self.assertEqual(kws, ["掃除機 おすすめ", "掃除機 比較", "掃除機 安い"])


if __name__ == "__main__":
    unittest.main()
