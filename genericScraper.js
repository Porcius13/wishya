/**
 * Generic Scraper - Bilinmeyen sitelerden ürün bilgilerini çekmek için
 * Playwright page objesi kullanarak en kaliteli şekilde veri çeker
 */

async function scrape(page, url) {
    console.log(`[DEBUG] Generic scraping başlıyor: ${url}`);
    
    const result = {
        title: null,
        price: null,
        brand: null,
        imageUrl: null
    };

    try {
        // Sayfa yüklendikten sonra biraz bekle
        await page.waitForTimeout(3000);
        
        // 1. JSON-LD (Structured Data) arama
        console.log("[DEBUG] JSON-LD aranıyor...");
        const jsonLdData = await extractJsonLd(page);
        if (jsonLdData) {
            result.title = jsonLdData.name || result.title;
            result.price = jsonLdData.price || result.price;
            result.brand = jsonLdData.brand || result.brand;
            result.imageUrl = jsonLdData.image || result.imageUrl;
            console.log("[DEBUG] JSON-LD verisi bulundu:", jsonLdData);
        }

        // 2. Open Graph meta tag'leri arama
        if (!result.title || !result.imageUrl) {
            console.log("[DEBUG] Open Graph meta tag'leri aranıyor...");
            const ogData = await extractOpenGraph(page);
            if (ogData) {
                result.title = result.title || ogData.title;
                result.imageUrl = result.imageUrl || ogData.image;
                result.brand = result.brand || ogData.brand;
                console.log("[DEBUG] Open Graph verisi bulundu:", ogData);
            }
        }

        // 3. Fiyat arama (regex ile)
        if (!result.price) {
            console.log("[DEBUG] Fiyat regex ile aranıyor...");
            result.price = await extractPrice(page);
            console.log("[DEBUG] Fiyat bulundu:", result.price);
        }

        // 4. Görsel fallback
        if (!result.imageUrl) {
            console.log("[DEBUG] Görsel fallback aranıyor...");
            result.imageUrl = await extractBestImage(page, url);
            console.log("[DEBUG] Görsel bulundu:", result.imageUrl);
        }

        // 5. Başlık fallback
        if (!result.title) {
            console.log("[DEBUG] Başlık fallback aranıyor...");
            result.title = await extractTitle(page);
            console.log("[DEBUG] Başlık bulundu:", result.title);
        }

        // 6. Marka fallback
        if (!result.brand) {
            console.log("[DEBUG] Marka fallback aranıyor...");
            result.brand = await extractBrand(page, url);
            console.log("[DEBUG] Marka bulundu:", result.brand);
        }

        console.log("[DEBUG] Generic scraping tamamlandı:", result);
        return result;

    } catch (error) {
        console.error("[HATA] Generic scraping hatası:", error);
        return result;
    }
}

/**
 * JSON-LD structured data'yı çıkar
 */
async function extractJsonLd(page) {
    try {
        const jsonLdScripts = await page.$$eval('script[type="application/ld+json"]', scripts => {
            return scripts.map(script => {
                try {
                    return JSON.parse(script.textContent);
                } catch (e) {
                    return null;
                }
            }).filter(data => data !== null);
        });

        for (const data of jsonLdScripts) {
            // Product schema kontrolü
            if (data['@type'] === 'Product' || data['@type'] === 'http://schema.org/Product') {
                return {
                    name: data.name || data.title,
                    price: extractPriceFromJsonLd(data),
                    brand: extractBrandFromJsonLd(data),
                    image: extractImageFromJsonLd(data)
                };
            }
            
            // Array içinde Product arama
            if (Array.isArray(data)) {
                for (const item of data) {
                    if (item['@type'] === 'Product' || item['@type'] === 'http://schema.org/Product') {
                        return {
                            name: item.name || item.title,
                            price: extractPriceFromJsonLd(item),
                            brand: extractBrandFromJsonLd(item),
                            image: extractImageFromJsonLd(item)
                        };
                    }
                }
            }
        }
        
        return null;
    } catch (error) {
        console.error("[HATA] JSON-LD çıkarma hatası:", error);
        return null;
    }
}

/**
 * JSON-LD'den fiyat çıkar
 */
function extractPriceFromJsonLd(data) {
    try {
        if (data.offers) {
            if (Array.isArray(data.offers)) {
                return data.offers[0]?.price;
            } else {
                return data.offers.price;
            }
        }
        return data.price;
    } catch (error) {
        return null;
    }
}

/**
 * JSON-LD'den marka çıkar
 */
function extractBrandFromJsonLd(data) {
    try {
        if (data.brand) {
            if (typeof data.brand === 'string') {
                return data.brand;
            } else if (data.brand.name) {
                return data.brand.name;
            }
        }
        return data.manufacturer?.name;
    } catch (error) {
        return null;
    }
}

/**
 * JSON-LD'den görsel çıkar
 */
function extractImageFromJsonLd(data) {
    try {
        if (data.image) {
            if (Array.isArray(data.image)) {
                return data.image[0];
            } else {
                return data.image;
            }
        }
        return null;
    } catch (error) {
        return null;
    }
}

/**
 * Open Graph meta tag'lerini çıkar
 */
async function extractOpenGraph(page) {
    try {
        const ogData = await page.evaluate(() => {
            const getMetaContent = (property) => {
                const meta = document.querySelector(`meta[property="${property}"]`) || 
                           document.querySelector(`meta[name="${property}"]`);
                return meta ? meta.getAttribute('content') : null;
            };

            return {
                title: getMetaContent('og:title') || getMetaContent('twitter:title'),
                image: getMetaContent('og:image') || getMetaContent('twitter:image'),
                brand: getMetaContent('brand') || getMetaContent('og:brand')
            };
        });

        return ogData.title || ogData.image || ogData.brand ? ogData : null;
    } catch (error) {
        console.error("[HATA] Open Graph çıkarma hatası:", error);
        return null;
    }
}

/**
 * Sayfada fiyat akıllı seçim ile ara
 */
async function extractPrice(page) {
    try {
        // 1. Meta tag'lerden fiyat ara
        console.log("[DEBUG] Meta tag'lerden fiyat aranıyor...");
        const metaPrice = await extractPriceFromMeta(page);
        if (metaPrice) {
            console.log("[DEBUG] Meta tag'den fiyat bulundu:", metaPrice);
            return metaPrice;
        }

        // 2. DOM tabanlı akıllı fiyat seçimi
        console.log("[DEBUG] DOM tabanlı fiyat aranıyor...");
        const domPrice = await extractPriceFromDOM(page);
        if (domPrice) {
            console.log("[DEBUG] DOM'dan fiyat bulundu:", domPrice);
            return domPrice;
        }

        // 3. Son çare: Regex ile HTML içinde ara
        console.log("[DEBUG] Regex ile fiyat aranıyor...");
        const regexPrice = await extractPriceFromRegex(page);
        if (regexPrice) {
            console.log("[DEBUG] Regex ile fiyat bulundu:", regexPrice);
            return regexPrice;
        }

        return null;
    } catch (error) {
        console.error("[HATA] Fiyat çıkarma hatası:", error);
        return null;
    }
}

/**
 * Meta tag'lerden fiyat çıkar
 */
async function extractPriceFromMeta(page) {
    try {
        const metaPrice = await page.evaluate(() => {
            const priceSelectors = [
                'meta[property="product:price:amount"]',
                'meta[property="og:price:amount"]',
                'meta[name="price"]',
                'meta[property="price"]',
                'meta[itemprop="price"]'
            ];

            for (const selector of priceSelectors) {
                const meta = document.querySelector(selector);
                if (meta && meta.getAttribute('content')) {
                    const content = meta.getAttribute('content').trim();
                    if (content && /[0-9]/.test(content)) {
                        return content;
                    }
                }
            }
            return null;
        });

        if (metaPrice) {
            // Fiyatı temizle ve formatla
            const cleanPrice = cleanAndFormatPrice(metaPrice);
            return cleanPrice;
        }

        return null;
    } catch (error) {
        console.error("[HATA] Meta fiyat çıkarma hatası:", error);
        return null;
    }
}

/**
 * DOM tabanlı akıllı fiyat seçimi
 */
async function extractPriceFromDOM(page) {
    try {
        const prices = await page.evaluate(() => {
            const priceCandidates = [];
            
            // Fiyat içerebilecek selector'lar (öncelik sırasına göre)
            const priceSelectors = [
                // Öncelikli selector'lar
                '[data-price]',
                '[data-testid*="price"]',
                '[class*="price"]',
                '[id*="price"]',
                '[data-qa*="price"]',
                
                // Genel selector'lar
                'span',
                'div',
                'p',
                'strong',
                'b'
            ];

            for (const selector of priceSelectors) {
                const elements = document.querySelectorAll(selector);
                
                elements.forEach(element => {
                    const text = element.textContent.trim();
                    if (text && (text.includes('₺') || text.includes('TL') || text.includes('TRY'))) {
                        // Fiyat değerini çıkar
                        const priceMatch = text.match(/([0-9]{1,3}(?:\.[0-9]{3})*,[0-9]{2}|[0-9]+(?:[.,][0-9]{2})?)/);
                        if (priceMatch) {
                            const priceStr = priceMatch[1].replace('.', '').replace(',', '.');
                            const priceNum = parseFloat(priceStr);
                            
                            if (priceNum > 0 && priceNum < 100000) {
                                // Element'in konumunu ve özelliklerini analiz et
                                const rect = element.getBoundingClientRect();
                                const isVisible = rect.width > 0 && rect.height > 0;
                                
                                // Öncelik skoru hesapla
                                let priority = 0;
                                
                                // Görünürlük
                                if (isVisible) priority += 10;
                                
                                // Sayfa üst kısmında olma
                                if (rect.top < window.innerHeight / 2) priority += 5;
                                
                                // Fiyat kelimelerine yakınlık
                                const parentText = element.parentElement?.textContent || '';
                                const hasPriceKeywords = /satış|indirimli|fiyat|price|sale|discount/i.test(parentText);
                                if (hasPriceKeywords) priority += 15;
                                
                                // Element türü
                                if (selector.includes('data-price')) priority += 20;
                                if (selector.includes('data-testid')) priority += 15;
                                if (selector.includes('class')) priority += 10;
                                
                                // Fiyat formatı (₺ ile başlayan daha güvenilir)
                                if (text.startsWith('₺') || text.startsWith('TL')) priority += 5;
                                
                                priceCandidates.push({
                                    text: text,
                                    price: priceNum,
                                    priority: priority,
                                    element: selector
                                });
                            }
                        }
                    }
                });
            }

            return priceCandidates;
        });

        if (prices.length === 0) {
            return null;
        }

        // Öncelik skoruna göre sırala
        prices.sort((a, b) => b.priority - a.priority);

        // En yüksek öncelikli fiyatı al
        const bestPrice = prices[0];
        
        // Eğer birden fazla benzer öncelikli fiyat varsa, ortalama fiyata yakın olanı seç
        const highPriorityPrices = prices.filter(p => p.priority >= bestPrice.priority - 5);
        
        if (highPriorityPrices.length > 1) {
            // Ortalama fiyatı hesapla
            const avgPrice = highPriorityPrices.reduce((sum, p) => sum + p.price, 0) / highPriorityPrices.length;
            
            // Ortalamaya en yakın fiyatı bul
            const closestToAverage = highPriorityPrices.reduce((closest, current) => {
                return Math.abs(current.price - avgPrice) < Math.abs(closest.price - avgPrice) ? current : closest;
            });
            
            return cleanAndFormatPrice(closestToAverage.text);
        }

        return cleanAndFormatPrice(bestPrice.text);
    } catch (error) {
        console.error("[HATA] DOM fiyat çıkarma hatası:", error);
        return null;
    }
}

/**
 * Regex ile HTML içinde fiyat ara (son çare)
 */
async function extractPriceFromRegex(page) {
    try {
        const pageContent = await page.content();
        
        // Türk Lirası fiyat regex'leri
        const pricePatterns = [
            /₺\s*([0-9]{1,3}(?:\.[0-9]{3})*,[0-9]{2})/g,  // ₺1.234,56
            /₺\s*([0-9]+(?:[.,][0-9]{2})?)/g,              // ₺1234,56
            /([0-9]{1,3}(?:\.[0-9]{3})*,[0-9]{2})\s*₺/g,  // 1.234,56₺
            /([0-9]+(?:[.,][0-9]{2})?)\s*₺/g,              // 1234,56₺
            /TL\s*([0-9]{1,3}(?:\.[0-9]{3})*,[0-9]{2})/g,  // TL 1.234,56
            /TL\s*([0-9]+(?:[.,][0-9]{2})?)/g,             // TL 1234,56
            /([0-9]{1,3}(?:\.[0-9]{3})*,[0-9]{2})\s*TL/g,  // 1.234,56 TL
            /([0-9]+(?:[.,][0-9]{2})?)\s*TL/g,             // 1234,56 TL
            /TRY\s*([0-9]{1,3}(?:\.[0-9]{3})*,[0-9]{2})/g, // TRY 1.234,56
            /TRY\s*([0-9]+(?:[.,][0-9]{2})?)/g,            // TRY 1234,56
            /([0-9]{1,3}(?:\.[0-9]{3})*,[0-9]{2})\s*TRY/g, // 1.234,56 TRY
            /([0-9]+(?:[.,][0-9]{2})?)\s*TRY/g             // 1234,56 TRY
        ];

        const allPrices = [];

        for (const pattern of pricePatterns) {
            const matches = pageContent.match(pattern);
            if (matches) {
                for (const match of matches) {
                    const priceMatch = match.match(/([0-9]{1,3}(?:\.[0-9]{3})*,[0-9]{2}|[0-9]+(?:[.,][0-9]{2})?)/);
                    if (priceMatch) {
                        const priceStr = priceMatch[1].replace('.', '').replace(',', '.');
                        const priceNum = parseFloat(priceStr);
                        
                        if (priceNum > 0 && priceNum < 100000) {
                            allPrices.push({
                                text: match.trim(),
                                price: priceNum
                            });
                        }
                    }
                }
            }
        }

        if (allPrices.length === 0) {
            return null;
        }

        // Fiyatları sırala ve ortalama fiyata yakın olanı seç
        allPrices.sort((a, b) => a.price - b.price);
        
        if (allPrices.length === 1) {
            return cleanAndFormatPrice(allPrices[0].text);
        }

        // Ortalama fiyatı hesapla
        const avgPrice = allPrices.reduce((sum, p) => sum + p.price, 0) / allPrices.length;
        
        // Ortalamaya en yakın fiyatı bul
        const closestToAverage = allPrices.reduce((closest, current) => {
            return Math.abs(current.price - avgPrice) < Math.abs(closest.price - avgPrice) ? current : closest;
        });

        return cleanAndFormatPrice(closestToAverage.text);
    } catch (error) {
        console.error("[HATA] Regex fiyat çıkarma hatası:", error);
        return null;
    }
}

/**
 * Fiyatı temizle ve formatla
 */
function cleanAndFormatPrice(priceText) {
    try {
        // Fiyatı temizle
        let cleanPrice = priceText.replace(/\s+/g, ' ').trim();
        
        // Fiyat değerini çıkar
        const priceMatch = cleanPrice.match(/([0-9]{1,3}(?:\.[0-9]{3})*,[0-9]{2}|[0-9]+(?:[.,][0-9]{2})?)/);
        if (priceMatch) {
            const priceStr = priceMatch[1].replace('.', '').replace(',', '.');
            const priceNum = parseFloat(priceStr);
            
            if (priceNum > 0 && priceNum < 100000) {
                // TL formatına çevir
                if (priceNum >= 1000) {
                    return `${priceNum.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} TL`;
                } else {
                    return `${priceNum.toFixed(2).replace('.', ',')} TL`;
                }
            }
        }
        
        return null;
    } catch (error) {
        console.error("[HATA] Fiyat temizleme hatası:", error);
        return null;
    }
}

/**
 * En iyi görseli seç
 */
async function extractBestImage(page, baseUrl) {
    try {
        const images = await page.evaluate((url) => {
            const imgElements = document.querySelectorAll('img');
            const imageData = [];

            imgElements.forEach(img => {
                let src = img.src || img.getAttribute('data-src') || img.getAttribute('data-lazy');
                
                if (src) {
                    // Relative URL'yi absolute yap
                    if (src.startsWith('//')) {
                        src = 'https:' + src;
                    } else if (src.startsWith('/')) {
                        const urlObj = new URL(url);
                        src = urlObj.origin + src;
                    }

                    // Sadece resim dosyalarını kabul et
                    if (/\.(jpg|jpeg|png|webp|gif)$/i.test(src)) {
                        const width = img.naturalWidth || img.width || 0;
                        const height = img.naturalHeight || img.height || 0;
                        const area = width * height;

                        imageData.push({
                            src: src,
                            width: width,
                            height: height,
                            area: area,
                            alt: img.alt || ''
                        });
                    }
                }
            });

            return imageData;
        }, baseUrl);

        if (images.length === 0) {
            return null;
        }

        // En büyük alanlı görseli seç
        const bestImage = images.reduce((best, current) => {
            return current.area > best.area ? current : best;
        });

        // Minimum boyut kontrolü (çok küçük görselleri filtrele)
        if (bestImage.area < 10000) { // 100x100 minimum
            return null;
        }

        return bestImage.src;
    } catch (error) {
        console.error("[HATA] Görsel çıkarma hatası:", error);
        return null;
    }
}

/**
 * Başlık çıkar
 */
async function extractTitle(page) {
    try {
        const title = await page.evaluate(() => {
            // Önce h1 tag'lerini kontrol et
            const h1Elements = document.querySelectorAll('h1');
            for (const h1 of h1Elements) {
                const text = h1.textContent.trim();
                if (text && text.length > 3 && text.length < 200) {
                    return text;
                }
            }

            // Sonra title tag'ini kontrol et
            const titleElement = document.querySelector('title');
            if (titleElement && titleElement.textContent.trim()) {
                return titleElement.textContent.trim();
            }

            // Son olarak h2 tag'lerini kontrol et
            const h2Elements = document.querySelectorAll('h2');
            for (const h2 of h2Elements) {
                const text = h2.textContent.trim();
                if (text && text.length > 3 && text.length < 200) {
                    return text;
                }
            }

            return null;
        });

        return title;
    } catch (error) {
        console.error("[HATA] Başlık çıkarma hatası:", error);
        return null;
    }
}

/**
 * Marka çıkar
 */
async function extractBrand(page, url) {
    try {
        // URL'den domain'i çıkar
        const domain = new URL(url).hostname.replace('www.', '');
        const domainParts = domain.split('.');
        const potentialBrand = domainParts[0];

        // Sayfada marka bilgisi ara
        const brandFromPage = await page.evaluate(() => {
            const brandSelectors = [
                'meta[name="brand"]',
                'meta[property="og:brand"]',
                '[data-brand]',
                '[class*="brand"]',
                '[id*="brand"]'
            ];

            for (const selector of brandSelectors) {
                const element = document.querySelector(selector);
                if (element) {
                    const brand = element.getAttribute('content') || 
                                 element.getAttribute('data-brand') || 
                                 element.textContent.trim();
                    if (brand && brand.length > 1 && brand.length < 50) {
                        return brand;
                    }
                }
            }

            return null;
        });

        if (brandFromPage) {
            return brandFromPage;
        }

        // Domain'den marka adını oluştur
        if (potentialBrand && potentialBrand.length > 2) {
            return potentialBrand.charAt(0).toUpperCase() + potentialBrand.slice(1);
        }

        return null;
    } catch (error) {
        console.error("[HATA] Marka çıkarma hatası:", error);
        return null;
    }
}

// Export fonksiyonu
module.exports = { scrape };

