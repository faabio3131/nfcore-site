"""Headless visual quality gate (optional local check; requires Playwright + Chrome).

Run: python scripts/visual_smoke.py
Screenshots go to the system temporary directory, never into the repository.
"""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(tempfile.gettempdir()) / "nfcore-visual-validation"
OUT.mkdir(parents=True, exist_ok=True)
PAGES = ["index.html", "core-cognitivo.html", "reforma-tributaria.html", "contato.html"]
WIDTHS = [320, 375, 768, 1024, 1440, 1920]


def main() -> None:
    problems: list[str] = []
    report = []
    with sync_playwright() as playwright:
        chrome_paths = [
            os.environ.get("NFCORE_BROWSER_PATH", ""),
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        ]
        binary = next((p for p in chrome_paths if p and Path(p).is_file()), None)
        browser = playwright.chromium.launch(
            headless=True,
            **({"executable_path": binary} if binary else {}),
            args=["--allow-file-access-from-files"],
        )
        try:
            for name in PAGES:
                for width in WIDTHS:
                    page = browser.new_page(viewport={"width": width, "height": 900}, device_scale_factor=1)
                    errors: list[str] = []
                    page.on("pageerror", lambda err: errors.append(str(err)))
                    response = page.goto((ROOT / name).as_uri(), wait_until="load")
                    page.evaluate("document.fonts.ready")
                    title = page.title()
                    metrics = page.evaluate("""() => {
                      const outside = [];
                      const check = 'h1,h2,h3,.phero .b,.phero .vis,.price-card,.geo-panel,.intel-card';
                      for (const n of document.querySelectorAll(check)) {
                        if (getComputedStyle(n).display === 'none') continue;
                        const r = n.getBoundingClientRect();
                        if (r.width && (r.left < -2 || r.right > innerWidth + 2))
                          outside.push(n.tagName.toLowerCase() + '.' + (n.className||'').toString().slice(0,32));
                        if (n.scrollWidth > n.clientWidth + 4 && ['H1','H2','H3'].includes(n.tagName))
                          outside.push('text-overflow:' + n.textContent.slice(0,32));
                      }
                      return { viewport: innerWidth, document: document.documentElement.scrollWidth,
                               outside, hero: !!document.querySelector('.phero h1') };
                    }""")
                    if not title or not metrics["hero"]:
                        problems.append(f"{name} {width}: title/hero ausente")
                    if metrics["outside"] or metrics["document"] > width + 2:
                        problems.append(f"{name} {width}: overflow {metrics}")
                    if errors:
                        problems.append(f"{name} {width}: JS {errors}")
                    if width in (375, 1440):
                        shot = OUT / f"{name.replace('.html','')}-{width}.png"
                        page.screenshot(path=str(shot), full_page=True)
                    if name == "index.html" and width in (375, 1440):
                        figure = page.locator(".chip-visual")
                        container = page.locator(".phero .vis")
                        ratio = figure.bounding_box()["width"] / container.bounding_box()["width"]
                        if not 0.68 <= ratio <= 0.72:
                            problems.append(f"chip -30% incorreto: {width}, ratio={ratio:.3f}")
                        if page.locator(".city-grid .city-name").count() != 22:
                            problems.append(f"{width}: SP não possui 22 municípios")
                        if page.locator(".region-card").count() != 6:
                            problems.append(f"{width}: faltam grupos UF")
                        if page.locator("#flow-tab-3").count() != 1:
                            problems.append(f"{width}: falta aba interativa")
                        else:
                            page.locator("#flow-tab-3").click()
                            if page.locator("#flow-tab-3").get_attribute("aria-selected") != "true":
                                problems.append(f"{width}: aba 3 não selecionada")
                            if not page.locator("#flow-panel-3").is_visible():
                                problems.append(f"{width}: painel 3 não abriu")
                            if page.locator("#flow-panel-1").is_visible():
                                problems.append(f"{width}: painel 1 não foi ocultado")
                            page.locator("#flow-tab-3").press("ArrowRight")
                            if page.locator("#flow-tab-4").get_attribute("aria-selected") != "true":
                                problems.append(f"{width}: teclado não navega pelas abas")
                            page.locator("#flow-tab-1").click()
                        states = page.locator(".region-card")
                        states.nth(1).locator("summary").click()
                        if not states.nth(1).evaluate("(n) => n.open"):
                            problems.append(f"{width}: MG não expande")
                        states.nth(1).locator("summary").click()
                        if states.nth(1).evaluate("(n) => n.open"):
                            problems.append(f"{width}: MG não recolhe")
                        glow = page.locator(".intel-card").first
                        glow.hover()
                        shadow = glow.evaluate("(n) => getComputedStyle(n).boxShadow")
                        if shadow == "none":
                            problems.append(f"{width}: neon glow não aplicado ao card de IA")
                    if width <= 1024:
                        button = page.locator("#burger")
                        if button.is_visible():
                            button.click()
                            if button.get_attribute("aria-expanded") != "true" or not page.locator("#menu").is_visible():
                                problems.append(f"{name} {width}: menu não abre")
                            page.keyboard.press("Escape")
                            if button.get_attribute("aria-expanded") != "false":
                                problems.append(f"{name} {width}: menu não fecha com Escape")
                    report.append({"page": name, "width": width, "metrics": metrics})
                    page.close()
        finally:
            browser.close()
    print(json.dumps({"cases": len(report), "failures": problems, "screenshots": str(OUT)}, ensure_ascii=False, indent=2))
    if problems:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
