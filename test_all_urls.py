import asyncio
import logging
from universal_scraper import UniversalScraper

# Logging ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def test_all_urls():
    """Tüm URL'leri test et"""
    
    # Test edilecek URL'ler
    urls = [
        "https://tr.uspoloassn.com/erkek-su-yesili-basic-tisort-50305929-vr048/",
        "https://www.jimmykey.com/tr/rahat-kesim-yuvarlak-yaka-kolsuz-mini-elbise_5sw064757/acik-vizon/22",
        "https://www.mavi.com/keten-karisimli-kahverengi-gomlek/p/0211616-82337?_gl=1*1avmh4n*_up*MQ..&gclid=CjwKCAjwy7HEBhBJEiwA5hQNouZhWNJEtU7ihoGNGWao4goy9iCUQ4NiUA4aR-UjngjUy-gVszxk_xoCAaIQAvD_BwE",
        "https://www.twist.com.tr/urun/gri-sort-tr-17716",
        "https://tr.benetton.com/kiz-bebek/kiz-bebek-pembe-mix-kolu-logo-detayli-astarli-kapusonlu-yagmurluk_164594",
        "https://www.reebok.com.tr/urun/reebok-new-id-ovrs-gfx-tee-mavi-erkek-kisa-kol-t-shirt-102055767",
        "https://www.adidas.com.tr/tr/sl-72-rs-ayakkabi/JS0749.html",
        "https://www.newbalance.com.tr/urun/new-balance-mnt3326-1183",
        "https://www.cizgimedikal.com/luks-likrali-uniforma-takimlar-tr-43/",
        "https://www.notusuniform.com/urun/petrol-yesili-klasik-erkek-uniforma-takim",
        "https://ontrailstore.com/products/ahsap-katlanir-masa?variant=42614447702240",
        "https://www.ellesse.com.tr/products/ellesse-erkek-polo-yaka-tisort-em460-bk",
        "https://www.superstep.com.tr/urun/adidas-inter-miami-cf-erkek-pembe-sweatshirt/ji6907/",
        "https://www.instreet.com.tr/urun/us-polo-assn-noah-5fx-beyaz-erkek-sneaker-101947861",
        "https://www.crocs.com.tr/urun/mellow-luxe-recovery-slide-black/",
        "https://www.lufian.com/gage-erkek-deri-sneaker-ayakkabi-siyah-8641",
        "https://www.suvari.com.tr/lacivert-slim-fit-duz-dugmeli-yaka-gomlek-gm2008100111-m09",
        "https://www.suwen.com.tr/p/pembe-tina-maskulen-pijama-takimi-sh25722660b334",
        "https://www.mavi.com/yesil-kargo-sort/p/0410203-71581",
        "https://www.ltbjeans.com/tr-TR/p/regular-askili-siyah-t-shirt-01225843036143_200"
    ]
    
    scraper = UniversalScraper()
    
    print("=== TÜM URL'LERİN TEST EDİLMESİ ===\n")
    
    successful_count = 0
    failed_count = 0
    
    for i, url in enumerate(urls, 1):
        print(f"\n--- TEST {i}/{len(urls)} ---")
        print(f"URL: {url}")
        
        try:
            result = await scraper.scrape_product(url, max_retries=2)
            
            if result:
                print(f"✅ BAŞARILI")
                print(f"   Başlık: {result.get('title', 'N/A')}")
                print(f"   Fiyat: {result.get('price', 'N/A')}")
                print(f"   Marka: {result.get('brand', 'N/A')}")
                print(f"   Site: {result.get('site', 'N/A')}")
                if result.get('image'):
                    print(f"   Görsel: {result['image'][:80]}...")
                if result.get('original_price'):
                    print(f"   İndirimsiz Fiyat: {result['original_price']}")
                successful_count += 1
            else:
                print(f"❌ BAŞARISIZ - Veri çekilemedi")
                failed_count += 1
                
        except Exception as e:
            print(f"❌ HATA - {str(e)}")
            failed_count += 1
    
    print(f"\n=== SONUÇLAR ===")
    print(f"Başarılı: {successful_count}")
    print(f"Başarısız: {failed_count}")
    print(f"Toplam: {len(urls)}")
    print(f"Başarı Oranı: {(successful_count/len(urls)*100):.1f}%")

if __name__ == "__main__":
    asyncio.run(test_all_urls())
