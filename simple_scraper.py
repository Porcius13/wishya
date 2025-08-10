import uuid
import re
import traceback
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, redirect, url_for
import time
import random

app = Flask(__name__)
products = []

BRANDS = [
    ("koton.com", "Koton"),
    ("ltbjeans.com", "LTB Jeans"),
    ("colins.com.tr", "Colin's"),
    ("defacto.com.tr", "Defacto"),
    ("boyner.com.tr", "Boyner"),
    ("superstep.com.tr", "Superstep"),
    ("catiuniform.com", "Çatı Uniform"),
    ("oysho.com", "Oysho"),
    ("mango.com", "Mango"),
    ("zara.com", "Zara"),
    ("bershka.com", "Bershka"),
    ("stradivarius.com", "Stradivarius"),
    ("pullandbear.com", "Pull&Bear"),
    ("hm.com", "H&M"),
    ("lcwaikiki.com", "LC Waikiki"),
    ("trendyol.com", "Trendyol"),
    ("adidas.com.tr", "Adidas"),
    ("nike.com", "Nike"),
    ("penti.com", "Penti"),
    ("mavi.com", "Mavi"),
]

def get_headers():
    """Gerçekçi headers oluştur"""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15"
    ]
    
    return {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
        'DNT': '1',
        'Referer': 'https://www.google.com/',
    }

def scrape_product(url):
    print(f"[DEBUG] Scraping başlıyor: {url}")
    
    # Marka tespiti
    brand = "Bilinmiyor"
    try:
        for domain, brand_name in BRANDS:
            if domain in url:
                brand = brand_name
                break
    except:
        pass
    
    try:
        # Session oluştur
        session = requests.Session()
        session.headers.update(get_headers())
        
        # Önce ana sayfaya git (bot korumasını aşmak için)
        try:
            if "mango.com" in url:
                session.get("https://shop.mango.com/tr", timeout=10)
                time.sleep(2)
            elif "zara.com" in url:
                session.get("https://www.zara.com/tr/", timeout=10)
                time.sleep(2)
            elif "bershka.com" in url:
                session.get("https://www.bershka.com/tr/", timeout=10)
                time.sleep(2)
        except:
            pass
        
        # Ürün sayfasını çek
        response = session.get(url, timeout=30)
        response.raise_for_status()
        
        # BeautifulSoup ile parse et
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Başlık çek
        title = None
        try:
            title_selectors = [
                'h1[data-testid="product-detail-name"]',
                'h1.product-name',
                'h1.product-title',
                'h1.title',
                'h1',
                'title'
            ]
            
            for selector in title_selectors:
                try:
                    if selector == 'title':
                        title_element = soup.find('title')
                        if title_element:
                            title = title_element.get_text()
                    else:
                        title_element = soup.select_one(selector)
                        if title_element:
                            title = title_element.get_text()
                    
                    if title and title.strip():
                        title = title.strip().upper()
                        title = re.sub(r'[^\w\s\-\.]', '', title)
                        title = re.sub(r'\s+', ' ', title).strip()
                        break
                except:
                    continue
            
            if not title:
                title = "Başlık bulunamadı"
                
        except Exception as e:
            print(f"[HATA] Başlık çekilemedi: {e}")
            title = "Başlık bulunamadı"

        # Görsel çek
        image = None
        try:
            img_selectors = [
                'img[data-testid="product-detail-image"]',
                'img.image-viewer-image',
                'img.product-gallery-image',
                'img.product-image',
                'img.main-image',
                'img[src*=".jpg"]',
                'img[src*=".jpeg"]',
                'img[src*=".webp"]',
                'img[src*=".png"]'
            ]
            
            for selector in img_selectors:
                try:
                    img_elements = soup.select(selector)
                    for img in img_elements:
                        src = img.get('src')
                        srcset = img.get('srcset')
                        
                        # src'yi kontrol et
                        if src:
                            if any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.webp', '.png']):
                                image = src
                                break
                        
                        # srcset'i kontrol et
                        if srcset and not image:
                            srcset_urls = srcset.split(',')
                            for srcset_url in srcset_urls:
                                url_part = srcset_url.strip().split(' ')[0]
                                if any(ext in url_part.lower() for ext in ['.jpg', '.jpeg', '.webp', '.png']):
                                    image = url_part
                                    break
                        
                        if image:
                            break
                    
                    if image:
                        break
                except:
                    continue
            
            # Regex fallback
            if not image:
                page_content = str(soup)
                img_pattern = re.compile(r'src=["\']([^"\']*\.(?:jpg|jpeg|webp|png)[^"\']*)["\']')
                match = img_pattern.search(page_content)
                if match:
                    image = match.group(1)
            
            # PullandBear için görsel kalitesini artır
            if image and ("pullandbear.net" in image or "pullandbear.com" in image):
                # Mevcut parametreleri kontrol et ve yüksek kalite için güncelle
                if "w=" in image and "f=auto" in image:
                    # Genişliği artır ve formatı optimize et
                    image = re.sub(r'w=\d+', 'w=2000', image)
                    image = re.sub(r'f=auto', 'f=webp', image)
                    print(f"[DEBUG] PullandBear görsel kalitesi artırıldı (simple): {image}")
                elif "w=" in image:
                    # Sadece genişliği artır
                    image = re.sub(r'w=\d+', 'w=2000', image)
                    print(f"[DEBUG] PullandBear görsel genişliği artırıldı (simple): {image}")
                elif "f=auto" in image:
                    # Sadece formatı optimize et
                    image = re.sub(r'f=auto', 'f=webp', image)
                    print(f"[DEBUG] PullandBear görsel formatı optimize edildi (simple): {image}")
                else:
                    # Parametre yoksa ekle
                    if "?" in image:
                        image += "&w=2000&f=webp"
                    else:
                        image += "?w=2000&f=webp"
                    print(f"[DEBUG] PullandBear görsel parametreleri eklendi (simple): {image}")
                    
        except Exception as e:
            print(f"[HATA] Görsel çekilemedi: {e}")
            image = None

        # Fiyat çek
        price = None
        try:
            price_selectors = [
                '.product-sale',
                '.product-price',
                '.price',
                'span.price',
                'div.price',
                'p.price',
                '[data-testid="product-price"]',
                '[class*="price"]',
                'span',
                'div',
                'p'
            ]
            
            for selector in price_selectors:
                try:
                    price_elements = soup.select(selector)
                    for element in price_elements:
                        text = element.get_text()
                        if text and ('₺' in text or 'TL' in text):
                            # Fiyat regex'i
                            price_pattern = re.compile(r'([0-9]{1,3}(?:\.[0-9]{3})*,[0-9]{2}\s*(?:₺|TL)|[0-9]{1,3}(?:\.[0-9]{3})*\s*(?:₺|TL)|[0-9]+(?:\.[0-9]{2})?\s*(?:₺|TL))')
                            match = price_pattern.search(text)
                            if match:
                                price = match.group(1)
                                break
                    
                    if price:
                        break
                except:
                    continue
            
            # Regex fallback
            if not price:
                page_text = soup.get_text()
                price_pattern = re.compile(r'([0-9]{1,3}(?:\.[0-9]{3})*,[0-9]{2}\s*(?:₺|TL)|[0-9]{1,3}(?:\.[0-9]{3})*\s*(?:₺|TL)|[0-9]+(?:\.[0-9]{2})?\s*(?:₺|TL))')
                match = price_pattern.search(page_text)
                if match:
                    price = match.group(1)
                else:
                    price = "🤷"
                    
        except Exception as e:
            print(f"[HATA] Fiyat çekilemedi: {e}")
            price = "🤷"

        print(f"[DEBUG] Çekilen başlık: {title}")
        print(f"[DEBUG] Çekilen fiyat: {price}")
        print(f"[DEBUG] Çekilen marka: {brand}")
        
        return {
            "id": str(uuid.uuid4()),
            "url": url,
            "name": title.strip() if title else "İsim bulunamadı",
            "price": price,
            "image": image,
            "brand": brand,
            "sizes": []
        }
        
    except Exception as e:
        print(f"[HATA] Scraping başarısız: {e}")
        traceback.print_exc()
        return {
            "id": str(uuid.uuid4()),
            "url": url,
            "name": "Scraping hatası",
            "price": "🤷",
            "image": None,
            "brand": brand,
            "sizes": []
        }

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        product_url = request.form.get("product_url")
        if product_url:
            try:
                product = scrape_product(product_url)
                if product:
                    products.append(product)
            except Exception as e:
                print(f"[HATA] Ürün eklenirken hata: {e}")
                traceback.print_exc()
        return redirect(url_for("index"))
    return render_template("index.html", products=products)

@app.route("/delete/<id>", methods=["POST"])
def delete_product(id):
    global products
    products = [p for p in products if p.get("id") != id]
    return redirect(url_for("index"))

@app.errorhandler(405)
def method_not_allowed(e):
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True) 