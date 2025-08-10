#!/usr/bin/env python3
"""
Basit Hepsiburada Scraper
"""

import asyncio
import logging
import re
from playwright.async_api import async_playwright

logging.basicConfig(level=logging.INFO)

async def scrape_hepsiburada_simple(url):
    """Hepsiburada'dan basit veri çekme"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        try:
            print(f"Sayfa yükleniyor: {url}")
            await page.goto(url, wait_until="networkidle", timeout=60000)
            await page.wait_for_timeout(3000)

            # Başlık çekme
            title = ""
            try:
                # Önce h1 elementlerini dene
                h1_elements = await page.query_selector_all("h1")
                for h1 in h1_elements:
                    text = await h1.inner_text()
                    if text and len(text.strip()) > 5:
                        title = text.strip()
                        break
                
                # H1 bulunamazsa diğer başlık elementlerini dene
                if not title:
                    title_elements = await page.query_selector_all("[class*='title'], [class*='product-name'], [data-testid*='product']")
                    for element in title_elements:
                        text = await element.inner_text()
                        if text and len(text.strip()) > 5:
                            title = text.strip()
                            break
            except Exception as e:
                print(f"Başlık çekme hatası: {e}")

            # Fiyat çekme
            current_price = ""
            original_price = ""
            
            try:
                # Tüm fiyat elementlerini bul
                price_elements = await page.query_selector_all("span, div")
                for element in price_elements:
                    text = await element.inner_text()
                    if text and ("₺" in text or "TL" in text) and any(char.isdigit() for char in text):
                        # Fiyat temizleme
                        price_clean = re.sub(r'[^\d.,]', '', text)
                        if price_clean:
                            # İlk bulunan fiyatı mevcut fiyat olarak al
                            if not current_price:
                                current_price = price_clean.replace(',', '.')
                            # İkinci bulunan fiyatı indirimsiz fiyat olarak al
                            elif not original_price and price_clean != current_price.replace('.', ','):
                                original_price = price_clean.replace(',', '.')
                                break
            except Exception as e:
                print(f"Fiyat çekme hatası: {e}")

            # Görsel çekme
            image = ""
            try:
                # Hepsiburada görsel URL'lerini ara
                img_elements = await page.query_selector_all("img[src*='productimages.hepsiburada.net']")
                for img in img_elements:
                    src = await img.get_attribute("src")
                    if src and "productimages.hepsiburada.net" in src:
                        # Orijinal boyut için parametreleri kaldır
                        base_url = src.split('?')[0] if '?' in src else src
                        image = base_url
                        break
                
                # Eğer bulunamazsa diğer görselleri dene
                if not image:
                    img_elements = await page.query_selector_all("img[class*='product'], img[class*='image']")
                    for img in img_elements:
                        src = await img.get_attribute("src")
                        if src and ("product" in src.lower() or "image" in src.lower()):
                            image = src
                            break
            except Exception as e:
                print(f"Görsel çekme hatası: {e}")

            # Marka tespiti
            brand = "Hepsiburada"
            if title:
                common_brands = ["GIPTA", "MOLESKINE", "LEUCHTTURM", "RHODIA", "CLAIREFONTAINE", "EXACOMPTA", "OXFORD", "PAPERBLANKS", "PETER PAUPER", "QUO VADIS", "SILVER POINT", "STAPLES", "TARGET", "WALMART", "AMAZON", "ALIEXPRESS", "BANGGOOD", "GEARBEST", "LIGHTINTHEBOX", "SHEIN", "WISH", "TEMU", "APPLE", "SAMSUNG", "XIAOMI", "HUAWEI", "OPPO", "VIVO", "REALME", "ONEPLUS", "GOOGLE", "NOKIA", "SONY", "LG", "ASUS", "ACER", "LENOVO", "DELL", "HP", "MSI", "RAZER", "LOGITECH", "STEELSERIES", "CORSAIR", "KINGSTON", "SANDISK", "WESTERN DIGITAL", "SEAGATE", "TOSHIBA", "INTEL", "AMD", "NVIDIA", "GIGABYTE", "ASROCK", "MSI", "EVGA", "THERMALTAKE", "COOLER MASTER", "NOCTUA", "BE QUIET", "SEASONIC"]
                for brand_name in common_brands:
                    if brand_name in title.upper():
                        brand = brand_name
                        break

            result = {
                "title": title,
                "current_price": current_price,
                "original_price": original_price,
                "image": image,
                "brand": brand,
                "url": url,
                "site": "hepsiburada.com"
            }

            print(f"✅ Başarılı! Başlık: {title}")
            return result

        except Exception as e:
            print(f"❌ Hata: {e}")
            return None
        finally:
            await browser.close()

def scrape_hepsiburada_product(url):
    """3 deneme ile Hepsiburada ürün verisi çekme"""
    for i in range(3):
        try:
            print(f"Deneme {i+1}/3...")
            result = asyncio.run(scrape_hepsiburada_simple(url))
            if result and result.get("title"):
                return result
        except Exception as e:
            print(f"Hata {i+1}: {e}")
    
    print("Tüm denemeler başarısız!")
    return None

# Test
if __name__ == "__main__":
    test_url = "https://www.hepsiburada.com/gipta-pera-ciltli-deri-kapak-9x14-cizgisiz-defter-pm-HBC00002QG0EE"
    result = scrape_hepsiburada_product(test_url)
    print("\n=== SONUÇ ===")
    print(result)
