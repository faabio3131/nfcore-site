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
        cards = re.findall(r'<article class="price-card[^"]*">(.*?)</article>', html, re.S)
        self.assertEqual(len(cards), 4)
        for card, (plan, amount, quota) in zip(cards, (
            ("Starter", "99", "300"),
            ("Pro", "249", "1.500"),
            ("Business", "590", "6.000"),
            ("Enterprise", "1.490", "25.000"),
        )):
            with self.subTest(plan=plan):
                self.assertIn(f'<span class="price-type">{plan}</span>', card)
                self.assertIn(f"<strong>{amount}</strong>", card)
                self.assertIn(f"<b>{quota} notas/mês</b>", card)
                self.assertIn("Contratar " + plan, card)
                self.assertNotIn("ilimitad", card.lower())
        self.assertIn(WHATSAPP, html)
        self.assertIn("contratação assistida", html.lower())

    def test_capabilities_and_evidence_caveats(self) -> None:
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        for marker in ("AES-256-GCM", "NCM", "CFOP", "LC 214/2025",
                       "Gemini 3.8 Flash", "GPT", "SP", "MG", "RJ",
                       "PR", "MT", "MS", "IBGE", "NF-e", "NFC-e", "NFS-e"):
            with self.subTest(marker=marker):
                self.assertIn(marker, html)
        self.assertIn("Nenhuma cidade listada é automaticamente homologada em produção.", html)
        self.assertIn("A IA não emite nem autoriza notas", html)

    def test_sp_22_municipalities_and_5_capitals_are_exact(self) -> None:
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        expected = {
            "Barueri": "3505708", "São Paulo": "3550308",
            "Campinas": "3509502", "Sorocaba": "3552205",
            "Guarulhos": "3518800", "Santos": "3548500",
            "São Caetano do Sul": "3548807", "Jundiaí": "3525904",
            "Suzano": "3552502", "Santana de Parnaíba": "3547304",
            "Osasco": "3534401", "Itapevi": "3522505",
            "Jandira": "3525003", "Mairiporã": "3528502",
            "Arujá": "3503901", "Louveira": "3527306",
            "Valinhos": "3556206", "Itu": "3523909",
            "Salto": "3545209", "Monte Mor": "3531803",
            "Guarujá": "3518701", "São Vicente": "3551009",
        }
        rows = re.findall(
            r'<li><span class="city-index">\d{2}</span>'
            r'<span class="city-name">([^<]+)</span><code>(\d{7})</code></li>',
            html,
        )
        self.assertEqual(len(rows), 22)
        self.assertEqual(dict(rows), expected)
        pilots = {
            "MG": ("Belo Horizonte", "3106200"),
            "RJ": ("Rio de Janeiro", "3304557"),
            "PR": ("Curitiba", "4106902"),
            "MT": ("Cuiabá", "5103403"),
            "MS": ("Campo Grande", "5002704"),
        }
        for uf, (city, ibge) in pilots.items():
            with self.subTest(uf=uf):
                self.assertIn(f'class="region-uf">{uf}</span>', html)
                self.assertIn(f"<h3>{city}</h3>", html)
                self.assertIn(f"IBGE {ibge}", html)
        self.assertIn("não de emissão liberada", html)
        self.assertIn("HOMOLOGAÇÃO EXTERNA PENDENTE", html)

    def test_authority_tabs_are_complete_and_interactive(self) -> None:
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertEqual(html.count('role="tab"'), 5)
        self.assertEqual(html.count('role="tabpanel"'), 5)
        for number in range(1, 6):
            self.assertIn(f'id="flow-tab-{number}"', html)
            self.assertIn(f'aria-controls="flow-panel-{number}"', html)
            self.assertIn(f'id="flow-panel-{number}"', html)
            self.assertIn(f'aria-labelledby="flow-tab-{number}"', html)
        self.assertEqual(html.count('aria-selected="true"'), 1)
        self.assertIn("chip-visual", html)
        self.assertIn("Segurança de nível militar", html)
        self.assertIn("Core Cognitivo vertical", html)
        self.assertIn("Sentinela Normativo", html)
        self.assertIn("“Nível militar” descreve", html)

    def test_original_palette_and_hover_only_card_emphasis(self) -> None:
        css = (ROOT / "assets" / "enterprise.css").read_text(encoding="utf-8")
        for marker in ("--a:#885cf6", "--btn:#8056ef", "--bg:#060812",
                       "width:70%", ".price-card.highlighted", "(hover:hover)",
                       ".strength-card", ".intel-card", ".region-card", ".flow-tab"):
            with self.subTest(marker=marker):
                self.assertIn(marker, css)
        self.assertNotIn("--a:#b32bff", css)
        self.assertNotIn("--btn:#a02af5", css)
        self.assertIn("border:1px solid #33405e", css)
        self.assertIn("box-shadow:none", css)
        self.assertIn("html[data-p=nfcore] .price-card .plan-btn.primary", css)
        for page in PAGES:
            html = (ROOT / page).read_text(encoding="utf-8")
            self.assertIn("assets/enterprise.css?v=20261106-palette", html)

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
