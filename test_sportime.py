"""
Sportime.com.tr için backtest scripti
Belirtilen URL'yi test eder ve sonuçları gösterir
"""
import asyncio
import json
from datetime import datetime
from app_old import scrape_product

TEST_URL = "https://sportime.com.tr/products/nike-air-max-1-gs-dz3307-112-cocuk-sneaker"

async def test_sportime():
    """Sportime URL'yi test et"""
    print("\n" + "="*80)
    print("SPORTIME.COM.TR BACKTEST")
    print("="*80)
    print(f"URL: {TEST_URL}")
    print("="*80)
    
    start_time = datetime.now()
    
    try:
        result = await scrape_product(TEST_URL)
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"\n{'='*80}")
        print("SONUÇLAR")
        print(f"{'='*80}")
        print(f"Süre: {duration:.2f} saniye")
        print(f"\n[OK] BASLIK:")
        print(f"   {result.get('name', 'YOK') if result else 'HATA'}")
        
        print(f"\n[PRICE] FIYAT:")
        print(f"   {result.get('price', 'YOK') if result else 'HATA'}")
        print(f"   Eski Fiyat: {result.get('old_price', 'YOK') if result else 'HATA'}")
        
        print(f"\n[IMAGE] GORSEL:")
        image_url = result.get('image') if result else None
        if image_url:
            print(f"   {image_url[:100]}...")
            print(f"   Uzunluk: {len(image_url)} karakter")
        else:
            print(f"   YOK")
        
        print(f"\n[BRAND] MARKA:")
        print(f"   {result.get('brand', 'YOK') if result else 'HATA'}")
        
        # Doğrulama
        print(f"\n{'='*80}")
        print("DOGRULAMA")
        print(f"{'='*80}")
        
        success = result and result.get('name') and result.get('name') != "İsim bulunamadı"
        has_price = result and result.get('price') and result.get('price') != "Fiyat bulunamadı"
        has_image = result and result.get('image')
        price_valid = False
        
        if has_price:
            price_str = str(result.get('price', ''))
            import re
            if re.search(r'\d', price_str):
                price_valid = True
        
        print(f"Baslik: {'[OK] VAR' if success else '[FAIL] YOK'}")
        print(f"Fiyat: {'[OK] VAR' if has_price else '[FAIL] YOK'}")
        print(f"Fiyat Gecerli: {'[OK] EVET' if price_valid else '[FAIL] HAYIR'}")
        print(f"Gorsel: {'[OK] VAR' if has_image else '[FAIL] YOK'}")
        
        if has_image:
            # Görsel URL kontrolü ve düzeltme
            if '&width=' in image_url or '?width=' in image_url:
                # Width parametresini kaldır veya büyüt
                import re
                image_url = re.sub(r'[?&]width=\d+', '', image_url)
                # Eğer width parametresi varsa, büyük bir değer ekle
                if '?' in image_url:
                    image_url += '&width=1000'
                else:
                    image_url += '?width=1000'
                print(f"[UYARI] Gorsel URL'deki width parametresi duzeltildi")
                print(f"Yeni URL: {image_url[:100]}...")
            
            if 'sportime.com.tr' in image_url or 'cdn.shopify.com' in image_url or 'shopify' in image_url.lower():
                print(f"Gorsel URL: [OK] DOGRU (Sportime/Shopify)")
            else:
                print(f"Gorsel URL: [WARN] FARKLI DOMAIN")
        
        # Sonuçları JSON'a kaydet
        report = {
            'test_date': datetime.now().isoformat(),
            'url': TEST_URL,
            'duration': duration,
            'success': success,
            'has_price': has_price,
            'price_valid': price_valid,
            'has_image': has_image,
            'result': result
        }
        
        filename = f'sportime_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n📊 Detaylı sonuçlar '{filename}' dosyasına kaydedildi.")
        
        return report
        
    except Exception as e:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"\n[ERROR] HATA")
        print(f"Süre: {duration:.2f} saniye")
        print(f"Hata: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return None

if __name__ == "__main__":
    asyncio.run(test_sportime())

