#!/usr/bin/env python3
"""
Render.com için optimize edilmiş scraper wrapper
Async/await sorunlarını çözer ve Render'da çalışacak şekilde ayarlanmıştır
"""

import asyncio
import logging
import os
from typing import Dict, Any, Optional
from site_specific_scrapers import SiteSpecificScrapers
from advanced_site_scrapers import AdvancedSiteScrapers

# Render.com için logging ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class RenderScraper:
    """
    Render.com için optimize edilmiş scraper
    """
    
    def __init__(self):
        self.site_scrapers = SiteSpecificScrapers()
        self.advanced_scrapers = AdvancedSiteScrapers()
        
        # Render.com için browser ayarları
        self.browser_args = [
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
    
    def _extract_domain(self, url: str) -> str:
        """URL'den domain çıkarır"""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain
    
    async def scrape_product_async(self, url: str, use_advanced: bool = True) -> Dict[str, Any]:
        """
        Async ürün scraping
        """
        try:
            if use_advanced:
                return await self.advanced_scrapers.scrape_product(url)
            else:
                return await self.site_scrapers.scrape_product(url)
        except Exception as e:
            logging.error(f"Scraping hatası: {e}")
            return {"error": str(e), "url": url}
    
    def scrape_product_sync(self, url: str, use_advanced: bool = True) -> Dict[str, Any]:
        """
        Sync wrapper for async scraping (Flask compatibility)
        """
        try:
            # Render.com'da event loop sorunlarını çözmek için
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            return loop.run_until_complete(self.scrape_product_async(url, use_advanced))
        except Exception as e:
            logging.error(f"Sync scraping hatası: {e}")
            return {"error": str(e), "url": url}
    
    def scrape_multiple_products_sync(self, urls: list, use_advanced: bool = True) -> list:
        """
        Birden fazla ürünü sync olarak scrape eder
        """
        results = []
        
        for i, url in enumerate(urls, 1):
            logging.info(f"[{i}/{len(urls)}] Scraping: {url}")
            
            try:
                result = self.scrape_product_sync(url, use_advanced)
                results.append(result)
                
                if "error" in result:
                    logging.warning(f"❌ Hata: {result['error']}")
                else:
                    logging.info(f"✅ Başarılı: {result.get('site', 'N/A')} - {result.get('title', 'N/A')[:30]}...")
                
            except Exception as e:
                logging.error(f"❌ Beklenmeyen hata: {e}")
                results.append({
                    "error": str(e),
                    "url": url
                })
            
            # Rate limiting
            import time
            time.sleep(1)
        
        return results
    
    def is_site_supported(self, url: str) -> bool:
        """URL'nin desteklenen bir site olup olmadığını kontrol eder"""
        domain = self._extract_domain(url)
        supported_sites = [
            "beymen.com", "ellesse.com.tr", "beyyoglu.com", "ninewest.com.tr",
            "levis.com.tr", "dockers.com.tr", "sarar.com", "salomon.com.tr",
            "abercrombie.com", "loft.com.tr", "ucla.com.tr", "yargici.com"
        ]
        return domain in supported_sites
    
    def get_supported_sites(self) -> list:
        """Desteklenen site listesini döndürür"""
        return [
            "beymen.com", "ellesse.com.tr", "beyyoglu.com", "ninewest.com.tr",
            "levis.com.tr", "dockers.com.tr", "sarar.com", "salomon.com.tr",
            "abercrombie.com", "loft.com.tr", "ucla.com.tr", "yargici.com"
        ]

# Global scraper instance
render_scraper = RenderScraper()

# Test fonksiyonu
def test_render_scraper():
    """Render scraper'ı test eder"""
    test_urls = [
        "https://www.beymen.com/tr/p_polo-ralph-lauren-beyaz-oxford-gomlek_1646218",
        "https://www.ellesse.com.tr/products/ellesse-erkek-polo-yaka-tisort-em460-bk",
        "https://www.beyyoglu.com/100-keten-oversize-gomlek-24ss53005006-27/"
    ]
    
    print("=== RENDER SCRAPER TEST ===")
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n[{i}/{len(test_urls)}] Testing: {url}")
        
        # Sync test
        result = render_scraper.scrape_product_sync(url)
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"✅ Success:")
            print(f"   Site: {result.get('site', 'N/A')}")
            print(f"   Title: {result.get('title', 'N/A')[:50]}...")
            print(f"   Current Price: {result.get('current_price', 'N/A')}")
            print(f"   Original Price: {result.get('original_price', 'N/A')}")
            print(f"   Image: {result.get('image_url', 'N/A')[:50]}...")

if __name__ == "__main__":
    test_render_scraper()
