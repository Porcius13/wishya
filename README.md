# Wishya - Ürün Kataloğu

Wishya, favori ürünlerinizi tek bir yerde toplamanızı ve fiyat takibi yapmanızı sağlayan bir web uygulamasıdır.

## Özellikler

- ✅ Ürün ekleme ve yönetimi
- ✅ Koleksiyonlar oluşturma
- ✅ Fiyat takibi
- ✅ localStorage ile lokal veri saklama (veritabanı gerektirmez)
- ✅ Modern ve responsive tasarım

## Yerel Kurulum

### Gereksinimler

- Python 3.11+
- pip

### Kurulum Adımları

1. Repository'yi klonlayın:
```bash
git clone <repository-url>
cd wishyachat/kataloggia-main/kataloggia-main
```

2. Virtual environment oluşturun:
```bash
python -m venv venv
```

3. Virtual environment'ı aktifleştirin:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

4. Bağımlılıkları yükleyin:
```bash
pip install -r requirements.txt
```

5. Uygulamayı çalıştırın:
```bash
python run.py
```

Uygulama `http://localhost:5000` adresinde çalışacaktır.

## Vercel'e Deploy Etme

### GitHub'a Push Etme

1. GitHub'da yeni bir repository oluşturun

2. Projeyi GitHub'a push edin:
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/kullaniciadi/repo-adi.git
git push -u origin main
```

### Vercel Deployment

1. [Vercel](https://vercel.com) hesabınıza giriş yapın

2. "New Project" butonuna tıklayın

3. GitHub repository'nizi seçin

4. Vercel otomatik olarak ayarları algılayacaktır:
   - **Framework Preset**: Other
   - **Build Command**: (boş bırakın)
   - **Output Directory**: (boş bırakın)
   - **Install Command**: `pip install -r requirements.txt`

5. Environment Variables (opsiyonel):
   - `SECRET_KEY`: Flask secret key (rastgele bir string)

6. "Deploy" butonuna tıklayın

7. Deployment tamamlandıktan sonra, uygulamanız canlı olacaktır!

## Veri Saklama

Bu uygulama **localStorage** kullanarak tüm verileri tarayıcıda saklar. Bu sayede:
- ✅ Veritabanı gerektirmez
- ✅ Her kullanıcının verileri kendi tarayıcısında saklanır
- ✅ Hızlı ve güvenli
- ✅ Vercel'in serverless yapısına uygundur

**Not**: Veriler sadece kullanıcının kendi tarayıcısında saklanır. Tarayıcı verilerini temizlerseniz, tüm verileriniz silinir.

## Proje Yapısı

```
kataloggia-main/
├── app/                    # Flask uygulama paketi
│   ├── api/               # API endpoints
│   ├── models/            # Veri modelleri
│   ├── routes/            # Route handlers
│   └── utils/             # Yardımcı fonksiyonlar
├── templates/             # HTML şablonları
├── static/                # CSS, JS, resimler
│   ├── css/
│   └── js/
│       └── localStorage.js  # localStorage yönetimi
├── app.py                 # Vercel entry point
├── run.py                 # Yerel çalıştırma
├── requirements.txt       # Python bağımlılıkları
├── vercel.json           # Vercel konfigürasyonu
└── README.md             # Bu dosya
```

## Kullanım

1. Uygulamaya kaydolun veya giriş yapın
2. Ürün URL'si ekleyerek favorilerinizi toplayın
3. Koleksiyonlar oluşturun ve ürünlerinizi organize edin
4. Fiyat takibi yaparak indirimleri kaçırmayın

## Teknolojiler

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript
- **Veri Saklama**: localStorage
- **Deployment**: Vercel

## Lisans

Bu proje kişisel kullanım içindir.

## Destek

Sorularınız için GitHub Issues kullanabilirsiniz.
