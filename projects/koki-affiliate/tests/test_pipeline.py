import shutil
import tempfile
import unittest
from pathlib import Path

from affiliate import store
from affiliate.config import Config
from affiliate.pipeline import build, run


class TestPipeline(unittest.TestCase):
    def _cfg(self, tmp):
        return Config(
            site_title="テストブログ",
            site_url="https://example.com",
            base_dir=str(Path(tmp) / "out"),
            content_dir=str(Path(tmp) / "content"),
            amazon_tag="test-22",
        )

    def test_run_creates_site(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = self._cfg(tmp)
            report = run("ロボット掃除機", 3, cfg)
            self.assertEqual(len(report.new_articles), 3)
            self.assertEqual(report.total, 3)

            base = Path(cfg.base_dir)
            for name in ("index.html", "style.css", "sitemap.xml", "robots.txt"):
                self.assertTrue((base / name).exists(), f"missing {name}")

            slug0 = report.new_articles[0].slug
            self.assertTrue((base / f"{slug0}.svg").exists())  # eyecatch image
            page = (base / f"{slug0}.html").read_text("utf-8")
            self.assertIn('class="eyecatch"', page)
            self.assertIn("og:image", page)
            self.assertIn("amazon.co.jp", page)
            self.assertIn("tag=test-22", page)
            self.assertIn("アフィリエイトプログラム", page)
            self.assertNotIn("{AFFILIATE_CTA}", page)

    def test_runs_accumulate(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = self._cfg(tmp)
            run("ロボット掃除機", 3, cfg)
            second = run("ロボット掃除機", 3, cfg)
            # New, non-duplicate keywords on the second run.
            self.assertEqual(second.total, 6)
            idx = (Path(cfg.base_dir) / "index.html").read_text("utf-8")
            self.assertEqual(idx.count('class="card"'), 6)

    def test_no_duplicates_when_exhausted(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = self._cfg(tmp)
            run("カメラ", 100, cfg)  # ask for more than the fallback can make
            run("カメラ", 100, cfg)  # second run should add nothing new
            slugs = [a.slug for a in store.load_all(cfg.content_dir)]
            self.assertEqual(len(slugs), len(set(slugs)))

    def test_build_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = self._cfg(tmp)
            run("扇風機", 2, cfg)
            shutil.rmtree(cfg.base_dir)
            n = build(cfg)
            self.assertEqual(n, 2)
            self.assertTrue((Path(cfg.base_dir) / "index.html").exists())

    def test_multiple_seeds(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = self._cfg(tmp)
            report = run(["カメラ", "三脚"], 4, cfg)
            self.assertEqual(len(report.new_articles), 4)


if __name__ == "__main__":
    unittest.main()
