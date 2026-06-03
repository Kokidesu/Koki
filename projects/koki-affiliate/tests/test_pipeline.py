import tempfile
import unittest
from pathlib import Path

from affiliate.config import Config
from affiliate.pipeline import run


class TestPipeline(unittest.TestCase):
    def test_run_produces_site(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = Config(
                site_title="テストブログ",
                site_url="https://example.com",
                base_dir=tmp,
                amazon_tag="test-22",
            )
            report = run("ロボット掃除機", 3, cfg)

            self.assertEqual(len(report.articles), 3)

            base = Path(tmp)
            # Core site files exist.
            for name in ("index.html", "style.css", "sitemap.xml", "robots.txt"):
                self.assertTrue((base / name).exists(), f"missing {name}")

            # One HTML page per article.
            for art in report.articles:
                self.assertTrue((base / f"{art.slug}.html").exists())

            index = (base / "index.html").read_text(encoding="utf-8")
            self.assertIn("テストブログ", index)
            for art in report.articles:
                self.assertIn(art.title, index)

            # Article page carries the affiliate CTA + disclosure.
            page = (base / f"{report.articles[0].slug}.html").read_text(encoding="utf-8")
            self.assertIn("amazon.co.jp", page)
            self.assertIn("tag=test-22", page)
            self.assertIn("アフィリエイトプログラム", page)  # footer disclosure
            self.assertNotIn("{AFFILIATE_CTA}", page)

    def test_unique_slugs(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = Config(base_dir=tmp)
            report = run("カメラ", 6, cfg)
            slugs = [a.slug for a in report.articles]
            self.assertEqual(len(slugs), len(set(slugs)))


if __name__ == "__main__":
    unittest.main()
