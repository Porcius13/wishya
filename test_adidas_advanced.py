import asyncio
import logging
from playwright.async_api import async_playwright
import time

# Logging ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def test_adidas_advanced():
    """Adidas için gelişmiş test"""
    
    url = "https://www.adidas.com.tr/tr/sl-72-rs-ayakkabi/JS0749.html"
    
    print(f"=== ADIDAS GELİŞMİŞ TEST ===\n")
    print(f"URL: {url}")
    
    try:
        async with async_playwright() as p:
            # Firefox ile dene (HTTP/2 sorunu olmayabilir)
            browser = await p.firefox.launch(
                headless=False,  # Görsel olarak izle
                args=[
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-setuid-sandbox'
                ]
            )
            
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
                viewport={'width': 1920, 'height': 1080},
                extra_http_headers={
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                    'Accept-Language': 'tr-TR,tr;q=0.9,en;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1',
                    'Cache-Control': 'max-age=0'
                }
            )
            
            page = await context.new_page()
            
            print(f"Sayfaya gidiliyor...")
            
            try:
                # Önce ana sayfaya git
                await page.goto("https://www.adidas.com.tr/", wait_until="domcontentloaded", timeout=30000)
                print(f"✅ Ana sayfa yüklendi")
                await page.wait_for_timeout(3000)
                
                # Şimdi ürün sayfasına git
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                print(f"✅ Ürün sayfası yüklendi")
                
                # Sayfanın tam yüklenmesini bekle
                await page.wait_for_timeout(10000)
                
                # Sayfa başlığını kontrol et
                title = await page.title()
                print(f"Sayfa başlığı: {title}")
                
                # URL'yi kontrol et
                current_url = page.url
                print(f"Güncel URL: {current_url}")
                
                # Sayfanın HTML içeriğini kontrol et
                html_content = await page.content()
                print(f"HTML uzunluğu: {len(html_content)} karakter")
                
                # JavaScript'in çalışmasını bekle
                await page.wait_for_timeout(5000)
                
                # Farklı selector'ları dene
                selectors_to_try = {
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
                }
                
                results = {}
                
                for field, field_selectors in selectors_to_try.items():
                    print(f"\n--- {field.upper()} ARAMA ---")
                    
                    for selector in field_selectors:
                        try:
                            elements = await page.query_selector_all(selector)
                            print(f"  {selector}: {len(elements)} element bulundu")
                            
                            for i, element in enumerate(elements[:3]):  # İlk 3 elementi kontrol et
                                try:
                                    if field == "image":
                                        value = await element.get_attribute("src")
                                    else:
                                        value = await element.inner_text()
                                    
                                    if value and value.strip():
                                        print(f"    Element {i+1}: {value[:100]}...")
                                        if field not in results:
                                            results[field] = value.strip()
                                            break
                                except Exception as e:
                                    continue
                            
                            if field in results:
                                break
                                
                        except Exception as e:
                            continue
                
                # JavaScript ile veri çekmeyi dene
                print(f"\n--- JAVASCRIPT İLE VERİ ÇEKME ---")
                
                js_results = await page.evaluate("""
                    () => {
                        const results = {};
                        
                        // Başlık arama
                        const titleSelectors = [
                            'h1',
                            '[data-testid="product-name"]',
                            '[data-qa-action="product-name"]',
                            '.product-name',
                            '.product-title',
                            '.gl-product-card__name',
                            '.gl-product-card__title'
                        ];
                        
                        for (const selector of titleSelectors) {
                            const element = document.querySelector(selector);
                            if (element && element.textContent.trim()) {
                                results.title = element.textContent.trim();
                                break;
                            }
                        }
                        
                        // Fiyat arama
                        const priceSelectors = [
                            '[data-testid="price"]',
                            '[data-qa-action="price"]',
                            '.price',
                            '.product-price',
                            '.gl-price',
                            '.gl-price__value',
                            '[data-auto-id="product-price"]'
                        ];
                        
                        for (const selector of priceSelectors) {
                            const element = document.querySelector(selector);
                            if (element && element.textContent.trim()) {
                                results.price = element.textContent.trim();
                                break;
                            }
                        }
                        
                        // Görsel arama
                        const imageSelectors = [
                            'img[class*="product"]',
                            'img[class*="image"]',
                            '.gl-product-card__image img',
                            '.gl-product-card__media img'
                        ];
                        
                        for (const selector of imageSelectors) {
                            const element = document.querySelector(selector);
                            if (element && element.src) {
                                results.image = element.src;
                                break;
                            }
                        }
                        
                        return results;
                    }
                """)
                
                print(f"JavaScript sonuçları: {js_results}")
                
                # Sonuçları birleştir
                final_results = {**results, **js_results}
                
                if final_results:
                    print(f"\n🎉 BAŞARILI! Veri çekildi")
                    for key, value in final_results.items():
                        print(f"{key.capitalize()}: {value}")
                    return final_results
                else:
                    print(f"\n❌ Veri bulunamadı")
                    
                    # Sayfanın screenshot'ını al
                    await page.screenshot(path="adidas_debug.png")
                    print(f"Debug screenshot kaydedildi: adidas_debug.png")
                    
                    return None
                    
            except Exception as e:
                print(f"❌ Sayfa yükleme hatası: {e}")
                return None
            finally:
                await browser.close()
    
    except Exception as e:
        print(f"❌ Genel hata: {e}")
        return None

if __name__ == "__main__":
    asyncio.run(test_adidas_advanced())
