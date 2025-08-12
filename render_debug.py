#!/usr/bin/env python3
"""
Render Debug Script - Görsel Çekme Sorunları İçin
Bu script Render üzerinde görsel çekme sorunlarını debug etmek için kullanılır.
"""

import asyncio
import os
import sys
from playwright.async_api import async_playwright
import json
from datetime import datetime

async def debug_image_extraction(url):
    """Görsel çekme işlemini debug et"""
    print(f"[DEBUG] Görsel çekme debug başlıyor: {url}")
    print(f"[DEBUG] Render environment: {os.environ.get('RENDER', 'False')}")
    print(f"[DEBUG] Current working directory: {os.getcwd()}")
    
    try:
        async with async_playwright() as p:
            # Browser'ı başlat
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-gpu',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor',
                ]
            )
            
            # Context oluştur
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
                viewport={'width': 390, 'height': 844},
                locale='tr-TR',
                timezone_id='Europe/Istanbul',
            )
            
            # Sayfa oluştur
            page = await context.new_page()
            
            print(f"[DEBUG] Sayfa oluşturuldu, URL'ye gidiliyor...")
            
            # URL'ye git
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            print(f"[DEBUG] Sayfa yüklendi")
            
            # Sayfa başlığını kontrol et
            title = await page.title()
            print(f"[DEBUG] Sayfa başlığı: {title}")
            
            # 5 saniye bekle
            await page.wait_for_timeout(5000)
            print(f"[DEBUG] 5 saniye beklendi")
            
            # Scroll yap
            await page.evaluate("window.scrollTo(0, 300)")
            await page.wait_for_timeout(2000)
            await page.evaluate("window.scrollTo(0, 600)")
            await page.wait_for_timeout(2000)
            print(f"[DEBUG] Scroll işlemleri tamamlandı")
            
            # Tüm img elementlerini bul
            all_images = await page.evaluate("""
                () => {
                    const images = Array.from(document.querySelectorAll('img'));
                    return images.map(img => ({
                        src: img.src,
                        alt: img.alt || '',
                        width: img.naturalWidth || img.width,
                        height: img.naturalHeight || img.height,
                        className: img.className || '',
                        id: img.id || '',
                        dataTestId: img.getAttribute('data-testid') || '',
                        loading: img.loading || '',
                        complete: img.complete
                    }));
                }
            """)
            
            print(f"[DEBUG] Toplam {len(all_images)} img elementi bulundu")
            
            # Görselleri filtrele ve analiz et
            valid_images = []
            for i, img in enumerate(all_images):
                if img['src'] and img['src'].strip():
                    # Logo, icon gibi görselleri filtrele
                    if not any(skip in img['src'].lower() for skip in ['logo', 'icon', 'banner', 'header', 'footer', 'avatar', 'profile']):
                        size = img['width'] * img['height']
                        valid_images.append({
                            'index': i,
                            'src': img['src'],
                            'alt': img['alt'],
                            'width': img['width'],
                            'height': img['height'],
                            'size': size,
                            'className': img['className'],
                            'id': img['id'],
                            'dataTestId': img['dataTestId'],
                            'loading': img['loading'],
                            'complete': img['complete']
                        })
            
            print(f"[DEBUG] {len(valid_images)} geçerli görsel bulundu")
            
            # Görselleri boyuta göre sırala
            valid_images.sort(key=lambda x: x['size'], reverse=True)
            
            # En büyük 5 görseli göster
            print(f"\n[DEBUG] En büyük 5 görsel:")
            for i, img in enumerate(valid_images[:5]):
                print(f"  {i+1}. {img['src']}")
                print(f"     Boyut: {img['width']}x{img['height']} ({img['size']} piksel)")
                print(f"     Alt: {img['alt']}")
                print(f"     Class: {img['className']}")
                print(f"     ID: {img['id']}")
                print(f"     Data-testid: {img['dataTestId']}")
                print(f"     Loading: {img['loading']}")
                print(f"     Complete: {img['complete']}")
                print()
            
            # Sayfanın HTML'ini kaydet (debug için)
            html_content = await page.content()
            with open('debug_page.html', 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"[DEBUG] HTML içeriği debug_page.html dosyasına kaydedildi")
            
            # Screenshot al
            await page.screenshot(path='debug_screenshot.png', full_page=True)
            print(f"[DEBUG] Screenshot debug_screenshot.png dosyasına kaydedildi")
            
            # Sonuçları JSON olarak kaydet
            debug_result = {
                'url': url,
                'timestamp': datetime.now().isoformat(),
                'page_title': title,
                'total_images': len(all_images),
                'valid_images': len(valid_images),
                'top_images': valid_images[:10],
                'render_environment': os.environ.get('RENDER', 'False'),
                'working_directory': os.getcwd()
            }
            
            with open('debug_result.json', 'w', encoding='utf-8') as f:
                json.dump(debug_result, f, indent=2, ensure_ascii=False)
            print(f"[DEBUG] Debug sonuçları debug_result.json dosyasına kaydedildi")
            
            await browser.close()
            
            return debug_result
            
    except Exception as e:
        print(f"[ERROR] Debug sırasında hata: {e}")
        return {'error': str(e)}

async def main():
    """Ana fonksiyon"""
    if len(sys.argv) != 2:
        print("Kullanım: python render_debug.py <URL>")
        sys.exit(1)
    
    url = sys.argv[1]
    result = await debug_image_extraction(url)
    
    if 'error' in result:
        print(f"[ERROR] Debug başarısız: {result['error']}")
        sys.exit(1)
    else:
        print(f"[SUCCESS] Debug tamamlandı!")
        print(f"Toplam görsel: {result['total_images']}")
        print(f"Geçerli görsel: {result['valid_images']}")
        
        if result['valid_images'] > 0:
            best_image = result['top_images'][0]
            print(f"En iyi görsel: {best_image['src']}")
        else:
            print("Hiç geçerli görsel bulunamadı!")

if __name__ == "__main__":
    asyncio.run(main())
