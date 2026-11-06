"""Static offline smoke tests for the public NFCore GitHub Pages site.

Run: python -m unittest discover -s tests -p 'test_*.py' -v
No external credentials, network calls or payment/fiscal operations.
"""
from __future__ import annotations

import re
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
PAGES = ("index.html", "core-cognitivo.html", "reforma-tributaria.html", "contato.html")
PORTAL = "https://app.nfcore.com.br/"
WHATSAPP = "https://wa.me/5511978350851"


class SiteParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[str] = []
        self.assets: list[str] = []
        self.ids: list[str] = []
        self.h1 = 0
        self.main = 0
        self.titles = 0
        self.nav_toggle = 0
        self.has_lang = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = dict(attrs)
        if tag == "html":
            self.has_lang = a.get("lang") == "pt-BR"
        if tag == "h1":
            self.h1 += 1
        if tag == "main":
            self.main += 1
        if tag == "title":
            self.titles += 1
        if a.get("id"):
            self.ids.append(a["id"])
        if tag == "button" and a.get("id") == "burger":
            if a.get("aria-expanded") == "false" and a.get("aria-controls") == "menu":
                self.nav_toggle += 1
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])
        if tag in ("img", "script", "link"):
            ref = a.get("src") or a.get("href")
            if ref and not ref.startswith(("https:", "http:", "data:")):
                self.assets.append(ref)


class TestSiteStructure(unittest.TestCase):
    def test_routes_and_accessibility(self) -> None:
        for page in PAGES:
            with self.subTest(page=page):
                path = ROOT / page
                self.assertTrue(path.is_file())
                html = path.read_text(encoding="utf-8")
                parsed = SiteParser()
                parsed.feed(html)
                parsed.close()
                self.assertTrue(parsed.has_lang, page)
                self.assertEqual(parsed.h1, 1, page)
                self.assertEqual(parsed.main, 1, page)
                self.assertEqual(parsed.titles, 1, page)
                self.assertEqual(parsed.nav_toggle, 1, page)
                self.assertEqual(len(parsed.ids), len(set(parsed.ids)), page)
                self.assertIn(PORTAL, html, page)
                self.assertIn("enterprise.css", html, page)
                self.assertNotIn("up.railway.app", html, page)
                for href in parsed.links + parsed.assets:
                    split = urlsplit(href)
                    if split.scheme or href.startswith(("//", "mailto:", "tel:", "javascript:")):
                        continue
                    target = ROOT / unquote(split.path or page)
                    self.assertTrue(target.is_file(), f"{page}: {href} não existe")
                    if split.fragment and target.suffix == ".html":
                        target_parser = SiteParser()
                        target_parser.feed(target.read_text(encoding="utf-8"))
                        self.assertIn(unquote(split.fragment), target_parser.ids, f"{page}: {href} sem id")

    def test_pricing_is_complete_and_explicit(self) -> None:
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        for plan, amount, count, quota in (
            ("Starter", "99", "1 CNPJ", "1.000 notas/mês"),
            ("Pro", "249", "3 CNPJs", "5.000 notas/mês"),
            ("Business", "590", "15 CNPJs", "25.000 notas/mês"),
            ("Enterprise", "1.490", "ilimitada", "Contabo"),
        ):
            with self.subTest(plan=plan):
                self.assertIn(plan, html)
                self.assertRegex(html, rf"<strong>{re.escape(amount)}</strong>")
                self.assertIn(count, html)
                self.assertIn(quota, html)
                self.assertIn("Contratar " + plan, html)
        self.assertEqual(html.count('class="price-card'), 4)
        self.assertIn(WHATSAPP, html)
        self.assertIn("contratação assistida", html.lower())

    def test_capabilities_and_evidence_caveats(self) -> None:
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        for marker in ("AES-256-GCM", "NCM", "CFOP", "LC 214/2025",
                       "Gemini 3.8 Flash", "GPT", "SP", "MG", "RJ",
                       "PR", "MT", "MS", "IBGE", "NF-e", "NFC-e", "NFS-e"):
            with self.subTest(marker=marker):
                self.assertIn(marker, html)
        self.assertIn("não declara todos os municípios homologados", html)
        self.assertIn("A IA não emite nem autoriza notas", html)

    def test_static_assets_and_legacy_urls(self) -> None:
        self.assertTrue((ROOT / ".nojekyll").exists())
        self.assertEqual((ROOT / "CNAME").read_text(encoding="utf-8").strip(), "nfcore.com.br")
        self.assertTrue((ROOT / "assets" / "site.css").is_file())
        self.assertTrue((ROOT / "assets" / "enterprise.css").is_file())
        js = (ROOT / "assets" / "site.js").read_text(encoding="utf-8")
        self.assertIn("aria-expanded", js)
        self.assertIn("Escape", js)


if __name__ == "__main__":
    unittest.main()
