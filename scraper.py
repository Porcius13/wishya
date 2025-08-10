import asyncio
import logging
import re
from urllib.parse import urlparse
from playwright.async_api import async_playwright

logging.basicConfig(level=logging.DEBUG)

# Site bazlı selector havuzu
SITE_SELECTORS = {
    "hepsiburada.com": {
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
        "price": [
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
        "brand": ["Hepsiburada"]
    },
    "sahibinden.com": {
        "title": [
            "h1",  # Ana başlık
            ".classified-title h1",
            "[class*='title'] h1",
            "h1[class*='title']"
        ],
        "price": [
            ".classified-price-wrapper",  # Ana fiyat wrapper
            ".classified-price",
            "[class*='price']",
            "span[class*='price']",
            ".price-wrapper"
        ],
        "image": [
            "img.s-image",  # Ana görsel
            "img.stdImg",
            "img[class*='s-image']",
            "img[class*='stdImg']",
            "label img",
            "img[src*='shbdn.com']"
        ],
        "brand": ["UNKNOWN"]  # Marka başlıktan tespit edilecek
    },
    "zara.com": {
        "title": [
            "h1[data-qa-action='product-name']",
            "h1.product-name",
            "h1",
            "[data-testid='product-name']",
            ".product-name",
            "h1[class*='product']",
            "[class*='product-name']",
            "[class*='title']",
            "h1 span",
            "h1"
        ],
        "price": [
            "span[data-qa-action='price-current']",
            ".price-current",
            "[data-testid='price']",
            ".price",
            "[class*='price']",
            "span[class*='price']",
            ".product-price",
            "[data-qa-action='price']",
            "span:contains('₺')",
            "span:contains('TL')"
        ],
        "image": [
            "img[data-qa-action='product-image']",
            "img.product-image",
            "img[loading='lazy']",
            "img[class*='product']",
            "img[class*='image']",
            "img[alt*='product']",
            "img[src*='product']",
            "img"
        ],
        "brand": ["ZARA"]
    },
    "mango.com": {
        "title": [
            "h1.product-name",
            "h1",
            "[data-testid='product-name']",
            ".product-name",
            "[class*='product-name']",
            "h1 span"
        ],
        "price": [
            ".product-price",
            "[data-testid='price']",
            ".price",
            "[class*='price']",
            "span[class*='price']"
        ],
        "image": [
            "img.product-image",
            "img[loading='lazy']",
            "img[class*='product']",
            "img[class*='image']",
            "img"
        ],
        "brand": ["MANGO"]
    },
    "hm.com": {
        "title": [
            "h1.product-name",
            "h1",
            "[data-testid='product-name']",
            ".product-name",
            "[class*='product-name']"
        ],
        "price": [
            ".product-price",
            "[data-testid='price']",
            ".price",
            "[class*='price']"
        ],
        "image": [
            "img.product-image",
            "img[loading='lazy']",
            "img[class*='product']",
            "img"
        ],
        "brand": ["H&M"]
    }
}

def get_site_selectors(url):
    """URL'den site tespiti yaparak uygun selector'ları döndürür"""
    domain = urlparse(url).netloc.lower()
    
    for site, selectors in SITE_SELECTORS.items():
        if site in domain:
            return selectors
    
    # Varsayılan selector'lar
    return {
        "title": ["h1", "[data-testid='product-name']", ".product-name"],
        "price": ["[data-testid='price']", ".price", "span[data-testid='price']"],
        "image": ["img[loading='lazy']", "img"],
        "brand": ["UNKNOWN"]
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

async def fetch_data(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            await page.goto(url, wait_until="networkidle", timeout=60000)
            await page.wait_for_timeout(5000)

            # Site bazlı selector'ları al
            selectors = get_site_selectors(url)
            domain = urlparse(url).netloc.lower()
            
            # Sayfanın yüklenmesini bekle
            await page.wait_for_load_state("domcontentloaded")
            
            # Veri çekme
            title = await extract_with_fallback(page, selectors["title"])
            price = await extract_with_fallback(page, selectors["price"])
            image = await extract_with_fallback(page, selectors["image"], "src")
            brand = selectors["brand"][0] if selectors["brand"] else "UNKNOWN"

            # Hepsiburada.com için özel işlemler
            if "hepsiburada.com" in domain:
                # İndirimsiz fiyatı da çek
                original_price = await extract_with_fallback(page, selectors.get("original_price", []))
                
                # Fiyat temizleme (Hepsiburada için)
                if price:
                    # TL, ₺ ve boşlukları kaldır, virgülü noktaya çevir
                    price_clean = re.sub(r'[^\d.,]', '', price)
                    price_clean = price_clean.replace(',', '.')
                    if price_clean:
                        price = price_clean
                
                if original_price:
                    # TL, ₺ ve boşlukları kaldır, virgülü noktaya çevir
                    original_price_clean = re.sub(r'[^\d.,]', '', original_price)
                    original_price_clean = original_price_clean.replace(',', '.')
                    if original_price_clean:
                        original_price = original_price_clean
                
                # Marka tespiti (başlıktan)
                if title:
                    common_brands = ["APPLE", "SAMSUNG", "XIAOMI", "HUAWEI", "OPPO", "VIVO", "REALME", "ONEPLUS", "GOOGLE", "NOKIA", "SONY", "LG", "ASUS", "ACER", "LENOVO", "DELL", "HP", "MSI", "RAZER", "LOGITECH", "STEELSERIES", "CORSAIR", "KINGSTON", "SANDISK", "WESTERN DIGITAL", "SEAGATE", "TOSHIBA", "INTEL", "AMD", "NVIDIA", "GIGABYTE", "ASROCK", "MSI", "EVGA", "THERMALTAKE", "COOLER MASTER", "NOCTUA", "BE QUIET", "SEASONIC", "CORSAIR", "EVGA", "THERMALTAKE", "COOLER MASTER", "NOCTUA", "BE QUIET", "SEASONIC", "GIPTA", "MOLESKINE", "LEUCHTTURM", "RHODIA", "CLAIREFONTAINE", "EXACOMPTA", "OXFORD", "PAPERBLANKS", "PETER PAUPER", "QUO VADIS", "SILVER POINT", "STAPLES", "TARGET", "WALMART", "AMAZON", "ALIEXPRESS", "BANGGOOD", "GEARBEST", "LIGHTINTHEBOX", "SHEIN", "WISH", "TEMU"]
                    for brand_name in common_brands:
                        if brand_name in title.upper():
                            brand = brand_name
                            break
            
            # Sahibinden.com için özel işlemler
            elif "sahibinden.com" in domain:
                # Fiyat temizleme (sahibinden.com için)
                if price:
                    # Binlik ayırıcıları kaldır
                    price_clean = re.sub(r'[^\d.,]', '', price)
                    price_clean = price_clean.replace('.', '').replace(',', '.')
                    if price_clean:
                        price = price_clean
                
                # Marka tespiti (başlıktan)
                if title:
                    common_brands = ["LADA", "BMW", "MERCEDES", "AUDI", "VOLKSWAGEN", "FORD", "RENAULT", "FIAT", "TOYOTA", "HONDA", "HYUNDAI", "KIA", "NISSAN", "MAZDA", "SUBARU", "MITSUBISHI", "OPEL", "PEUGEOT", "CITROEN", "SKODA", "SEAT", "VOLVO", "SAAB", "JAGUAR", "LAND ROVER", "RANGE ROVER", "MINI", "ALFA ROMEO", "MASERATI", "FERRARI", "LAMBORGHINI", "PORSCHE", "ASTON MARTIN", "BENTLEY", "ROLLS ROYCE", "LEXUS", "INFINITI", "ACURA", "BUICK", "CADILLAC", "CHEVROLET", "CHRYSLER", "DODGE", "JEEP", "LINCOLN", "PONTIAC", "SATURN", "SCION", "SMART", "SUZUKI", "DAIHATSU", "ISUZU", "MAHINDRA", "TATA", "MG", "ROVER", "VAUXHALL", "VAZ", "GAZ", "UAZ", "ZAZ", "MOSKVICH", "IZH", "KAMAZ", "URAL", "ZIL", "MAZ", "KRAZ", "BELAZ", "KAMAZ", "URAL", "ZIL", "MAZ", "KRAZ", "BELAZ"]
                    for brand_name in common_brands:
                        if brand_name in title.upper():
                            brand = brand_name
                            break
            else:
                # Diğer siteler için standart fiyat temizleme
                if price:
                    # Sadece sayıları ve nokta/virgül al
                    price_clean = re.sub(r'[^\d.,]', '', price)
                    if price_clean:
                        price = price_clean
                else:
                    # Alternatif fiyat arama
                    try:
                        price_elements = await page.query_selector_all("[class*='price'], [class*='Price'], span:contains('₺'), span:contains('TL')")
                        for element in price_elements:
                            text = await element.inner_text()
                            if text and any(char.isdigit() for char in text):
                                price_clean = re.sub(r'[^\d.,]', '', text)
                                if price_clean:
                                    price = price_clean
                                    break
                    except Exception as e:
                        logging.debug(f"[DEBUG] Alternatif fiyat arama başarısız: {e}")

            # Başlık temizleme ve büyük harf
            if title:
                title = title.upper()
            else:
                # Alternatif başlık arama
                try:
                    title_elements = await page.query_selector_all("h1, h2, [class*='title'], [class*='Title'], [class*='product'], [class*='Product']")
                    for element in title_elements:
                        text = await element.inner_text()
                        if text and len(text.strip()) > 5:
                            title = text.strip().upper()
                            break
                except Exception as e:
                    logging.debug(f"[DEBUG] Alternatif başlık arama başarısız: {e}")

            # Marka adını büyük harf yap
            brand = brand.upper()
            
            # Görsel için alternatif arama
            if not image:
                try:
                    img_elements = await page.query_selector_all("img[src*='product'], img[src*='image'], img[alt*='product'], img[class*='product'], img[class*='image']")
                    for img in img_elements:
                        src = await img.get_attribute("src")
                        if src and ("product" in src.lower() or "image" in src.lower()):
                            image = src
                            break
                except Exception as e:
                    logging.debug(f"[DEBUG] Alternatif görsel arama başarısız: {e}")
            
            # Sahibinden.com için görsel kalitesini artır
            if image and "shbdn.com" in image:
                # Orijinal boyut için parametreleri kaldır
                base_url = image.split('?')[0] if '?' in image else image
                image = base_url
                logging.debug(f"[DEBUG] Sahibinden.com görsel kalitesi artırıldı: {image}")
            
            # PullandBear için görsel kalitesini artır
            elif image and ("pullandbear.net" in image or "pullandbear.com" in image):
                # Mevcut parametreleri kontrol et ve yüksek kalite için güncelle
                if "w=" in image and "f=auto" in image:
                    # Genişliği artır ve formatı optimize et
                    image = re.sub(r'w=\d+', 'w=2000', image)
                    image = re.sub(r'f=auto', 'f=webp', image)
                    logging.debug(f"[DEBUG] PullandBear görsel kalitesi artırıldı (scraper): {image}")
                elif "w=" in image:
                    # Sadece genişliği artır
                    image = re.sub(r'w=\d+', 'w=2000', image)
                    logging.debug(f"[DEBUG] PullandBear görsel genişliği artırıldı (scraper): {image}")
                elif "f=auto" in image:
                    # Sadece formatı optimize et
                    image = re.sub(r'f=auto', 'f=webp', image)
                    logging.debug(f"[DEBUG] PullandBear görsel formatı optimize edildi (scraper): {image}")
                else:
                    # Parametre yoksa ekle
                    if "?" in image:
                        image += "&w=2000&f=webp"
                    else:
                        image += "?w=2000&f=webp"
                    logging.debug(f"[DEBUG] PullandBear görsel parametreleri eklendi (scraper): {image}")

            result = {
                "title": title,
                "image": image,
                "price": price,
                "brand": brand,
                "url": url
            }
            
            # Hepsiburada için indirimsiz fiyat ekle
            if "hepsiburada.com" in domain and 'original_price' in locals():
                result["original_price"] = original_price

            logging.info(f"[BAŞARILI] {url} - {title}")
            return result

        except Exception as e:
            logging.error(f"[HATA] Veri çekilemedi: {url} - {e}")
            return None
        finally:
            await browser.close()

def scrape_product(url):
    """3 deneme ile ürün verisi çekme"""
    # Hepsiburada için Selenium kullan
    domain = urlparse(url).netloc.lower()
    if "hepsiburada.com" in domain:
        try:
            from selenium_hepsiburada_scraper import scrape_hepsiburada_product
            return scrape_hepsiburada_product(url)
        except ImportError:
            logging.warning("[UYARI] Selenium scraper bulunamadı, Playwright kullanılıyor")
    
    # Diğer siteler için Playwright kullan
    for i in range(3):
        try:
            logging.debug(f"[DEBUG] Deneme {i+1}/3 - {url}")
            result = asyncio.run(fetch_data(url))
            if result:
                return result
        except Exception as e:
            logging.debug(f"[DEBUG] Hata {i+1}: {e}")
    
    logging.error(f"[HATA] Tüm denemeler başarısız: {url}")
    return None
