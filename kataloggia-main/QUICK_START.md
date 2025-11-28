# 🚀 Hızlı Başlangıç - Farklı Lokalde Çalıştırma

## ⚡ Hızlı Başlatma

### Windows

```powershell
# Varsayılan port (5000)
python run.py

# Farklı port ile
$env:PORT=8080; python run.py

# Veya start.bat dosyasını düzenleyip çalıştırın
start.bat
```

### Linux/Mac

```bash
# Varsayılan port (5000)
python3 run.py

# Farklı port ile
PORT=8080 python3 run.py

# Veya start.sh dosyasını düzenleyip çalıştırın
chmod +x start.sh
./start.sh
```

### Gelişmiş Kullanım (run_local.py)

```bash
# Port belirterek
python run_local.py --port 8080

# Host ve port belirterek
python run_local.py --host 127.0.0.1 --port 3000

# Debug modunu kapatarak
python run_local.py --port 8080 --no-debug

# Tüm seçenekleri görmek için
python run_local.py --help
```

## 📋 İlk Kurulum

### 1. Bağımlılıkları Yükleyin

```bash
pip install -r requirements.txt
playwright install
```

### 2. Veritabanı

İlk çalıştırmada otomatik oluşturulur.

### 3. Çalıştırın

```bash
python run.py
```

## 🔧 Port Değiştirme

### Yöntem 1: Ortam Değişkeni

**Windows PowerShell:**
```powershell
$env:PORT=8080; python run.py
```

**Windows CMD:**
```cmd
set PORT=8080 && python run.py
```

**Linux/Mac:**
```bash
PORT=8080 python3 run.py
```

### Yöntem 2: run.py'yi Düzenleme

`run.py` dosyasında:
```python
port = int(os.environ.get('PORT', 8080))  # 8080 olarak değiştir
```

### Yöntem 3: run_local.py Kullanma

```bash
python run_local.py --port 8080
```

## 🌐 Erişim

Uygulama başladıktan sonra:
- **Yerel:** http://localhost:PORT
- **Ağ:** http://YOUR_IP:PORT

## ⚠️ Sorun Giderme

### Port Zaten Kullanılıyor

```bash
# Windows
netstat -ano | findstr :5000

# Linux/Mac
lsof -i :5000
```

Farklı bir port kullanın veya process'i sonlandırın.

### Import Hataları

```bash
# Virtual environment aktif mi kontrol edin
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### Veritabanı Hatası

```bash
# Veritabanını silip yeniden oluşturun
rm favit.db  # Linux/Mac
del favit.db  # Windows
python run.py
```

## 📝 Notlar

- İlk çalıştırmada veritabanı otomatik oluşturulur
- Redis ve Celery opsiyoneldir
- Debug modu varsayılan olarak açıktır

