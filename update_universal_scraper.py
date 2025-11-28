import asyncio
import logging
from universal_scraper import UniversalScraper

# Logging ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def update_universal_scraper():
    """Universal scraper'a Adidas konfigürasyonu ekle"""
    
    scraper = UniversalScraper()
    
    # Adidas için özel konfigürasyon ekle
    adidas_config = {
        "name": "Adidas",
        "selectors": {
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
                "h1 span",
                ".gl-product-card__name",
                ".gl-product-card__title"
            ],
            "price": [
                "[data-testid='price']",
                "[data-qa-action='price']",
                ".price",
                ".product-price",
                "[class*='price']",
                "span[class*='price']",
                ".gl-price",
                ".gl-price__value",
                "[data-auto-id='product-price']"
            ],
            "image": [
                "img[class*='product']",
                "img[class*='image']",
                "img[loading='lazy']",
                "img[alt*='product']",
                "img[src*='product']",
                ".gl-product-card__image img",
                ".gl-product-card__media img"
            ]
        },
        "price_cleaner": scraper._clean_general_price,
        "image_enhancer": scraper._enhance_general_image,
        "brand_detector": lambda title: "ADIDAS",
        "wait_time": 10000,  # Daha uzun bekleme süresi
        "timeout": 60000,
        "browser": "firefox",  # Firefox kullan
        "pre_navigation": True  # Önce ana sayfaya git
    }
    
    # Konfigürasyonu ekle
    scraper.add_site_config("adidas.com.tr", adidas_config)
    
    print("✅ Adidas konfigürasyonu eklendi!")
    
    # Test et
    test_url = "https://www.adidas.com.tr/tr/sl-72-rs-ayakkabi/JS0749.html"
    print(f"\n--- ADIDAS TEST ---")
    print(f"URL: {test_url}")
    
    result = await scraper.scrape_product(test_url)
    
    if result:
        print(f"✅ BAŞARILI!")
        print(f"Başlık: {result.get('title', 'N/A')}")
        print(f"Fiyat: {result.get('price', 'N/A')}")
        print(f"Marka: {result.get('brand', 'N/A')}")
        print(f"Site: {result.get('site', 'N/A')}")
        if result.get('image'):
            print(f"Görsel: {result['image'][:80]}...")
    else:
        print(f"❌ BAŞARISIZ!")
    
    # Konfigürasyonları kaydet
    scraper.save_configs("updated_scraper_configs.json")
    print(f"\n✅ Konfigürasyonlar kaydedildi: updated_scraper_configs.json")

if __name__ == "__main__":
    asyncio.run(update_universal_scraper())
