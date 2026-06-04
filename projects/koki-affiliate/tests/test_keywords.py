import unittest

from affiliate.config import Config
from affiliate.keywords import expand


class TestKeywords(unittest.TestCase):
    def test_fallback_count_and_seed(self):
        # No API key in test env -> deterministic fallback.
        kws = expand("ロボット掃除機", 5, Config())
        self.assertEqual(len(kws), 5)
        for kw in kws:
            self.assertIn("ロボット掃除機", kw)

    def test_more_than_suffixes(self):
        kws = expand("カメラ", 15, Config())
        self.assertEqual(len(kws), 15)
        self.assertEqual(len(set(kws)), 15)  # all unique

    def test_empty_seed(self):
        self.assertEqual(expand("   ", 5, Config()), [])


if __name__ == "__main__":
    unittest.main()
