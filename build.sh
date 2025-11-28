#!/bin/bash
# Render.com için build script

echo "🚀 Render.com build başlatılıyor..."

# Python dependencies kurulumu
echo "📦 Python dependencies kuruluyor..."
pip install -r requirements.txt

# Playwright kurulumu
echo "🌐 Playwright kuruluyor..."
playwright install chromium
playwright install-deps chromium
playwright install-deps

# Browser dependencies kurulumu
echo "🔧 Browser dependencies kuruluyor..."
apt-get update -qq && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    procps \
    libxss1 \
    libnss3 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    libatspi2.0-0 \
    libgtk-3-0 \
    libgdk-pixbuf2.0-0

echo "✅ Build tamamlandı!"
