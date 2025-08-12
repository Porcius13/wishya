#!/bin/bash

# Render Build Script - Görsel Çekme Optimizasyonu

echo "🚀 Render build script başlıyor..."

# Playwright browser'larını yükle
echo "📦 Playwright browser'ları yükleniyor..."
playwright install chromium
playwright install-deps chromium

# Debug script'ini çalıştırılabilir yap
echo "🔧 Debug script'i hazırlanıyor..."
chmod +x render_debug.py

# Test scraping'i çalıştır
echo "🧪 Test scraping başlatılıyor..."
python render_debug.py "https://www2.hm.com/tr_tr/productpage.1234567890.html" || echo "⚠️ Test scraping başarısız, devam ediliyor..."

echo "✅ Build tamamlandı!"
echo "📝 Debug için: python render_debug.py <URL>"
echo "🌐 API endpoint: /api/debug/scrape"
