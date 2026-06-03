"""Verify the *production* (Claude) code paths by mocking the LLM, so we know
they work the moment a real ANTHROPIC_API_KEY is present."""

import unittest
from unittest import mock

from affiliate import generate, keywords
from affiliate.config import Config


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
        self.assertEqual(art.description, "説明X")
        self.assertIn("{AFFILIATE_CTA}", art.body_md)

    def test_generate_strips_code_fence(self):
        fake = '```json\n{"title":"T","description":"D","body_markdown":"本文だけ"}\n```'
        with mock.patch("affiliate.generate.llm.have_llm", return_value=True), mock.patch(
            "affiliate.generate.llm.complete", return_value=fake
        ):
            art = generate.generate("掃除機", Config())
        self.assertEqual(art.title, "T")
        # CTA marker is appended when the model forgets it.
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
