const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');

puppeteer.use(StealthPlugin());

/**
 * Scrapes product data from a given URL.
 * @param {string} url - The product URL.
 * @returns {Promise<Object>} - The scraped product data.
 */
async function scrape(url) {
    const browser = await puppeteer.launch({
        headless: "new",
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--window-size=1920,1080'
        ]
    });

    try {
        const page = await browser.newPage();
        await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36');
        await page.setViewport({ width: 1920, height: 1080 });

        console.error(`Navigating to ${url}...`); // Use stderr for logs so stdout is clean JSON
        await page.goto(url, { waitUntil: 'networkidle2', timeout: 60000 });

        const domain = new URL(url).hostname;
        let data = {};

        if (domain.includes('nike.com')) {
            data = await scrapeNike(page);
        } else if (domain.includes('bershka.com')) {
            data = await scrapeBershka(page);
        } else if (domain.includes('decathlon')) {
            data = await scrapeDecathlon(page);
        } else {
            data = await scrapeGeneric(page);
        }

        // Clean up data
        if (data.price) {
            // Ensure price is a string or number, maybe normalize?
            // For now, keep as extracted
        }

        return data;

    } catch (error) {
        console.error("Scraping failed:", error);
        return { error: error.message };
    } finally {
        await browser.close();
    }
}

async function scrapeNike(page) {
    return await page.evaluate(() => {
        const data = {};

        // 1. Price (DOM - Specific for Nike)
        const priceEl = document.querySelector('[data-testid="currentPrice-container"]');
        if (priceEl) {
            data.price = priceEl.innerText.trim();
        } else {
            // Fallback
            const allElements = Array.from(document.querySelectorAll('div, span, p'));
            const priceCandidate = allElements.find(el =>
                /^\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?\s*TL$/.test(el.innerText.trim())
            );
            if (priceCandidate) data.price = priceCandidate.innerText.trim();
        }

        // 2. Name
        const h1 = document.querySelector('h1');
        data.name = h1 ? h1.innerText.trim() : null;

        // 3. Image
        const images = Array.from(document.querySelectorAll('img'));
        const productImages = images.filter(img =>
            img.src && !img.src.includes('icon') && !img.src.includes('logo') && img.naturalWidth > 400
        );
        if (productImages.length > 0) data.image = productImages[0].src;

        // 4. JSON-LD Fallback
        if (!data.price || !data.image) {
            const scripts = document.querySelectorAll('script[type="application/ld+json"]');
            scripts.forEach(s => {
                try {
                    const json = JSON.parse(s.innerText);
                    if (json['@type'] === 'Product') {
                        if (!data.name) data.name = json.name;
                        if (!data.image) data.image = json.image;
                        if (!data.price && json.offers) {
                            const offer = Array.isArray(json.offers) ? json.offers[0] : json.offers;
                            data.price = offer.price;
                            data.currency = offer.priceCurrency;
                        }
                    }
                } catch (e) { }
            });
        }
        data.brand = "Nike";
        return data;
    });
}

async function scrapeBershka(page) {
    return await page.evaluate(() => {
        const data = {};
        // Bershka is best with JSON-LD
        const scripts = document.querySelectorAll('script[type="application/ld+json"]');
        scripts.forEach(s => {
            try {
                const json = JSON.parse(s.innerText);
                if (json['@type'] === 'Product') {
                    data.name = json.name;
                    data.description = json.description;
                    data.image = json.image;
                    data.brand = json.brand ? json.brand.name : "Bershka";
                    data.sku = json.sku;
                    if (json.offers) {
                        const offer = Array.isArray(json.offers) ? json.offers[0] : json.offers;
                        data.price = offer.price;
                        data.currency = offer.priceCurrency;
                    }
                }
            } catch (e) { }
        });
        return data;
    });
}

async function scrapeDecathlon(page) {
    return await page.evaluate(() => {
        const data = {};
        // Decathlon uses window.__DKT
        try {
            if (window.__DKT && window.__DKT._ctx && window.__DKT._ctx.data) {
                const supermodel = window.__DKT._ctx.data.find(item => item.type === 'Supermodel');
                if (supermodel && supermodel.data) {
                    const modelData = supermodel.data.models ? supermodel.data.models[0] : null;
                    if (modelData) {
                        data.name = modelData.webLabel;
                        data.image = modelData.image ? modelData.image.url : null;
                        if (modelData.skus && modelData.skus.length > 0) {
                            const sku = modelData.skus[0];
                            data.price = sku.price;
                            data.currency = sku.currency;
                            data.originalPrice = sku.previousPrice;
                            data.discountRate = sku.discountRate;
                        }
                    }
                    data.brand = supermodel.data.brand ? supermodel.data.brand.label : null;
                    data.description = supermodel.data.description;
                }
            }
        } catch (e) { }

        // Fallback
        if (!data.name) {
            const h1 = document.querySelector('h1');
            data.name = h1 ? h1.innerText.trim() : null;
        }
        return data;
    });
}

async function scrapeGeneric(page) {
    return await page.evaluate(() => {
        const data = {};
        // 1. JSON-LD
        const scripts = document.querySelectorAll('script[type="application/ld+json"]');
        scripts.forEach(s => {
            try {
                const json = JSON.parse(s.innerText);
                if (json['@type'] === 'Product') {
                    data.name = json.name;
                    data.image = json.image;
                    if (json.offers) {
                        const offer = Array.isArray(json.offers) ? json.offers[0] : json.offers;
                        data.price = offer.price;
                        data.currency = offer.priceCurrency;
                    }
                }
            } catch (e) { }
        });

        // 2. Open Graph
        if (!data.name) {
            const ogTitle = document.querySelector('meta[property="og:title"]');
            if (ogTitle) data.name = ogTitle.content;
        }
        if (!data.image) {
            const ogImage = document.querySelector('meta[property="og:image"]');
            if (ogImage) data.image = ogImage.content;
        }

        // 3. H1
        if (!data.name) {
            const h1 = document.querySelector('h1');
            data.name = h1 ? h1.innerText.trim() : document.title;
        }

        return data;
    });
}

module.exports = { scrape };
