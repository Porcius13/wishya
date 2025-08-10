import asyncio
import logging
import re
import time
import json
from urllib.parse import urlparse
from playwright.async_api import async_playwright
from typing import Dict, List, Optional, Any
import random

# Logging ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class UniversalScraper:
    """
    Evrensel web scraping sistemi
    Yeni siteler için otomatik tespit ve fallback mekanizmaları
    """
    
    def __init__(self):
        # Site bazlı selector konfigürasyonları
        self.site_configs = {
            "hepsiburada.com": {
                "name": "Hepsiburada",
                "selectors": {
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
                    ]
                },
                "price_cleaner": self._clean_hepsiburada_price,
                "image_enhancer": self._enhance_hepsiburada_image,
                "brand_detector": self._detect_tech_brands,
                "wait_time": 3000,
                "timeout": 60000
            },
            
            "sahibinden.com": {
                "name": "Sahibinden",
                "selectors": {
                    "title": [
                        "h1",
                        ".classified-title h1",
                        "[class*='title'] h1",
                        "h1[class*='title']"
                    ],
                    "price": [
                        ".classified-price-wrapper",
                        ".classified-price",
                        "[class*='price']",
                        "span[class*='price']",
                        ".price-wrapper"
                    ],
                    "image": [
                        "img.s-image",
                        "img.stdImg",
                        "img[class*='s-image']",
                        "img[class*='stdImg']",
                        "label img",
                        "img[src*='shbdn.com']"
                    ],
                    "description": [
                        ".classified-info",
                        ".classified-description",
                        "[class*='description']",
                        ".info-list"
                    ]
                },
                "price_cleaner": self._clean_sahibinden_price,
                "image_enhancer": self._enhance_sahibinden_image,
                "brand_detector": self._detect_car_brands,
                "wait_time": 2000,
                "timeout": 30000
            },
            
            "zara.com": {
                "name": "Zara",
                "selectors": {
                    "title": [
                        "h1[data-qa-action='product-name']",
                        "h1.product-name",
                        "h1",
                        "[data-testid='product-name']",
                        ".product-name",
                        "h1[class*='product']",
                        "[class*='product-name']",
                        "[class*='title']"
                    ],
                    "price": [
                        "span[data-qa-action='price-current']",
                        ".price-current",
                        "[data-testid='price']",
                        ".price",
                        "[class*='price']",
                        "span[class*='price']"
                    ],
                    "image": [
                        "img[data-qa-action='product-image']",
                        "img.product-image",
                        "img[loading='lazy']",
                        "img[class*='product']",
                        "img[class*='image']",
                        "img[alt*='product']",
                        "img"
                    ]
                },
                "price_cleaner": self._clean_general_price,
                "image_enhancer": self._enhance_general_image,
                "brand_detector": lambda title: "ZARA",
                "wait_time": 3000,
                "timeout": 45000
            },
            
            "mango.com": {
                "name": "Mango",
                "selectors": {
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
                        "[class*='price']",
                        "span[class*='price']"
                    ],
                    "image": [
                        "img.product-image",
                        "img[loading='lazy']",
                        "img[class*='product']",
                        "img[class*='image']",
                        "img"
                    ]
                },
                "price_cleaner": self._clean_general_price,
                "image_enhancer": self._enhance_general_image,
                "brand_detector": lambda title: "MANGO",
                "wait_time": 3000,
                "timeout": 45000
            },
            
            "hm.com": {
                "name": "H&M",
                "selectors": {
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
                    ]
                },
                "price_cleaner": self._clean_general_price,
                "image_enhancer": self._enhance_general_image,
                "brand_detector": lambda title: "H&M",
                "wait_time": 3000,
                "timeout": 45000
            }
        }
        
        # Genel selector'lar (bilinmeyen siteler için)
        self.general_selectors = {
            "title": [
                "h1",
                "h1[class*='product']",
                "h1[class*='title']",
                "[data-testid='product-name']",
                "[data-qa-action='product-name']",
                ".product-name",
                ".product-title",
                "[class*='product-name']",
                "[class*='product-title']",
                "h2[class*='product']",
                "h2[class*='title']"
            ],
            "price": [
                "[data-testid='price']",
                "[data-qa-action='price']",
                ".price",
                ".product-price",
                "[class*='price']",
                "span[class*='price']",
                "div[class*='price']",
                "span:contains('₺')",
                "span:contains('TL')",
                "span:contains('$')",
                "span:contains('€')"
            ],
            "image": [
                "img[class*='product']",
                "img[class*='image']",
                "img[loading='lazy']",
                "img[alt*='product']",
                "img[src*='product']",
                "img[src*='image']",
                "img[data-testid='product-image']",
                "img[data-qa-action='product-image']",
                "img"
            ]
        }
        
        # Marka listeleri
        self.tech_brands = [
            "APPLE", "SAMSUNG", "XIAOMI", "HUAWEI", "OPPO", "VIVO", "REALME", "ONEPLUS", 
            "GOOGLE", "NOKIA", "SONY", "LG", "ASUS", "ACER", "LENOVO", "DELL", "HP", 
            "MSI", "RAZER", "LOGITECH", "STEELSERIES", "CORSAIR", "KINGSTON", "SANDISK", 
            "WESTERN DIGITAL", "SEAGATE", "TOSHIBA", "INTEL", "AMD", "NVIDIA", "GIGABYTE", 
            "ASROCK", "EVGA", "THERMALTAKE", "COOLER MASTER", "NOCTUA", "BE QUIET", 
            "SEASONIC", "GIPTA", "MOLESKINE", "LEUCHTTURM", "RHODIA", "CLAIREFONTAINE", 
            "EXACOMPTA", "OXFORD", "PAPERBLANKS", "PETER PAUPER", "QUO VADIS", "SILVER POINT"
        ]
        
        self.car_brands = [
            "LADA", "BMW", "MERCEDES", "AUDI", "VOLKSWAGEN", "FORD", "RENAULT", "FIAT", 
            "TOYOTA", "HONDA", "HYUNDAI", "KIA", "NISSAN", "MAZDA", "SUBARU", "MITSUBISHI", 
            "OPEL", "PEUGEOT", "CITROEN", "SKODA", "SEAT", "VOLVO", "SAAB", "JAGUAR", 
            "LAND ROVER", "RANGE ROVER", "MINI", "ALFA ROMEO", "MASERATI", "FERRARI", 
            "LAMBORGHINI", "PORSCHE", "ASTON MARTIN", "BENTLEY", "ROLLS ROYCE", "LEXUS", 
            "INFINITI", "ACURA", "BUICK", "CADILLAC", "CHEVROLET", "CHRYSLER", "DODGE", 
            "JEEP", "LINCOLN", "PONTIAC", "SATURN", "SCION", "SMART", "SUZUKI", "DAIHATSU", 
            "ISUZU", "MAHINDRA", "TATA", "MG", "ROVER", "VAUXHALL", "VAZ", "GAZ", "UAZ", 
            "ZAZ", "MOSKVICH", "IZH", "KAMAZ", "URAL", "ZIL", "MAZ", "KRAZ", "BELAZ"
        ]
        
        self.fashion_brands = [
            "ZARA", "MANGO", "H&M", "UNIQLO", "PULL&BEAR", "BERSHKA", "STRADIVARIUS", 
            "MASSIMO DUTTI", "OYSHO", "ZARA HOME", "UTERQÜE", "LEFTIES", "COS", "ARKET", 
            "& OTHER STORIES", "MONKI", "WEEKDAY", "CHEAP MONDAY", "NAKED", "LINDEX", 
            "KAPP AHL", "LAGER 157", "NEW YORKER", "C&A", "PENNY", "TALLY WEIJL", 
            "ESPRIT", "TOMMY HILFIGER", "CALVIN KLEIN", "LEVI'S", "DIESEL", "G-STAR RAW", 
            "CARHARTT", "VANS", "CONVERSE", "ADIDAS", "NIKE", "PUMA", "REEBOK", "UMBRO", 
            "LACOSTE", "RALPH LAUREN", "POLO", "BURBERRY", "GUCCI", "PRADA", "LOUIS VUITTON", 
            "CHANEL", "HERMES", "FENDI", "BOTTEGA VENETA", "SAINT LAURENT", "BALENCIAGA", 
            "GIVENCHY", "DIOR", "CELINE", "LOEWE", "BOTTEGA VENETA", "SAINT LAURENT", 
            "BALENCIAGA", "GIVENCHY", "DIOR", "CELINE", "LOEWE"
        ]

    def _get_site_config(self, url: str) -> Dict[str, Any]:
        """URL'den site konfigürasyonunu al"""
        domain = urlparse(url).netloc.lower()
        
        for site_domain, config in self.site_configs.items():
            if site_domain in domain:
                return config
        
        # Bilinmeyen site için genel konfigürasyon
        return {
            "name": "Unknown",
            "selectors": self.general_selectors,
            "price_cleaner": self._clean_general_price,
            "image_enhancer": self._enhance_general_image,
            "brand_detector": self._detect_general_brands,
            "wait_time": 3000,
            "timeout": 45000
        }

    async def _extract_with_fallback(self, page, selectors: List[str], attribute: str = "innerText") -> str:
        """Fallback'li veri çekme"""
        for selector in selectors:
            try:
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

    async def _smart_extract(self, page, field: str, config: Dict[str, Any]) -> str:
        """Akıllı veri çekme - birden fazla yöntem dener"""
        selectors = config["selectors"].get(field, [])
        
        # 1. Yöntem: Site özel selector'ları
        result = await self._extract_with_fallback(page, selectors)
        if result:
            return result
        
        # 2. Yöntem: Genel selector'lar
        general_selectors = self.general_selectors.get(field, [])
        result = await self._extract_with_fallback(page, general_selectors)
        if result:
            return result
        
        # 3. Yöntem: Akıllı arama
        if field == "title":
            return await self._smart_title_search(page)
        elif field == "price":
            return await self._smart_price_search(page)
        elif field == "image":
            return await self._smart_image_search(page)
        
        return ""

    async def _smart_title_search(self, page) -> str:
        """Akıllı başlık arama"""
        try:
            # H1, H2 elementlerini kontrol et
            for tag in ["h1", "h2"]:
                elements = await page.query_selector_all(tag)
                for element in elements:
                    text = await element.inner_text()
                    if text and len(text.strip()) > 5 and len(text.strip()) < 200:
                        return text.strip()
            
            # Class'ında title/product geçen elementleri kontrol et
            title_elements = await page.query_selector_all("[class*='title'], [class*='Title'], [class*='product'], [class*='Product']")
            for element in title_elements:
                text = await element.inner_text()
                if text and len(text.strip()) > 5 and len(text.strip()) < 200:
                    return text.strip()
            
            # Meta title'ı kontrol et
            meta_title = await page.get_attribute("title", "innerText")
            if meta_title and len(meta_title.strip()) > 5:
                return meta_title.strip()
                
        except Exception as e:
            logging.debug(f"[DEBUG] Akıllı başlık arama hatası: {e}")
        
        return ""

    async def _smart_price_search(self, page) -> str:
        """Akıllı fiyat arama"""
        try:
            # Para birimi sembolleri içeren elementleri ara
            currency_selectors = [
                "span:contains('₺')", "span:contains('TL')", "span:contains('$')", 
                "span:contains('€')", "span:contains('£')", "div:contains('₺')", 
                "div:contains('TL')", "div:contains('$')", "div:contains('€')"
            ]
            
            for selector in currency_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    for element in elements:
                        text = await element.inner_text()
                        if text and any(char.isdigit() for char in text):
                            return text.strip()
                except:
                    continue
            
            # Class'ında price geçen elementleri kontrol et
            price_elements = await page.query_selector_all("[class*='price'], [class*='Price']")
            for element in price_elements:
                text = await element.inner_text()
                if text and any(char.isdigit() for char in text):
                    return text.strip()
                    
        except Exception as e:
            logging.debug(f"[DEBUG] Akıllı fiyat arama hatası: {e}")
        
        return ""

    async def _smart_image_search(self, page) -> str:
        """Akıllı görsel arama"""
        try:
            # Ürün görselleri için özel selector'lar
            image_selectors = [
                "img[src*='product']", "img[src*='image']", "img[alt*='product']",
                "img[class*='product']", "img[class*='image']", "img[loading='lazy']",
                "img[data-testid*='image']", "img[data-qa-action*='image']"
            ]
            
            for selector in image_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    for element in elements:
                        src = await element.get_attribute("src")
                        if src and ("product" in src.lower() or "image" in src.lower()):
                            return src
                except:
                    continue
            
            # İlk geçerli görseli al
            img_elements = await page.query_selector_all("img")
            for img in img_elements:
                src = await img.get_attribute("src")
                if src and src.startswith("http") and not src.endswith(".svg"):
                    return src
                    
        except Exception as e:
            logging.debug(f"[DEBUG] Akıllı görsel arama hatası: {e}")
        
        return ""

    # Fiyat temizleme fonksiyonları
    def _clean_hepsiburada_price(self, price_text: str) -> str:
        """Hepsiburada fiyat temizleme"""
        if not price_text:
            return ""
        
        # TL, ₺ ve boşlukları kaldır, virgülü noktaya çevir
        price_clean = re.sub(r'[^\d.,]', '', price_text)
        price_clean = price_clean.replace(',', '.')
        return price_clean

    def _clean_sahibinden_price(self, price_text: str) -> str:
        """Sahibinden fiyat temizleme"""
        if not price_text:
            return ""
        
        # Binlik ayırıcıları kaldır
        price_clean = re.sub(r'[^\d.,]', '', price_text)
        price_clean = price_clean.replace('.', '').replace(',', '.')
        return price_clean

    def _clean_general_price(self, price_text: str) -> str:
        """Genel fiyat temizleme"""
        if not price_text:
            return ""
        
        # Sadece sayıları ve nokta/virgül al
        price_clean = re.sub(r'[^\d.,]', '', price_text)
        return price_clean

    # Görsel kalitesi artırma fonksiyonları
    def _enhance_hepsiburada_image(self, image_url: str) -> str:
        """Hepsiburada görsel kalitesi artırma"""
        if image_url and "productimages.hepsiburada.net" in image_url:
            # Orijinal boyut için parametreleri kaldır
            base_url = image_url.split('?')[0] if '?' in image_url else image_url
            return base_url
        return image_url

    def _enhance_sahibinden_image(self, image_url: str) -> str:
        """Sahibinden görsel kalitesi artırma"""
        if image_url and "shbdn.com" in image_url:
            # Orijinal boyut için parametreleri kaldır
            base_url = image_url.split('?')[0] if '?' in image_url else image_url
            return base_url
        return image_url

    def _enhance_general_image(self, image_url: str) -> str:
        """Genel görsel kalitesi artırma"""
        if not image_url:
            return ""
        
        # PullandBear için özel işlem
        if "pullandbear.net" in image_url or "pullandbear.com" in image_url:
            if "w=" in image_url and "f=auto" in image_url:
                image_url = re.sub(r'w=\d+', 'w=2000', image_url)
                image_url = re.sub(r'f=auto', 'f=webp', image_url)
            elif "w=" in image_url:
                image_url = re.sub(r'w=\d+', 'w=2000', image_url)
            elif "f=auto" in image_url:
                image_url = re.sub(r'f=auto', 'f=webp', image_url)
            else:
                if "?" in image_url:
                    image_url += "&w=2000&f=webp"
                else:
                    image_url += "?w=2000&f=webp"
        
        return image_url

    # Marka tespit fonksiyonları
    def _detect_tech_brands(self, title: str) -> str:
        """Teknoloji markalarını tespit et"""
        if not title:
            return "UNKNOWN"
        
        title_upper = title.upper()
        for brand in self.tech_brands:
            if brand in title_upper:
                return brand
        return "UNKNOWN"

    def _detect_car_brands(self, title: str) -> str:
        """Araba markalarını tespit et"""
        if not title:
            return "UNKNOWN"
        
        title_upper = title.upper()
        for brand in self.car_brands:
            if brand in title_upper:
                return brand
        return "UNKNOWN"

    def _detect_general_brands(self, title: str) -> str:
        """Genel marka tespiti"""
        if not title:
            return "UNKNOWN"
        
        title_upper = title.upper()
        
        # Önce teknoloji markalarını kontrol et
        for brand in self.tech_brands:
            if brand in title_upper:
                return brand
        
        # Sonra araba markalarını kontrol et
        for brand in self.car_brands:
            if brand in title_upper:
                return brand
        
        # Son olarak moda markalarını kontrol et
        for brand in self.fashion_brands:
            if brand in title_upper:
                return brand
        
        return "UNKNOWN"

    async def _setup_browser(self):
        """Tarayıcı kurulumu"""
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu'
            ]
        )
        
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        
        page = await context.new_page()
        
        # Sayfa yükleme optimizasyonları
        await page.route("**/*.{png,jpg,jpeg,gif,svg,webp}", lambda route: route.abort())
        await page.route("**/*.{css,woff,woff2,ttf}", lambda route: route.abort())
        
        return playwright, browser, context, page

    async def scrape_product(self, url: str, max_retries: int = 3) -> Optional[Dict[str, Any]]:
        """Ürün verisi çekme"""
        config = self._get_site_config(url)
        
        for attempt in range(max_retries):
            try:
                logging.info(f"[DENEME {attempt + 1}/{max_retries}] {config['name']} - {url}")
                
                playwright, browser, context, page = await self._setup_browser()
                
                try:
                    # Sayfaya git
                    await page.goto(url, wait_until="domcontentloaded", timeout=config["timeout"])
                    await page.wait_for_timeout(config["wait_time"])
                    
                    # Sayfanın tam yüklenmesini bekle
                    try:
                        await page.wait_for_load_state("networkidle", timeout=10000)
                    except:
                        pass
                    
                    # Veri çekme
                    title = await self._smart_extract(page, "title", config)
                    price = await self._smart_extract(page, "price", config)
                    image = await self._smart_extract(page, "image", config)
                    
                    # Hepsiburada için indirimsiz fiyat
                    original_price = ""
                    if "hepsiburada.com" in url:
                        original_price = await self._smart_extract(page, "original_price", config)
                    
                    # Veri temizleme ve işleme
                    if title:
                        title = title.strip().upper()
                    
                    if price:
                        price = config["price_cleaner"](price)
                    
                    if image:
                        image = config["image_enhancer"](image)
                    
                    # Marka tespiti
                    brand = config["brand_detector"](title)
                    
                    # Sonuç oluşturma
                    result = {
                        "title": title,
                        "price": price,
                        "image": image,
                        "brand": brand,
                        "url": url,
                        "site": config["name"],
                        "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    # Hepsiburada için indirimsiz fiyat ekle
                    if original_price:
                        result["original_price"] = config["price_cleaner"](original_price)
                    
                    # Veri doğrulama
                    if not title or not price:
                        logging.warning(f"[UYARI] Eksik veri: {url}")
                        if attempt < max_retries - 1:
                            continue
                    
                    logging.info(f"[BAŞARILI] {config['name']} - {title}")
                    return result
                    
                finally:
                    await browser.close()
                    await playwright.stop()
                    
            except Exception as e:
                logging.error(f"[HATA] Deneme {attempt + 1} başarısız: {url} - {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(random.uniform(2, 5))  # Rastgele bekleme
        
        logging.error(f"[HATA] Tüm denemeler başarısız: {url}")
        return None

    def scrape_product_sync(self, url: str, max_retries: int = 3) -> Optional[Dict[str, Any]]:
        """Senkron ürün verisi çekme"""
        return asyncio.run(self.scrape_product(url, max_retries))

    async def scrape_multiple_products(self, urls: List[str], max_retries: int = 3) -> List[Dict[str, Any]]:
        """Birden fazla ürün verisi çekme"""
        results = []
        
        for url in urls:
            result = await self.scrape_product(url, max_retries)
            if result:
                results.append(result)
            await asyncio.sleep(random.uniform(1, 3))  # Rate limiting
        
        return results

    def add_site_config(self, domain: str, config: Dict[str, Any]):
        """Yeni site konfigürasyonu ekleme"""
        self.site_configs[domain] = config
        logging.info(f"[BİLGİ] Yeni site konfigürasyonu eklendi: {domain}")

    def save_configs(self, filename: str = "scraper_configs.json"):
        """Konfigürasyonları dosyaya kaydet"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.site_configs, f, indent=2, ensure_ascii=False)
            logging.info(f"[BİLGİ] Konfigürasyonlar kaydedildi: {filename}")
        except Exception as e:
            logging.error(f"[HATA] Konfigürasyon kaydetme hatası: {e}")

    def load_configs(self, filename: str = "scraper_configs.json"):
        """Konfigürasyonları dosyadan yükle"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                configs = json.load(f)
                self.site_configs.update(configs)
            logging.info(f"[BİLGİ] Konfigürasyonlar yüklendi: {filename}")
        except Exception as e:
            logging.error(f"[HATA] Konfigürasyon yükleme hatası: {e}")


# Kullanım örneği
if __name__ == "__main__":
    scraper = UniversalScraper()
    
    # Test URL'leri
    test_urls = [
        "https://www.hepsiburada.com/gipta-pera-ciltli-deri-kapak-9x14-cizgisiz-defter-pm-HBC00002QG0EE",
        "https://www.sahibinden.com/ilan/vasita-arazi-suv-pickup-lada-turkiye-de-tek-lada-niva-dolu-dolu-asiri-emek-verilmis-restore-1249924513/detay",
        "https://www.zara.com/tr/tr/oversize-blazer-p04234543.html"
    ]
    
    print("=== Evrensel Scraper Test ===")
    
    for url in test_urls:
        print(f"\n--- {url} ---")
        result = scraper.scrape_product_sync(url)
        
        if result:
            print(f"Başlık: {result['title']}")
            print(f"Fiyat: {result['price']}")
            print(f"Marka: {result['brand']}")
            print(f"Site: {result['site']}")
            print(f"Görsel: {result['image'][:100]}...")
            if 'original_price' in result:
                print(f"İndirimsiz Fiyat: {result['original_price']}")
        else:
            print("Veri çekilemedi!")
    
    # Konfigürasyonları kaydet
    scraper.save_configs()
