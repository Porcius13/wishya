import asyncio
import logging
import re
from urllib.parse import urlparse
from playwright.async_api import async_playwright
import time

logging.basicConfig(level=logging.DEBUG)

class SahibindenScraper:
    def __init__(self):
        self.selectors = {
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
            "description": [
                ".classified-info",
                ".classified-description",
                "[class*='description']",
                ".info-list"
            ]
        }
    
    async def extract_with_fallback(self, page, selectors, attribute="innerText"):
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
    
    async def clean_price(self, price_text):
        """Fiyat metnini temizle"""
        if not price_text:
            return ""
        
        # Sadece sayıları ve nokta/virgül al
        price_clean = re.sub(r'[^\d.,]', '', price_text)
        
        # Binlik ayırıcıları kaldır
        price_clean = price_clean.replace('.', '').replace(',', '.')
        
        return price_clean
    
    async def get_all_images(self, page):
        """Tüm ürün görsellerini al"""
        images = []
        try:
            # Ana görsel
            main_image = await self.extract_with_fallback(page, self.selectors["image"], "src")
            if main_image:
                images.append(main_image)
            
            # Diğer görseller
            img_elements = await page.query_selector_all("img[src*='shbdn.com']")
            for img in img_elements:
                src = await img.get_attribute("src")
                if src and src not in images:
                    images.append(src)
            
            # Görsel kalitesini artır
            enhanced_images = []
            for img in images:
                if "shbdn.com" in img:
                    # Orijinal boyut için parametreleri kaldır
                    base_url = img.split('?')[0] if '?' in img else img
                    enhanced_images.append(base_url)
                else:
                    enhanced_images.append(img)
            
            return enhanced_images[:10]  # Maksimum 10 görsel
            
        except Exception as e:
            logging.debug(f"[DEBUG] Görsel toplama hatası: {e}")
            return images
    
    async def get_product_details(self, page):
        """Ürün detaylarını al"""
        details = {}
        try:
            # Detay listesi
            detail_elements = await page.query_selector_all(".classified-info-list li, .info-list li")
            for element in detail_elements:
                text = await element.inner_text()
                if ':' in text:
                    key, value = text.split(':', 1)
                    details[key.strip()] = value.strip()
            
            return details
        except Exception as e:
            logging.debug(f"[DEBUG] Detay toplama hatası: {e}")
            return details
    
    async def fetch_data(self, url):
        """Sahibinden.com'dan ürün verisi çek"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()

            try:
                # Sayfaya git
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_timeout(2000)
                
                # Sayfanın yüklenmesini bekle
                try:
                    await page.wait_for_load_state("networkidle", timeout=10000)
                except:
                    pass
                
                # Başlık çek
                title = await self.extract_with_fallback(page, self.selectors["title"])
                
                # Fiyat çek
                price_text = await self.extract_with_fallback(page, self.selectors["price"])
                price = await self.clean_price(price_text)
                
                # Görselleri çek
                images = await self.get_all_images(page)
                main_image = images[0] if images else ""
                
                # Detayları çek
                details = await self.get_product_details(page)
                
                # Açıklama çek
                description = await self.extract_with_fallback(page, self.selectors["description"])
                
                # Başlık temizleme
                if title:
                    title = title.strip().upper()
                
                # Marka tespiti (başlıktan)
                brand = "UNKNOWN"
                if title:
                    # Sahibinden.com'da genellikle marka başlıkta geçer
                    common_brands = ["LADA", "BMW", "MERCEDES", "AUDI", "VOLKSWAGEN", "FORD", "RENAULT", "FIAT", "TOYOTA", "HONDA"]
                    for brand_name in common_brands:
                        if brand_name in title:
                            brand = brand_name
                            break
                
                result = {
                    "title": title,
                    "image": main_image,
                    "images": images,
                    "price": price,
                    "price_text": price_text,
                    "brand": brand,
                    "url": url,
                    "description": description,
                    "details": details
                }

                logging.info(f"[BAŞARILI] Sahibinden.com - {title}")
                return result

            except Exception as e:
                logging.error(f"[HATA] Sahibinden.com veri çekilemedi: {url} - {e}")
                return None
            finally:
                await browser.close()
    
    def scrape_product(self, url):
        """3 deneme ile ürün verisi çekme"""
        for i in range(3):
            try:
                logging.debug(f"[DEBUG] Sahibinden.com Deneme {i+1}/3 - {url}")
                result = asyncio.run(self.fetch_data(url))
                if result:
                    return result
                time.sleep(2)  # Denemeler arası bekleme
            except Exception as e:
                logging.debug(f"[DEBUG] Sahibinden.com Hata {i+1}: {e}")
                time.sleep(2)
        
        logging.error(f"[HATA] Sahibinden.com tüm denemeler başarısız: {url}")
        return None

# Kullanım örneği
if __name__ == "__main__":
    scraper = SahibindenScraper()
    
    # Test URL'i
    test_url = "https://www.sahibinden.com/ilan/vasita-arazi-suv-pickup-lada-turkiye-de-tek-lada-niva-dolu-dolu-asiri-emek-verilmis-restore-1249924513/detay"
    
    result = scraper.scrape_product(test_url)
    if result:
        print("Başlık:", result["title"])
        print("Fiyat:", result["price"])
        print("Fiyat Metni:", result["price_text"])
        print("Ana Görsel:", result["image"])
        print("Marka:", result["brand"])
        print("Görsel Sayısı:", len(result["images"]))
        print("Detaylar:", result["details"])
    else:
        print("Veri çekilemedi!")
