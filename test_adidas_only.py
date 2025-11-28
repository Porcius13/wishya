import asyncio
import logging
from universal_scraper import UniversalScraper

# Logging ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def test_adidas_only():
    """Sadece Adidas'ı test et"""
    
    url = "https://www.adidas.com.tr/tr/sl-72-rs-ayakkabi/JS0749.html"
    
    print(f"=== ADIDAS TEST ===\n")
    print(f"URL: {url}")
    
    scraper = UniversalScraper()
    
    try:
        result = await scraper.scrape_product(url, max_retries=1)
        
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
            
    except Exception as e:
        print(f"❌ HATA: {e}")

if __name__ == "__main__":
    asyncio.run(test_adidas_only())
