import unittest

from affiliate.affiliate import amazon_search_url, cta_html, inject, rakuten_url
from affiliate.config import Config


class TestAffiliate(unittest.TestCase):
    def test_amazon_url_with_tag(self):
        url = amazon_search_url("ロボット掃除機", "mytag-22")
        self.assertTrue(url.startswith("https://www.amazon.co.jp/s?k="))
        self.assertIn("tag=mytag-22", url)
        self.assertNotIn(" ", url)  # url-encoded

    def test_amazon_url_without_tag(self):
        url = amazon_search_url("foo", "")
        self.assertNotIn("tag=", url)

    def test_rakuten_url(self):
        url = rakuten_url("カメラ", "https://search.rakuten.co.jp/search/mall/{kw}/")
        self.assertIn("search.rakuten.co.jp", url)
        self.assertNotIn("{kw}", url)

    def test_cta_has_disclosure_and_rel(self):
        cta = cta_html("空気清浄機", Config(amazon_tag="t-22"))
        self.assertIn("PR / 広告", cta)
        self.assertIn('rel="nofollow sponsored noopener"', cta)
        self.assertIn("空気清浄機", cta)

    def test_inject_replaces_marker(self):
        body = "本文\n\n{AFFILIATE_CTA}\n"
        out = inject(body, "扇風機", Config())
        self.assertNotIn("{AFFILIATE_CTA}", out)
        self.assertIn('<div class="cta">', out)


if __name__ == "__main__":
    unittest.main()
