import unittest

from affiliate.images import eyecatch_svg


class TestImages(unittest.TestCase):
    def test_svg_structure(self):
        svg = eyecatch_svg("ロボット掃除機の選び方", "おすすめ研究所", seed=0)
        self.assertTrue(svg.startswith("<svg"))
        self.assertIn("</svg>", svg)
        self.assertIn('width="1200"', svg)
        self.assertIn('height="630"', svg)

    def test_title_and_site_present(self):
        svg = eyecatch_svg("掃除機", "マイサイト", seed=1)
        self.assertIn("掃除機", svg)
        self.assertIn("マイサイト", svg)

    def test_escapes_special_chars(self):
        svg = eyecatch_svg("A & B <x>", "S&T", seed=2)
        self.assertIn("&amp;", svg)
        self.assertNotIn("<x>", svg)

    def test_long_title_is_wrapped_and_truncated(self):
        svg = eyecatch_svg("あ" * 100, "site", seed=0)
        self.assertIn("…", svg)
        self.assertIn("<tspan", svg)

    def test_seed_rotates_palette(self):
        a = eyecatch_svg("t", "s", seed=0)
        b = eyecatch_svg("t", "s", seed=1)
        self.assertNotEqual(a, b)


if __name__ == "__main__":
    unittest.main()
