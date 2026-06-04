import unittest

from affiliate.markdown import to_html


class TestMarkdown(unittest.TestCase):
    def test_heading_and_paragraph(self):
        html = to_html("## 見出し\n\n本文です。")
        self.assertIn("<h2>見出し</h2>", html)
        self.assertIn("<p>本文です。</p>", html)

    def test_bold_and_link(self):
        html = to_html("これは **太字** と [リンク](https://example.com) です。")
        self.assertIn("<strong>太字</strong>", html)
        self.assertIn('<a href="https://example.com">リンク</a>', html)

    def test_unordered_list(self):
        html = to_html("- A\n- B\n- C")
        self.assertEqual(html.count("<li>"), 3)
        self.assertIn("<ul>", html)

    def test_table(self):
        md = "| 列1 | 列2 |\n| --- | --- |\n| a | b |\n| c | d |"
        html = to_html(md)
        self.assertIn("<table>", html)
        self.assertIn("<th>列1</th>", html)
        self.assertIn("<td>a</td>", html)
        self.assertEqual(html.count("<tr>"), 3)  # header + 2 rows

    def test_raw_html_passthrough(self):
        md = '<div class="cta">\n<a href="x">y</a>\n</div>'
        html = to_html(md)
        self.assertIn('<div class="cta">', html)
        self.assertIn('<a href="x">y</a>', html)


if __name__ == "__main__":
    unittest.main()
