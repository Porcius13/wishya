# 🔄 Migration Guide - Yeni Yapıya Geçiş

## ✅ Tamamlanan İyileştirmeler

### 1. Modüler Backend Architecture
- ✅ Blueprint yapısı oluşturuldu
- ✅ RESTful API endpoints hazırlandı
- ✅ Service layer pattern eklendi
- ✅ Application factory pattern

### 2. Modern UI
- ✅ Toast notifications
- ✅ Skeleton loading
- ✅ Loading states
- ✅ Confirmation dialogs
- ✅ Smooth animations

## 📁 Yeni Dosya Yapısı

```
kataloggia-main/
├── app/                      # Yeni modüler yapı
│   ├── __init__.py          # Application factory
│   ├── config.py            # Configuration
│   ├── api/v1/              # RESTful API
│   ├── routes/              # Web routes
│   ├── services/            # Business logic
│   ├── models/              # Data models
│   └── utils/               # Utilities
├── run.py                   # Yeni entry point
├── app.py                   # Eski app (backward compatible)
└── models.py               # Mevcut models (backward compatible)
```

## 🚀 Nasıl Kullanılır?

### Option 1: Yeni Yapı (Önerilen)
```bash
python run.py
```

### Option 2: Eski Yapı (Hala Çalışıyor)
```bash
python app.py
```

## 📡 API Kullanımı

### Örnek: Ürün Ekleme

**Eski Yöntem:**
```javascript
// Form submit
form.action = '/add_product';
form.submit();
```

**Yeni Yöntem (API):**
```javascript
fetch('/api/v1/scraping/scrape', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        url: 'https://example.com/product'
    })
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        // Ürün bilgilerini al
        const productData = data.data;
        
        // Ürünü ekle
        return fetch('/api/v1/products', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name: productData.name,
                price: productData.price,
                url: productData.url,
                brand: productData.brand,
                image: productData.image
            })
        });
    }
});
```

## 🔄 Geçiş Stratejisi

### Aşama 1: ✅ Tamamlandı
- Modüler yapı oluşturuldu
- API endpoints hazırlandı
- Service layer eklendi

### Aşama 2: 🔄 Devam Ediyor
- Frontend'i API'ye bağlama
- Mevcut route'ları yeni yapıya taşıma
- Test coverage

### Aşama 3: 📋 Planlanan
- SQLAlchemy ORM
- PostgreSQL migration
- Advanced features

## 📝 Notlar

- **Backward Compatibility**: Eski `app.py` hala çalışıyor
- **Gradual Migration**: Yeni özellikler yeni yapıda, eskiler eski yapıda
- **No Breaking Changes**: Mevcut özellikler çalışmaya devam ediyor

## 🎯 Sonraki Adımlar

1. Frontend'i API'ye bağlama
2. Eski route'ları yeni yapıya taşıma
3. Test coverage ekleme
4. SQLAlchemy migration
5. PostgreSQL support

