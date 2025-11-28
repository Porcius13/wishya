#!/usr/bin/env python3
"""
Domain çıkarma fonksiyonunu debug etmek için test dosyası
"""

from urllib.parse import urlparse

def extract_domain(url: str) -> str:
    """URL'den domain çıkarır"""
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    # www. kısmını kaldır
    if domain.startswith('www.'):
        domain = domain[4:]
    return domain

# Test URL'leri
test_urls = [
    "https://www.beymen.com/tr/p_polo-ralph-lauren-beyaz-oxford-gomlek_1646218",
    "https://www.ellesse.com.tr/products/ellesse-erkek-polo-yaka-tisort-em460-bk",
    "https://www.beyyoglu.com/100-keten-oversize-gomlek-24ss53005006-27/",
    "https://www.ninewest.com.tr/urun/nine-west-margarita-5fx-siyah-kadin-topuklu-sandalet-101928976",
    "https://www.levis.com.tr/levis-511-slim-fit_117340",
    "https://www.dockers.com.tr/smart-360-flex-ultimate-chino-slim-fit-pantolon_2661",
    "https://sarar.com/sarar-loreto-kot-elbise-18167",
    "https://www.salomon.com.tr/acs-plus-unisex-sneaker-l47705300",
    "https://www.abercrombie.com/shop/wd/p/premium-polished-tee-57648335?categoryId=12204&faceout=model&seq=13",
    "https://www.loft.com.tr/p/loose-fit-erkek-tshirt-kkol-6931",
    "https://ucla.com.tr/canary-haki-bisiklet-yaka-gofre-baskili-modal-kumas-standard-fit-erkek-tshirt",
    "https://www.yargici.com/kahverengi-regular-fit-keten-gomlek-p-198901"
]

print("Domain çıkarma testi:")
print("=" * 50)

for url in test_urls:
    domain = extract_domain(url)
    print(f"URL: {url}")
    print(f"Domain: {domain}")
    print("-" * 30)

# Konfigürasyonlardaki domain'leri de kontrol et
config_domains = [
    "beymen.com",
    "ellesse.com.tr", 
    "beyyoglu.com",
    "ninewest.com.tr",
    "levis.com.tr",
    "dockers.com.tr",
    "sarar.com",
    "salomon.com.tr",
    "abercrombie.com",
    "loft.com.tr",
    "ucla.com.tr",
    "yargici.com"
]

print("\nKonfigürasyon domain'leri:")
print("=" * 30)
for domain in config_domains:
    print(f"  {domain}")
