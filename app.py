# -*- coding: utf-8 -*-
"""
Wishya - Universal Product Scraper
Python 3.8+ compatible version for Render deployment
Optimized for Render Free Plan
"""
import sys
import os
import gc
import psutil

# Python version check for Render compatibility
if sys.version_info < (3, 8):
    print("Python 3.8+ required")
    sys.exit(1)

# Set encoding for Render
import locale
try:
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'C.UTF-8')
    except:
        pass

# Render deployment fix - ensure proper encoding
import uuid
import asyncio
import re
import traceback
import json
import hashlib
import time
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from models import init_db, User, Product, Collection, PriceTracking, Notification, get_db_connection

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("[UYARI] python-dotenv yüklü değil, .env dosyası yüklenmeyecek")
    pass

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'favit-secret-key-2025')

# Render Free Plan Optimizations
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000  # 1 year cache

# Database configuration for Render
if os.environ.get('RENDER'):
    # Render PostgreSQL configuration
    app.config['DATABASE_URL'] = os.environ.get('DATABASE_URL')
    if app.config['DATABASE_URL'] and app.config['DATABASE_URL'].startswith('postgres://'):
        app.config['DATABASE_URL'] = app.config['DATABASE_URL'].replace('postgres://', 'postgresql://', 1)
    print(f"[DEBUG] Render PostgreSQL URL: {app.config['DATABASE_URL'][:30]}...")
else:
    # Local SQLite configuration
    app.config['DATABASE_URL'] = 'sqlite:///wishya.db'
    print(f"[DEBUG] Local SQLite URL: {app.config['DATABASE_URL']}")

# Simple cache for scraping results (memory optimized for free plan)
scraping_cache = {}
CACHE_DURATION = 1800  # 30 minutes cache (reduced from 1 hour)
MAX_CACHE_SIZE = 50  # Maximum cache entries

# Memory management for free plan
def cleanup_memory():
    """Clean up memory for Render free plan"""
    gc.collect()
    if psutil.virtual_memory().percent > 80:
        scraping_cache.clear()
        gc.collect()
    print(f"[DEBUG] Memory cleanup completed - Usage: {psutil.virtual_memory().percent}%")

# File to store dynamically added brands
BRANDS_FILE = "dynamic_brands.json"

# Site-specific scraping configurations
SITE_CONFIGS = {
    "columbia.com.tr": {
        "image_selectors": [
            "img.product-image",
            "img[class*='product'][class*='image']",
            "img[class*='main'][class*='image']",
            "img[class*='detail'][class*='image']",
            "img[src*='columbia.com.tr']",
            "img[src*='columbia']",
            "img[alt*='product']",
            "img[alt*='ürün']",
            "img[alt*='Columbia']",
            "img[title*='product']",
            "img[title*='ürün']",
            "img[title*='Columbia']",
            "img[loading='lazy']",
            "img[decoding='async']",
            "img[data-nimg='1']",
            "img[style*='color:transparent']",
            "img[fetchpriority='high']",
            "img[loading='eager']",
            ".product-gallery img",
            ".product-images img",
            ".gallery img",
            ".images img"
        ],
        "price_selectors": [
            "span.price",
            "span[class*='price']",
            "div.price",
            "div[class*='price']",
            "p.price",
            "p[class*='price']",
            ".price-current",
            ".current-price",
            ".product-price",
            "[class*='price'][class*='current']",
            "[class*='current'][class*='price']",
            "span[data-price]",
            "div[data-price]",
            ".price-value",
            ".price-amount"
        ],
        "old_price_selectors": [
            "span.old-price",
            "span[class*='old'][class*='price']",
            "div.old-price",
            "div[class*='old'][class*='price']",
            ".price-old",
            ".old-price",
            "[class*='price'][class*='old']",
            "[class*='old'][class*='price']",
            ".price-before",
            ".before-price"
        ],
        "title_selectors": [
            "h1.product-name",
            "h1.product-title",
            "h1[class*='product']",
            ".product-name",
            ".product-title",
            "[class*='product'][class*='name']",
            "[class*='product'][class*='title']",
            "h1[data-product-name]",
            "h1[data-product-title]"
        ],
        "size_selectors": [
            "select[name*='size'] option",
            "select[name*='beden'] option", 
            "select[name*='numara'] option",
            ".size-selector option",
            ".beden-selector option",
            ".numara-selector option",
            "[data-size]",
            "[data-beden]",
            "[data-numara]",
            ".size-option",
            ".beden-option",
            ".numara-option",
            "input[name*='size'][type='radio']",
            "input[name*='beden'][type='radio']",
            "input[name*='numara'][type='radio']"
        ]
    },
    "mudo.com.tr": {
        "image_selectors": [
            "img.product-image",
            "img.product-main-image",
            "img.main-product-image",
            "img[class*='product'][class*='image']",
            "img[class*='main'][class*='image']",
            "img[class*='detail'][class*='image']",
            "img[src*='mudo.com.tr']",
            "img[src*='mudo']",
            "img[alt*='product']",
            "img[alt*='ürün']",
            "img[alt*='Mudo']",
            "img[title*='product']",
            "img[title*='ürün']",
            "img[title*='Mudo']",
            "img[loading='lazy']",
            "img[decoding='async']",
            "img[data-nimg='1']",
            "img[style*='color:transparent']",
            "img[fetchpriority='high']",
            "img[loading='eager']",
            ".product-gallery img",
            ".product-images img",
            ".gallery img",
            ".images img",
            ".product-slider img",
            ".product-carousel img"
        ],
        "price_selectors": [
            "span.price",
            "span[class*='price']",
            "div.price",
            "div[class*='price']",
            "p.price",
            "p[class*='price']",
            ".price-current",
            ".current-price",
            ".product-price",
            "[class*='price'][class*='current']",
            "[class*='current'][class*='price']",
            "span[data-price]",
            "div[data-price]",
            ".price-value",
            ".price-amount"
        ],
        "old_price_selectors": [
            "span.old-price",
            "span[class*='old'][class*='price']",
            "div.old-price",
            "div[class*='old'][class*='price']",
            ".price-old",
            ".old-price",
            "[class*='price'][class*='old']",
            "[class*='old'][class*='price']",
            ".price-before",
            ".before-price"
        ],
        "title_selectors": [
            "h1.product-name",
            "h1.product-title",
            "h1[class*='product']",
            ".product-name",
            ".product-title",
            "[class*='product'][class*='name']",
            "[class*='product'][class*='title']",
            "h1[data-product-name]",
            "h1[data-product-title]"
        ],
        "size_selectors": [
            "select[name*='size'] option",
            "select[name*='beden'] option", 
            "select[name*='numara'] option",
            ".size-selector option",
            ".beden-selector option",
            ".numara-selector option",
            "[data-size]",
            "[data-beden]",
            "[data-numara]",
            ".size-option",
            ".beden-option",
            ".numara-option",
            "input[name*='size'][type='radio']",
            "input[name*='beden'][type='radio']",
            "input[name*='numara'][type='radio']"
        ]
    },
    "ltbjeans.com": {
        "image_selectors": [
            "img[src*='ltbjeans-hybris-p1.mncdn.com']",
            "img[alt*='Regular Askılı']",
            "img[title*='Regular Askılı']"
        ],
        "price_selectors": [
            "span.dis__new--price",
            ".dis__new--price"
        ],
        "old_price_selectors": [
            "span.dis__old--price",
            ".dis__old--price"
        ],
        "title_selectors": [
            "h1.product-name",
            "h1.product-title",
            ".product-name"
        ]
    },
    "zara.com": {
        "image_selectors": [
            "img.media-image__image.media__wrapper--media",
            "img[class*='media-image__image'][class*='media__wrapper--media']",
            "img.media-image__image",
            "img.media__wrapper--media",
            "img[class*='media-image__image']",
            "img[class*='media__wrapper--media']",
            "img[data-qa-action='product-image']",
            "img[data-testid='product-detail-image']",
            "img[data-testid='product-image']",
            "img.product-image",
            "img[class*='product'][class*='image']",
            "img[class*='main'][class*='image']",
            "img[class*='detail'][class*='image']",
            "img[loading='lazy']",
            "img[src*='static.zara.net']",
            "img[src*='zara.net']",
            "img[src*='zara.com']",
            "img[alt*='product']",
            "img[alt*='ürün']",
            "img[alt*='Zara']",
            "img[title*='product']",
            "img[title*='ürün']",
            "img[title*='Zara']",
            "img[srcset*='zara']",
            "img[srcset*='static.zara.net']",
            "img[decoding='async']",
            "img[data-nimg='1']",
            "img[style*='color:transparent']",
            "img[fetchpriority='high']",
            "img[loading='eager']"
        ],
        "price_selectors": [
            "span[data-qa-action='price-current']",
            "span[data-testid='price']",
            "span[data-testid='current-price']",
            "span.price-current",
            "span.current-price",
            "span[class*='price'][class*='current']",
            "span[class*='current'][class*='price']",
            ".price-current",
            ".current-price",
            "[data-testid='price']",
            "[data-testid='current-price']",
            "[class*='price'][class*='current']",
            "[class*='current'][class*='price']",
            ".price",
            "span[class*='price']",
            "div[class*='price']",
            "p[class*='price']"
        ],
        "old_price_selectors": [
            "span[data-qa-action='price-old']",
            "span[data-testid='old-price']",
            "span.price-old",
            "span.old-price",
            ".price-old",
            ".old-price",
            "[data-testid='old-price']",
            "[class*='price'][class*='old']",
            "[class*='old'][class*='price']"
        ],
        "title_selectors": [
            "h1[data-qa-action='product-name']",
            "h1[data-testid='product-name']",
            "h1.product-name",
            "h1.product-title",
            ".product-name",
            ".product-title",
            "[data-testid='product-name']",
            "[data-qa-action='product-name']"
        ]
    },
    "mango.com": {
        "image_selectors": [
            "img[src*='static.mango.com']",
            "img[src*='media.mango.com']",
            "img.product-image",
            "img[class*='product'][class*='image']",
            "img[data-testid='product-image']",
            "img[alt*='product']",
            "img[alt*='ürün']"
        ],
        "price_selectors": [
            "span[data-testid='price']",
            "span.price",
            ".price",
            "[data-testid='price']"
        ],
        "old_price_selectors": [
            "span[data-testid='old-price']",
            "span.old-price",
            ".old-price",
            "[data-testid='old-price']"
        ],
        "title_selectors": [
            "h1[data-testid='product-name']",
            "h1.product-name",
            ".product-name",
            "[data-testid='product-name']"
        ]
    },
    "wwfmarket.com": {
        "image_selectors": [
            "img[src*='wwfmarket.com/cdn']",
            "img.product-image",
            "img[class*='product'][class*='image']"
        ],
        "price_selectors": [
            "span.price",
            ".price",
            "[data-testid='price']"
        ],
        "old_price_selectors": [
            "span.old-price",
            ".old-price",
            "[data-testid='old-price']"
        ],
        "title_selectors": [
            "h1.product-name",
            ".product-name",
            "[data-testid='product-name']"
        ]
    }
}

def get_site_config(url):
    """URL'den site konfigürasyonunu al"""
    for domain, config in SITE_CONFIGS.items():
        if domain in url:
            return config
    return None

async def extract_with_site_config(page, url, site_config):
    """Site-specific konfigürasyon kullanarak veri çek"""
    title = None
    price = None
    old_price = None
    image = None
    
    try:
        # Başlık çekme
        if site_config and 'title_selectors' in site_config:
            for selector in site_config['title_selectors']:
                try:
                    title_element = await page.query_selector(selector)
                    if title_element:
                        title = await title_element.text_content()
                        if title and title.strip():
                            title = title.strip().upper()
                            title = re.sub(r'[^\w\s\-\.]', '', title)
                            title = re.sub(r'\s+', ' ', title).strip()
                            print(f"[DEBUG] Site-specific başlık bulundu: {title}")
                            break
                except Exception as e:
                    print(f"[DEBUG] Title selector hatası {selector}: {e}")
                    continue
        
        # Fiyat çekme
        if site_config and 'price_selectors' in site_config:
            for selector in site_config['price_selectors']:
                try:
                    price_element = await page.query_selector(selector)
                    if price_element:
                        price_text = await price_element.text_content()
                        if price_text and price_text.strip():
                            # Fiyat temizleme ve TL ekleme
                            price_text = price_text.strip()
                            # Superstep için özel fiyat temizleme
                            if "superstep.com.tr" in url:
                                # Superstep fiyatları "6.503 TL" formatında gelir (6.503 = 6,503 TL)
                                # Nokta binlik ayırıcı olarak kullanılıyor, virgül ondalık ayırıcı
                                # 6.503 -> 6503 (altı bin beş yüz üç)
                                price_clean = re.sub(r'[^\d,\.]', '', price_text)
                                if price_clean:
                                    # Nokta binlik ayırıcıyı kaldır
                                    price_clean = price_clean.replace('.', '')
                                    # Virgül ondalık ayırıcıyı nokta yap
                                    price_clean = price_clean.replace(',', '.')
                                    if price_clean:
                                        price_num = float(price_clean)
                                        # Türkçe format: 6.503 TL
                                        price = f"{price_num:,.0f} TL".replace(',', 'X').replace('.', ',').replace('X', '.')
                                        print(f"[DEBUG] Superstep fiyat temizlendi: {price}")
                                        break
                            # MediaMarkt için özel fiyat temizleme
                            elif "mediamarkt.com.tr" in url:
                                # MediaMarkt fiyatları "₺ 35.999," formatında gelir
                                # Sadece sayıları ve nokta/virgül işaretlerini al
                                price_text = re.sub(r'[^\d,\.]', '', price_text)
                                # Eğer sonunda virgül varsa kaldır (35.999, -> 35.999)
                                if price_text.endswith(','):
                                    price_text = price_text[:-1]
                                # Nokta binlik ayırıcı, virgül ondalık ayırıcı olarak bırak
                                # 35.999 -> 35999 (binlik ayırıcıyı kaldır)
                                if '.' in price_text:
                                    price_text = price_text.replace('.', '')
                                print(f"[DEBUG] MediaMarkt fiyat temizlendi: {price_text}")
                            else:
                                # Diğer siteler için standart temizleme
                                price_text = re.sub(r'[^\d,\.]', '', price_text)
                                price_text = price_text.replace(',', '.')
                            
                            # Sayısal değer kontrolü
                            if re.match(r'^\d+\.?\d*$', price_text):
                                price_num = float(price_text)

                                # MediaMarkt için özel fiyat temizleme
                                if "mediamarkt.com.tr" in url:
                                    # MediaMarkt fiyatları genellikle binlik ayırıcı ile gelir (35.999)
                                    # Bu durumda nokta binlik ayırıcı, virgül ondalık ayırıcı
                                    if price_num >= 1000:
                                        # Binlik ayırıcıyı kaldır ve doğru formatla
                                        price_str = str(int(price_num))
                                        # Türkçe format: 35.999 TL
                                        if len(price_str) > 3:
                                            formatted_price = ""
                                            for i, digit in enumerate(reversed(price_str)):
                                                if i > 0 and i % 3 == 0:
                                                    formatted_price = "." + formatted_price
                                                formatted_price = digit + formatted_price
                                            price = f"{formatted_price} TL"
                                        else:
                                            price = f"{price_str} TL"
                                    else:
                                        price = f"{int(price_num)} TL"
                                    print(f"[DEBUG] MediaMarkt fiyat temizlendi: {price}")
                                # Sahibinden.com için özel fiyat temizleme
                                elif "sahibinden.com" in url:
                                    # Binlik ayırıcıları kaldır
                                    price_clean = re.sub(r'[^\d.,]', '', str(price_num))
                                    price_clean = price_clean.replace('.', '').replace(',', '.')
                                    if price_clean:
                                        price = price_clean
                                        print(f"[DEBUG] Sahibinden.com fiyat temizlendi: {price}")
                                else:
                                    # Diğer siteler için standart format
                                    if price_num >= 1000:
                                        price = f"{price_num:,.2f} TL".replace(',', 'X').replace('.', ',').replace('X', '.')
                                    else:
                                        price = f"{price_num:.2f} TL".replace('.', ',')
                                print(f"[DEBUG] Site-specific fiyat bulundu: {price}")
                                break
                except Exception as e:
                    print(f"[DEBUG] Price selector hatası {selector}: {e}")
                    continue
        
        # Eski fiyat çekme
        if site_config and 'old_price_selectors' in site_config:
            for selector in site_config['old_price_selectors']:
                try:
                    old_price_element = await page.query_selector(selector)
                    if old_price_element:
                        old_price_text = await old_price_element.text_content()
                        if old_price_text and old_price_text.strip():
                            # Fiyat temizleme ve TL ekleme
                            old_price_text = old_price_text.strip()
                            # Superstep için özel eski fiyat temizleme
                            if "superstep.com.tr" in url:
                                # Superstep eski fiyatları "9.290 TL" formatında gelir (9.290 = 9,290 TL)
                                # Nokta binlik ayırıcı olarak kullanılıyor, virgül ondalık ayırıcı
                                # 9.290 -> 9290 (dokuz bin iki yüz doksan)
                                old_price_clean = re.sub(r'[^\d,\.]', '', old_price_text)
                                if old_price_clean:
                                    # Nokta binlik ayırıcıyı kaldır
                                    old_price_clean = old_price_clean.replace('.', '')
                                    # Virgül ondalık ayırıcıyı nokta yap
                                    old_price_clean = old_price_clean.replace(',', '.')
                                    if old_price_clean:
                                        old_price_num = float(old_price_clean)
                                        # Türkçe format: 9.290 TL
                                        old_price = f"{old_price_num:,.0f} TL".replace(',', 'X').replace('.', ',').replace('X', '.')
                                        print(f"[DEBUG] Superstep eski fiyat temizlendi: {old_price}")
                                        break
                            # Mavi için özel eski fiyat temizleme
                            elif "mavi.com" in url:
                                # Mavi eski fiyatları "499,99 TL" formatında gelir
                                # Virgül ondalık ayırıcı olarak kullanılıyor
                                old_price_clean = re.sub(r'[^\d,\.]', '', old_price_text)
                                if old_price_clean:
                                    # Virgül ondalık ayırıcıyı nokta yap
                                    old_price_clean = old_price_clean.replace(',', '.')
                                    if old_price_clean:
                                        old_price_num = float(old_price_clean)
                                        # Türkçe format: 499,99 TL
                                        old_price = f"{old_price_num:.2f} TL".replace('.', ',')
                                        print(f"[DEBUG] Mavi eski fiyat temizlendi: {old_price}")
                                        break
                            else:
                                # Diğer siteler için standart temizleme
                                old_price_text = re.sub(r'[^\d,\.]', '', old_price_text)
                                old_price_text = old_price_text.replace(',', '.')
                            
                            # Sayısal değer kontrolü
                            if re.match(r'^\d+\.?\d*$', old_price_text):
                                old_price_num = float(old_price_text)

                                # Diğer siteler için standart TL formatına çevir
                                if old_price_num >= 1000:
                                    old_price = f"{old_price_num:,.2f} TL".replace(',', 'X').replace('.', ',').replace('X', '.')
                                else:
                                    old_price = f"{old_price_num:.2f} TL".replace('.', ',')
                                print(f"[DEBUG] Site-specific eski fiyat bulundu: {old_price}")
                                break
                except Exception as e:
                    print(f"[DEBUG] Old price selector hatası {selector}: {e}")
                    continue
        
        # Görsel çekme
        if site_config and 'image_selectors' in site_config:
            for selector in site_config['image_selectors']:
                try:
                    img_element = await page.query_selector(selector)
                    if img_element:
                        # Önce srcset'i kontrol et (daha yüksek kalite için)
                        srcset = await img_element.get_attribute('srcset')
                        src = await img_element.get_attribute('src')
                        
                        # srcset'ten en yüksek kaliteli görseli al
                        if srcset:
                            # srcset formatı: "url1 1x, url2 2x, url3 3x"
                            srcset_parts = srcset.split(',')
                            highest_res = None
                            max_width = 0
                            
                            for part in srcset_parts:
                                part = part.strip()
                                if ' ' in part:
                                    url_part, size_part = part.rsplit(' ', 1)
                                    if 'w' in size_part:
                                        width = int(size_part.replace('w', ''))
                                        if width > max_width:
                                            max_width = width
                                            highest_res = url_part.strip()
                            
                            if highest_res:
                                src = highest_res
                        
                        if src and (any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.webp', '.png']) or 'assets.mmsrg.com' in src):
                            # Relative URL'yi absolute yap
                            if src.startswith('//'):
                                src = 'https:' + src
                            elif src.startswith('/'):
                                from urllib.parse import urlparse
                                parsed = urlparse(url)
                                src = f"{parsed.scheme}://{parsed.netloc}{src}"
                            
                            # Superstep için görsel kalitesini optimize et
                            if "superstep.com.tr" in url and "akinoncloud.com" in src:
                                # Superstep görselleri için boyut parametresini yüksek kaliteye çevir
                                if 'size' in src:
                                    # Mevcut boyutu bul ve yüksek kaliteye çevir
                                    size_match = re.search(r'size(\d+)', src)
                                    if size_match:
                                        current_size = size_match.group(1)
                                        # Eğer boyut 1000'den küçükse, 1920'ye çevir
                                        if int(current_size) < 1000:
                                            src = src.replace(f'size{current_size}', 'size1920')
                                            print(f"[DEBUG] Superstep görsel kalitesi artırıldı: {current_size} -> 1920")
                            # Diğer siteler için boyut parametrelerini optimize et
                            elif 'w=' in src and 'h=' in src:
                                # Boyut parametrelerini daha yüksek değerlerle değiştir
                                src = re.sub(r'w=\d+', 'w=800', src)
                                src = re.sub(r'h=\d+', 'h=1200', src)
                            
                            # Zara için görsel kalitesini artır
                            if "zara.net" in src or "zara.com" in src:
                                # Zara görselleri için kalite optimizasyonu
                                if "static.zara.net" in src:
                                    # Mevcut parametreleri kontrol et ve yüksek kalite için güncelle
                                    if "w=" in src:
                                        # Genişliği artır
                                        src = re.sub(r'w=\d+', 'w=2000', src)
                                        print(f"[DEBUG] Zara görsel genişliği artırıldı: {src}")
                                    elif "h=" in src:
                                        # Yüksekliği artır
                                        src = re.sub(r'h=\d+', 'h=2000', src)
                                        print(f"[DEBUG] Zara görsel yüksekliği artırıldı: {src}")
                                    else:
                                        # Parametre yoksa ekle
                                        if "?" in src:
                                            src += "&w=2000&h=2000"
                                        else:
                                            src += "?w=2000&h=2000"
                                        print(f"[DEBUG] Zara görsel parametreleri eklendi: {src}")
                                else:
                                    print(f"[DEBUG] Zara görsel mevcut kalite: {src}")
                            
                            # PullandBear için görsel kalitesini artır
                            if "pullandbear.net" in src or "pullandbear.com" in src:
                                # Mevcut parametreleri kontrol et ve yüksek kalite için güncelle
                                if "w=" in src and "f=auto" in src:
                                    # Genişliği artır ve formatı optimize et
                                    src = re.sub(r'w=\d+', 'w=2000', src)
                                    src = re.sub(r'f=auto', 'f=webp', src)
                                    print(f"[DEBUG] PullandBear görsel kalitesi artırıldı (site-config): {src}")
                                elif "w=" in src:
                                    # Sadece genişliği artır
                                    src = re.sub(r'w=\d+', 'w=2000', src)
                                    print(f"[DEBUG] PullandBear görsel genişliği artırıldı (site-config): {src}")
                                elif "f=auto" in src:
                                    # Sadece formatı optimize et
                                    src = re.sub(r'f=auto', 'f=webp', src)
                                    print(f"[DEBUG] PullandBear görsel formatı optimize edildi (site-config): {src}")
                                else:
                                    # Parametre yoksa ekle
                                    if "?" in src:
                                        src += "&w=2000&f=webp"
                                    else:
                                        src += "?w=2000&f=webp"
                                    print(f"[DEBUG] PullandBear görsel parametreleri eklendi (site-config): {src}")
                            
                            # Mavi için görsel kalitesini artır (basitleştirilmiş)
                            if "mavi.com" in src or "sky-static.mavi.com" in src:
                                # Mavi görselleri için basit kalite optimizasyonu
                                if "sky-static.mavi.com" in src:
                                    # Sadece düşük kaliteli görselleri yükselt
                                    if "600x600" in src:
                                        src = src.replace("600x600", "800x800")
                                        print(f"[DEBUG] Mavi görsel kalitesi artırıldı: 600x600 -> 800x800")
                                    elif "400x400" in src:
                                        src = src.replace("400x400", "800x800")
                                        print(f"[DEBUG] Mavi görsel kalitesi artırıldı: 400x400 -> 800x800")
                                    else:
                                        print(f"[DEBUG] Mavi görsel mevcut kalite: {src}")
                            
                            image = src
                            print(f"[DEBUG] Site-specific görsel bulundu: {image}")
                            break
                except Exception as e:
                    print(f"[DEBUG] Image selector hatası {selector}: {e}")
                    continue
    
    except Exception as e:
        print(f"[HATA] Site-specific extraction hatası: {e}")
    
    return title, price, old_price, image

def get_cache_key(url):
    """URL için cache key oluştur"""
    return hashlib.md5(url.encode()).hexdigest()

def get_cached_result(url):
    """Cache'den sonuç al"""
    cache_key = get_cache_key(url)
    if cache_key in scraping_cache:
        cached_data, timestamp = scraping_cache[cache_key]
        if time.time() - timestamp < CACHE_DURATION:
            return cached_data
    return None

def set_cached_result(url, data):
    """Sonucu cache'e kaydet (memory optimized for free plan)"""
    cache_key = get_cache_key(url)
    
    # Clean up old cache entries if cache is too large
    if len(scraping_cache) >= MAX_CACHE_SIZE:
        # Remove oldest entries
        sorted_cache = sorted(scraping_cache.items(), key=lambda x: x[1][1])
        for key, _ in sorted_cache[:10]:  # Remove 10 oldest entries
            del scraping_cache[key]
    
    scraping_cache[cache_key] = (data, time.time())
    
    # Clean up memory if needed
    cleanup_memory()

def extract_domain_from_url(url):
    """URL'den domain çıkar"""
    from urllib.parse import urlparse
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        # www. prefix'ini kaldır
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain
    except:
        return None

def load_dynamic_brands():
    """Dinamik olarak eklenen markaları yükle"""
    try:
        if os.path.exists(BRANDS_FILE):
            with open(BRANDS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"[HATA] Dinamik markalar yüklenemedi: {e}")
    return []

def save_dynamic_brands(brands):
    """Dinamik markaları kaydet"""
    try:
        with open(BRANDS_FILE, 'w', encoding='utf-8') as f:
            json.dump(brands, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[HATA] Dinamik markalar kaydedilemedi: {e}")

def add_brand_automatically(domain):
    """Yeni markayı otomatik olarak ekle"""
    if not domain:
        return None
    
    # Domain'den marka adını oluştur
    brand_name = domain.split('.')[0].title()
    
    # Özel durumlar için düzeltmeler
    brand_mappings = {
        'kaft': 'Kaft',
        'mavi': 'Mavi',
        'zara': 'Zara',
        'mango': 'Mango',
        'bershka': 'Bershka',
        'pullandbear': 'Pull&Bear',
        'boyner': 'Boyner',
        'catiuniform': 'Çatı Uniform',
        'ontrailstore': 'Ontrail Store',
        'wwfmarket': 'WWF Market',
        'superstep': 'Superstep',
        'kigili': 'Kigili',
        'jackjones': 'Jack & Jones',
        'selected': 'Selected',
        'vakko': 'Vakko',
        'beymen': 'Beymen',
        'neta-porter': 'Net-a-Porter',
        'farfetch': 'Farfetch',
        'asos': 'ASOS',
        'zalando': 'Zalando',
        'uniqlo': 'Uniqlo',
        'gap': 'Gap',
        'oldnavy': 'Old Navy',
        'bananarepublic': 'Banana Republic',
        'tommyhilfiger': 'Tommy Hilfiger',
        'calvinklein': 'Calvin Klein',
        'levis': 'Levi\'s'
    }
    
    # Özel mapping varsa kullan
    if domain.split('.')[0].lower() in brand_mappings:
        brand_name = brand_mappings[domain.split('.')[0].lower()]
    
    # Dinamik markaları yükle
    dynamic_brands = load_dynamic_brands()
    
    # Marka zaten var mı kontrol et
    for existing_domain, existing_name in dynamic_brands:
        if existing_domain == domain:
            return existing_name
    
    # Yeni markayı ekle
    new_brand = (domain, brand_name)
    dynamic_brands.append(new_brand)
    save_dynamic_brands(dynamic_brands)
    
    print(f"[YENİ MARKA] Otomatik olarak eklendi: {domain} -> {brand_name}")
    return brand_name

def detect_brand_from_url(url):
    """URL'den marka tespit et"""
    domain = extract_domain_from_url(url)
    if not domain:
        return "Bilinmiyor"
    
    # Sahibinden.com için özel işlem
    if "sahibinden.com" in domain:
        return "Sahibinden.com"
    
    # Önce sabit BRANDS listesinde ara
    for brand_domain, brand_name in BRANDS:
        if brand_domain in domain:
            return brand_name
    
    # Dinamik markalarda ara
    dynamic_brands = load_dynamic_brands()
    for brand_domain, brand_name in dynamic_brands:
        if brand_domain in domain:
            return brand_name
    
    # Marka bulunamadı, otomatik ekle
    new_brand_name = add_brand_automatically(domain)
    if new_brand_name:
        return new_brand_name
    
    return "Bilinmiyor"

def detect_sahibinden_brand_from_title(title):
    """Sahibinden.com başlığından araç markasını tespit et"""
    if not title:
        return "UNKNOWN"
    
    title_upper = title.upper()
    
    # Araç markaları listesi
    car_brands = [
        "LADA", "BMW", "MERCEDES", "AUDI", "VOLKSWAGEN", "FORD", "RENAULT", "FIAT", 
        "TOYOTA", "HONDA", "HYUNDAI", "KIA", "NISSAN", "MAZDA", "SUBARU", "MITSUBISHI", 
        "OPEL", "PEUGEOT", "CITROEN", "SKODA", "SEAT", "VOLVO", "SAAB", "JAGUAR", 
        "LAND ROVER", "RANGE ROVER", "MINI", "ALFA ROMEO", "MASERATI", "FERRARI", 
        "LAMBORGHINI", "PORSCHE", "ASTON MARTIN", "BENTLEY", "ROLLS ROYCE", "LEXUS", 
        "INFINITI", "ACURA", "BUICK", "CADILLAC", "CHEVROLET", "CHRYSLER", "DODGE", 
        "JEEP", "LINCOLN", "PONTIAC", "SATURN", "SCION", "SMART", "SUZUKI", "DAIHATSU", 
        "ISUZU", "MAHINDRA", "TATA", "MG", "ROVER", "VAUXHALL", "VAZ", "GAZ", "UAZ", 
        "ZAZ", "MOSKVICH", "IZH", "KAMAZ", "URAL", "ZIL", "MAZ", "KRAZ", "BELAZ"
    ]
    
    for brand in car_brands:
        if brand in title_upper:
            return brand
    
    return "UNKNOWN"

# Login manager setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)

# Initialize database
with app.app_context():
    init_db()

# Health check endpoint
@app.route('/health')
def health_check():
    """Health check endpoint for Render"""
    try:
        # Database bağlantısını test et
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        conn.close()
        return jsonify({'status': 'healthy', 'database': 'connected'}), 200
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

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
    ("kigili.com", "Kigili"),
    ("kaft.com", "Kaft"),
    ("jackjones.com", "Jack & Jones"),
    ("selected.com", "Selected"),
    ("lesbenjamins.com", "Les Benjamins"),
    ("vakko.com", "Vakko"),
    ("beymen.com", "Beymen"),
    ("net-a-porter.com", "Net-a-Porter"),
    ("farfetch.com", "Farfetch"),
    ("asos.com", "ASOS"),
    ("zalando.com", "Zalando"),
    ("uniqlo.com", "Uniqlo"),
    ("gap.com", "Gap"),
    ("oldnavy.com", "Old Navy"),
    ("bananarepublic.com", "Banana Republic"),
    ("tommyhilfiger.com", "Tommy Hilfiger"),
    ("calvinklein.com", "Calvin Klein"),
    ("levis.com", "Levi's"),
    ("wrangler.com", "Wrangler"),
    ("diesel.com", "Diesel"),
    ("guess.com", "Guess"),
    ("esprit.com", "Esprit"),
    ("benetton.com", "Benetton"),
    ("sandro.com", "Sandro"),
    ("maje.com", "Maje"),
    ("claudiepierlot.com", "Claudie Pierlot"),
    ("comptoir-des-cotonniers.com", "Comptoir des Cotonniers"),
    ("promod.com", "Promod"),
    ("jennyfer.com", "Jennyfer"),
    ("pimkie.com", "Pimkie"),
    ("etam.com", "Etam"),
    ("cache-cache.com", "Cache Cache"),
    ("devred.com", "Devred"),
    ("camaieu.com", "Camaieu"),
    ("kiabi.com", "Kiabi"),
    ("camaieu.com", "Camaieu"),
    ("devred.com", "Devred"),
    ("cache-cache.com", "Cache Cache"),
    ("etam.com", "Etam"),
    ("pimkie.com", "Pimkie"),
    ("jennyfer.com", "Jennyfer"),
    ("promod.com", "Promod"),
    ("comptoir-des-cotonniers.com", "Comptoir des Cotonniers"),
    ("maje.com", "Maje"),
    ("sandro.com", "Sandro"),
    ("benetton.com", "Benetton"),
    ("esprit.com", "Esprit"),
    ("guess.com", "Guess"),
    ("diesel.com", "Diesel"),
    ("wrangler.com", "Wrangler"),
    ("levis.com", "Levi's"),
    ("calvinklein.com", "Calvin Klein"),
    ("tommyhilfiger.com", "Tommy Hilfiger"),
    ("bananarepublic.com", "Banana Republic"),
    ("oldnavy.com", "Old Navy"),
    ("gap.com", "Gap"),
    ("uniqlo.com", "Uniqlo"),
    ("zalando.com", "Zalando"),
    ("asos.com", "ASOS"),
    ("farfetch.com", "Farfetch"),
    ("net-a-porter.com", "Net-a-Porter"),
    ("beymen.com", "Beymen"),
    ("vakko.com", "Vakko"),
    ("selected.com", "Selected"),
    ("jackjones.com", "Jack & Jones"),
    ("kigili.com", "Kigili"),
    ("mediamarkt.com.tr", "MediaMarkt"),
]

# Gelişmiş bot koruması aşma fonksiyonları
def get_advanced_stealth_script():
    """Gelişmiş stealth script döndür"""
    return """
        // Gelişmiş bot koruması aşma
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        Object.defineProperty(navigator, 'plugins', { 
            get: () => [
                {name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer', description: 'Portable Document Format'},
                {name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai', description: ''},
                {name: 'Native Client', filename: 'internal-nacl-plugin', description: 'Native Client Executable'}
            ]
        });
        Object.defineProperty(navigator, 'languages', { get: () => ['tr-TR', 'tr', 'en-US', 'en'] });
        Object.defineProperty(navigator, 'permissions', { 
            get: () => ({ 
                query: async () => ({ state: 'granted' }),
                request: async () => ({ state: 'granted' })
            }) 
        });
        window.chrome = { 
            runtime: { onConnect: {}, onMessage: {}, sendMessage: () => {}, connect: () => {} },
            loadTimes: () => {}, csi: () => {}, app: {}
        };
        Object.defineProperty(navigator, 'userAgent', {
            get: () => 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1'
        });
        Object.defineProperty(screen, 'width', { get: () => 390 });
        Object.defineProperty(screen, 'height', { get: () => 844 });
        Object.defineProperty(navigator, 'connection', {
            get: () => ({ effectiveType: '4g', rtt: 50, downlink: 10, saveData: false })
        });
        Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 8 });
        Object.defineProperty(navigator, 'deviceMemory', { get: () => 8 });
        Object.defineProperty(navigator, 'platform', { get: () => 'iPhone' });
        Object.defineProperty(navigator, 'vendor', { get: () => 'Apple Computer, Inc.' });
        Object.defineProperty(navigator, 'cookieEnabled', { get: () => true });
        Object.defineProperty(navigator, 'doNotTrack', { get: () => null });
        Object.defineProperty(navigator, 'maxTouchPoints', { get: () => 5 });
        
        // WebGL fingerprinting engelleme
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {
            if (parameter === 37445) return 'Apple Inc.';
            if (parameter === 37446) return 'Apple GPU';
            return getParameter.call(this, parameter);
        };
        
        // Canvas fingerprinting engelleme
        const originalGetContext = HTMLCanvasElement.prototype.getContext;
        HTMLCanvasElement.prototype.getContext = function(type, ...args) {
            const context = originalGetContext.call(this, type, ...args);
            if (type === '2d') {
                const originalFillText = context.fillText;
                context.fillText = function(...args) {
                    return originalFillText.apply(this, args);
                };
            }
            return context;
        };
    """

def get_enhanced_selectors():
    """Gelişmiş selector'ları döndür"""
    return {
        "mango.com": {
            "title_selectors": [
                'h1.ProductDetail_title___WrC_.texts_titleL__7qeP6',
                'h1[class*="ProductDetail_title"]',
                'h1[class*="texts_titleL"]',
                'h1[class*="product"]',
                'h1[class*="title"]',
                'h1[class*="name"]',
                'h1',
                'title',
                '[data-testid*="product"]',
                '[data-testid*="title"]',
                '[class*="product-name"]',
                '[class*="product-title"]',
                '[class*="ProductDetail"]',
                '[class*="texts_title"]'
            ],
            "price_selectors": [
                'span.SinglePrice_center__TMNty.texts_bodyM__Y2ZHT.SinglePrice_finalPrice__XBL1k',
                'span[class*="SinglePrice_finalPrice"]',
                'span[class*="finalPrice"]',
                'span[class*="SinglePrice_center"]',
                'span[class*="texts_bodyM"]',
                'span[class*="SinglePrice"]',
                'span[class*="price"]',
                'span[class*="Price"]',
                'div[class*="price"]',
                'p[class*="price"]'
            ],
            "image_selectors": [
                'img.ImageGridItem_image__VVZxr',
                'img[src*="shop.mango.com/assets"]',
                'img[srcset*="shop.mango.com/assets"]',
                'img[data-nimg="1"]',
                'img[style*="color:transparent"]',
                'img[decoding="async"]',
                'img[class*="ImageGridItem"]',
                'img[class*="image"]',
                'img[data-testid="product-image"]',
                'img[class*="product"]',
                'img[src*="mango"]'
            ]
        },
        "sahibinden.com": {
            "title_selectors": [
                'h1',
                '.classified-title h1',
                '[class*="title"] h1',
                'h1[class*="title"]',
                'h1.classified-title',
                'h1[class*="classified"]'
            ],
            "price_selectors": [
                '.classified-price-wrapper',
                '.classified-price',
                '[class*="price"]',
                'span[class*="price"]',
                '.price-wrapper',
                'span.classified-price-wrapper',
                'h3 span',
                'span'
            ],
            "image_selectors": [
                'img.s-image',
                'img.stdImg',
                'img[class*="s-image"]',
                'img[class*="stdImg"]',
                'label img',
                'img[src*="shbdn.com"]'
            ]
        },
        "avva.com.tr": {
            "title_selectors": [
                'h1',
                'h1[class*="title"]',
                'h1[class*="product"]',
                'h1[class*="name"]',
                '[class*="product-title"]',
                '[class*="product-name"]',
                'title'
            ],
            "price_selectors": [
                'span.spanFiyat',
                '.spanFiyat',
                'span[class*="fiyat"]',
                '.price',
                '.product-price',
                '[class*="price"]',
                'span[class*="price"]',
                'div[class*="price"]',
                'p[class*="price"]',
                'strong[class*="price"]',
                'b[class*="price"]'
            ],
            "image_selectors": [
                'img[src*="avva.com.tr"]',
                'img[src*="avva"]',
                'img.product-image',
                'img.main-image',
                'img[class*="product"]',
                'img[class*="main"]',
                'img[class*="detail"]',
                'img[alt*="ürün"]',
                'img[alt*="product"]',
                'img[alt*="main"]',
                'img[alt*="detail"]',
                'img[src*=".jpg"]',
                'img[src*=".jpeg"]',
                'img[src*=".webp"]',
                'img[src*=".png"]'
            ],
            "size_selectors": [
                '.size-options',
                '.size-selector',
                '.size-list',
                '[class*="size"]',
                '[class*="beden"]',
                'select[class*="size"]',
                'select[class*="beden"]',
                'option[class*="size"]',
                'option[class*="beden"]',
                '.product-sizes',
                '.available-sizes',
                '.size-option',
                '.beden-option'
            ]
        },
        "zara.com": {
            "title_selectors": [
                'h1[data-qa-action="product-name"]',
                'h1[data-testid="product-name"]',
                'h1[data-testid="product-title"]',
                'h1.product-name',
                'h1.product-title',
                'h1[class*="product"][class*="name"]',
                'h1[class*="product"][class*="title"]',
                'h1[class*="name"]',
                'h1[class*="title"]',
                '[data-testid="product-name"]',
                '[data-testid="product-title"]',
                '[class*="product-name"]',
                '[class*="product-title"]',
                '[class*="name"]',
                '[class*="title"]',
                'h1',
                'title'
            ],
            "price_selectors": [
                'span[data-qa-action="price-current"]',
                'span[data-testid="price"]',
                'span[data-testid="current-price"]',
                'span.price-current',
                'span.current-price',
                'span[class*="price"][class*="current"]',
                'span[class*="current"][class*="price"]',
                '.price-current',
                '.current-price',
                '[data-testid="price"]',
                '[data-testid="current-price"]',
                '[class*="price"][class*="current"]',
                '[class*="current"][class*="price"]',
                '.price',
                'span.price',
                'div.price',
                'p.price',
                '[class*="price"]',
                'span[class*="price"]',
                'div[class*="price"]',
                'p[class*="price"]'
            ],
            "image_selectors": [
                'img.media-image__image.media__wrapper--media',
                'img[class*="media-image__image"][class*="media__wrapper--media"]',
                'img.media-image__image',
                'img.media__wrapper--media',
                'img[class*="media-image__image"]',
                'img[class*="media__wrapper--media"]',
                'img[data-qa-action="product-image"]',
                'img[data-testid="product-detail-image"]',
                'img[data-testid="product-image"]',
                'img.product-image',
                'img[class*="product"][class*="image"]',
                'img[class*="main"][class*="image"]',
                'img[class*="detail"][class*="image"]',
                'img[loading="lazy"]',
                'img[src*="static.zara.net"]',
                'img[src*="zara.net"]',
                'img[src*="zara.com"]',
                'img[alt*="product"]',
                'img[alt*="ürün"]',
                'img[alt*="Zara"]',
                'img[title*="product"]',
                'img[title*="ürün"]',
                'img[title*="Zara"]',
                'img[srcset*="zara"]',
                'img[srcset*="static.zara.net"]',
                'img[decoding="async"]',
                'img[data-nimg="1"]',
                'img[style*="color:transparent"]',
                'img[fetchpriority="high"]',
                'img[loading="eager"]'
            ],
            "old_price_selectors": [
                'span[data-qa-action="price-old"]',
                'span[data-testid="old-price"]',
                'span[data-testid="original-price"]',
                'span.price-old',
                'span.old-price',
                'span.original-price',
                'span[class*="price"][class*="old"]',
                'span[class*="old"][class*="price"]',
                'span[class*="price"][class*="original"]',
                'span[class*="original"][class*="price"]',
                '.price-old',
                '.old-price',
                '.original-price',
                '[data-testid="old-price"]',
                '[data-testid="original-price"]',
                '[class*="price"][class*="old"]',
                '[class*="old"][class*="price"]',
                '[class*="price"][class*="original"]',
                '[class*="original"][class*="price"]',
                's.price',
                'del.price',
                'span[class*="crossed"]',
                'span[class*="strikethrough"]',
                'span[class*="line-through"]',
                'span[class*="previous"]',
                'span[class*="before"]',
                'del[class*="price"]',
                's[class*="price"]'
            ],
            "size_selectors": [
                '.size-options',
                '.size-selector',
                '.size-list',
                '[class*="size"]',
                '[class*="beden"]',
                'select[class*="size"]',
                'select[class*="beden"]',
                'option[class*="size"]',
                'option[class*="beden"]',
                '.product-sizes',
                '.available-sizes',
                '.size-option',
                '.beden-option'
            ]
        },
        "superstep.com.tr": {
            "title_selectors": [
                'h1',
                'h1[class*="title"]',
                'h1[class*="product"]',
                'h1[class*="name"]',
                '[class*="product-title"]',
                '[class*="product-name"]',
                'title'
            ],
            "price_selectors": [
                'span.text-lg.leading-6.md\\:leading-7.font-bold.h-full.inline-block.text-primary[data-testid="price"]',
                'span[data-testid="price"]',
                'span.text-lg.leading-6.md\\:leading-7.font-bold',
                'span[class*="text-lg"][class*="font-bold"][class*="text-primary"]',
                'span[class*="price"]',
                'span[data-testid*="price"]',
                'span[class*="font-bold"]',
                'span[class*="text-primary"]'
            ],
            "image_selectors": [
                'img[alt*="New Balance"]',
                'img[title*="New Balance"]',
                'img[fetchpriority="high"]',
                'img[loading="eager"]',
                'img[data-nimg="1"]',
                'img[src*="akn-ss.a-cdn.akinoncloud.com"]',
                'img[srcset*="akn-ss.a-cdn.akinoncloud.com"]',
                'img[decoding="async"]',
                'img[style*="color: transparent"]',
                'img[width="1200"][height="1200"]',
                'img[src*="akinoncloud.com"]',
                'img[srcset*="akinoncloud.com"]'
            ],
            "old_price_selectors": [
                'span.font-medium.line-through',
                'span[class*="font-medium"][class*="line-through"]',
                'span[class*="line-through"]',
                'span[class*="strikethrough"]'
            ],
            "size_selectors": [
                '.size-options',
                '.size-selector',
                '.size-list',
                '[class*="size"]',
                '[class*="beden"]',
                'select[class*="size"]',
                'select[class*="beden"]',
                'option[class*="size"]',
                'option[class*="beden"]',
                '.product-sizes',
                '.available-sizes',
                '.size-option',
                '.beden-option'
            ]
        },
        "hm.com": {
            "title_selectors": [
                'h1[data-testid="product-name"]',
                'h1[data-qa-action="product-name"]',
                'h1.product-name',
                'h1.product-title',
                'h1[class*="product"][class*="name"]',
                'h1[class*="product"][class*="title"]',
                'h1[class*="name"]',
                'h1[class*="title"]',
                '[data-testid="product-name"]',
                '[data-qa-action="product-name"]',
                '[class*="product-name"]',
                '[class*="product-title"]',
                '[class*="name"]',
                '[class*="title"]',
                'h1',
                'title'
            ],
            "price_selectors": [
                'span[data-testid="price"]',
                'span[data-qa-action="price"]',
                'span.price',
                'span.product-price',
                'span[class*="price"]',
                'span[class*="product-price"]',
                '.price',
                '.product-price',
                '[data-testid="price"]',
                '[data-qa-action="price"]',
                '[class*="price"]',
                'span:contains("₺")',
                'span:contains("TL")',
                'span:contains("$")',
                'span:contains("€")'
            ],
            "image_selectors": [
                'img.product-image',
                'img[class*="product-image"]',
                'img[class*="product"][class*="image"]',
                'img[data-testid="product-image"]',
                'img[data-qa-action="product-image"]',
                'img[alt*="product"]',
                'img[alt*="ürün"]',
                'img[alt*="H&M"]',
                'img[title*="product"]',
                'img[title*="ürün"]',
                'img[title*="H&M"]',
                'img[src*="hm.com"]',
                'img[src*="hmcdn.net"]',
                'img[src*="static.hm.com"]',
                'img[loading="lazy"]',
                'img[decoding="async"]',
                'img[data-nimg="1"]',
                'img[style*="color:transparent"]',
                'img[fetchpriority="high"]',
                'img[loading="eager"]',
                'img[srcset*="hm.com"]',
                'img[srcset*="hmcdn.net"]',
                'img[srcset*="static.hm.com"]'
            ],
            "old_price_selectors": [
                'span[data-testid="old-price"]',
                'span[data-testid="original-price"]',
                'span.price-old',
                'span.old-price',
                'span.original-price',
                'span[class*="price"][class*="old"]',
                'span[class*="old"][class*="price"]',
                'span[class*="price"][class*="original"]',
                'span[class*="original"][class*="price"]',
                '.price-old',
                '.old-price',
                '.original-price',
                '[data-testid="old-price"]',
                '[data-testid="original-price"]',
                '[class*="price"][class*="old"]',
                '[class*="old"][class*="price"]',
                '[class*="price"][class*="original"]',
                '[class*="original"][class*="price"]',
                's.price',
                'del.price',
                'span[class*="crossed"]',
                'span[class*="strikethrough"]',
                'span[class*="line-through"]',
                'span[class*="previous"]',
                'span[class*="before"]',
                'del[class*="price"]',
                's[class*="price"]'
            ],
            "size_selectors": [
                '.size-options',
                '.size-selector',
                '.size-list',
                '[class*="size"]',
                '[class*="beden"]',
                'select[class*="size"]',
                'select[class*="beden"]',
                'option[class*="size"]',
                'option[class*="beden"]',
                '.product-sizes',
                '.available-sizes',
                '.size-option',
                '.beden-option'
            ]
        }
    }

# Rate limiting ve retry mekanizması
import time
from collections import defaultdict
from datetime import datetime, timedelta

# Rate limiting için global değişkenler
request_timestamps = defaultdict(list)
RATE_LIMIT_PER_DOMAIN = 2  # Her domain için saniyede maksimum istek
RATE_LIMIT_WINDOW = 60  # 60 saniyelik pencere

def check_rate_limit(domain):
    """Rate limiting kontrolü"""
    now = datetime.now()
    timestamps = request_timestamps[domain]
    
    # Eski timestamp'leri temizle (60 saniyeden eski)
    timestamps = [ts for ts in timestamps if now - ts < timedelta(seconds=RATE_LIMIT_WINDOW)]
    request_timestamps[domain] = timestamps
    
    # Rate limit kontrolü
    if len(timestamps) >= RATE_LIMIT_PER_DOMAIN:
        oldest_timestamp = min(timestamps)
        wait_time = RATE_LIMIT_WINDOW - (now - oldest_timestamp).total_seconds()
        if wait_time > 0:
            print(f"[RATE LIMIT] {domain} için {wait_time:.2f} saniye bekleniyor...")
            time.sleep(wait_time)
    
    # Yeni timestamp ekle
    request_timestamps[domain].append(now)

# Gelişmiş hata yakalama ve loglama sistemi
import logging
import json
from datetime import datetime

# Logging konfigürasyonu
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraping.log'),
        logging.StreamHandler()
    ]
)

# Scraping istatistikleri
scraping_stats = {
    'total_requests': 0,
    'successful_requests': 0,
    'failed_requests': 0,
    'domain_stats': defaultdict(lambda: {'success': 0, 'failed': 0}),
    'error_log': []
}

def log_scraping_error(url, error, attempt=1):
    """Scraping hatasını logla"""
    domain = extract_domain_from_url(url)
    error_info = {
        'timestamp': datetime.now().isoformat(),
        'url': url,
        'domain': domain,
        'error': str(error),
        'attempt': attempt
    }
    scraping_stats['error_log'].append(error_info)
    scraping_stats['failed_requests'] += 1
    scraping_stats['domain_stats'][domain]['failed'] += 1
    
    logging.error(f"Scraping hatası - URL: {url}, Domain: {domain}, Hata: {error}, Deneme: {attempt}")

def log_scraping_success(url, domain):
    """Başarılı scraping'i logla"""
    scraping_stats['successful_requests'] += 1
    scraping_stats['domain_stats'][domain]['success'] += 1
    logging.info(f"Başarılı scraping - URL: {url}, Domain: {domain}")

def get_scraping_stats():
    """Scraping istatistiklerini döndür"""
    total = scraping_stats['total_requests']
    success = scraping_stats['successful_requests']
    failed = scraping_stats['failed_requests']
    
    stats = {
        'total_requests': total,
        'successful_requests': success,
        'failed_requests': failed,
        'success_rate': (success / total * 100) if total > 0 else 0,
        'domain_stats': dict(scraping_stats['domain_stats']),
        'recent_errors': scraping_stats['error_log'][-10:]  # Son 10 hata
    }
    return stats

# Gelişmiş hata yakalama ile scraping fonksiyonunu güncelle
async def retry_scraping(url, max_retries=3, base_delay=2):
    """Retry mekanizması ile scraping - Gelişmiş hata yakalama"""
    domain = extract_domain_from_url(url)
    scraping_stats['total_requests'] += 1
    
    for attempt in range(max_retries):
        try:
            # Rate limiting kontrolü
            check_rate_limit(domain)
            
            print(f"[RETRY] Deneme {attempt + 1}/{max_retries} - {url}")
            
            # Scraping işlemi
            result = await perform_scraping(url)
            
            # Başarılı sonuç kontrolü
            if result and result.get('name') and result.get('name') != "İsim bulunamadı" and result.get('name') != "Scraping hatası - Lütfen URL'yi kontrol edin":
                print(f"[SUCCESS] Başarılı scraping - Deneme {attempt + 1}")
                log_scraping_success(url, domain)
                return result
            
            # Başarısız sonuç, tekrar dene
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)  # Exponential backoff
                print(f"[RETRY] Başarısız, {delay} saniye sonra tekrar deneniyor...")
                await asyncio.sleep(delay)
            
        except Exception as e:
            print(f"[RETRY ERROR] Deneme {attempt + 1} hatası: {e}")
            log_scraping_error(url, e, attempt + 1)
            
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)
                print(f"[RETRY] Hata sonrası {delay} saniye bekleniyor...")
                await asyncio.sleep(delay)
    
    # Tüm denemeler başarısız
    print(f"[FAILED] Tüm {max_retries} deneme başarısız")
    log_scraping_error(url, "Tüm denemeler başarısız", max_retries)
    
    return {
        "id": str(uuid.uuid4()),
        "url": url,
        "name": "Scraping başarısız - Lütfen URL'yi kontrol edin",
        "price": "🤷",
        "old_price": None,
        "image": None,
        "brand": detect_brand_from_url(url),
        "sizes": []
    }

# Hata durumlarını izleme ve raporlama
def monitor_scraping_health():
    """Scraping sağlığını izle"""
    stats = get_scraping_stats()
    
    # Başarı oranı düşükse uyarı
    if stats['success_rate'] < 70:
        logging.warning(f"Düşük başarı oranı: {stats['success_rate']:.2f}%")
    
    # En çok hata alan domain'leri raporla
    problematic_domains = []
    for domain, domain_stats in stats['domain_stats'].items():
        total = domain_stats['success'] + domain_stats['failed']
        if total > 5:  # En az 5 istek yapılmışsa
            success_rate = (domain_stats['success'] / total) * 100
            if success_rate < 50:
                problematic_domains.append({
                    'domain': domain,
                    'success_rate': success_rate,
                    'total_requests': total
                })
    
    if problematic_domains:
        logging.warning("Problemli domain'ler tespit edildi:")
        for domain_info in problematic_domains:
            logging.warning(f"  {domain_info['domain']}: {domain_info['success_rate']:.2f}% başarı ({domain_info['total_requests']} istek)")
    
    return stats

# API endpoint'leri ekle
@app.route("/api/scraping/stats")
@login_required
def get_scraping_statistics():
    """Scraping istatistiklerini döndür"""
    stats = monitor_scraping_health()
    return jsonify(stats)

@app.route("/api/scraping/health")
@login_required
def get_scraping_health():
    """Scraping sağlık durumunu döndür"""
    stats = get_scraping_stats()
    
    health_status = {
        'status': 'healthy' if stats['success_rate'] >= 80 else 'warning' if stats['success_rate'] >= 60 else 'critical',
        'success_rate': stats['success_rate'],
        'total_requests': stats['total_requests'],
        'recent_errors_count': len(stats['recent_errors']),
        'timestamp': datetime.now().isoformat()
    }
    
    return jsonify(health_status)

@app.route("/api/scraping/errors")
@login_required
def get_recent_errors():
    """Son hataları döndür"""
    return jsonify({
        'errors': scraping_stats['error_log'][-20:],  # Son 20 hata
        'total_errors': len(scraping_stats['error_log'])
    })

@app.route("/api/debug/scrape", methods=['POST'])
def debug_scrape():
    """Debug için scraping test endpoint'i"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL gerekli'}), 400
        
        print(f"[DEBUG] Test scraping başlıyor: {url}")
        
        # Asenkron scraping'i çalıştır
        import asyncio
        result = asyncio.run(scrape_product(url))
        
        return jsonify({
            'success': True,
            'result': result,
            'debug_info': {
                'url': url,
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        print(f"[DEBUG] Test scraping hatası: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'debug_info': {
                'url': url if 'url' in locals() else None,
                'timestamp': datetime.now().isoformat()
            }
        }), 500

# Hata durumlarını düzeltme önerileri
def get_error_suggestions(error_type, domain):
    """Hata türüne göre düzeltme önerileri"""
    suggestions = {
        'timeout': [
            'Sayfa yükleme süresini artırın',
            'Daha uzun bekleme süreleri ekleyin',
            'Network bağlantısını kontrol edin'
        ],
        'bot_detection': [
            'User-Agent değiştirin',
            'Daha fazla stealth script ekleyin',
            'İstek aralığını artırın',
            'Proxy kullanmayı düşünün'
        ],
        'selector_not_found': [
            'CSS selector\'ları güncelleyin',
            'Sayfa yapısını kontrol edin',
            'Alternatif selector\'lar ekleyin'
        ],
        'access_denied': [
            'Bot koruması aşma yöntemlerini geliştirin',
            'Daha fazla bekleme süresi ekleyin',
            'Site-specific yaklaşımlar kullanın'
        ]
    }
    
    return suggestions.get(error_type, ['Genel hata durumu - Logları kontrol edin'])

# Otomatik hata düzeltme önerileri
def analyze_and_suggest_fixes():
    """Hataları analiz et ve düzeltme önerileri sun"""
    stats = get_scraping_stats()
    suggestions = []
    
    # Son hataları analiz et
    recent_errors = stats['recent_errors']
    error_types = {}
    
    for error in recent_errors:
        error_msg = error['error'].lower()
        domain = error['domain']
        
        if 'timeout' in error_msg:
            error_types['timeout'] = error_types.get('timeout', 0) + 1
        elif 'bot' in error_msg or 'captcha' in error_msg:
            error_types['bot_detection'] = error_types.get('bot_detection', 0) + 1
        elif 'selector' in error_msg or 'element' in error_msg:
            error_types['selector_not_found'] = error_types.get('selector_not_found', 0) + 1
        elif 'access denied' in error_msg or '403' in error_msg:
            error_types['access_denied'] = error_types.get('access_denied', 0) + 1
    
    # En çok görülen hata türüne göre öneri ver
    if error_types:
        most_common_error = max(error_types, key=error_types.get)
        suggestions = get_error_suggestions(most_common_error, 'general')
    
    return {
        'error_analysis': error_types,
        'suggestions': suggestions,
        'total_errors_analyzed': len(recent_errors)
    }

@app.route("/api/scraping/suggestions")
@login_required
def get_scraping_suggestions():
    """Scraping iyileştirme önerilerini döndür"""
    analysis = analyze_and_suggest_fixes()
    return jsonify(analysis)

async def perform_scraping(url):
    """Asıl scraping işlemi (Render free plan optimized)"""
    print(f"[DEBUG] Scraping başlıyor: {url}")
    
    # Memory cleanup before scraping
    cleanup_memory()
    
    # Check cache
    cached_data = get_cached_result(url)
    if cached_data:
        print(f"[DEBUG] Cache'ten veri alındı: {url}")
        return cached_data
    
    # Domain kontrolü
    domain = extract_domain_from_url(url)
    if not domain:
        print(f"[HATA] Geçersiz URL: {url}")
        return {
            "id": str(uuid.uuid4()),
            "url": url,
            "name": "Geçersiz URL",
            "price": "🤷",
            "old_price": None,
            "image": None,
            "brand": "Bilinmiyor",
            "sizes": []
        }
    
    # Hepsiburada için Selenium kullan
    if "hepsiburada.com" in url:
        print(f"[DEBUG] Hepsiburada için Selenium kullanılıyor")
        try:
            from selenium_hepsiburada_scraper import scrape_hepsiburada_product
            result = scrape_hepsiburada_product(url)
            if result:
                standardized_result = {
                    'name': result.get('title', ''),
                    'price': result.get('current_price', ''),
                    'image': result.get('image', ''),
                    'brand': result.get('brand', ''),
                    'url': result.get('url', url)
                }
                set_cached_result(url, standardized_result)
                return standardized_result
        except ImportError:
            print(f"[UYARI] Selenium scraper bulunamadı, Playwright kullanılıyor")
        except Exception as e:
            print(f"[HATA] Hepsiburada Selenium hatası: {e}")
    
    # Dinamik marka tespiti
    brand = detect_brand_from_url(url)
    print(f"[DEBUG] Tespit edilen marka: {brand}")
    
    # Render'da headless mode kullan
    headless = True
    print(f"[DEBUG] Browser headless mode: {headless}")
    
    try:
        async with async_playwright() as p:
            # Browser'ı başlat - Render optimized ayarları
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-gpu',
                    '--disable-plugins',
                    '--disable-extensions',
                    '--disable-background-timer-throttling',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-renderer-backgrounding',
                    '--disable-features=TranslateUI',
                    '--disable-ipc-flooding-protection',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor',
                    '--disable-default-apps',
                    '--disable-sync',
                    '--disable-translate',
                    '--hide-scrollbars',
                    '--mute-audio',
                    '--no-default-browser-check',
                    '--no-pings',
                    '--disable-prompt-on-repost',
                    '--disable-hang-monitor',
                    '--disable-client-side-phishing-detection',
                    '--disable-component-update',
                    '--disable-domain-reliability',
                    '--disable-features=AudioServiceOutOfProcess',
                    '--disable-setuid-sandbox',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-background-networking',
                    '--disable-background-media-suspend',
                    '--memory-pressure-off',
                    '--max_old_space_size=4096',
                    '--single-process',
                    '--disable-dev-shm-usage',
                    '--disable-software-rasterizer',
                    '--disable-background-networking',
                    '--disable-default-apps',
                    '--disable-extensions',
                    '--disable-sync',
                    '--disable-translate',
                    '--hide-scrollbars',
                    '--metrics-recording-only',
                    '--mute-audio',
                    '--no-first-run',
                    '--safebrowsing-disable-auto-update',
                    '--ignore-certificate-errors',
                    '--ignore-ssl-errors',
                    '--ignore-certificate-errors-spki-list',
                    '--disable-web-security',
                    '--allow-running-insecure-content',
                    '--disable-features=VizDisplayCompositor',
                    '--disable-ipc-flooding-protection'
                ]
            )
            print(f"[DEBUG] Browser başlatıldı")
            
            try:
                # Context oluştur - Gelişmiş ayarlar
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    viewport={'width': 1920, 'height': 1080},
                    locale='tr-TR',
                    timezone_id='Europe/Istanbul',
                    extra_http_headers={
                        'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Referer': 'https://www.google.com/',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1',
                        'Sec-Fetch-Dest': 'document',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-Site': 'none',
                        'Sec-Fetch-User': '?1',
                        'Cache-Control': 'max-age=0',
                        'DNT': '1',
                        'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                        'Sec-Ch-Ua-Mobile': '?0',
                        'Sec-Ch-Ua-Platform': '"Windows"',
                    }
                )
                print(f"[DEBUG] Context oluşturuldu")
                
                # Sayfa oluştur
                page = await context.new_page()
                
                # Gelişmiş stealth script ekle
                await page.add_init_script(get_advanced_stealth_script())
                
                # Ürün sayfasına git
                await navigate_to_product_page(page, url)
                
                # Render'da daha uzun bekleme
                print(f"[DEBUG] Sayfa yükleme tamamlandı, veri çekme başlıyor...")
                await page.wait_for_timeout(5000)  # 5 saniye ek bekleme
                
                # Gelişmiş veri çekme
                title, price, old_price, image, sizes = await extract_enhanced_data(page, url)
                
                print(f"[DEBUG] ===== SCRAPING SONUÇLARI =====")
                print(f"[DEBUG] URL: {url}")
                print(f"[DEBUG] Başlık: {title}")
                print(f"[DEBUG] Mevcut Fiyat: {price}")
                print(f"[DEBUG] Eski Fiyat: {old_price}")
                print(f"[DEBUG] Marka: {brand}")
                print(f"[DEBUG] Görsel: {image}")
                print(f"[DEBUG] ================================")
                
                # Fiyat karşılaştırması için ek debug
                if price and old_price and price != "🤷" and old_price != "🤷":
                    print(f"[DEBUG] Fiyat analizi: Mevcut={price}, Eski={old_price}")
                    try:
                        # Basit sayısal karşılaştırma
                        price_clean = re.sub(r'[^\d,\.]', '', price)
                        old_price_clean = re.sub(r'[^\d,\.]', '', old_price)
                        
                        if ',' in price_clean and '.' in price_clean:
                            price_clean = price_clean.replace(',', '')
                        elif ',' in price_clean:
                            price_clean = price_clean.replace(',', '.')
                            
                        if ',' in old_price_clean and '.' in old_price_clean:
                            old_price_clean = old_price_clean.replace(',', '')
                        elif ',' in old_price_clean:
                            old_price_clean = old_price_clean.replace(',', '.')
                        
                        price_num = float(price_clean)
                        old_price_num = float(old_price_clean)
                        
                        if price_num > old_price_num:
                            print(f"[DEBUG] ⚠️  Mevcut fiyat ({price_num}) eski fiyattan ({old_price_num}) büyük!")
                        else:
                            print(f"[DEBUG] ✅ Fiyatlar mantıklı: Mevcut ({price_num}) <= Eski ({old_price_num})")
                    except:
                        print(f"[DEBUG] Fiyat sayısal karşılaştırma yapılamadı")
                
                result = {
                    "id": str(uuid.uuid4()),
                    "url": url,
                    "name": title.strip() if title else "İsim bulunamadı",
                    "price": price,
                    "old_price": old_price,
                    "image": image,
                    "brand": brand,
                    "sizes": sizes
                }
                set_cached_result(url, result)
                return result
                
            finally:
                await browser.close()

    except Exception as e:
        print(f"[HATA] Scraping başarısız: {e}")
        traceback.print_exc()
        result = {
            "id": str(uuid.uuid4()),
            "url": url,
            "name": "Scraping hatası - Lütfen URL'yi kontrol edin",
            "price": "🤷",
            "old_price": None,
            "image": None,
            "brand": brand,
            "sizes": []
        }
        set_cached_result(url, result)
        return result

# Ana scraping fonksiyonunu güncelle
async def scrape_product(url):
    """Ana scraping fonksiyonu - Retry mekanizması ile"""
    return await retry_scraping(url, max_retries=3, base_delay=2)



async def navigate_to_product_page(page, url):
    """Ürün sayfasına gitme işlemleri - Render optimized"""
    print(f"[DEBUG] Ürün sayfasına gidiliyor: {url}")
    
    # Genel ürün sayfası yükleme (tüm siteler için)
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=45000)
        print(f"[DEBUG] Sayfa yüklendi, bekleniyor...")
        await page.wait_for_timeout(2000)
        
        # Sayfanın tam yüklenmesini bekle
        try:
            await page.wait_for_load_state("networkidle", timeout=20000)
            print(f"[DEBUG] Network idle durumu beklendi")
        except:
            print(f"[DEBUG] Network idle timeout, devam ediliyor")
            pass
        
        # Basit scroll
        await page.evaluate("window.scrollTo(0, 300)")
        await page.wait_for_timeout(1000)
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(1000)
        
        print(f"[DEBUG] Genel sayfa hazırlığı tamamlandı")
    except Exception as e:
        print(f"[DEBUG] Genel sayfa yükleme hatası: {e}")
    
    # Site-specific işlemler (sadece kritik siteler için)
    if "zara.com" in url:
        print(f"[DEBUG] Zara için ek bekleme...")
        await page.wait_for_timeout(3000)
    elif "mango.com" in url:
        print(f"[DEBUG] Mango için ek bekleme...")
        await page.wait_for_timeout(3000)
    elif "bershka.com" in url:
        print(f"[DEBUG] Bershka için ek bekleme...")
        await page.wait_for_timeout(3000)
    elif "sahibinden.com" in url:
        print(f"[DEBUG] Sahibinden.com için ek bekleme...")
        await page.wait_for_timeout(3000)
    elif "hm.com" in url:
        print(f"[DEBUG] H&M ürün sayfasına gidiliyor...")
        
        # H&M ürün sayfasına git
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(8000)  # Daha uzun bekleme
        
        # Sayfanın tam yüklenmesini bekle
        try:
            await page.wait_for_load_state("networkidle", timeout=30000)
        except:
            pass
        
        # H&M için ek insan benzeri davranışlar
        await page.mouse.move(300, 300)
        await page.wait_for_timeout(1000)
        
        # Sayfayı scroll et
        await page.evaluate("window.scrollTo(0, 300)")
        await page.wait_for_timeout(2000)
        await page.evaluate("window.scrollTo(0, 600)")
        await page.wait_for_timeout(2000)
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(1000)
        
        # Mouse hareketleri
        await page.mouse.move(400, 400)
        await page.wait_for_timeout(500)
        await page.mouse.move(500, 500)
        await page.wait_for_timeout(500)
        
        # Bot koruması kontrolü
        try:
            page_title = await page.title()
            if "Access Denied" in page_title or "403" in page_title or "Forbidden" in page_title:
                print(f"[DEBUG] H&M bot koruması tespit edildi, daha uzun bekleniyor...")
                await page.wait_for_timeout(15000)  # 15 saniye daha bekle
                await page.reload()
                await page.wait_for_timeout(8000)
        except:
            pass
        
        print(f"[DEBUG] H&M ürün sayfası hazırlandı")
    else:
        # Diğer siteler için normal yaklaşım
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(5000)
        
        # Sayfanın tam yüklenmesini bekle
        try:
            await page.wait_for_load_state("networkidle", timeout=20000)
        except:
            pass
        
        # Ek bekleme
        await page.wait_for_timeout(3000)

async def extract_sizes(page, url, site_config):
    """Beden bilgilerini çekme işlemleri - Render optimized"""
    sizes = []
    
    # Site-specific beden çekme
    if site_config and 'size_selectors' in site_config:
        for selector in site_config['size_selectors']:
            try:
                size_elements = await page.query_selector_all(selector)
                for element in size_elements:
                    size_text = await element.text_content()
                    if size_text and size_text.strip():
                        sizes.append(size_text.strip())
                if sizes:
                    print(f"[DEBUG] Site-specific bedenler bulundu: {sizes}")
                    break
            except Exception as e:
                print(f"[DEBUG] Size selector hatası {selector}: {e}")
                continue
    
    # Columbia.com.tr ve Mudo.com.tr için özel filtreleme
    is_columbia = "columbia.com.tr" in url
    is_mudo = "mudo.com.tr" in url
    
    # Gelişmiş selector'ları kullan
    domain = extract_domain_from_url(url)
    enhanced_selectors = get_enhanced_selectors()
    if domain in enhanced_selectors and "size_selectors" in enhanced_selectors[domain]:
        selectors = enhanced_selectors[domain]["size_selectors"]
    else:
        selectors = [
            '.size-options',
            '.size-selector',
            '.size-list',
            '[class*="size"]',
            '[class*="beden"]',
            'select[class*="size"]',
            'select[class*="beden"]',
            'option[class*="size"]',
            'option[class*="beden"]',
            '.product-sizes',
            '.available-sizes',
            '.size-option',
            '.beden-option'
        ]
    
    for selector in selectors:
        try:
            size_elements = await page.query_selector_all(selector)
            for element in size_elements:
                text = await element.text_content()
                if text:
                    # Beden bilgilerini temizle ve ekle
                    size_text = text.strip()
                    
                    # Columbia.com.tr ve Mudo.com.tr için özel filtreleme
                    if is_columbia or is_mudo:
                        # Menü öğelerini filtrele
                        skip_words = [
                            'e-posta', 'email', 'üye ol', 'register', 'login', 'giriş', 'üye olun',
                            'montlar', 'ceketler', 'pantolonlar', 'elbiseler', 'ayakkabılar',
                            'yeni sezon', 'new season', 'indirim', 'sale', 'kampanya',
                            'kategoriler', 'categories', 'markalar', 'brands', 'yardım',
                            'help', 'iletişim', 'contact', 'hakkında', 'about', 'gizlilik',
                            'privacy', 'şartlar', 'terms', 'koşullar', 'conditions',
                            'sepet', 'cart', 'favoriler', 'favorites', 'hesabım', 'account',
                            'çıkış', 'logout', 'arama', 'search', 'menü', 'menu'
                        ]
                        
                        # Skip words kontrolü
                        if any(skip_word in size_text.lower() for skip_word in skip_words):
                            continue
                        
                        # Çok uzun metinleri filtrele (Columbia ve Mudo için daha sıkı)
                        if len(size_text) > 8:
                            continue
                    
                    if size_text and len(size_text) <= 10:  # Genel uzunluk kontrolü
                        # Beden formatları kontrolü
                        if any(size in size_text.upper() for size in ['XS', 'S', 'M', 'L', 'XL', 'XXL', 'XXXL', '2XL', '3XL', '4XL']):
                            if size_text not in sizes:
                                sizes.append(size_text)
                        elif any(size in size_text for size in ['36', '37', '38', '39', '40', '41', '42', '43', '44', '45', '46', '47', '48']):
                            if size_text not in sizes:
                                sizes.append(size_text)
                        # Columbia için ek beden formatları
                        elif is_columbia and any(size in size_text for size in ['36.5', '37.5', '38.5', '39.5', '40.5', '41.5', '42.5', '43.5', '44.5', '45.5']):
                            if size_text not in sizes:
                                sizes.append(size_text)
            
            if sizes:
                break
        except:
            continue
    
    print(f"[DEBUG] Çekilen bedenler: {sizes}")
    return sizes

async def extract_enhanced_data(page, url):
    """Gelişmiş veri çekme işlemleri - Render optimized"""
    print(f"[DEBUG] Gelişmiş veri çekme başlıyor: {url}")
    
    # Site-specific konfigürasyon al
    site_config = get_site_config(url)
    
    # Başlık çekme
    title = await extract_title(page, url, site_config)
    
    # Fiyat çekme
    price = await extract_price(page, url, site_config)
    
    # Eski fiyat çekme
    old_price = await extract_old_price(page, url, site_config)
    
    # Görsel çekme
    image = await extract_image(page, url, site_config)
    
    # Beden bilgisi çekme
    sizes = await extract_sizes(page, url, site_config)
    
    return title, price, old_price, image, sizes
    


async def extract_title(page, url, site_config):
    """Başlık çekme işlemleri - Render optimized"""
    title = None
    
    # Site-specific başlık çekme
    if site_config and 'title_selectors' in site_config:
        for selector in site_config['title_selectors']:
            try:
                title_element = await page.query_selector(selector)
                if title_element:
                    title = await title_element.text_content()
                    if title and title.strip():
                        title = title.strip().upper()
                        title = re.sub(r'[^\w\s\-\.]', '', title)
                        title = re.sub(r'\s+', ' ', title).strip()
                        print(f"[DEBUG] Site-specific başlık bulundu: {title}")
                        break
            except Exception as e:
                print(f"[DEBUG] Title selector hatası {selector}: {e}")
                continue
    
    # Gelişmiş selector'ları kullan
    domain = extract_domain_from_url(url)
    enhanced_selectors = get_enhanced_selectors()
    if domain in enhanced_selectors:
        selectors = enhanced_selectors[domain]["title_selectors"]
    else:
        selectors = [
            'h1[data-testid="product-detail-name"]',
            'h1.product-name',
            'h1.product-title',
            'h1.title',
            'h1',
            'title'
        ]
    
    for selector in selectors:
        try:
            if selector == 'title':
                title_element = await page.query_selector('title')
                if title_element:
                    title = await title_element.text_content()
            else:
                title_element = await page.query_selector(selector)
                if title_element:
                    title = await title_element.text_content()
            
            if title and title.strip():
                title = title.strip().upper()
                title = re.sub(r'[^\w\s\-\.]', '', title)
                title = re.sub(r'\s+', ' ', title).strip()
                break
        except:
            continue
    
    if not title or title == "WWW.SAHIBINDEN.COM":
        title = "Başlık bulunamadı"
    
    return title

async def extract_image(page, url, site_config):
    """Görsel çekme işlemleri - Render optimized"""
    image = None
    
    print(f"[DEBUG] Görsel çekme başlıyor: {url}")
    
    # Site-specific görsel çekme
    if site_config and 'image_selectors' in site_config:
        for selector in site_config['image_selectors']:
            try:
                img_element = await page.query_selector(selector)
                if img_element:
                    src = await img_element.get_attribute('src')
                    if src and (any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.webp', '.png'])):
                        # Relative URL'yi absolute yap
                        if src.startswith('//'):
                            src = 'https:' + src
                        elif src.startswith('/'):
                            from urllib.parse import urlparse
                            parsed = urlparse(url)
                            src = f"{parsed.scheme}://{parsed.netloc}{src}"
                        
                        image = src
                        print(f"[DEBUG] Site-specific görsel bulundu: {image}")
                        break
            except Exception as e:
                print(f"[DEBUG] Image selector hatası {selector}: {e}")
                continue
    
    # Pull&Bear için özel görsel çekme
    if "pullandbear.com" in url:
        print(f"[DEBUG] Pull&Bear özel görsel çekme başlıyor")
        
        # Pull&Bear'ın özel görsel selector'ları
        pullandbear_selectors = [
            # Ana ürün görseli
            'img[data-testid="product-image"]',
            'img[data-testid="product-detail-image"]',
            'img.product-image',
            'img.product-detail-image',
            'img.main-image',
            # Galeri görselleri
            'img[class*="gallery"]',
            'img[class*="carousel"]',
            'img[class*="slider"]',
            'img[class*="pdp"]',
            # Genel selector'lar
            'img[src*="product"]',
            'img[src*="main"]',
            'img[src*="detail"]',
            'img[src*="image"]',
            'img[src*="gallery"]',
            'img[src*="pdp"]',
            # Tüm img elementleri
            'img'
        ]
        
        for selector in pullandbear_selectors:
            try:
                print(f"[DEBUG] Pull&Bear selector deneniyor: {selector}")
                
                # Sayfayı scroll et
                await page.evaluate("window.scrollTo(0, 300)")
                await page.wait_for_timeout(1000)
                await page.evaluate("window.scrollTo(0, 600)")
                await page.wait_for_timeout(1000)
                
                img_elements = await page.query_selector_all(selector)
                print(f"[DEBUG] Pull&Bear {len(img_elements)} img elementi bulundu")
                
                for img in img_elements:
                    try:
                        src = await img.get_attribute('src')
                        srcset = await img.get_attribute('srcset')
                        alt = await img.get_attribute('alt') or ''
                        
                        print(f"[DEBUG] Pull&Bear element: src={src}, alt={alt}")
                        
                        # Ürün görseli kontrolü
                        if src and any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.webp', '.png', '.gif']):
                            # Logo, icon gibi görselleri filtrele
                            if not any(skip in src.lower() for skip in ['logo', 'icon', 'banner', 'header', 'footer', 'avatar', 'profile']):
                                # Boyut kontrolü
                                try:
                                    size = await img.bounding_box()
                                    if size and size['width'] > 100 and size['height'] > 100:
                                        image = src
                                        print(f"[DEBUG] Pull&Bear uygun görsel bulundu: {image}")
                                        break
                                except:
                                    image = src
                                    print(f"[DEBUG] Pull&Bear boyut kontrolü yapılamadı, görsel kabul edildi: {image}")
                                    break
                        
                        # srcset kontrolü
                        if srcset and not image:
                            srcset_urls = srcset.split(',')
                            for srcset_url in srcset_urls:
                                url_part = srcset_url.strip().split(' ')[0]
                                if any(ext in url_part.lower() for ext in ['.jpg', '.jpeg', '.webp', '.png', '.gif']):
                                    if not any(skip in url_part.lower() for skip in ['logo', 'icon', 'banner']):
                                        image = url_part
                                        print(f"[DEBUG] Pull&Bear srcset'ten görsel bulundu: {image}")
                                        break
                        
                        if image:
                            break
                            
                    except Exception as e:
                        print(f"[DEBUG] Pull&Bear element işlenirken hata: {e}")
                        continue
                
                if image:
                    break
                    
            except Exception as e:
                print(f"[DEBUG] Pull&Bear selector {selector} hatası: {e}")
                continue
        
        if image:
            # Görsel URL'ini düzelt
            if image.startswith('//'):
                image = 'https:' + image
            elif image.startswith('/'):
                from urllib.parse import urlparse
                parsed_url = urlparse(url)
                image = f"{parsed_url.scheme}://{parsed_url.netloc}{image}"
            elif not image.startswith('http'):
                from urllib.parse import urljoin
                image = urljoin(url, image)
            
            print(f"[DEBUG] Pull&Bear final görsel URL: {image}")
            return image
        else:
            print(f"[DEBUG] Pull&Bear hiçbir görsel bulunamadı!")
    
    # Mudo.com.tr için özel görsel çekme
    if "mudo.com.tr" in url:
        print(f"[DEBUG] Mudo.com.tr özel görsel çekme başlıyor")
        
        # Mudo'nun özel görsel selector'ları
        mudo_selectors = [
            # Ana ürün görseli
            'img.product-image',
            'img.product-main-image',
            'img.main-product-image',
            'img[class*="product"][class*="image"]',
            'img[class*="main"][class*="image"]',
            'img[class*="detail"][class*="image"]',
            # Galeri görselleri
            'img[class*="gallery"]',
            'img[class*="carousel"]',
            'img[class*="slider"]',
            'img[class*="pdp"]',
            # Mudo özel selector'ları
            'img[src*="mudo.com.tr"]',
            'img[src*="mudo"]',
            'img[alt*="Mudo"]',
            'img[alt*="mudo"]',
            'img[title*="Mudo"]',
            'img[title*="mudo"]',
            # Genel selector'lar
            'img[src*="product"]',
            'img[src*="main"]',
            'img[src*="detail"]',
            'img[src*="image"]',
            'img[src*="gallery"]',
            'img[src*="pdp"]',
            # Tüm img elementleri
            'img'
        ]
        
        for selector in mudo_selectors:
            try:
                print(f"[DEBUG] Mudo selector deneniyor: {selector}")
                
                # Sayfayı scroll et
                await page.evaluate("window.scrollTo(0, 300)")
                await page.wait_for_timeout(1000)
                await page.evaluate("window.scrollTo(0, 600)")
                await page.wait_for_timeout(1000)
                
                img_elements = await page.query_selector_all(selector)
                print(f"[DEBUG] Mudo {len(img_elements)} img elementi bulundu")
                
                for img in img_elements:
                    try:
                        src = await img.get_attribute('src')
                        srcset = await img.get_attribute('srcset')
                        alt = await img.get_attribute('alt') or ''
                        
                        print(f"[DEBUG] Mudo element: src={src}, alt={alt}")
                        
                        # Ürün görseli kontrolü
                        if src and any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.webp', '.png', '.gif']):
                            # Logo, icon gibi görselleri filtrele
                            if not any(skip in src.lower() for skip in ['logo', 'icon', 'banner', 'header', 'footer', 'avatar', 'profile']):
                                # Boyut kontrolü
                                try:
                                    size = await img.bounding_box()
                                    if size and size['width'] > 100 and size['height'] > 100:
                                        image = src
                                        print(f"[DEBUG] Mudo uygun görsel bulundu: {image}")
                                        break
                                except:
                                    image = src
                                    print(f"[DEBUG] Mudo boyut kontrolü yapılamadı, görsel kabul edildi: {image}")
                                    break
                        
                        # srcset kontrolü
                        if srcset and not image:
                            srcset_urls = srcset.split(',')
                            for srcset_url in srcset_urls:
                                url_part = srcset_url.strip().split(' ')[0]
                                if any(ext in url_part.lower() for ext in ['.jpg', '.jpeg', '.webp', '.png', '.gif']):
                                    if not any(skip in url_part.lower() for skip in ['logo', 'icon', 'banner']):
                                        image = url_part
                                        print(f"[DEBUG] Mudo srcset'ten görsel bulundu: {image}")
                                        break
                        
                        if image:
                            break
                            
                    except Exception as e:
                        print(f"[DEBUG] Mudo element işlenirken hata: {e}")
                        continue
                
                if image:
                    break
                    
            except Exception as e:
                print(f"[DEBUG] Mudo selector {selector} hatası: {e}")
                continue
        
        if image:
            # Görsel URL'ini düzelt
            if image.startswith('//'):
                image = 'https:' + image
            elif image.startswith('/'):
                from urllib.parse import urlparse
                parsed_url = urlparse(url)
                image = f"{parsed_url.scheme}://{parsed_url.netloc}{image}"
            elif not image.startswith('http'):
                from urllib.parse import urljoin
                image = urljoin(url, image)
            
            print(f"[DEBUG] Mudo final görsel URL: {image}")
            return image
        else:
            print(f"[DEBUG] Mudo hiçbir görsel bulunamadı!")
    
    # Columbia.com.tr için özel görsel çekme
    if "columbia.com.tr" in url:
        print(f"[DEBUG] Columbia.com.tr özel görsel çekme başlıyor")
        
        # Columbia'nın özel görsel selector'ları
        columbia_selectors = [
            # Ana ürün görseli
            'img.product-image',
            'img.product-main-image',
            'img.main-product-image',
            'img[class*="product"][class*="image"]',
            'img[class*="main"][class*="image"]',
            'img[class*="detail"][class*="image"]',
            # Galeri görselleri
            'img[class*="gallery"]',
            'img[class*="carousel"]',
            'img[class*="slider"]',
            'img[class*="pdp"]',
            # Columbia özel selector'ları
            'img[src*="columbia.com.tr"]',
            'img[src*="columbia"]',
            'img[alt*="Columbia"]',
            'img[alt*="columbia"]',
            'img[title*="Columbia"]',
            'img[title*="columbia"]',
            # Genel selector'lar
            'img[src*="product"]',
            'img[src*="main"]',
            'img[src*="detail"]',
            'img[src*="image"]',
            'img[src*="gallery"]',
            'img[src*="pdp"]',
            # Tüm img elementleri
            'img'
        ]
        
        for selector in columbia_selectors:
            try:
                print(f"[DEBUG] Columbia selector deneniyor: {selector}")
                
                # Sayfayı scroll et
                await page.evaluate("window.scrollTo(0, 300)")
                await page.wait_for_timeout(1000)
                await page.evaluate("window.scrollTo(0, 600)")
                await page.wait_for_timeout(1000)
                
                img_elements = await page.query_selector_all(selector)
                print(f"[DEBUG] Columbia {len(img_elements)} img elementi bulundu")
                
                for img in img_elements:
                    try:
                        src = await img.get_attribute('src')
                        srcset = await img.get_attribute('srcset')
                        alt = await img.get_attribute('alt') or ''
                        
                        print(f"[DEBUG] Columbia element: src={src}, alt={alt}")
                        
                        # Ürün görseli kontrolü
                        if src and any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.webp', '.png', '.gif']):
                            # Logo, icon gibi görselleri filtrele
                            if not any(skip in src.lower() for skip in ['logo', 'icon', 'banner', 'header', 'footer', 'avatar', 'profile']):
                                # Boyut kontrolü
                                try:
                                    size = await img.bounding_box()
                                    if size and size['width'] > 100 and size['height'] > 100:
                                        image = src
                                        print(f"[DEBUG] Columbia uygun görsel bulundu: {image}")
                                        break
                                except:
                                    image = src
                                    print(f"[DEBUG] Columbia boyut kontrolü yapılamadı, görsel kabul edildi: {image}")
                                    break
                        
                        # srcset kontrolü
                        if srcset and not image:
                            srcset_urls = srcset.split(',')
                            for srcset_url in srcset_urls:
                                url_part = srcset_url.strip().split(' ')[0]
                                if any(ext in url_part.lower() for ext in ['.jpg', '.jpeg', '.webp', '.png', '.gif']):
                                    if not any(skip in url_part.lower() for skip in ['logo', 'icon', 'banner']):
                                        image = url_part
                                        print(f"[DEBUG] Columbia srcset'ten görsel bulundu: {image}")
                                        break
                        
                        if image:
                            break
                            
                    except Exception as e:
                        print(f"[DEBUG] Columbia element işlenirken hata: {e}")
                        continue
                
                if image:
                    break
                    
            except Exception as e:
                print(f"[DEBUG] Columbia selector {selector} hatası: {e}")
                continue
        
        if image:
            # Görsel URL'ini düzelt
            if image.startswith('//'):
                image = 'https:' + image
            elif image.startswith('/'):
                from urllib.parse import urlparse
                parsed_url = urlparse(url)
                image = f"{parsed_url.scheme}://{parsed_url.netloc}{image}"
            elif not image.startswith('http'):
                from urllib.parse import urljoin
                image = urljoin(url, image)
            
            print(f"[DEBUG] Columbia final görsel URL: {image}")
            return image
        else:
            print(f"[DEBUG] Columbia hiçbir görsel bulunamadı!")
    
    # Bershka için özel görsel çekme
    if "bershka.com" in url:
        print(f"[DEBUG] Bershka özel görsel çekme başlıyor")
        
        # Bershka'nın özel görsel selector'ları
        bershka_selectors = [
            # Ana ürün görseli
            'img.product-image',
            'img.product-main-image',
            'img.main-product-image',
            'img[class*="product"][class*="image"]',
            'img[class*="main"][class*="image"]',
            'img[class*="detail"][class*="image"]',
            # Galeri görselleri
            'img[class*="gallery"]',
            'img[class*="carousel"]',
            'img[class*="slider"]',
            'img[class*="pdp"]',
            # Genel selector'lar
            'img[src*="product"]',
            'img[src*="main"]',
            'img[src*="detail"]',
            'img[src*="image"]',
            'img[src*="gallery"]',
            'img[src*="pdp"]',
            # Tüm img elementleri
            'img'
        ]
        
        for selector in bershka_selectors:
            try:
                print(f"[DEBUG] Bershka selector deneniyor: {selector}")
                
                # Sayfayı scroll et
                await page.evaluate("window.scrollTo(0, 300)")
                await page.wait_for_timeout(1000)
                await page.evaluate("window.scrollTo(0, 600)")
                await page.wait_for_timeout(1000)
                
                img_elements = await page.query_selector_all(selector)
                print(f"[DEBUG] Bershka {len(img_elements)} img elementi bulundu")
                
                for img in img_elements:
                    try:
                        src = await img.get_attribute('src')
                        srcset = await img.get_attribute('srcset')
                        alt = await img.get_attribute('alt') or ''
                        
                        print(f"[DEBUG] Bershka element: src={src}, alt={alt}")
                        
                        # Ürün görseli kontrolü
                        if src and any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.webp', '.png', '.gif']):
                            # Logo, icon gibi görselleri filtrele
                            if not any(skip in src.lower() for skip in ['logo', 'icon', 'banner', 'header', 'footer', 'avatar', 'profile']):
                                # Boyut kontrolü
                                try:
                                    size = await img.bounding_box()
                                    if size and size['width'] > 100 and size['height'] > 100:
                                        image = src
                                        print(f"[DEBUG] Bershka uygun görsel bulundu: {image}")
                                        break
                                except:
                                    image = src
                                    print(f"[DEBUG] Bershka boyut kontrolü yapılamadı, görsel kabul edildi: {image}")
                                    break
                        
                        # srcset kontrolü
                        if srcset and not image:
                            srcset_urls = srcset.split(',')
                            for srcset_url in srcset_urls:
                                url_part = srcset_url.strip().split(' ')[0]
                                if any(ext in url_part.lower() for ext in ['.jpg', '.jpeg', '.webp', '.png', '.gif']):
                                    if not any(skip in url_part.lower() for skip in ['logo', 'icon', 'banner']):
                                        image = url_part
                                        print(f"[DEBUG] Bershka srcset'ten görsel bulundu: {image}")
                                        break
                        
                        if image:
                            break
                            
                    except Exception as e:
                        print(f"[DEBUG] Bershka element işlenirken hata: {e}")
                        continue
                
                if image:
                    break
                    
            except Exception as e:
                print(f"[DEBUG] Bershka selector {selector} hatası: {e}")
                continue
        
        if image:
            # Görsel URL'ini düzelt
            if image.startswith('//'):
                image = 'https:' + image
            elif image.startswith('/'):
                from urllib.parse import urlparse
                parsed_url = urlparse(url)
                image = f"{parsed_url.scheme}://{parsed_url.netloc}{image}"
            elif not image.startswith('http'):
                from urllib.parse import urljoin
                image = urljoin(url, image)
            
            print(f"[DEBUG] Bershka final görsel URL: {image}")
            return image
        else:
            print(f"[DEBUG] Bershka hiçbir görsel bulunamadı!")
    
    # Render'da daha uzun bekleme
    
    # Render'da daha uzun bekleme
    try:
        await page.wait_for_timeout(3000)  # 3 saniye bekle
        print(f"[DEBUG] Sayfa yükleme beklendi")
    except:
        pass
    
    # Gelişmiş selector'ları kullan
    domain = extract_domain_from_url(url)
    enhanced_selectors = get_enhanced_selectors()
    if domain in enhanced_selectors:
        selectors = enhanced_selectors[domain]["image_selectors"]
        print(f"[DEBUG] Domain-specific selector'lar kullanılıyor: {domain}")
    else:
        selectors = [
            # Öncelikli selector'lar
            'img[data-testid="product-detail-image"]',
            'img[data-testid="product-image"]',
            'img.product-detail-image',
            'img.product-main-image',
            'img.main-product-image',
            'img[class*="product"][class*="image"]',
            'img[class*="main"][class*="image"]',
            'img[class*="detail"][class*="image"]',
            'img[alt*="ürün"]',
            'img[alt*="product"]',
            'img[alt*="main"]',
            'img[alt*="detail"]',
            # Genel selector'lar
            'img[src*="product"]',
            'img[src*="main"]',
            'img[src*="detail"]',
            'img[src*="image"]',
            # Tüm img elementleri (son çare)
            'img'
        ]
        print(f"[DEBUG] Genel selector'lar kullanılıyor")
    
    print(f"[DEBUG] Toplam {len(selectors)} selector deneniyor")
    
    for i, selector in enumerate(selectors):
        try:
            print(f"[DEBUG] Selector {i+1}/{len(selectors)} deneniyor: {selector}")
            
            # Sayfayı scroll et (görsellerin yüklenmesi için)
            await page.evaluate("window.scrollTo(0, 300)")
            await page.wait_for_timeout(1000)
            await page.evaluate("window.scrollTo(0, 600)")
            await page.wait_for_timeout(1000)
            
            img_elements = await page.query_selector_all(selector)
            print(f"[DEBUG] {len(img_elements)} img elementi bulundu")
            
            for j, img in enumerate(img_elements):
                try:
                    src = await img.get_attribute('src')
                    srcset = await img.get_attribute('srcset')
                    alt = await img.get_attribute('alt') or ''
                    
                    print(f"[DEBUG] Element {j+1}: src={src}, alt={alt}")
                    
                    # Ürün görseli olup olmadığını kontrol et
                    if src and any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.webp', '.png', '.gif']):
                        # Logo, icon gibi küçük görselleri filtrele
                        if not any(skip in src.lower() for skip in ['logo', 'icon', 'banner', 'header', 'footer', 'avatar', 'profile']):
                            # Boyut kontrolü (çok küçük görselleri filtrele)
                            try:
                                size = await img.bounding_box()
                                if size and size['width'] > 100 and size['height'] > 100:
                                    image = src
                                    print(f"[DEBUG] Uygun görsel bulundu: {image}")
                                    break
                            except:
                                image = src
                                print(f"[DEBUG] Boyut kontrolü yapılamadı, görsel kabul edildi: {image}")
                                break
                    
                    # srcset kontrolü
                    if srcset and not image:
                        srcset_urls = srcset.split(',')
                        for srcset_url in srcset_urls:
                            url_part = srcset_url.strip().split(' ')[0]
                            if any(ext in url_part.lower() for ext in ['.jpg', '.jpeg', '.webp', '.png', '.gif']):
                                if not any(skip in url_part.lower() for skip in ['logo', 'icon', 'banner']):
                                    image = url_part
                                    print(f"[DEBUG] srcset'ten görsel bulundu: {image}")
                                    break
                    
                    if image:
                        break
                        
                except Exception as e:
                    print(f"[DEBUG] Element {j+1} işlenirken hata: {e}")
                    continue
            
            if image:
                break
                
        except Exception as e:
            print(f"[DEBUG] Selector {selector} hatası: {e}")
            continue
    
    # Görsel URL'ini düzelt
    if image:
        if image.startswith('//'):
            image = 'https:' + image
        elif image.startswith('/'):
            from urllib.parse import urlparse
            parsed_url = urlparse(url)
            image = f"{parsed_url.scheme}://{parsed_url.netloc}{image}"
        elif not image.startswith('http'):
            from urllib.parse import urljoin
            image = urljoin(url, image)
        
        print(f"[DEBUG] Final görsel URL: {image}")
    else:
        print(f"[DEBUG] Hiçbir görsel bulunamadı! Alternatif yöntem deneniyor...")
        
        # Alternatif yöntem: Tüm görselleri topla ve en uygun olanını seç
        try:
            all_images = await page.evaluate("""
                () => {
                    const images = Array.from(document.querySelectorAll('img'));
                    return images.map(img => ({
                        src: img.src,
                        alt: img.alt || '',
                        width: img.naturalWidth || img.width,
                        height: img.naturalHeight || img.height,
                        className: img.className || '',
                        id: img.id || ''
                    })).filter(img => 
                        img.src && 
                        img.src.length > 0 &&
                        !img.src.includes('logo') &&
                        !img.src.includes('icon') &&
                        !img.src.includes('banner') &&
                        !img.src.includes('header') &&
                        !img.src.includes('footer') &&
                        !img.src.includes('avatar') &&
                        !img.src.includes('profile')
                    );
                }
            """)
            
            print(f"[DEBUG] Alternatif yöntemle {len(all_images)} görsel bulundu")
            
            # En büyük görseli seç
            best_image = None
            max_size = 0
            
            for img_info in all_images:
                size = img_info.get('width', 0) * img_info.get('height', 0)
                if size > max_size and size > 10000:  # En az 100x100 piksel
                    max_size = size
                    best_image = img_info.get('src')
            
            if best_image:
                image = best_image
                print(f"[DEBUG] Alternatif yöntemle görsel bulundu: {image}")
            else:
                print(f"[DEBUG] Alternatif yöntemle de görsel bulunamadı")
                
        except Exception as e:
            print(f"[DEBUG] Alternatif görsel çekme hatası: {e}")
    
    return image

async def extract_price(page, url, site_config):
    """Fiyat çekme işlemleri - Render optimized"""
    price = None
    
    # Site-specific fiyat çekme
    if site_config and 'price_selectors' in site_config:
        for selector in site_config['price_selectors']:
            try:
                price_element = await page.query_selector(selector)
                if price_element:
                    price_text = await price_element.text_content()
                    if price_text and price_text.strip():
                        price_text = price_text.strip()
                        price_text = re.sub(r'[^\d,\.]', '', price_text)
                        price_text = price_text.replace(',', '.')
                        
                        if re.match(r'^\d+\.?\d*$', price_text):
                            price_num = float(price_text)
                            if price_num >= 1000:
                                price = f"{price_num:,.2f} TL".replace(',', 'X').replace('.', ',').replace('X', '.')
                            else:
                                price = f"{price_num:.2f} TL".replace('.', ',')
                            print(f"[DEBUG] Site-specific fiyat bulundu: {price}")
                            break
            except Exception as e:
                print(f"[DEBUG] Price selector hatası {selector}: {e}")
                continue
    
    # Gelişmiş selector'ları kullan
    domain = extract_domain_from_url(url)
    enhanced_selectors = get_enhanced_selectors()
    if domain in enhanced_selectors:
        selectors = enhanced_selectors[domain]["price_selectors"]
    else:
        # Önce mevcut/indirimli fiyatları ara, sonra genel fiyatları
        selectors = [
            # Öncelikli olarak mevcut/indirimli fiyat selector'ları
            '.price-current',
            '.sale-price',
            '.discount-price',
            '.price-sale',
            '.product-sale',
            '.current-price',
            '.final-price',
            '.price-final',
            '.price-now',
            '.price-new',
            '[data-testid="current-price"]',
            '[data-testid="sale-price"]',
            '[data-testid="final-price"]',
            '[class*="current"][class*="price"]',
            '[class*="sale"][class*="price"]',
            '[class*="discount"][class*="price"]',
            '[class*="final"][class*="price"]',
            '[class*="new"][class*="price"]',
            # Sonra genel fiyat selector'ları
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
    
    for selector in selectors:
        try:
            price_elements = await page.query_selector_all(selector)
            for element in price_elements:
                text = await element.text_content()
                if text and ('₺' in text or 'TL' in text):
                    # Eski fiyat selector'larını kontrol et - bunları atla
                    element_class = await element.get_attribute('class') or ''
                    element_id = await element.get_attribute('id') or ''
                    element_style = await element.get_attribute('style') or ''
                    
                    # Eski fiyat göstergelerini kontrol et
                    is_old_price = any(indicator in (element_class + element_id + element_style).lower() 
                                     for indicator in ['old', 'original', 'before', 'previous', 'crossed', 'strikethrough', 'line-through'])
                    
                    if is_old_price:
                        print(f"[DEBUG] Eski fiyat elementi atlandı: {text}")
                        continue
                    
                    # Fiyat regex'i
                    price_pattern = re.compile(r'([0-9]{1,3}(?:\.[0-9]{3})*,[0-9]{2}\s*(?:₺|TL)|[0-9]{1,3}(?:\.[0-9]{3})*\s*(?:₺|TL)|[0-9]+(?:\.[0-9]{2})?\s*(?:₺|TL))')
                    match = price_pattern.search(text)
                    if match:
                        price = match.group(1)
                        print(f"[DEBUG] Mevcut fiyat bulundu: {price} (selector: {selector})")
                        break
            if price:
                break
        except:
            continue
    
    # Regex fallback
    if not price:
        try:
            page_text = await page.text_content()
            price_pattern = re.compile(r'([0-9]{1,3}(?:\.[0-9]{3})*,[0-9]{2}\s*(?:₺|TL)|[0-9]{1,3}(?:\.[0-9]{3})*\s*(?:₺|TL)|[0-9]+(?:\.[0-9]{2})?\s*(?:₺|TL))')
            match = price_pattern.search(page_text)
            if match:
                price = match.group(1)
            else:
                price = "🤷"
        except Exception as e:
            print(f"[DEBUG] Page text content hatası: {e}")
            price = "🤷"
    
    print(f"[DEBUG] Mevcut fiyat çekme sonucu: {price}")
    return price

async def compare_and_validate_prices(current_price, old_price):
    """Fiyatları karşılaştır ve doğrula"""
    if not current_price or not old_price:
        return current_price, old_price
    
    try:
        # Fiyatları sayısal değerlere çevir
        def extract_numeric_price(price_str):
            if not price_str or price_str == "🤷":
                return None
            # Sadece sayıları ve nokta/virgülü al
            clean_price = re.sub(r'[^\d,\.]', '', price_str)
            if ',' in clean_price and '.' in clean_price:
                # Hem virgül hem nokta varsa, virgülü binlik ayırıcı olarak kabul et
                clean_price = clean_price.replace(',', '')
            elif ',' in clean_price:
                # Sadece virgül varsa, ondalık ayırıcı olarak kabul et
                clean_price = clean_price.replace(',', '.')
            return float(clean_price)
        
        current_num = extract_numeric_price(current_price)
        old_num = extract_numeric_price(old_price)
        
        if current_num and old_num:
            # Eğer mevcut fiyat eski fiyattan büyükse, muhtemelen yanlış
            if current_num > old_num:
                print(f"[DEBUG] Fiyat karşılaştırması: Mevcut fiyat ({current_price}) eski fiyattan ({old_price}) büyük, değiştiriliyor")
                return old_price, current_price
            else:
                print(f"[DEBUG] Fiyat karşılaştırması: Mevcut fiyat ({current_price}) eski fiyattan ({old_price}) küçük, doğru")
        
    except Exception as e:
        print(f"[DEBUG] Fiyat karşılaştırma hatası: {e}")
    
    return current_price, old_price

async def extract_old_price(page, url, site_config):
    """Eski fiyat çekme işlemleri - Render optimized"""
    old_price = None
    
    # Site-specific eski fiyat çekme
    if site_config and 'old_price_selectors' in site_config:
        for selector in site_config['old_price_selectors']:
            try:
                old_price_element = await page.query_selector(selector)
                if old_price_element:
                    old_price_text = await old_price_element.text_content()
                    if old_price_text and old_price_text.strip():
                        old_price_text = old_price_text.strip()
                        old_price_text = re.sub(r'[^\d,\.]', '', old_price_text)
                        old_price_text = old_price_text.replace(',', '.')
                        
                        if re.match(r'^\d+\.?\d*$', old_price_text):
                            old_price_num = float(old_price_text)
                            if old_price_num >= 1000:
                                old_price = f"{old_price_num:,.2f} TL".replace(',', 'X').replace('.', ',').replace('X', '.')
                            else:
                                old_price = f"{old_price_num:.2f} TL".replace('.', ',')
                            print(f"[DEBUG] Site-specific eski fiyat bulundu: {old_price}")
                            break
            except Exception as e:
                print(f"[DEBUG] Old price selector hatası {selector}: {e}")
                continue
    
    # Genel eski fiyat selector'ları
    old_price_selectors = [
        '.old-price',
        '.price-old',
        '.original-price',
        '.price-original',
        '.price-before',
        '.price-previous',
        's.price',
        'del.price',
        '[class*="old"][class*="price"]',
        '[class*="original"][class*="price"]',
        '.nodiscount-price',  # Mavi sitesi için
        'span.nodiscount-price',  # Mavi sitesi için
        'span[class*="crossed"]',
        'span[class*="strikethrough"]',
        'span[class*="line-through"]',
        'span[class*="previous"]',
        'span[class*="before"]',
        'del[class*="price"]',
        's[class*="price"]',
        'span[class*="discount"]',
        'span[class*="sale"]',
        '[data-testid*="old"]',
        '[data-testid*="original"]',
        '[data-testid*="previous"]',
        'span[style*="text-decoration: line-through"]',
        'span[style*="text-decoration:line-through"]'
    ]
    
    for selector in old_price_selectors:
        try:
            old_price_elements = await page.query_selector_all(selector)
            for element in old_price_elements:
                text = await element.text_content()
                if text and ('₺' in text or 'TL' in text):
                    # Mavi sitesi için özel temizleme
                    if "mavi.com" in url and "nodiscount-price" in str(element):
                        # Mavi eski fiyatları "499,99 TL" formatında gelir
                        old_price_clean = re.sub(r'[^\d,\.]', '', text)
                        if old_price_clean:
                            # Virgül ondalık ayırıcıyı nokta yap
                            old_price_clean = old_price_clean.replace(',', '.')
                            if old_price_clean:
                                try:
                                    old_price_num = float(old_price_clean)
                                    # Türkçe format: 499,99 TL
                                    old_price = f"{old_price_num:.2f} TL".replace('.', ',')
                                    print(f"[DEBUG] Mavi eski fiyat genel selector'dan bulundu: {old_price}")
                                    break
                                except ValueError:
                                    continue
                    else:
                        # Diğer siteler için gelişmiş pattern
                        # Önce temizleme yap
                        text_clean = re.sub(r'[^\d,\.\s₺TL]', '', text)
                        
                        # Farklı fiyat formatlarını dene
                        price_patterns = [
                            r'([0-9]{1,3}(?:\.[0-9]{3})*,[0-9]{2}\s*(?:₺|TL))',  # 1.234,56 TL
                            r'([0-9]{1,3}(?:\.[0-9]{3})*\s*(?:₺|TL))',  # 1.234 TL
                            r'([0-9]+(?:\.[0-9]{2})?\s*(?:₺|TL))',  # 1234.56 TL
                            r'([0-9]+,[0-9]{2}\s*(?:₺|TL))',  # 1234,56 TL
                            r'([0-9]+\s*(?:₺|TL))',  # 1234 TL
                            r'([0-9]+(?:\.[0-9]{3})*\s*(?:₺|TL))',  # 1.234 TL (nokta binlik ayırıcı)
                        ]
                        
                        for pattern in price_patterns:
                            match = re.search(pattern, text_clean)
                            if match:
                                old_price = match.group(1)
                                print(f"[DEBUG] Eski fiyat bulundu: {old_price}")
                                break
                        
                        if old_price:
                            break
            if old_price:
                break
        except:
            continue
    
    print(f"[DEBUG] Eski fiyat çekme sonucu: {old_price}")
    return old_price

@app.route("/")
def index():
    # Health check for Render free plan
    cleanup_memory()
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return render_template("index.html")



@app.route("/test-scraping")
def test_scraping():
    """Test scraping endpoint for debugging"""
    import asyncio
    
    # Test URL'leri
    test_urls = [
        "https://www2.hm.com/tr_tr/productpage.1234567.html",  # H&M örnek
        "https://www.zara.com/tr/tr/example-product-p1234567.html",  # Zara örnek
    ]
    
    results = []
    
    for url in test_urls:
        try:
            # Async scraping'i test et
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(scrape_product(url))
                results.append({
                    "url": url,
                    "success": True,
                    "data": result
                })
            finally:
                loop.close()
        except Exception as e:
            results.append({
                "url": url,
                "success": False,
                "error": str(e)
            })
    
    return jsonify({
        "test_results": results,
        "message": "Test scraping completed"
    })

@app.route("/admin/brands")
@login_required
def manage_brands():
    """Dinamik markaları yönet"""
    dynamic_brands = load_dynamic_brands()
    all_brands = BRANDS + dynamic_brands
    return render_template("manage_brands.html", brands=all_brands, dynamic_brands=dynamic_brands)

@app.route("/admin/brands/add", methods=["POST"])
@login_required
def add_brand_manual():
    """Manuel olarak marka ekle"""
    domain = request.form.get("domain")
    brand_name = request.form.get("brand_name")
    
    if domain and brand_name:
        dynamic_brands = load_dynamic_brands()
        
        # Zaten var mı kontrol et
        for existing_domain, existing_name in dynamic_brands:
            if existing_domain == domain:
                flash("Bu domain zaten mevcut", "error")
                return redirect(url_for("manage_brands"))
        
        # Yeni markayı ekle
        new_brand = (domain, brand_name)
        dynamic_brands.append(new_brand)
        save_dynamic_brands(dynamic_brands)
        
        flash(f"Marka başarıyla eklendi: {domain} -> {brand_name}", "success")
    else:
        flash("Domain ve marka adı gerekli", "error")
    
    return redirect(url_for("manage_brands"))

@app.route("/admin/brands/delete/<domain>", methods=["POST"])
@login_required
def delete_brand(domain):
    """Dinamik markayı sil"""
    dynamic_brands = load_dynamic_brands()
    
    # Markayı bul ve sil
    for i, (brand_domain, brand_name) in enumerate(dynamic_brands):
        if brand_domain == domain:
            deleted_brand = dynamic_brands.pop(i)
            save_dynamic_brands(dynamic_brands)
            flash(f"Marka silindi: {deleted_brand[0]} -> {deleted_brand[1]}", "success")
            break
    else:
        flash("Marka bulunamadı", "error")
    
    return redirect(url_for("manage_brands"))

@app.route("/dashboard")
@login_required
def dashboard():
    try:
        products = current_user.get_products()
        return render_template("dashboard.html", products=products)
    except Exception as e:
        print(f"[HATA] Dashboard yükleme hatası: {e}")
        flash("Ürünler yüklenirken hata oluştu", "error")
        return render_template("dashboard.html", products=[])

@app.route("/profile")
@login_required
def profile():
    """Kullanıcının profil sayfası"""
    return render_template("profile.html", user=current_user)

@app.route("/profile/settings", methods=["GET", "POST"])
@login_required
def profile_settings():
    """Hesap ayarları sayfası"""
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        
        if username and username != current_user.username:
            if User.get_by_username(username):
                flash("Bu kullanıcı adı zaten kullanılıyor", "error")
            else:
                current_user.username = username
                current_user.save()
                flash("Kullanıcı adı güncellendi", "success")
        
        if email and email != current_user.email:
            if User.get_by_email(email):
                flash("Bu e-posta adresi zaten kullanılıyor", "error")
            else:
                current_user.email = email
                current_user.save()
                flash("E-posta adresi güncellendi", "success")
        
        if current_password and new_password:
            if current_user.check_password(current_password):
                current_user.set_password(new_password)
                current_user.save()
                flash("Şifre güncellendi", "success")
            else:
                flash("Mevcut şifre yanlış", "error")
    
    return render_template("profile_settings.html", user=current_user)

@app.route("/profile/preferences", methods=["GET", "POST"])
@login_required
def profile_preferences():
    """Kullanıcı tercihleri sayfası"""
    if request.method == "POST":
        theme = request.form.get("theme", "light")
        language = request.form.get("language", "tr")
        notifications = request.form.get("notifications", "off") == "on"
        
        # Tercihleri kaydet (şimdilik session'da)
        session['user_theme'] = theme
        session['user_language'] = language
        session['user_notifications'] = notifications
        
        flash("Tercihleriniz güncellendi", "success")
    
    return render_template("profile_preferences.html", user=current_user)

@app.route("/profile/collections")
@login_required
def profile_collections():
    """Kullanıcının koleksiyonları sayfası"""
    collections = Collection.get_user_collections(current_user.id)
    return render_template("profile_collections.html", collections=collections)

@app.route("/profile/favorites")
@login_required
def profile_favorites():
    """Kullanıcının favorileri sayfası"""
    products = Product.get_user_products(current_user.id)
    return render_template("profile_favorites.html", products=products)

@app.route("/profile/<profile_url>")
def public_profile(profile_url):
    """Kullanıcının public profilini göster"""
    user = User.get_by_profile_url(profile_url)
    if not user:
        flash("Kullanıcı bulunamadı", "error")
        return redirect(url_for("index"))
    
    products = user.get_products()
    return render_template("public_profile.html", user=user, products=products)

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        remember = request.form.get("remember") == "1"
        
        user = User.get_by_username(username)
        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash("Başarıyla giriş yaptınız!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Kullanıcı adı veya şifre hatalı", "error")
    
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        
        # Form validasyonu
        if not username or not email or not password or not confirm_password:
            flash("Tüm alanları doldurun", "error")
            return render_template("register.html")
        
        if len(username) < 3:
            flash("Kullanıcı adı en az 3 karakter olmalıdır", "error")
            return render_template("register.html")
        
        if len(password) < 6:
            flash("Şifre en az 6 karakter olmalıdır", "error")
            return render_template("register.html")
        
        if password != confirm_password:
            flash("Şifreler eşleşmiyor", "error")
            return render_template("register.html")
        
        try:
            print(f"[DEBUG] Register işlemi başladı: {username}, {email}")
            
            # Kullanıcı adı kontrolü
            print(f"[DEBUG] Kullanıcı adı kontrolü yapılıyor...")
            if User.get_by_username(username):
                flash("Bu kullanıcı adı zaten kullanılıyor", "error")
                return render_template("register.html")
            
            # Email kontrolü
            print(f"[DEBUG] Email kontrolü yapılıyor...")
            if User.get_by_email(email):
                flash("Bu email adresi zaten kullanılıyor", "error")
                return render_template("register.html")
            
            # Veritabanını başlat (eğer yoksa)
            print(f"[DEBUG] Veritabanı başlatılıyor...")
            from models import init_db
            init_db()
            
            print(f"[DEBUG] Kullanıcı oluşturuluyor...")
            user = User.create(username, email, password)
            if user:
                print(f"[DEBUG] Kullanıcı başarıyla oluşturuldu, giriş yapılıyor...")
                login_user(user)
                flash("Hesabınız başarıyla oluşturuldu!", "success")
                return redirect(url_for("dashboard"))
            else:
                print(f"[HATA] User.create None döndürdü")
                flash("Kayıt sırasında bir hata oluştu", "error")
        except Exception as e:
            print(f"[HATA] Kayıt hatası: {e}")
            print(f"[HATA] Hata türü: {type(e)}")
            import traceback
            print(f"[HATA] Traceback: {traceback.format_exc()}")
            flash(f"Kayıt sırasında bir hata oluştu: {str(e)}", "error")
    
    return render_template("register.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Başarıyla çıkış yaptınız", "success")
    return redirect(url_for("index"))

@app.route("/add_product", methods=["POST"])
@login_required
def add_product():
    product_url = request.form.get("product_url")
    bulk_urls = request.form.get("bulk_urls")
    
    if product_url:
        product_data = None  # Variable'ı önceden tanımla
        try:
            # Async scraping'i Flask context'inde çalıştır
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                product_data = loop.run_until_complete(scrape_product(product_url))
            finally:
                loop.close()
                
            if product_data:
                    # Hepsiburada için özel alan adları
                    name = product_data.get('title') or product_data.get('name', '')
                    price = product_data.get('current_price') or product_data.get('price', '')
                    old_price = product_data.get('old_price')
                    image = product_data.get('image', '')
                    brand = product_data.get('brand', '')
                    
                    print(f"[DEBUG] ===== ÜRÜN EKLEME =====")
                    print(f"[DEBUG] Name: {name}")
                    print(f"[DEBUG] Price: {price}")
                    print(f"[DEBUG] Old Price: {old_price}")
                    print(f"[DEBUG] Image: {image}")
                    print(f"[DEBUG] Brand: {brand}")
                    print(f"[DEBUG] URL: {product_data['url']}")
                    print(f"[DEBUG] ========================")
                    
                    Product.create(
                        current_user.id,
                        name,
                        price,
                        image,
                        brand,
                        product_data['url'],
                        old_price
                    )
                    flash(f"Ürün eklendi: {name}", "success")
        except Exception as e:
            flash("Ürün eklenirken hata oluştu", "error")
            print(f"[HATA] Ürün eklenirken hata: {e}")
            traceback.print_exc()
    
    elif bulk_urls:
        urls = [url.strip() for url in bulk_urls.split('\n') if url.strip()]
        added_count = 0
        
        for url in urls:
            product_data = None  # Variable'ı önceden tanımla
            try:
                # Async scraping'i Flask context'inde çalıştır
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    product_data = loop.run_until_complete(scrape_product(url))
                finally:
                    loop.close()
                    
                if product_data:
                    name = product_data.get('title') or product_data.get('name', '')
                    price = product_data.get('current_price') or product_data.get('price', '')
                    old_price = product_data.get('old_price')
                    image = product_data.get('image', '')
                    brand = product_data.get('brand', '')
                    
                    print(f"[DEBUG] ===== TOPLU ÜRÜN EKLEME =====")
                    print(f"[DEBUG] URL: {url}")
                    print(f"[DEBUG] Name: {name}")
                    print(f"[DEBUG] Price: {price}")
                    print(f"[DEBUG] Old Price: {old_price}")
                    print(f"[DEBUG] Image: {image}")
                    print(f"[DEBUG] Brand: {brand}")
                    print(f"[DEBUG] ==============================")
                    
                    Product.create(
                        current_user.id,
                        name,
                        price,
                        image,
                        brand,
                        product_data['url'],
                        old_price
                    )
                    added_count += 1
            except Exception as e:
                print(f"[HATA] Toplu ekleme hatası ({url}): {e}")
        
        if added_count > 0:
            flash(f"{added_count} ürün eklendi", "success")
        else:
            flash("Hiçbir ürün eklenemedi", "error")
    
    return redirect(url_for("dashboard"))

@app.route("/delete_product/<product_id>", methods=["POST"])
@login_required
def delete_product(product_id):
    Product.delete(product_id, current_user.id)
    flash("Ürün silindi", "success")
    return redirect(url_for("dashboard"))

# Koleksiyon route'ları
@app.route("/collections")
@login_required
def collections():
    """Kullanıcının koleksiyonlarını göster"""
    user_collections = Collection.get_user_collections(current_user.id)
    return render_template("collections.html", collections=user_collections)

@app.route("/collections/create", methods=["GET", "POST"])
@login_required
def create_collection():
    """Yeni koleksiyon oluştur"""
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        collection_type = request.form.get("type")
        privacy = request.form.get("privacy", "public")
        
        if name and collection_type:
            # Gizlilik ayarını boolean'a çevir
            is_public = privacy == "public"
            collection = Collection.create(current_user.id, name, description, collection_type, is_public)
            flash("Koleksiyon oluşturuldu", "success")
            return redirect(url_for("collections"))
        else:
            flash("Lütfen gerekli alanları doldurun", "error")
    
    return render_template("create_collection.html")

@app.route("/collections/<collection_id>")
@login_required
def view_collection(collection_id):
    """Koleksiyon detayını göster"""
    collection = Collection.get_by_id(collection_id)
    if not collection or collection.user_id != current_user.id:
        flash("Koleksiyon bulunamadı", "error")
        return redirect(url_for("collections"))
    
    products = collection.get_products()
    return render_template("view_collection.html", collection=collection, products=products)

@app.route("/collections/<collection_id>/add_product/<product_id>", methods=["POST"])
@login_required
def add_to_collection(collection_id, product_id):
    """Koleksiyona ürün ekle"""
    collection = Collection.get_by_id(collection_id)
    if not collection or collection.user_id != current_user.id:
        flash("Koleksiyon bulunamadı", "error")
        return redirect(url_for("collections"))
    
    if collection.add_product(product_id):
        flash("Ürün koleksiyona eklendi", "success")
    else:
        flash("Ürün zaten koleksiyonda", "error")
    
    return redirect(request.referrer or url_for("dashboard"))

@app.route("/collections/<collection_id>/remove_product/<product_id>", methods=["POST"])
@login_required
def remove_from_collection(collection_id, product_id):
    """Koleksiyondan ürün çıkar"""
    collection = Collection.get_by_id(collection_id)
    if not collection or collection.user_id != current_user.id:
        flash("Koleksiyon bulunamadı", "error")
        return redirect(url_for("collections"))
    
    collection.remove_product(product_id)
    flash("Ürün koleksiyondan çıkarıldı", "success")
    return redirect(request.referrer or url_for("collections"))

@app.route("/collections/<collection_id>/delete", methods=["POST"])
@login_required
def delete_collection(collection_id):
    """Koleksiyonu sil"""
    collection = Collection.get_by_id(collection_id)
    if not collection or collection.user_id != current_user.id:
        flash("Koleksiyon bulunamadı", "error")
        return redirect(url_for("collections"))
    
    collection.delete()
    flash("Koleksiyon silindi", "success")
    return redirect(url_for("collections"))

@app.route("/collection/<share_url>")
def public_collection(share_url):
    """Paylaşılan koleksiyonu göster"""
    collection = Collection.get_by_share_url(share_url)
    if not collection:
        flash("Koleksiyon bulunamadı", "error")
        return redirect(url_for("index"))
    
    user = User.get_by_id(collection.user_id)
    products = collection.get_products()
    return render_template("public_collection.html", collection=collection, user=user, products=products)

@app.route("/price-tracking")
@login_required
def price_tracking():
    """Fiyat takip ana sayfası"""
    from models import PriceTracking
    
    # Kullanıcının fiyat takiplerini getir (ürün bilgileriyle birlikte)
    tracking_items = PriceTracking.get_user_trackings_with_products(current_user.id)
    
    # İstatistikleri hesapla
    tracking_stats = {
        'total_products': len(tracking_items),
        'active_alerts': sum(1 for item in tracking_items if item[7]),  # alert_price
        'price_drops': 0,  # Bu özellik henüz implement edilmedi
        'total_savings': 0  # Bu özellik henüz implement edilmedi
    }
    
    return render_template("price_tracking.html", 
                         tracking_items=tracking_items, 
                         tracking_stats=tracking_stats)

@app.route("/price-tracking/add", methods=["POST"])
@login_required
def add_price_tracking():
    """Yeni fiyat takibi ekle"""
    from models import PriceTracking, Product
    
    product_name = request.form.get("product_name")
    current_price = request.form.get("current_price")
    alert_price = request.form.get("alert_price")
    
    if not product_name or not current_price:
        flash("Ürün adı ve fiyat gereklidir", "error")
        return redirect(url_for("price_tracking"))
    
    try:
        # Önce ürünü oluştur
        product = Product.create(
            current_user.id,
            product_name,
            current_price,
            None,
            "Bilinmeyen",
            "#"
        )
        
        # Fiyat takibini oluştur
        PriceTracking.create(
            current_user.id,
            product.id,
            current_price,
            None,
            alert_price if alert_price else None
        )
        
        flash("Fiyat takibi başarıyla eklendi", "success")
        
    except Exception as e:
        flash(f"Fiyat takibi eklenirken hata oluştu: {str(e)}", "error")
    
    return redirect(url_for("price_tracking"))

@app.route("/price-tracking/<tracking_id>/history")
@login_required
def get_price_history(tracking_id):
    """Fiyat geçmişini JSON olarak döndür"""
    # Bu özellik henüz implement edilmedi
    return jsonify({
        "success": False,
        "message": "Fiyat geçmişi özelliği henüz mevcut değil"
    })

@app.route("/price-tracking/update-alert", methods=["POST"])
@login_required
def update_price_alert():
    """Fiyat alarmını güncelle"""
    # Bu özellik henüz implement edilmedi
    return jsonify({
        "success": False,
        "message": "Fiyat alarmı güncelleme özelliği henüz mevcut değil"
    })

@app.route("/price-tracking/<tracking_id>/remove", methods=["DELETE"])
@login_required
def remove_price_tracking(tracking_id):
    """Fiyat takibini kaldır"""
    try:
        from models import PriceTracking
        
        # Fiyat takibini bul
        tracking = PriceTracking.get_by_id(tracking_id)
        if not tracking or tracking.user_id != current_user.id:
            return jsonify({"success": False, "message": "Fiyat takibi bulunamadı"})
        
        # Fiyat takibini sil
        if tracking.delete():
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "message": "Fiyat takibi silinemedi"})
        
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route("/price-tracking/update-prices")
@login_required
def update_prices():
    """Otomatik fiyat güncellemesi simüle et"""
    # Bu özellik henüz implement edilmedi
    return jsonify({
        "success": True, 
        "updated": False,
        "message": "Otomatik fiyat güncelleme özelliği henüz mevcut değil"
    })

# Bildirim sistemi için yeni rotalar
@app.route("/notifications")
@login_required
def get_notifications():
    """Kullanıcının bildirimlerini getir"""
    from models import Notification
    
    # Kullanıcının bildirimlerini getir
    notifications = Notification.get_user_notifications(current_user.id)
    unread_count = Notification.get_unread_count(current_user.id)
    
    return jsonify({
        "success": True,
        "notifications": [
            {
                "id": n.id,
                "title": n.title,
                "message": n.message,
                "type": n.type,
                "is_read": n.is_read,
                "created_at": n.created_at.isoformat() if hasattr(n.created_at, 'isoformat') else str(n.created_at)
            } for n in notifications
        ],
        "unread_count": unread_count
    })

@app.route("/notifications/mark-read/<notification_id>", methods=["POST"])
@login_required
def mark_notification_read(notification_id):
    """Bildirimi okundu olarak işaretle"""
    from models import Notification
    
    if Notification.mark_as_read(notification_id):
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "message": "Bildirim işaretlenemedi"})

@app.route("/notifications/mark-all-read", methods=["POST"])
@login_required
def mark_all_notifications_read():
    """Tüm bildirimleri okundu olarak işaretle"""
    from models import Notification
    
    if Notification.mark_all_as_read(current_user.id):
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "message": "Bildirimler işaretlenemedi"})

# Yeni rotalar: Ürünleri fiyat takibine ekleme/kaldırma
@app.route("/product/<product_id>/add-to-tracking", methods=["POST"])
@login_required
def add_product_to_tracking(product_id):
    """Ürünü fiyat takibine ekle"""
    from models import PriceTracking, Product
    
    try:
        # Ürünü kontrol et
        product = Product.get_by_id(product_id)
        if not product:
            return jsonify({"success": False, "message": "Ürün bulunamadı"})
        
        # Kullanıcının bu ürünü zaten takip edip etmediğini kontrol et
        existing_tracking = PriceTracking.get_by_product_and_user(product_id, current_user.id)
        if existing_tracking:
            return jsonify({"success": False, "message": "Bu ürün zaten takip ediliyor"})
        
        # Fiyatı sayısal değere çevir
        try:
            price_str = product.price.replace('₺', '').replace(',', '').strip()
            current_price = float(price_str)
        except:
            current_price = 0.0
        
        # Fiyat takibine ekle
        tracking_id = PriceTracking.create(
            current_user.id,
            product_id,
            current_price,
            current_price,
            current_price * 0.9  # %10 indirim alarmı
        )
        
        if tracking_id:
            return jsonify({
                "success": True, 
                "message": f"{product.name} fiyat takibine eklendi",
                "tracking_id": tracking_id
            })
        else:
            return jsonify({"success": False, "message": "Fiyat takibi eklenirken hata oluştu"})
            
    except Exception as e:
        print(f"[HATA] Fiyat takibi ekleme hatası: {e}")
        return jsonify({"success": False, "message": "Bir hata oluştu"})

@app.route("/product/<product_id>/remove-from-tracking", methods=["POST"])
@login_required
def remove_product_from_tracking(product_id):
    """Ürünü fiyat takibinden kaldır"""
    from models import PriceTracking, Product
    
    try:
        # Ürünü kontrol et
        product = Product.get_by_id(product_id)
        if not product:
            return jsonify({"success": False, "message": "Ürün bulunamadı"})
        
        # Takip kaydını bul ve kaldır
        tracking = PriceTracking.get_by_product_and_user(product_id, current_user.id)
        if not tracking:
            return jsonify({"success": False, "message": "Bu ürün takip edilmiyor"})
        
        success = PriceTracking.remove_tracking(tracking.id)
        
        if success:
            return jsonify({
                "success": True, 
                "message": f"{product.name} fiyat takibinden kaldırıldı"
            })
        else:
            return jsonify({"success": False, "message": "Fiyat takibi kaldırılırken hata oluştu"})
            
    except Exception as e:
        print(f"[HATA] Fiyat takibi kaldırma hatası: {e}")
        return jsonify({"success": False, "message": "Bir hata oluştu"})

@app.route("/product/<product_id>/tracking-status")
@login_required
def get_product_tracking_status(product_id):
    """Ürünün fiyat takip durumunu kontrol et"""
    from models import PriceTracking
    
    try:
        tracking = PriceTracking.get_by_product_and_user(product_id, current_user.id)
        is_tracked = tracking is not None
        
        return jsonify({
            "success": True,
            "is_tracked": is_tracked,
            "tracking_id": tracking.id if tracking else None
        })
        
    except Exception as e:
        print(f"[HATA] Takip durumu kontrol hatası: {e}")
        return jsonify({"success": False, "is_tracked": False})



@app.errorhandler(405)
def method_not_allowed(e):
    return redirect(url_for("index"))

# CSP Headers
@app.after_request
def add_security_headers(response):
    response.headers['Content-Security-Policy'] = "default-src 'self' 'unsafe-inline' 'unsafe-eval'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self'"
    return response

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))