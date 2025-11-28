import asyncio
import logging
import re
import json
from urllib.parse import urlparse
from playwright.async_api import async_playwright

logging.basicConfig(level=logging.DEBUG)

# Site bazlı selector havuzu
SITE_SELECTORS = {
    "zara.com": {
        "title": [
            "h1[data-qa-action='product-name']",
            "h1.product-name",
            "h1",
            "[data-testid='product-name']",
            ".product-name"
        ],
        "price": [
            "span[data-qa-action='price-current']",
            ".price-current",
            "[data-testid='price']",
            ".product-price"
        ],
        "image": [
            "img[data-qa-action='product-image']",
            "img.product-image",
            "img[loading='lazy']"
        ],
        "brand": ["ZARA"]
    },
    "mango.com": {
        "title": ["h1.product-name", "h1", "[data-testid='product-name']"],
        "price": [".product-price", "[data-testid='price']", ".price"],
        "image": ["img.product-image", "img[loading='lazy']"],
        "brand": ["MANGO"]
    },
    "hm.com": {
        "title": ["h1.product-name", "h1", "[data-testid='product-name']"],
        "price": [".product-price", "[data-testid='price']", ".price"],
        "image": ["img.product-image", "img[loading='lazy']"],
        "brand": ["H&M"]
    },
    "nike.com": {
        "title": ["h1[id='pdp_product_title']", "h1", "[data-testid='product-title']"],
        "price": ["[data-testid='currentPrice-container']", ".product-price", "[data-testid='price']"],
        "image": ["img[data-testid='hero-image']", "img[src*='static.nike.com']", "img"],
        "brand": ["NIKE"]
    },
    "bershka.com": {
        "title": ["h1.product-title", "h1"],
        "price": [".current-price-elem", ".price-elem"],
        "image": ["img.image-item", "img"],
        "brand": ["BERSHKA"]
    },
    "amazon": {
        "title": ["#productTitle", "#title", "span#productTitle"],
        "price": [
            ".a-price .a-offscreen", 
            "#priceblock_ourprice", 
            "#priceblock_dealprice", 
            "#corePrice_feature_div .a-offscreen",
            "#corePriceDisplay_desktop_feature_div .a-offscreen",
            ".a-price"
        ],
        "image": ["#landingImage", "#imgTagWrapperId img", "#main-image", "img[data-a-image-name]"],
        "brand": ["#bylineInfo", "#brand", "a#bylineInfo"]
    },
    "teknosa.com": {
        "title": ["h1.pdp-title", "h1.product-title", "h1"],
        "price": [
            ".pdp-price .price", 
            ".price-tag", 
            ".current-price", 
            ".product-price",
            "div[class*='price']"
        ],
        "image": ["#pdp-main-image", ".pdp-image img", "img.pdp-image"],
        "brand": ["b.pdp-brand", ".pdp-brand a", ".brand-name"]
    },
    "adidas.com.tr": {
        "title": ["h1[data-auto-id='product-title']", "h1.gl-heading", "h1"],
        "price": [".gl-price-item", ".gl-price", ".product-price"],
        "image": ["img[data-auto-id='image']", "img.product-image", "div.image-carousel img"],
        "brand": ["ADIDAS"]
    }
}

async def extract_jsonld(page):
    """JSON-LD verisini çeker"""
    try:
        return await page.evaluate('''() => {
            const scripts = document.querySelectorAll('script[type="application/ld+json"]');
            for (const script of scripts) {
                try {
                    const json = JSON.parse(script.innerText);
                    
                    // Direkt Product objesi
                    if (json['@type'] === 'Product') return json;
                    
                    // Array içinde Product
                    if (Array.isArray(json)) {
                        const product = json.find(i => i['@type'] === 'Product');
                        if (product) return product;
                    }
                    
                    // Graph içinde Product
                    if (json['@graph']) {
                        const product = json['@graph'].find(i => i['@type'] === 'Product');
                        if (product) return product;
                    }
                } catch (e) {}
            }
            return null;
        }''')
    except Exception as e:
        logging.debug(f"JSON-LD extraction failed: {e}")
        return None

async def extract_meta_tags(page):
    """Meta tag ve OG tag verilerini çeker"""
    return await page.evaluate('''() => {
        const data = {};
        
        // Title
        const ogTitle = document.querySelector('meta[property="og:title"]');
        if (ogTitle) data.title = ogTitle.content;
        
        // Image
        const ogImage = document.querySelector('meta[property="og:image"]');
        if (ogImage) data.image = ogImage.content;
        
        // Price
        const priceAmount = document.querySelector('meta[property="product:price:amount"]');
        if (priceAmount) data.price = priceAmount.content;
        
        const price = document.querySelector('meta[name="price"]');
        if (price && !data.price) data.price = price.content;
        
        return data;
    }''')

async def extract_decathlon_data(page):
    """Decathlon özel veri çekme (window.__DKT)"""
    return await page.evaluate('''() => {
        try {
            if (window.__DKT && window.__DKT._ctx && window.__DKT._ctx.data) {
                const supermodel = window.__DKT._ctx.data.find(item => item.type === 'Supermodel');
                if (supermodel && supermodel.data) {
                    const modelData = supermodel.data.models ? supermodel.data.models[0] : null;
                    if (modelData) {
                        let price = null;
                        if (modelData.skus && modelData.skus.length > 0) {
                            price = modelData.skus[0].price;
                        }
                        return {
                            title: modelData.webLabel,
                            image: modelData.image ? modelData.image.url : null,
                            price: price,
                            brand: supermodel.data.brand ? supermodel.data.brand.label : "DECATHLON"
                        };
                    }
                }
            }
        } catch (e) { return null; }
        return null;
    }''')

async def extract_teknosa_data(page):
    """Teknosa özel veri çekme (window.insider_object)"""
    return await page.evaluate('''() => {
        try {
            if (window.insider_object && window.insider_object.product) {
                const p = window.insider_object.product;
                return {
                    title: p.name,
                    price: p.unit_price || p.unit_sale_price,
                    image: p.product_image_url,
                    brand: null // Markayı generic extractor'a bırak
                };
            }
        } catch (e) { return null; }
        return null;
    }''')

def get_site_selectors(url):
    domain = urlparse(url).netloc.lower()
    for site, selectors in SITE_SELECTORS.items():
        if site in domain:
            return selectors
    return None

try:
    from playwright_stealth import Stealth
except ImportError:
    Stealth = None

async def fetch_data(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-infobars',
                '--window-position=0,0',
                '--ignore-certificate-errors',
                '--ignore-certificate-errors-spki-list',
                '--disable-accelerated-2d-canvas',
                '--no-zygote',
                '--no-first-run',
                '--disable-gpu',
                '--disable-blink-features=AutomationControlled'
            ]
        )
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="tr-TR",
            timezone_id="Europe/Istanbul",
            extra_http_headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
                "Referer": "https://www.google.com/",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": '"Windows"',
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "cross-site",
                "Sec-Fetch-User": "?1"
            }
        )
        
        # Anti-detection scripts
        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        await context.add_init_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
        await context.add_init_script("Object.defineProperty(navigator, 'languages', {get: () => ['tr-TR', 'tr', 'en-US', 'en']})")
        
        page = await context.new_page()
        
        # Apply stealth if available
        if Stealth:
            await Stealth().apply_stealth_async(page)

        try:
            logging.info(f"Navigating to {url}")
            
            # Adidas ve Zara için özel timeout ve wait stratejisi
            if "adidas.com" in url or "zara.com" in url:
                await page.goto(url, wait_until="domcontentloaded", timeout=90000)
                try:
                    await page.wait_for_load_state("networkidle", timeout=30000)
                except:
                    pass
            else:
                await page.goto(url, wait_until="domcontentloaded", timeout=90000)
            
            # Rastgele bekleme
            import random
            await page.wait_for_timeout(random.randint(3000, 7000))

            result = {
                "title": None,
                "price": None,
                "original_price": None,
                "discount_message": None,
                "image": None,
                "brand": None,
                "url": url
            }

            # 1. Decathlon Özel Kontrolü
            if "decathlon" in url:
                decathlon_data = await extract_decathlon_data(page)
                if decathlon_data:
                    logging.info("Decathlon data found via window object")
                    result.update(decathlon_data)
                    # Decathlon verisi genelde tamdır, dönülebilir
                    if result["title"] and result["price"]:
                        return result
            
            # 2. Teknosa Özel Kontrolü
            if "teknosa" in url:
                teknosa_data = await extract_teknosa_data(page)
                if teknosa_data:
                    logging.info("Teknosa data found via window object")
                    # Mevcut result ile birleştir (None olmayanları al)
                    for k, v in teknosa_data.items():
                        if v: result[k] = v

            # 3. JSON-LD Kontrolü (En güvenilir kaynak)
            json_data = await extract_jsonld(page)
            if json_data:
                logging.info("JSON-LD data found")
                if not result["title"]:
                    result["title"] = json_data.get("name")
                
                if not result["image"]:
                    img = json_data.get("image")
                    if isinstance(img, list):
                        result["image"] = img[0]
                    elif isinstance(img, dict):
                        result["image"] = img.get("url")
                    else:
                        result["image"] = img
                
                if not result["price"]:
                    offers = json_data.get("offers")
                    if offers:
                        if isinstance(offers, list):
                            result["price"] = offers[0].get("price")
                        elif isinstance(offers, dict):
                            result["price"] = offers.get("price")
                            if offers.get("@type") == "AggregateOffer":
                                result["original_price"] = offers.get("highPrice")
                
                if not result["brand"]:
                    brand_data = json_data.get("brand")
                    if brand_data:
                        if isinstance(brand_data, dict):
                            result["brand"] = brand_data.get("name")
                        else:
                            result["brand"] = brand_data

            # 4. Meta Tags / OG Tags Kontrolü
            if not result["title"] or not result["price"] or not result["image"]:
                meta_data = await extract_meta_tags(page)
                if meta_data:
                    if not result["title"] and meta_data.get("title"):
                        result["title"] = meta_data["title"]
                    if not result["image"] and meta_data.get("image"):
                        result["image"] = meta_data["image"]
                    if not result["price"] and meta_data.get("price"):
                        result["price"] = meta_data["price"]

            # 5. DOM Selectors (Site bazlı veya fallback)
            selectors = get_site_selectors(url)
            if not selectors:
                selectors = {
                    "title": ["h1", "[data-testid='product-name']", ".product-name", "title"],
                    "price": ["[data-testid='price']", ".price", "span[class*='price']"],
                    "original_price": ["del", ".old-price", "[data-testid='original-price']", "span[class*='old']", "span[class*='original']"],
                    "image": ["img[loading='lazy']", "img"],
                    "brand": ["UNKNOWN"]
                }
            else:
                if "original_price" not in selectors:
                    selectors["original_price"] = ["del", ".old-price", "[data-testid='original-price']", "span[class*='old']"]

            # Eksik verileri DOM'dan çekmeye çalış
            if not result["title"]:
                for sel in selectors["title"]:
                    try:
                        el = await page.query_selector(sel)
                        if el:
                            text = await el.inner_text()
                            if text:
                                result["title"] = text.strip()
                                break
                    except: continue

            if not result["price"]:
                for sel in selectors["price"]:
                    try:
                        el = await page.query_selector(sel)
                        if el:
                            text = await el.inner_text()
                            if text:
                                result["price"] = text.strip()
                                break
                    except: continue
            
            # Original Price (İndirimsiz Fiyat) Arama
            if not result["original_price"]:
                for sel in selectors["original_price"]:
                    try:
                        el = await page.query_selector(sel)
                        if el:
                            text = await el.inner_text()
                            if text:
                                result["original_price"] = text.strip()
                                break
                    except: continue

            # Kampanya / Sepette İndirim Mesajı Arama (Geniş Kapsamlı)
            try:
                # Tüm sayfa metnini çek
                page_text = await page.evaluate("document.body.innerText")
                
                # Satır satır incele
                lines = page_text.split('\n')
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                        
                    lower_line = line.lower()
                    # Anahtar kelimeler: sepette, sepete özel, sepet fiyatı
                    if "sepette" in lower_line or "sepete özel" in lower_line:
                        # Çok uzun metinleri ele
                        if len(line) < 150:
                            # Eğer içinde rakam varsa (fiyat belirtiyorsa) daha değerli
                            if any(char.isdigit() for char in line):
                                result["discount_message"] = line
                                break
                            # Henüz mesaj bulamadıysak bunu tut
                            if not result["discount_message"]:
                                result["discount_message"] = line
            except Exception as e:
                logging.debug(f"Deep campaign extraction failed: {e}")

            if not result["image"]:
                for sel in selectors["image"]:
                    try:
                        el = await page.query_selector(sel)
                        if el:
                            src = await el.get_attribute("src")
                            if src:
                                result["image"] = src
                                break
                    except: continue

            if not result["brand"]:
                for sel in selectors.get("brand", []):
                    # Eğer selector bir CSS selector değil de direkt marka adıysa (örn: "ZARA")
                    # CSS selector karakterleri: . # [ ] > + :
                    if not any(c in sel for c in [".", "#", "[", "]", ">", "+", ":"]):
                        result["brand"] = sel
                        break
                        
                    try:
                        el = await page.query_selector(sel)
                        if el:
                            text = await el.inner_text()
                            if text:
                                # "Brand: Puma" gibi textleri temizle
                                clean_text = text.replace("Marka:", "").replace("Brand:", "").strip()
                                if clean_text:
                                    result["brand"] = clean_text
                                    break
                    except: continue

            if not result["brand"]:
                # Domain'den marka çıkar
                domain = urlparse(url).netloc
                if "amazon" in domain:
                    result["brand"] = "AMAZON"
                elif "trendyol" in domain:
                    result["brand"] = "TRENDYOL"
                elif "hepsiburada" in domain:
                    result["brand"] = "HEPSIBURADA"
                else:
                    result["brand"] = domain.replace("www.", "").split(".")[0].upper()

            # Son Temizlik ve Formatlama
            if result["title"]:
                result["title"] = result["title"].strip().upper()
            
            if result["price"]:
                result["price"] = str(result["price"]).strip()
            
            if result["original_price"]:
                result["original_price"] = str(result["original_price"]).strip()
                if result["original_price"] == result["price"]:
                    result["original_price"] = None

            logging.info(f"Scraping result: {result}")
            return result

        except Exception as e:
            logging.error(f"Error scraping {url}: {e}")
            return None
        finally:
            await browser.close()

def scrape_product(url):
    """Main entry point - 3 deneme hakkı"""
    for i in range(3):
        try:
            logging.debug(f"Attempt {i+1}/3 - {url}")
            result = asyncio.run(fetch_data(url))
            if result and result.get("title"): # En azından başlık olmalı
                return result
        except Exception as e:
            logging.debug(f"Attempt {i+1} failed: {e}")
            # Son deneme değilse bekle
            if i < 2:
                import time
                time.sleep(2)
    
    logging.error(f"All attempts failed for {url}")
    return None
