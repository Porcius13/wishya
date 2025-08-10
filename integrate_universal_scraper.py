#!/usr/bin/env python3
"""
Evrensel Scraper Entegrasyon Dosyası
Mevcut projeye UniversalScraper'ı entegre eder
"""

import asyncio
import logging
from universal_scraper import UniversalScraper
from typing import Dict, List, Optional, Any

# Logging ayarları
logging.basicConfig(level=logging.INFO)

class IntegratedScraper:
    """
    Mevcut proje ile entegre edilmiş scraper
    UniversalScraper'ı kullanarak gelişmiş özellikler sağlar
    """
    
    def __init__(self):
        self.universal_scraper = UniversalScraper()
        self.scraping_history = []
        self.failed_urls = []
        
    async def scrape_with_fallback(self, url: str, max_retries: int = 3) -> Optional[Dict[str, Any]]:
        """
        Fallback mekanizması ile scraping
        Önce UniversalScraper, sonra mevcut scraper'ları dener
        """
        logging.info(f"[ENTEGRASYON] Scraping başlatılıyor: {url}")
        
        # 1. UniversalScraper ile dene
        result = await self.universal_scraper.scrape_product(url, max_retries)
        
        if result:
            logging.info(f"[ENTEGRASYON] UniversalScraper başarılı: {url}")
            self.scraping_history.append({
                "url": url,
                "method": "universal",
                "success": True,
                "timestamp": result.get("scraped_at", "")
            })
            return result
        
        # 2. Site özel scraper'ları dene
        result = await self._try_site_specific_scrapers(url)
        
        if result:
            logging.info(f"[ENTEGRASYON] Site özel scraper başarılı: {url}")
            self.scraping_history.append({
                "url": url,
                "method": "site_specific",
                "success": True,
                "timestamp": result.get("scraped_at", "")
            })
            return result
        
        # 3. Başarısız
        logging.error(f"[ENTEGRASYON] Tüm yöntemler başarısız: {url}")
        self.failed_urls.append(url)
        self.scraping_history.append({
            "url": url,
            "method": "all_failed",
            "success": False,
            "timestamp": ""
        })
        return None
    
    async def _try_site_specific_scrapers(self, url: str) -> Optional[Dict[str, Any]]:
        """Site özel scraper'ları dener"""
        try:
            # Hepsiburada için Selenium scraper
            if "hepsiburada.com" in url:
                try:
                    from selenium_hepsiburada_scraper import scrape_hepsiburada_product
                    result = scrape_hepsiburada_product(url)
                    if result:
                        return self._convert_to_universal_format(result, "Hepsiburada")
                except ImportError:
                    logging.debug("[ENTEGRASYON] Selenium scraper bulunamadı")
            
            # Sahibinden için özel scraper
            elif "sahibinden.com" in url:
                try:
                    from sahibinden_scraper import SahibindenScraper
                    scraper = SahibindenScraper()
                    result = scraper.scrape_product(url)
                    if result:
                        return self._convert_to_universal_format(result, "Sahibinden")
                except ImportError:
                    logging.debug("[ENTEGRASYON] Sahibinden scraper bulunamadı")
            
            # Genel scraper
            else:
                try:
                    from scraper import scrape_product
                    result = scrape_product(url)
                    if result:
                        return self._convert_to_universal_format(result, "General")
                except ImportError:
                    logging.debug("[ENTEGRASYON] Genel scraper bulunamadı")
                    
        except Exception as e:
            logging.error(f"[ENTEGRASYON] Site özel scraper hatası: {e}")
        
        return None
    
    def _convert_to_universal_format(self, result: Dict[str, Any], site_name: str) -> Dict[str, Any]:
        """Mevcut scraper sonuçlarını evrensel formata çevirir"""
        import time
        
        # Farklı scraper'ların farklı alan isimleri olabilir
        title = result.get("title", result.get("name", ""))
        price = result.get("price", result.get("current_price", ""))
        image = result.get("image", result.get("img", ""))
        brand = result.get("brand", "UNKNOWN")
        
        return {
            "title": title,
            "price": price,
            "image": image,
            "brand": brand,
            "url": result.get("url", ""),
            "site": site_name,
            "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "original_price": result.get("original_price", "")
        }
    
    def scrape_sync(self, url: str, max_retries: int = 3) -> Optional[Dict[str, Any]]:
        """Senkron scraping"""
        return asyncio.run(self.scrape_with_fallback(url, max_retries))
    
    async def scrape_multiple_with_fallback(self, urls: List[str], max_retries: int = 3) -> List[Dict[str, Any]]:
        """Birden fazla URL'yi fallback ile scrape et"""
        results = []
        
        for url in urls:
            result = await self.scrape_with_fallback(url, max_retries)
            if result:
                results.append(result)
            
            # Rate limiting
            await asyncio.sleep(2)
        
        return results
    
    def get_scraping_stats(self) -> Dict[str, Any]:
        """Scraping istatistiklerini döndürür"""
        total_attempts = len(self.scraping_history)
        successful = len([h for h in self.scraping_history if h["success"]])
        failed = total_attempts - successful
        
        method_stats = {}
        for history in self.scraping_history:
            method = history["method"]
            if method not in method_stats:
                method_stats[method] = {"success": 0, "failed": 0}
            
            if history["success"]:
                method_stats[method]["success"] += 1
            else:
                method_stats[method]["failed"] += 1
        
        return {
            "total_attempts": total_attempts,
            "successful": successful,
            "failed": failed,
            "success_rate": (successful / total_attempts * 100) if total_attempts > 0 else 0,
            "method_stats": method_stats,
            "failed_urls": self.failed_urls
        }
    
    def add_custom_site_config(self, domain: str, config: Dict[str, Any]):
        """Özel site konfigürasyonu ekle"""
        self.universal_scraper.add_site_config(domain, config)
        logging.info(f"[ENTEGRASYON] Özel konfigürasyon eklendi: {domain}")
    
    def save_configs(self, filename: str = "integrated_configs.json"):
        """Konfigürasyonları kaydet"""
        self.universal_scraper.save_configs(filename)
        logging.info(f"[ENTEGRASYON] Konfigürasyonlar kaydedildi: {filename}")
    
    def load_configs(self, filename: str = "integrated_configs.json"):
        """Konfigürasyonları yükle"""
        self.universal_scraper.load_configs(filename)
        logging.info(f"[ENTEGRASYON] Konfigürasyonlar yüklendi: {filename}")


# Flask uygulaması entegrasyonu için yardımcı fonksiyonlar
def integrate_with_flask_app(app):
    """Flask uygulamasına entegre et"""
    integrated_scraper = IntegratedScraper()
    
    @app.route('/api/scrape', methods=['POST'])
    def scrape_product_api():
        """API endpoint for scraping"""
        from flask import request, jsonify
        
        try:
            data = request.get_json()
            url = data.get('url')
            
            if not url:
                return jsonify({"error": "URL gerekli"}), 400
            
            result = integrated_scraper.scrape_sync(url)
            
            if result:
                return jsonify({
                    "success": True,
                    "data": result,
                    "stats": integrated_scraper.get_scraping_stats()
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "Veri çekilemedi",
                    "stats": integrated_scraper.get_scraping_stats()
                }), 404
                
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/scrape/batch', methods=['POST'])
    def scrape_multiple_products_api():
        """Toplu scraping API endpoint"""
        from flask import request, jsonify
        
        try:
            data = request.get_json()
            urls = data.get('urls', [])
            
            if not urls:
                return jsonify({"error": "URL listesi gerekli"}), 400
            
            results = asyncio.run(integrated_scraper.scrape_multiple_with_fallback(urls))
            
            return jsonify({
                "success": True,
                "data": results,
                "stats": integrated_scraper.get_scraping_stats()
            })
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/scrape/stats', methods=['GET'])
    def get_scraping_stats_api():
        """Scraping istatistikleri API endpoint"""
        from flask import jsonify
        
        return jsonify(integrated_scraper.get_scraping_stats())
    
    return integrated_scraper


# Mevcut app.py entegrasyonu için örnek
def update_existing_app():
    """Mevcut app.py dosyasını güncelle"""
    
    # app.py'ye eklenecek import
    integration_code = '''
# Universal Scraper Entegrasyonu
from integrate_universal_scraper import IntegratedScraper

# Global scraper instance
integrated_scraper = IntegratedScraper()

# Mevcut scrape_product fonksiyonunu güncelle
def scrape_product(url):
    """Gelişmiş ürün scraping"""
    return integrated_scraper.scrape_sync(url)

# Yeni API endpoint'leri ekle
@app.route('/api/v2/scrape', methods=['POST'])
def scrape_product_v2():
    """Gelişmiş scraping API"""
    from flask import request, jsonify
    
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({"error": "URL gerekli"}), 400
        
        result = integrated_scraper.scrape_sync(url)
        
        if result:
            return jsonify({
                "success": True,
                "data": result,
                "stats": integrated_scraper.get_scraping_stats()
            })
        else:
            return jsonify({
                "success": False,
                "error": "Veri çekilemedi",
                "stats": integrated_scraper.get_scraping_stats()
            }), 404
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/v2/stats', methods=['GET'])
def get_scraping_stats():
    """Scraping istatistikleri"""
    from flask import jsonify
    return jsonify(integrated_scraper.get_scraping_stats())
'''
    
    return integration_code


# Test fonksiyonu
def test_integration():
    """Entegrasyon testi"""
    print("=== Entegrasyon Testi ===")
    
    integrated_scraper = IntegratedScraper()
    
    # Test URL'leri
    test_urls = [
        "https://www.hepsiburada.com/gipta-pera-ciltli-deri-kapak-9x14-cizgisiz-defter-pm-HBC00002QG0EE",
        "https://www.sahibinden.com/ilan/vasita-arazi-suv-pickup-lada-turkiye-de-tek-lada-niva-dolu-dolu-asiri-emek-verilmis-restore-1249924513/detay",
        "https://www.zara.com/tr/tr/oversize-blazer-p04234543.html"
    ]
    
    print("Tek tek test...")
    for url in test_urls:
        print(f"\n--- {url} ---")
        result = integrated_scraper.scrape_sync(url)
        
        if result:
            print(f"✅ Başarılı: {result['site']} - {result['title'][:50]}...")
        else:
            print("❌ Başarısız")
    
    print("\nToplu test...")
    results = asyncio.run(integrated_scraper.scrape_multiple_with_fallback(test_urls))
    print(f"Başarılı: {len(results)}/{len(test_urls)}")
    
    print("\nİstatistikler:")
    stats = integrated_scraper.get_scraping_stats()
    for key, value in stats.items():
        if key != "failed_urls":
            print(f"  {key}: {value}")


if __name__ == "__main__":
    test_integration()
