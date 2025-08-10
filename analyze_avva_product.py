#!/usr/bin/env python3
"""
AVVA Ürün Analiz Scripti
Son eklenen AVVA ürününün scraping sonuçlarını analiz eder
"""

import asyncio
from app import scrape_product

async def analyze_avva_product():
    """AVVA ürününü analiz et"""
    url = "https://www.avva.com.tr/siyah-bisiklet-yaka-enjeksiyon-transfer-cep-baskili-interlok-t-shirt-37158"
    
    print("=== AVVA ÜRÜN ANALİZİ ===")
    print(f"🔗 URL: {url}")
    print("⏳ Scraping başlıyor...")
    
    try:
        result = await scrape_product(url)
        
        if result:
            print("✅ Scraping başarılı!")
            print(f"📦 Ürün Adı: {result['name']}")
            print(f"💰 Fiyat: {result['price']}")
            print(f"🏷️ Marka: {result['brand']}")
            print(f"🖼️ Görsel: {'Var' if result['image'] else 'Yok'}")
            print(f"📏 Bedenler: {len(result['sizes'])} adet")
            print(f"📅 Eski Fiyat: {result['old_price'] or 'Yok'}")
            
            print("\n=== SORUN ANALİZİ ===")
            issues = []
            
            if not result['image']:
                issues.append("❌ Ürün görseli çekilemedi")
            if not result['sizes']:
                issues.append("❌ Beden bilgisi çekilemedi")
            if not result['old_price']:
                issues.append("⚠️ Eski fiyat bilgisi yok (normal olabilir)")
            
            if issues:
                print("Tespit edilen sorunlar:")
                for issue in issues:
                    print(f"  {issue}")
            else:
                print("✅ Hiçbir sorun tespit edilmedi!")
                
        else:
            print("❌ Scraping başarısız!")
            
    except Exception as e:
        print(f"❌ Hata oluştu: {e}")

if __name__ == "__main__":
    asyncio.run(analyze_avva_product())
