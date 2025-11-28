# 🏗️ Backend Architecture - Modüler Yapı

## ✨ Yeni Yapı

### 📁 Klasör Organizasyonu

```
kataloggia-main/
├── app/
│   ├── __init__.py          # Application factory
│   ├── config.py            # Configuration settings
│   ├── api/
│   │   ├── v1/
│   │   │   ├── auth.py      # Authentication endpoints
│   │   │   ├── products.py  # Product CRUD API
│   │   │   ├── collections.py
│   │   │   ├── scraping.py
│   │   │   ├── users.py
│   │   │   └── errors.py   # Error handlers
│   ├── routes/
│   │   ├── main.py          # Public routes
│   │   ├── dashboard.py     # Dashboard routes
│   │   └── profile.py       # Profile routes
│   ├── services/
│   │   ├── product_service.py
│   │   ├── auth_service.py
│   │   ├── scraping_service.py
│   │   └── collection_service.py
│   ├── models/
│   │   ├── user.py
│   │   ├── product.py
│   │   └── collection.py
│   └── utils/
│       └── scraper.py
├── models.py                # Mevcut model (backward compatibility)
├── app.py                   # Eski app (backward compatibility)
└── run.py                   # Yeni entry point
```

## 🎯 Özellikler

### 1. **Blueprint Yapısı**
- Route'lar modüllere ayrıldı
- Her modül kendi sorumluluğuna sahip
- Daha temiz kod organizasyonu

### 2. **RESTful API**
- `/api/v1/products` - Product CRUD
- `/api/v1/collections` - Collection management
- `/api/v1/scraping` - Scraping endpoints
- `/api/v1/auth` - Authentication
- `/api/v1/users` - User management

### 3. **Service Layer**
- Business logic service layer'da
- Controller'lar sadece HTTP işlemleri
- Daha test edilebilir kod

### 4. **Application Factory**
- `create_app()` pattern
- Farklı config'ler için hazır
- Test için kolay setup

## 📡 API Endpoints

### Products API

```bash
# Tüm ürünleri getir
GET /api/v1/products

# Yeni ürün ekle
POST /api/v1/products
{
  "name": "Ürün Adı",
  "price": "100 TL",
  "url": "https://...",
  "brand": "Marka",
  "image": "https://..."
}

# Ürün getir
GET /api/v1/products/{id}

# Ürün güncelle
PUT /api/v1/products/{id}

# Ürün sil
DELETE /api/v1/products/{id}
```

### Collections API

```bash
# Tüm koleksiyonları getir
GET /api/v1/collections

# Yeni koleksiyon oluştur
POST /api/v1/collections
{
  "name": "Koleksiyon Adı",
  "description": "Açıklama",
  "type": "custom",
  "is_public": true
}

# Koleksiyona ürün ekle
POST /api/v1/collections/{id}/products/{product_id}
```

### Scraping API

```bash
# Ürün çek
POST /api/v1/scraping/scrape
{
  "url": "https://..."
}

# Toplu çekme
POST /api/v1/scraping/batch
{
  "urls": ["https://...", "https://..."]
}
```

### Auth API

```bash
# Login
POST /api/v1/auth/login
{
  "username": "user",
  "password": "pass"
}

# Register
POST /api/v1/auth/register
{
  "username": "user",
  "email": "email@example.com",
  "password": "pass"
}

# Logout
POST /api/v1/auth/logout

# Mevcut kullanıcı
GET /api/v1/auth/me
```

## 🚀 Kullanım

### Yeni Entry Point

```bash
# Eski yöntem (hala çalışıyor)
python app.py

# Yeni yöntem (önerilen)
python run.py
```

### Development

```python
from app import create_app

app = create_app('development')
app.run(debug=True)
```

### Production

```python
from app import create_app

app = create_app('production')
# Gunicorn ile çalıştır
```

## 🔄 Migration Planı

### Aşama 1: ✅ Tamamlandı
- Blueprint yapısı oluşturuldu
- API endpoints hazırlandı
- Service layer eklendi

### Aşama 2: 🔄 Devam Ediyor
- Mevcut route'ları yeni yapıya taşıma
- Backward compatibility sağlama
- Test coverage

### Aşama 3: 📋 Planlanan
- SQLAlchemy ORM migration
- PostgreSQL support
- Advanced features

## 📝 Notlar

- Mevcut `app.py` hala çalışıyor (backward compatibility)
- Yeni yapı `run.py` ile başlatılıyor
- Models mevcut `models.py`'yi kullanıyor (geçiş aşaması)
- Tüm API endpoints `/api/v1/` prefix'i ile

## 🎉 Avantajlar

1. ✅ **Modüler Yapı**: Kod daha organize
2. ✅ **Test Edilebilirlik**: Her modül ayrı test edilebilir
3. ✅ **Ölçeklenebilirlik**: Yeni özellikler kolay eklenir
4. ✅ **API Versioning**: `/api/v1/` ile versioning hazır
5. ✅ **Separation of Concerns**: Her katman kendi sorumluluğunda

