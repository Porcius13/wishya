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

class SiteSpecificScrapers:
    """
    Site spesifik scraping sistemi
    Her site için özel selector'lar ve temizleme fonksiyonları
    """
    
    def __init__(self):
        self.site_configs = {
            "beymen.com": {
                "name": "Beymen",
                "selectors": {
                    "title": [
                        "span.o-productDetail__description",
                        "h1.o-productDetail__description",
                        ".o-productDetail__description"
                    ],
                    "current_price": [
                        "ins#priceNew.m-price__new",
                        "ins.m-price__new",
                        "#priceNew",
                        ".m-price__new"
                    ],
                    "original_price": [
                        "del#priceOld.m-price__old",
                        "del.m-price__old",
                        "#priceOld",
                        ".m-price__old"
                    ],
                    "image": [
                        "img.m-productDetailImage__item",
                        "img[class*='m-productDetailImage__item']",
                        "img[src*='cdn.beymen.com']",
                        "img[alt*='product']"
                    ]
                },
                "price_cleaner": self._clean_beymen_price,
                "wait_time": 2000,
                "timeout": 30000
            },
            
            "ellesse.com.tr": {
                "name": "Ellesse",
                "selectors": {
                    "title": [
                        "h1.product__title.h4",
                        "h1.product__title",
                        ".product__title",
                        "h1[class*='product__title']"
                    ],
                    "current_price": [
                        "span.price-item.price-item--sale.price-item--last",
                        "span.price-item--sale",
                        ".price-item--sale",
                        "span[class*='price-item--sale']"
                    ],
                    "original_price": [
                        "s.price-item.price-item--regular",
                        "s.price-item--regular",
                        ".price-item--regular",
                        "s[class*='price-item--regular']"
                    ],
                    "image": [
                        "img[src*='cdn.shop/files']",
                        "img[src*='ellesse.com.tr/cdn']",
                        "img[alt*='product']",
                        "img[class*='image-magnify']"
                    ]
                },
                "price_cleaner": self._clean_ellesse_price,
                "wait_time": 2000,
                "timeout": 30000
            },
            
            "beyyoglu.com": {
                "name": "Beyyoglu",
                "selectors": {
                    "title": [
                        "h2.product-info__title",
                        ".product-info__title",
                        "h2[class*='product-info__title']"
                    ],
                    "current_price": [
                        "pz-price[use-currency-symbol='false'][use-currency-after-price='true'][currency-code='TL']:last-of-type",
                        "pz-price[rendered='true']:last-of-type",
                        "pz-price:last-of-type",
                        "pz-price"
                    ],
                    "original_price": [
                        "pz-price[use-currency-symbol='false'][use-currency-after-price='true'][currency-code='TL']:first-of-type",
                        "pz-price[rendered='true']:first-of-type",
                        "pz-price:first-of-type"
                    ],
                    "image": [
                        "img[src*='akinoncloud.com']",
                        "img[data-src*='akinoncloud.com']",
                        "img[alt*='product']"
                    ]
                },
                "price_cleaner": self._clean_beyyoglu_price,
                "wait_time": 2000,
                "timeout": 30000
            },
            
            "ninewest.com.tr": {
                "name": "Nine West",
                "selectors": {
                    "title": [
                        "h1.product-name.mb-0.mb-lg-2.mt-0.order-1.order-lg-0.description.text-capitalize",
                        "h1.product-name",
                        ".product-name",
                        "h1[class*='product-name']"
                    ],
                    "current_price": [
                        "div.product-pricing-one__price",
                        ".product-pricing-one__price",
                        "div[class*='product-pricing-one__price']"
                    ],
                    "original_price": [
                        "span:contains('2.999,00 TL')",
                        "span:contains('TL')",
                        "span[class*='price']",
                        ".old-price"
                    ],
                    "image": [
                        "img[src*='floimages.mncdn.com']",
                        "img[class*='ls-is-cached']",
                        "img[alt*='product']"
                    ]
                },
                "price_cleaner": self._clean_ninewest_price,
                "wait_time": 2000,
                "timeout": 30000
            },
            
            "levis.com.tr": {
                "name": "Levi's",
                "selectors": {
                    "title": [
                        "h1.product-title.lhead-2.xdesktop-only.text-transform-none.mb-0",
                        "h1.product-title",
                        ".product-title",
                        "h1[class*='product-title']"
                    ],
                    "current_price": [
                        "span.new-price",
                        ".new-price",
                        "span[class*='new-price']"
                    ],
                    "original_price": [
                        "span.old-price",
                        ".old-price",
                        "span[class*='old-price']"
                    ],
                    "image": [
                        "img[src*='st-levis.mncdn.com']",
                        "img[class*='xxxdesktop-only']",
                        "img[alt*='product']"
                    ]
                },
                "price_cleaner": self._clean_levis_price,
                "wait_time": 2000,
                "timeout": 30000
            },
            
            "dockers.com.tr": {
                "name": "Dockers",
                "selectors": {
                    "title": [
                        "div.product-title.lhead-2.h1",
                        "div.product-title",
                        ".product-title",
                        "div[class*='product-title']"
                    ],
                    "current_price": [
                        "span.new-price",
                        ".new-price",
                        "span[class*='new-price']"
                    ],
                    "original_price": [
                        "span.old-price",
                        ".old-price",
                        "span[class*='old-price']"
                    ],
                    "image": [
                        "img[src*='st-dockers.mncdn.com']",
                        "img[class*='xxxdesktop-only']",
                        "img[alt*='product']"
                    ]
                },
                "price_cleaner": self._clean_dockers_price,
                "wait_time": 2000,
                "timeout": 30000
            },
            
            "sarar.com": {
                "name": "Sarar",
                "selectors": {
                    "title": [
                        "h1#product-title",
                        "#product-title",
                        "h1[class*='product-title']"
                    ],
                    "current_price": [
                        "span.cart-price",
                        ".cart-price",
                        "span[class*='cart-price']"
                    ],
                    "original_price": [
                        "span.product-price",
                        ".product-price",
                        "span[class*='product-price']"
                    ],
                    "image": [
                        "img[src*='witcdn.sarar.com']",
                        "img[alt*='product']",
                        "img[data-toggle='zoom-image']"
                    ]
                },
                "price_cleaner": self._clean_sarar_price,
                "wait_time": 2000,
                "timeout": 30000
            },
            
            "salomon.com.tr": {
                "name": "Salomon",
                "selectors": {
                    "title": [
                        "span:contains('ACS +')",
                        "span[class*='product-title']",
                        ".product-title",
                        "h1",
                        "h2"
                    ],
                    "current_price": [
                        "span.spanFiyat:last-of-type",
                        "span.spanFiyat:nth-of-type(2)",
                        ".spanFiyat:last-of-type",
                        "span[class*='spanFiyat']:last-of-type"
                    ],
                    "original_price": [
                        "span.spanFiyat:first-of-type",
                        "span.spanFiyat:nth-of-type(1)",
                        ".spanFiyat:first-of-type",
                        "span[class*='spanFiyat']:first-of-type"
                    ],
                    "image": [
                        "img[src*='static.ticimax.cloud']",
                        "img[class*='cloudzoom-gallery']",
                        "img[alt*='product']"
                    ]
                },
                "price_cleaner": self._clean_salomon_price,
                "wait_time": 2000,
                "timeout": 30000
            },
            
            "abercrombie.com": {
                "name": "Abercrombie",
                "selectors": {
                    "title": [
                        "h1.product-title-component.product-title-main-header",
                        "h1.product-title-component",
                        ".product-title-component",
                        "h1[class*='product-title']"
                    ],
                    "current_price": [
                        "span.product-price-text.product-price-font-size[data-variant='discount']",
                        "span[data-variant='discount']",
                        ".product-price-text[data-variant='discount']"
                    ],
                    "original_price": [
                        "span.product-price-text.product-price-font-size[data-variant='original']",
                        "span[data-variant='original']",
                        ".product-price-text[data-variant='original']"
                    ],
                    "image": [
                        "img[src*='img.abercrombie.com']",
                        "img[alt*='model image']",
                        "img[class*='product']"
                    ]
                },
                "price_cleaner": self._clean_abercrombie_price,
                "wait_time": 2000,
                "timeout": 30000
            },
            
            "loft.com.tr": {
                "name": "Loft",
                "selectors": {
                    "title": [
                        "h1.product-detail-product-name.text-left.text-lg-left.p-lg-0",
                        "h1.product-detail-product-name",
                        ".product-detail-product-name",
                        "h1[class*='product-detail-product-name']"
                    ],
                    "current_price": [
                        "div.product-detail-price.float-left.mr-md-3",
                        ".product-detail-price",
                        "div[class*='product-detail-price']"
                    ],
                    "original_price": [
                        "div.product-detail-old-price.float-left.mr-3",
                        ".product-detail-old-price",
                        "div[class*='product-detail-old-price']"
                    ],
                    "image": [
                        "img.img-fluid.productDetailImage",
                        "img.productDetailImage",
                        "img[src*='img-loft-tr.mncdn.com']",
                        "img[alt*='product']"
                    ]
                },
                "price_cleaner": self._clean_loft_price,
                "wait_time": 2000,
                "timeout": 30000
            },
            
            "ucla.com.tr": {
                "name": "UCLA",
                "selectors": {
                    "title": [
                        "h1.product-name",
                        ".product-name",
                        "h1[class*='product-name']"
                    ],
                    "current_price": [
                        "span[style*='color: rgb(0, 59, 92)']",
                        "span[style*='color: rgb(0, 59, 92)']:not([style*='font-size: 20px'])",
                        ".current-price"
                    ],
                    "original_price": [
                        "span[style*='font-size: 20px; color: rgb(0, 59, 92)']",
                        "span[style*='font-size: 20px']",
                        ".original-price"
                    ],
                    "image": [
                        "img[src*='ucla.com.tr']",
                        "img[alt*='product']",
                        "img[class*='product']"
                    ]
                },
                "price_cleaner": self._clean_ucla_price,
                "wait_time": 2000,
                "timeout": 30000
            },
            
            "yargici.com": {
                "name": "Yargıcı",
                "selectors": {
                    "title": [
                        "h1.MuiTypography-root.MuiTypography-bodyBold18Italic",
                        "h1[class*='MuiTypography-bodyBold18Italic']",
                        ".MuiTypography-bodyBold18Italic"
                    ],
                    "current_price": [
                        "span.MuiTypography-root.MuiTypography-bodyRegular22",
                        "span[class*='MuiTypography-bodyRegular22']",
                        ".MuiTypography-bodyRegular22"
                    ],
                    "original_price": [
                        "span.MuiTypography-root.MuiTypography-bodyRegular20Strikethrough",
                        "span[class*='MuiTypography-bodyRegular20Strikethrough']",
                        ".MuiTypography-bodyRegular20Strikethrough"
                    ],
                    "image": [
                        "img[src*='img-phantomyargici.sm.mncdn.com']",
                        "img[alt*='product']",
                        "img[style*='object-fit: cover']"
                    ]
                },
                "price_cleaner": self._clean_yargici_price,
                "wait_time": 2000,
                "timeout": 30000
            }
        }
    
    async def scrape_product(self, url: str) -> Dict[str, Any]:
        """
        Verilen URL'den ürün bilgilerini çeker
        """
        domain = self._extract_domain(url)
        config = self.site_configs.get(domain)
        
        if not config:
            return {"error": f"Site {domain} için konfigürasyon bulunamadı"}
        
        async with async_playwright() as p:
            # Render.com için browser ayarları
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-gpu',
                    '--disable-background-timer-throttling',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-renderer-backgrounding',
                    '--disable-features=TranslateUI',
                    '--disable-ipc-flooding-protection'
                ]
            )
            page = await browser.new_page()
            
            try:
                await page.goto(url, wait_until="networkidle", timeout=config["timeout"])
                await page.wait_for_timeout(config["wait_time"])
                
                # Ürün bilgilerini çek
                product_data = {
                    "url": url,
                    "site": config["name"],
                    "title": await self._extract_text(page, config["selectors"]["title"]),
                    "current_price": await self._extract_text(page, config["selectors"]["current_price"]),
                    "original_price": await self._extract_text(page, config["selectors"]["original_price"]),
                    "image_url": await self._extract_image(page, config["selectors"]["image"])
                }
                
                # Fiyat temizleme
                if config.get("price_cleaner"):
                    product_data = config["price_cleaner"](product_data)
                
                return product_data
                
            except Exception as e:
                logging.error(f"Scraping hatası: {e}")
                return {"error": str(e)}
            finally:
                await browser.close()
    
    async def _extract_text(self, page, selectors: List[str]) -> str:
        """
        Sayfadan metin çıkarır
        """
        for selector in selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    text = await element.text_content()
                    if text and text.strip():
                        return text.strip()
            except Exception:
                continue
        return ""
    
    async def _extract_image(self, page, selectors: List[str]) -> str:
        """
        Sayfadan resim URL'si çıkarır
        """
        for selector in selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    src = await element.get_attribute("src")
                    if src:
                        return src
                    data_src = await element.get_attribute("data-src")
                    if data_src:
                        return data_src
            except Exception:
                continue
        return ""
    
    def _extract_domain(self, url: str) -> str:
        """
        URL'den domain çıkarır
        """
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        # www. kısmını kaldır
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain
    
    # Fiyat temizleme fonksiyonları
    def _clean_beymen_price(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Beymen fiyat temizleme"""
        if data["current_price"]:
            data["current_price"] = re.sub(r'[^\d,.]', '', data["current_price"])
        if data["original_price"]:
            data["original_price"] = re.sub(r'[^\d,.]', '', data["original_price"])
        return data
    
    def _clean_ellesse_price(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Ellesse fiyat temizleme"""
        if data["current_price"]:
            data["current_price"] = re.sub(r'[^\d,.]', '', data["current_price"])
        if data["original_price"]:
            data["original_price"] = re.sub(r'[^\d,.]', '', data["original_price"])
        return data
    
    def _clean_beyyoglu_price(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Beyyoglu fiyat temizleme"""
        if data["current_price"]:
            data["current_price"] = re.sub(r'[^\d,.]', '', data["current_price"])
        if data["original_price"]:
            data["original_price"] = re.sub(r'[^\d,.]', '', data["original_price"])
        return data
    
    def _clean_ninewest_price(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Nine West fiyat temizleme"""
        if data["current_price"]:
            data["current_price"] = re.sub(r'[^\d,.]', '', data["current_price"])
        if data["original_price"]:
            data["original_price"] = re.sub(r'[^\d,.]', '', data["original_price"])
        return data
    
    def _clean_levis_price(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Levi's fiyat temizleme"""
        if data["current_price"]:
            data["current_price"] = re.sub(r'[^\d,.]', '', data["current_price"])
        if data["original_price"]:
            data["original_price"] = re.sub(r'[^\d,.]', '', data["original_price"])
        return data
    
    def _clean_dockers_price(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Dockers fiyat temizleme"""
        if data["current_price"]:
            data["current_price"] = re.sub(r'[^\d,.]', '', data["current_price"])
        if data["original_price"]:
            data["original_price"] = re.sub(r'[^\d,.]', '', data["original_price"])
        return data
    
    def _clean_sarar_price(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sarar fiyat temizleme"""
        if data["current_price"]:
            data["current_price"] = re.sub(r'[^\d,.]', '', data["current_price"])
        if data["original_price"]:
            data["original_price"] = re.sub(r'[^\d,.]', '', data["original_price"])
        return data
    
    def _clean_salomon_price(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Salomon fiyat temizleme"""
        if data["current_price"]:
            data["current_price"] = re.sub(r'[^\d,.]', '', data["current_price"])
        if data["original_price"]:
            data["original_price"] = re.sub(r'[^\d,.]', '', data["original_price"])
        return data
    
    def _clean_abercrombie_price(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Abercrombie fiyat temizleme"""
        if data["current_price"]:
            data["current_price"] = re.sub(r'[^\d,.]', '', data["current_price"])
        if data["original_price"]:
            data["original_price"] = re.sub(r'[^\d,.]', '', data["original_price"])
        return data
    
    def _clean_loft_price(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Loft fiyat temizleme"""
        if data["current_price"]:
            data["current_price"] = re.sub(r'[^\d,.]', '', data["current_price"])
        if data["original_price"]:
            data["original_price"] = re.sub(r'[^\d,.]', '', data["original_price"])
        return data
    
    def _clean_ucla_price(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """UCLA fiyat temizleme"""
        if data["current_price"]:
            data["current_price"] = re.sub(r'[^\d,.]', '', data["current_price"])
        if data["original_price"]:
            data["original_price"] = re.sub(r'[^\d,.]', '', data["original_price"])
        return data
    
    def _clean_yargici_price(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Yargıcı fiyat temizleme"""
        if data["current_price"]:
            data["current_price"] = re.sub(r'[^\d,.]', '', data["current_price"])
        if data["original_price"]:
            data["original_price"] = re.sub(r'[^\d,.]', '', data["original_price"])
        return data

# Test fonksiyonu
async def test_scrapers():
    """
    Tüm scraper'ları test eder
    """
    scraper = SiteSpecificScrapers()
    
    test_urls = [
        "https://www.beymen.com/tr/p_polo-ralph-lauren-beyaz-oxford-gomlek_1646218",
        "https://www.ellesse.com.tr/products/ellesse-erkek-polo-yaka-tisort-em460-bk",
        "https://www.beyyoglu.com/100-keten-oversize-gomlek-24ss53005006-27/",
        "https://www.ninewest.com.tr/urun/nine-west-margarita-5fx-siyah-kadin-topuklu-sandalet-101928976",
        "https://www.levis.com.tr/levis-511-slim-fit_117340",
        "https://www.dockers.com.tr/smart-360-flex-ultimate-chino-slim-fit-pantolon_2661",
        "https://sarar.com/sarar-loreto-kot-elbise-18167",
        "https://www.salomon.com.tr/acs-plus-unisex-sneaker-l47705300",
        "https://www.abercrombie.com/shop/wd/p/premium-polished-tee-57648335?categoryId=12204&faceout=model&seq=13",
        "https://www.loft.com.tr/p/loose-fit-erkek-tshirt-kkol-6931",
        "https://ucla.com.tr/canary-haki-bisiklet-yaka-gofre-baskili-modal-kumas-standard-fit-erkek-tshirt",
        "https://www.yargici.com/kahverengi-regular-fit-keten-gomlek-p-198901"
    ]
    
    results = []
    for url in test_urls:
        print(f"\nScraping: {url}")
        result = await scraper.scrape_product(url)
        results.append(result)
        print(f"Result: {result}")
        await asyncio.sleep(2)  # Rate limiting
    
    # Sonuçları JSON dosyasına kaydet
    with open("scraping_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\nTüm sonuçlar scraping_results.json dosyasına kaydedildi.")

if __name__ == "__main__":
    asyncio.run(test_scrapers())
