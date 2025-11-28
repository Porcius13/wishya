import asyncio
import json
from datetime import datetime
from app_old import scrape_product

TEST_URL = "https://lesbenjamins.com/collections/erkek-ust-giyim/products/relaxed-tee-045-lb25fwturmuts-045?variant=43543390060623"

async def get_product_info():
    """Les Benjamins URL'den ürün bilgilerini çek"""
    print("\n" + "="*80)
    print("LES BENJAMINS URUN BILGILERI")
    print("="*80)
    print(f"URL: {TEST_URL}")
    print("="*80)
    
    start_time = datetime.now()
    
    try:
        result = await scrape_product(TEST_URL)
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"\n{'='*80}")
        print("SONUCLAR:")
        print(f"{'='*80}")
        
        if result:
            print(f"\n[BASLIK]:")
            print(f"   {result.get('name', 'YOK')}")
            
            print(f"\n[FIYAT]:")
            print(f"   {result.get('price', 'YOK')}")
            print(f"   Eski Fiyat: {result.get('old_price', 'YOK')}")
            
            print(f"\n[GORSEL]:")
            image_url = result.get('image')
            if image_url:
                print(f"   {image_url[:100]}...")
                print(f"   Uzunluk: {len(image_url)} karakter")
            else:
                print(f"   YOK")
            
            print(f"\n[MARKA]:")
            print(f"   {result.get('brand', 'YOK')}")
            
            print(f"\n[SURE]: {duration:.2f} saniye")
        else:
            print("HATA: Urun bilgileri cekilemedi.")
        
        return result
        
    except Exception as e:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"\n[HATA]: {e}")
        print(f"Sure: {duration:.2f} saniye")
        import traceback
        traceback.print_exc()
        
        return None

if __name__ == "__main__":
    asyncio.run(get_product_info())

