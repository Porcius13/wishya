# 🚀 Farklı Lokalde Çalıştırma Rehberi

## 📋 Gereksinimler

1. **Python 3.8+** yüklü olmalı
2. **Git** (opsiyonel, kod çekmek için)
3. **Redis** (opsiyonel, caching için)
4. **Celery** (opsiyonel, background jobs için)

## 🔧 Kurulum Adımları

### 1. Projeyi İndirin/Klonlayın

```bash
# Eğer Git kullanıyorsanız:
git clone <repository-url>
cd kataloggia-main/kataloggia-main

# Veya dosyaları manuel olarak kopyalayın
```

### 2. Virtual Environment Oluşturun

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Bağımlılıkları Yükleyin

```bash
pip install -r requirements.txt

# Playwright browser'ları yükleyin
playwright install
```

### 4. Ortam Değişkenlerini Ayarlayın

`.env` dosyası oluşturun (veya mevcut olanı düzenleyin):

```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///favit.db
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
SENTRY_DSN=  # Opsiyonel
```

### 5. Veritabanını Başlatın

```bash
python run.py
# İlk çalıştırmada veritabanı otomatik oluşturulur
```

## 🎯 Çalıştırma

### Yöntem 1: Standart Port (5000)

```bash
python run.py
```

Uygulama: `http://localhost:5000`

### Yöntem 2: Farklı Port

`run.py` dosyasını düzenleyin:

```python
if __name__ == "__main__":
    socketio = get_socketio()
    port = int(os.environ.get('PORT', 5000))  # Varsayılan 5000
    if socketio:
        socketio.run(app, host="0.0.0.0", port=port, debug=True)
    else:
        app.run(host="0.0.0.0", port=port, debug=True)
```

Veya ortam değişkeni ile:

```bash
# Windows PowerShell
$env:PORT=8080; python run.py

# Windows CMD
set PORT=8080 && python run.py

# Linux/Mac
PORT=8080 python run.py
```

### Yöntem 3: Gunicorn ile Production

```bash
gunicorn -w 4 -b 0.0.0.0:5000 "run:app"
```

## 🔍 Sorun Giderme

### Port Zaten Kullanılıyor

```bash
# Windows - Port'u kullanan process'i bulun
netstat -ano | findstr :5000

# Linux/Mac
lsof -i :5000
```

### Redis Bağlantı Hatası

Redis yüklü değilse, caching devre dışı kalır ama uygulama çalışır.

### Veritabanı Hatası

```bash
# Veritabanını sıfırlamak için
rm favit.db  # Linux/Mac
del favit.db  # Windows
python run.py  # Yeniden oluşturur
```

## 📝 Notlar

- İlk çalıştırmada veritabanı otomatik oluşturulur
- Redis ve Celery opsiyoneldir, olmadan da çalışır
- Debug modu aktif (production'da kapatın)

