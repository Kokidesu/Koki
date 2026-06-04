import tempfile
import unittest

from affiliate import store
from affiliate.generate import Article


def _mk(slug, date="2026-06-03"):
    return Article(
        keyword="kw",
        title="タイトル",
        description="説明",
        slug=slug,
        body_md="本文",
        date=date,
        generator="template",
    )


class TestStore(unittest.TestCase):
    def test_save_and_load_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            store.save_article(_mk("a"), d)
            store.save_article(_mk("b"), d)
            arts = store.load_all(d)
            self.assertEqual(len(arts), 2)
            self.assertEqual({a.slug for a in arts}, {"a", "b"})
            self.assertIsInstance(arts[0], Article)

    def test_load_missing_dir(self):
        self.assertEqual(store.load_all("/no/such/dir/here"), [])

    def test_sorted_newest_first(self):
        with tempfile.TemporaryDirectory() as d:
            store.save_article(_mk("old", "2026-01-01"), d)
            store.save_article(_mk("new", "2026-12-31"), d)
            arts = store.load_all(d)
            self.assertEqual(arts[0].slug, "new")

    def test_existing_slugs(self):
        with tempfile.TemporaryDirectory() as d:
            store.save_article(_mk("x"), d)
            self.assertEqual(store.existing_slugs(d), {"x"})


if __name__ == "__main__":
    unittest.main()
