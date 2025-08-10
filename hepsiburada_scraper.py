import asyncio
import logging
import re
from urllib.parse import urlparse
from playwright.async_api import async_playwright

logging.basicConfig(level=logging.DEBUG)

# Hepsiburada özel selector'ları
HEPSIBURADA_SELECTORS = {
    "title": [
        "h1[data-test-id='product-name']",
        "h1.product-name",
        "h1",
        "[data-testid='product-name']",
        ".product-name",
        "h1[class*='product']",
        "[class*='product-name']",
        "[class*='title']"
    ],
    "current_price": [
        "div.z7kokklsVwh0K5zFWjIO.nUoGYtEwzHyrjX2lvABI span",
        "div[class*='z7kokklsVwh0K5zFWjIO'] span",
        "[data-test-id='price-current']",
        ".price-current",
        "[class*='price'] span",
        "span[class*='price']"
    ],
    "original_price": [
        "div.ETYrVpXSa3c1UlXVAjTK div.tNv_XWzIy14eaJxLI5K9 span.uY6qgF91fGtRUWsRau94",
        "div[class*='ETYrVpXSa3c1UlXVAjTK'] div[class*='tNv_XWzIy14eaJxLI5K9'] span[class*='uY6qgF91fGtRUWsRau94']",
        "[data-test-id='prev-price']",
        ".prev-price",
        "[class*='prev-price']",
        "span[class*='prev-price']"
    ],
    "image": [
        "img.i9jTSpEeoI29_M1mOKct.hb-HbImage-view__image",
        "img[class*='i9jTSpEeoI29_M1mOKct']",
        "img[class*='hb-HbImage-view__image']",
        "img[alt*='product']",
        "img[src*='productimages.hepsiburada.net']",
        "img[class*='product-image']",
        "img"
    ],
    "brand": ["Hepsiburada"]  # Varsayılan marka
}

async def extract_with_fallback(page, selectors, attribute="innerText"):
    """Fallback'li veri çekme"""
    for selector in selectors:
        try:
            # Önce elementin var olup olmadığını kontrol et
            element = await page.query_selector(selector)
            if not element:
                continue
                
            if attribute == "innerText":
                result = await page.inner_text(selector)
            else:
                result = await page.get_attribute(selector, attribute)
            
            if result and result.strip():
                return result.strip()
        except Exception as e:
            logging.debug(f"[DEBUG] Selector başarısız: {selector} - {e}")
            continue
    
    return ""

async def fetch_hepsiburada_data(url):
    """Hepsiburada'dan ürün verisi çekme"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            await page.goto(url, wait_until="networkidle", timeout=60000)
            await page.wait_for_timeout(3000)

            # Sayfanın yüklenmesini bekle
            await page.wait_for_load_state("domcontentloaded")
            
            # Veri çekme
            title = await extract_with_fallback(page, HEPSIBURADA_SELECTORS["title"])
            current_price = await extract_with_fallback(page, HEPSIBURADA_SELECTORS["current_price"])
            original_price = await extract_with_fallback(page, HEPSIBURADA_SELECTORS["original_price"])
            image = await extract_with_fallback(page, HEPSIBURADA_SELECTORS["image"], "src")
            brand = HEPSIBURADA_SELECTORS["brand"][0]

            # Fiyat temizleme
            if current_price:
                # TL, ₺ ve boşlukları kaldır, virgülü noktaya çevir
                current_price_clean = re.sub(r'[^\d.,]', '', current_price)
                current_price_clean = current_price_clean.replace(',', '.')
                if current_price_clean:
                    current_price = current_price_clean

            if original_price:
                # TL, ₺ ve boşlukları kaldır, virgülü noktaya çevir
                original_price_clean = re.sub(r'[^\d.,]', '', original_price)
                original_price_clean = original_price_clean.replace(',', '.')
                if original_price_clean:
                    original_price = original_price_clean

            # Başlık temizleme
            if title:
                title = title.strip()

            # Görsel kalitesini artır
            if image and "productimages.hepsiburada.net" in image:
                # Orijinal boyut için parametreleri kaldır
                base_url = image.split('?')[0] if '?' in image else image
                image = base_url

            # Marka tespiti (başlıktan)
            if title:
                common_brands = ["APPLE", "SAMSUNG", "XIAOMI", "HUAWEI", "OPPO", "VIVO", "REALME", "ONEPLUS", "GOOGLE", "NOKIA", "SONY", "LG", "ASUS", "ACER", "LENOVO", "DELL", "HP", "MSI", "RAZER", "LOGITECH", "STEELSERIES", "CORSAIR", "KINGSTON", "SANDISK", "WESTERN DIGITAL", "SEAGATE", "TOSHIBA", "INTEL", "AMD", "NVIDIA", "GIGABYTE", "ASROCK", "MSI", "EVGA", "THERMALTAKE", "COOLER MASTER", "NOCTUA", "BE QUIET", "SEASONIC", "CORSAIR", "EVGA", "THERMALTAKE", "COOLER MASTER", "NOCTUA", "BE QUIET", "SEASONIC"]
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

            logging.info(f"[BAŞARILI] Hepsiburada - {url} - {title}")
            return result

        except Exception as e:
            logging.error(f"[HATA] Hepsiburada veri çekilemedi: {url} - {e}")
            return None
        finally:
            await browser.close()

def scrape_hepsiburada_product(url):
    """3 deneme ile Hepsiburada ürün verisi çekme"""
    for i in range(3):
        try:
            logging.debug(f"[DEBUG] Hepsiburada Deneme {i+1}/3 - {url}")
            result = asyncio.run(fetch_hepsiburada_data(url))
            if result:
                return result
        except Exception as e:
            logging.debug(f"[DEBUG] Hepsiburada Hata {i+1}: {e}")
    
    logging.error(f"[HATA] Tüm denemeler başarısız: {url}")
    return None

# Test fonksiyonu
if __name__ == "__main__":
    test_url = "https://www.hepsiburada.com/gipta-pera-ciltli-deri-kapak-9x14-cizgisiz-defter-pm-HBC00002QG0EE"
    result = scrape_hepsiburada_product(test_url)
    print("Hepsiburada Scraper Sonucu:")
    print(result)
