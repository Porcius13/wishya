import asyncio
import logging
from playwright.async_api import async_playwright

# Logging ayarları
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def test_adidas_directly():
    """Adidas URL'sini doğrudan test et"""
    
    url = "https://www.adidas.com.tr/tr/sl-72-rs-ayakkabi/JS0749.html"
    
    print(f"=== ADIDAS TEST ===\n")
    print(f"URL: {url}")
    
    try:
        async with async_playwright() as p:
            # Farklı browser seçenekleri dene
            browsers = [
                ("chromium", {"headless": True}),
                ("firefox", {"headless": True}),
                ("webkit", {"headless": True})
            ]
            
            for browser_name, browser_options in browsers:
                print(f"\n--- {browser_name.upper()} ile test ---")
                
                try:
                    if browser_name == "chromium":
                        browser = await p.chromium.launch(**browser_options)
                    elif browser_name == "firefox":
                        browser = await p.firefox.launch(**browser_options)
                    else:
                        browser = await p.webkit.launch(**browser_options)
                    
                    context = await browser.new_context(
                        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                        viewport={'width': 1920, 'height': 1080},
                        extra_http_headers={
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                            'Accept-Language': 'tr-TR,tr;q=0.9,en;q=0.8',
                            'Accept-Encoding': 'gzip, deflate, br',
                            'DNT': '1',
                            'Connection': 'keep-alive',
                            'Upgrade-Insecure-Requests': '1',
                        }
                    )
                    
                    page = await context.new_page()
                    
                    # Sayfa yükleme optimizasyonları
                    await page.route("**/*.{png,jpg,jpeg,gif,svg,webp}", lambda route: route.abort())
                    await page.route("**/*.{css,woff,woff2,ttf}", lambda route: route.abort())
                    
                    print(f"Sayfaya gidiliyor...")
                    
                    # Farklı wait_until seçenekleri dene
                    try:
                        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                        print(f"✅ Sayfa yüklendi (domcontentloaded)")
                    except Exception as e1:
                        print(f"❌ domcontentloaded başarısız: {e1}")
                        try:
                            await page.goto(url, wait_until="load", timeout=30000)
                            print(f"✅ Sayfa yüklendi (load)")
                        except Exception as e2:
                            print(f"❌ load başarısız: {e2}")
                            try:
                                await page.goto(url, wait_until="commit", timeout=30000)
                                print(f"✅ Sayfa yüklendi (commit)")
                            except Exception as e3:
                                print(f"❌ commit başarısız: {e3}")
                                continue
                    
                    await page.wait_for_timeout(5000)
                    
                    # Sayfa başlığını kontrol et
                    title = await page.title()
                    print(f"Sayfa başlığı: {title}")
                    
                    # URL'yi kontrol et
                    current_url = page.url
                    print(f"Güncel URL: {current_url}")
                    
                    # Ürün verilerini çekmeye çalış
                    try:
                        # Başlık arama
                        title_selectors = [
                            "h1",
                            "h1[class*='product']",
                            "h1[class*='title']",
                            "[data-testid='product-name']",
                            "[data-qa-action='product-name']",
                            ".product-name",
                            ".product-title"
                        ]
                        
                        product_title = ""
                        for selector in title_selectors:
                            try:
                                element = await page.query_selector(selector)
                                if element:
                                    text = await element.inner_text()
                                    if text and len(text.strip()) > 5:
                                        product_title = text.strip()
                                        print(f"✅ Başlık bulundu: {product_title}")
                                        break
                            except:
                                continue
                        
                        # Fiyat arama
                        price_selectors = [
                            "[data-testid='price']",
                            "[data-qa-action='price']",
                            ".price",
                            ".product-price",
                            "[class*='price']",
                            "span[class*='price']"
                        ]
                        
                        product_price = ""
                        for selector in price_selectors:
                            try:
                                element = await page.query_selector(selector)
                                if element:
                                    text = await element.inner_text()
                                    if text and any(char.isdigit() for char in text):
                                        product_price = text.strip()
                                        print(f"✅ Fiyat bulundu: {product_price}")
                                        break
                            except:
                                continue
                        
                        # Görsel arama
                        image_selectors = [
                            "img[class*='product']",
                            "img[class*='image']",
                            "img[loading='lazy']",
                            "img[alt*='product']",
                            "img[src*='product']"
                        ]
                        
                        product_image = ""
                        for selector in image_selectors:
                            try:
                                element = await page.query_selector(selector)
                                if element:
                                    src = await element.get_attribute("src")
                                    if src and src.startswith("http"):
                                        product_image = src
                                        print(f"✅ Görsel bulundu: {src[:80]}...")
                                        break
                            except:
                                continue
                        
                        if product_title or product_price:
                            print(f"\n🎉 BAŞARILI! {browser_name} ile veri çekildi")
                            print(f"Başlık: {product_title}")
                            print(f"Fiyat: {product_price}")
                            print(f"Görsel: {product_image[:80] if product_image else 'N/A'}...")
                            await browser.close()
                            return True
                        else:
                            print(f"❌ Veri bulunamadı")
                    
                    except Exception as e:
                        print(f"❌ Veri çekme hatası: {e}")
                    
                    await browser.close()
                    
                except Exception as e:
                    print(f"❌ {browser_name} hatası: {e}")
                    continue
    
    except Exception as e:
        print(f"❌ Genel hata: {e}")
    
    return False

if __name__ == "__main__":
    asyncio.run(test_adidas_directly())
