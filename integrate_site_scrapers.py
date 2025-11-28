#!/usr/bin/env python3
"""
Site Spesifik Scraper Entegrasyonu
Bu dosya, yeni site spesifik scraper'ları mevcut universal scraper sistemine entegre eder.
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from site_specific_scrapers import SiteSpecificScrapers
from advanced_site_scrapers import AdvancedSiteScrapers

# Logging ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class IntegratedScraper:
    """
    Entegre scraper sistemi
    Site spesifik scraper'ları ve universal scraper'ı birleştirir
    """
    
    def __init__(self):
        self.site_scrapers = SiteSpecificScrapers()
        self.advanced_scrapers = AdvancedSiteScrapers()
        
        # Desteklenen site listesi
        self.supported_sites = [
            "beymen.com",
            "ellesse.com.tr", 
            "beyyoglu.com",
            "ninewest.com.tr",
            "levis.com.tr",
            "dockers.com.tr",
            "sarar.com",
            "salomon.com.tr",
            "abercrombie.com",
            "loft.com.tr",
            "ucla.com.tr",
            "yargici.com"
        ]
    
    def _extract_domain(self, url: str) -> str:
        """URL'den domain çıkarır"""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        # www. kısmını kaldır
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain
    
    def is_site_supported(self, url: str) -> bool:
        """URL'nin desteklenen bir site olup olmadığını kontrol eder"""
        domain = self._extract_domain(url)
        return domain in self.supported_sites
    
    async def scrape_product(self, url: str, use_advanced: bool = True) -> Dict[str, Any]:
        """
        Ürün bilgilerini çeker
        Önce site spesifik scraper'ı dener, başarısız olursa universal scraper'a geçer
        """
        domain = self._extract_domain(url)
        
        # Site spesifik scraper kullan
        if domain in self.supported_sites:
            try:
                if use_advanced:
                    result = await self.advanced_scrapers.scrape_product(url)
                else:
                    result = await self.site_scrapers.scrape_product(url)
                
                if "error" not in result:
                    result["scraper_type"] = "site_specific"
                    result["scraper_version"] = "advanced" if use_advanced else "basic"
                    return result
                else:
                    logging.warning(f"Site spesifik scraper başarısız: {result['error']}")
                    
            except Exception as e:
                logging.error(f"Site spesifik scraper hatası: {e}")
        
        # Universal scraper'a geç (mevcut sisteminizde varsa)
        try:
            # Burada mevcut universal scraper'ınızı çağırabilirsiniz
            # result = await self.universal_scraper.scrape_product(url)
            # result["scraper_type"] = "universal"
            # return result
            
            # Şimdilik hata döndür
            return {
                "error": f"Site {domain} için scraper bulunamadı",
                "url": url,
                "scraper_type": "none"
            }
            
        except Exception as e:
            return {
                "error": f"Universal scraper hatası: {e}",
                "url": url,
                "scraper_type": "none"
            }
    
    async def scrape_multiple_products(self, urls: list, use_advanced: bool = True) -> list:
        """Birden fazla ürünü scrape eder"""
        results = []
        
        for i, url in enumerate(urls, 1):
            print(f"[{i}/{len(urls)}] Scraping: {url}")
            
            try:
                result = await self.scrape_product(url, use_advanced)
                results.append(result)
                
                if "error" in result:
                    print(f"❌ Hata: {result['error']}")
                else:
                    print(f"✅ Başarılı: {result.get('site', 'N/A')} - {result.get('title', 'N/A')[:30]}...")
                
            except Exception as e:
                print(f"❌ Beklenmeyen hata: {e}")
                results.append({
                    "error": str(e),
                    "url": url,
                    "scraper_type": "none"
                })
            
            # Rate limiting
            await asyncio.sleep(1)
        
        return results
    
    def get_supported_sites(self) -> list:
        """Desteklenen site listesini döndürür"""
        return self.supported_sites.copy()
    
    def add_site_support(self, domain: str, config: dict):
        """Yeni site desteği ekler"""
        if domain not in self.supported_sites:
            self.supported_sites.append(domain)
            # Site konfigürasyonunu ekle
            self.site_scrapers.site_configs[domain] = config
            self.advanced_scrapers.site_configs[domain] = config
            logging.info(f"Yeni site eklendi: {domain}")
        else:
            logging.warning(f"Site zaten destekleniyor: {domain}")

# Test fonksiyonu
async def test_integrated_scraper():
    """Entegre scraper'ı test eder"""
    scraper = IntegratedScraper()
    
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
    
    print("=== ENTEGRE SCRAPER TEST ===")
    print(f"Desteklenen siteler: {len(scraper.get_supported_sites())}")
    
    # Temel scraper test
    print("\n--- Temel Scraper Test ---")
    basic_results = await scraper.scrape_multiple_products(test_urls, use_advanced=False)
    
    # Gelişmiş scraper test
    print("\n--- Gelişmiş Scraper Test ---")
    advanced_results = await scraper.scrape_multiple_products(test_urls, use_advanced=True)
    
    # Sonuçları analiz et
    basic_success = sum(1 for r in basic_results if "error" not in r)
    advanced_success = sum(1 for r in advanced_results if "error" not in r)
    
    print(f"\n📊 Sonuçlar:")
    print(f"   Temel Scraper: {basic_success}/{len(test_urls)} başarılı")
    print(f"   Gelişmiş Scraper: {advanced_success}/{len(test_urls)} başarılı")
    
    return basic_results, advanced_results

# Kullanım örneği
async def example_usage():
    """Kullanım örneği"""
    scraper = IntegratedScraper()
    
    # Tek ürün scrape et
    url = "https://www.beymen.com/tr/p_polo-ralph-lauren-beyaz-oxford-gomlek_1646218"
    result = await scraper.scrape_product(url)
    
    if "error" not in result:
        print(f"✅ Başarılı:")
        print(f"   Site: {result['site']}")
        print(f"   Başlık: {result['title']}")
        print(f"   Güncel Fiyat: {result['current_price']}")
        print(f"   Eski Fiyat: {result['original_price']}")
        print(f"   Scraper Tipi: {result['scraper_type']}")
        print(f"   Scraper Versiyon: {result['scraper_version']}")
    else:
        print(f"❌ Hata: {result['error']}")

if __name__ == "__main__":
    print("🚀 Entegre Scraper Test Başlatılıyor...")
    
    try:
        # Örnek kullanım
        asyncio.run(example_usage())
        
        # Tam test
        # basic_results, advanced_results = asyncio.run(test_integrated_scraper())
        
    except KeyboardInterrupt:
        print("\n⏹️ Test kullanıcı tarafından durduruldu.")
    except Exception as e:
        print(f"\n❌ Test sırasında hata oluştu: {e}")
