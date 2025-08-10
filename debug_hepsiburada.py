#!/usr/bin/env python3
"""
Hepsiburada Debug - HTML yapısını inceleme
"""

import asyncio
import logging
from playwright.async_api import async_playwright

logging.basicConfig(level=logging.DEBUG)

async def debug_hepsiburada_page():
    """Hepsiburada sayfasının HTML yapısını debug et"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Görünür modda çalıştır
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        try:
            url = "https://www.hepsiburada.com/gipta-pera-ciltli-deri-kapak-9x14-cizgisiz-defter-pm-HBC00002QG0EE"
            print(f"Sayfa yükleniyor: {url}")
            
            await page.goto(url, wait_until="networkidle", timeout=60000)
            await page.wait_for_timeout(5000)

            print("\n=== SAYFA BAŞLIĞI ===")
            title = await page.title()
            print(f"Title: {title}")

            print("\n=== H1 ELEMENTLERİ ===")
            h1_elements = await page.query_selector_all("h1")
            for i, h1 in enumerate(h1_elements):
                text = await h1.inner_text()
                print(f"H1 {i+1}: {text}")

            print("\n=== FİYAT ELEMENTLERİ ===")
            # Mevcut fiyat
            current_price_selectors = [
                "div.z7kokklsVwh0K5zFWjIO.nUoGYtEwzHyrjX2lvABI span",
                "div[class*='z7kokklsVwh0K5zFWjIO'] span",
                "[data-test-id='price-current']",
                ".price-current",
                "[class*='price'] span",
                "span[class*='price']"
            ]
            
            for selector in current_price_selectors:
                elements = await page.query_selector_all(selector)
                for i, element in enumerate(elements):
                    text = await element.inner_text()
                    print(f"Current Price {selector} {i+1}: {text}")

            # İndirimsiz fiyat
            original_price_selectors = [
                "div.ETYrVpXSa3c1UlXVAjTK div.tNv_XWzIy14eaJxLI5K9 span.uY6qgF91fGtRUWsRau94",
                "div[class*='ETYrVpXSa3c1UlXVAjTK'] div[class*='tNv_XWzIy14eaJxLI5K9'] span[class*='uY6qgF91fGtRUWsRau94']",
                "[data-test-id='prev-price']",
                ".prev-price",
                "[class*='prev-price']",
                "span[class*='prev-price']"
            ]
            
            for selector in original_price_selectors:
                elements = await page.query_selector_all(selector)
                for i, element in enumerate(elements):
                    text = await element.inner_text()
                    print(f"Original Price {selector} {i+1}: {text}")

            print("\n=== GÖRSEL ELEMENTLERİ ===")
            image_selectors = [
                "img.i9jTSpEeoI29_M1mOKct.hb-HbImage-view__image",
                "img[class*='i9jTSpEeoI29_M1mOKct']",
                "img[class*='hb-HbImage-view__image']",
                "img[alt*='product']",
                "img[src*='productimages.hepsiburada.net']",
                "img[class*='product-image']"
            ]
            
            for selector in image_selectors:
                elements = await page.query_selector_all(selector)
                for i, element in enumerate(elements):
                    src = await element.get_attribute("src")
                    alt = await element.get_attribute("alt")
                    print(f"Image {selector} {i+1}: src={src}, alt={alt}")

            print("\n=== TÜM FİYAT ELEMENTLERİ ===")
            all_price_elements = await page.query_selector_all("[class*='price'], [class*='Price'], span:contains('₺'), span:contains('TL')")
            for i, element in enumerate(all_price_elements):
                text = await element.inner_text()
                class_attr = await element.get_attribute("class")
                print(f"Price Element {i+1}: {text} (class: {class_attr})")

            print("\n=== SAYFA HTML'İ ===")
            html = await page.content()
            print(html[:2000])  # İlk 2000 karakter

            input("Devam etmek için Enter'a basın...")

        except Exception as e:
            print(f"Hata: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_hepsiburada_page())
