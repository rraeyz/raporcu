# Raporcu - Yapay Zeka Destekli Deney Raporu Yazım Uygulaması

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](https://github.com/rraeyz/raporcu)
[![Downloads](https://img.shields.io/github/downloads/rraeyz/raporcu/total.svg)](https://github.com/rraeyz/raporcu/releases)

Deney raporları oluşturmak için geliştirilmiş **masaüstü uygulaması**. Sesli olarak kaydedilen deney prosedürlerini yapay zeka desteğiyle profesyonel raporlara dönüştürür.

[📥 İndir](#-hazır-uygulama-indirin) · [Özellikler](#-özellikler) · [Geliştirici Kurulumu](#-geliştirici-kurulumu) · [Web Versiyonu](https://github.com/rraeyz/raporcuweb)

</div>

---

## 📥 Hazır Uygulama İndirin

**Geliştirici değil misiniz?** Python kurmadan direkt çalışabilir sürümü indirin:

**Windows:**
- [Raporcu-v1.0.0-Windows.exe](https://github.com/rraeyz/raporcu/releases/latest) (64-bit)

**macOS / Linux:**
- Kaynak koddan çalıştırın (aşağıdaki kurulum talimatlarını izleyin)

> ⚠️ **Not:** İlk çalıştırmada Windows Defender uyarısı alabilirsiniz. "Daha fazla bilgi" → "Yine de çalıştır" seçeneğini kullanın.

---

## 🎯 Özellikler

- 🎤 **Ses Kaydı:** Deney prosedürlerini sesli olarak kaydetme
- 🗣️ **Ses Tanıma:** Whisper veya Google Speech Recognition ile otomatik metin dönüşümü
- ⌨️ **Manuel Giriş:** Deney prosedürünü metin olarak manuel olarak girme imkanı
- 🤖 **AI Destekli Rapor:** Claude, GPT, Gemini modelleri ile otomatik rapor oluşturma
- 📊 **Zengin İçerik:**
  - Görsel ekleme (deney sonuçları için grafikler, diyagramlar)
  - Tablo ve matematiksel formül desteği
  - Kaynak yöneticisi
- 💾 **Dışa Aktarma:** PDF veya Word formatında rapor çıktısı
- 🌍 **Çoklu Dil:** Türkçe ve İngilizce dil desteği
- 💡 **Kullanıcı Dostu:** Son kullanılan pencere boyutu ve konumunu hatırlama
- 🎨 **Tema:** Koyu/açık/sistem teması desteği

## 📸 Ekran Görüntüleri

*(Ekran görüntüleri eklenecek)*

## 🚀 Kurulum

### Gereksinimler

- Python 3.8 veya üzeri
- FFmpeg (ses işleme için)
- İnternet bağlantısı (AI API servisleri için)
- API anahtarı (Google AI, OpenAI veya Anthropic)

### Adım Adım Kurulum

1. **Repository'yi klonlayın:**
```bash
git clone https://github.com/rraeyz/raporcu.git
cd raporcu
```

2. **Sanal ortam oluşturun (opsiyonel ama önerilir):**
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

3. **Gerekli kütüphaneleri yükleyin:**
```bash
pip install -r requirements.txt
```

4. **FFmpeg'i yükleyin:**
   - Windows: [FFmpeg İndirme Sayfası](https://ffmpeg.org/download.html)
   - Linux: `sudo apt install ffmpeg`
   - Mac: `brew install ffmpeg`

5. **Ayarları yapılandırın:**
```bash
# settings.json.example dosyasını settings.json olarak kopyalayın
copy settings.json.example settings.json  # Windows
# cp settings.json.example settings.json  # Linux/Mac
```

`settings.json` dosyasını açın ve API anahtarınızı ekleyin:
```json
{
    "api_keys": {
        "Google": "YOUR_API_KEY_HERE",
        "Anthropic": "",
        "OpenAI": ""
    }
}
```

6. **Uygulamayı başlatın:**
```bash
python main.py
```

### 🎯 Hızlı Kurulum (Windows)

Alternatif olarak, `kurulum.bat` dosyasını çalıştırarak otomatik kurulum yapabilirsiniz:
```bash
kurulum(ffmpeg kurulumlu).bat
```

## 📖 Kullanım

1. Uygulamayı başlatın: `python main.py`
2. "Yeni Rapor" butonuna tıklayın
3. Deney bilgilerini girin (başlık, tarih, araştırmacı adı vb.)
4. **Ses Kaydı:** Mikrofon butonuna tıklayın ve deney prosedürünüzü sesli olarak anlatın
5. **Dosya Ekleme:** Görüntü veya dosya eklemek için ilgili butonları kullanın
6. **Rapor Oluştur:** AI ile otomatik rapor taslağı oluşturun
7. **Düzenle ve Kaydet:** Raporu düzenleyin ve PDF/Word olarak kaydedin

## 🛠️ Teknolojiler

- **GUI:** CustomTkinter (modern, cross-platform)
- **Ses İşleme:** PyAudio, Pydub, SpeechRecognition
- **AI Entegrasyonu:** OpenAI, Google Generative AI, Anthropic
- **Whisper:** Offline ses tanıma (opsiyonel)
- **Dosya İşleme:** python-docx, PyMuPDF, ReportLab
- **Görselleştirme:** Matplotlib, SymPy

> 💡 **Web versiyonu mu arıyorsunuz?** → [RaporcuWeb](https://github.com/rraeyz/raporcuweb) (Flask tabanlı web uygulaması)

## 📋 Desteklenen AI Modelleri

- **Google Gemini:** 2.0 Flash, 2.5 Flash, 2.5 Pro
- **Anthropic Claude:** 3 Opus, 3 Sonnet
- **OpenAI:** GPT-4 Turbo

## 🤝 Katkıda Bulunma

Katkılarınızı bekliyoruz! Pull request göndermekten çekinmeyin.

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/AmazingFeature`)
3. Commit edin (`git commit -m 'Add some AmazingFeature'`)
4. Push edin (`git push origin feature/AmazingFeature`)
5. Pull Request açın

## 🔧 Geliştirici: EXE Oluşturma

Uygulamayı tek bir `.exe` dosyası olarak derlemek için:

**1. PyInstaller Yükleyin:**
```bash
pip install pyinstaller
```

**2. Build Scripti Çalıştırın:**
```bash
# Windows
build.bat

# veya manuel:
python build_exe.py
```

**3. Test Edin:**
```bash
dist\Raporcu.exe
```

**4. GitHub Release Oluşturun:**
- GitHub'da "Releases" → "Create a new release"
- Tag: `v1.0.0`
- Title: `Raporcu v1.0.0`
- `dist/Raporcu.exe` dosyasını yükleyin
- Release notes yazın
- "Publish release"

> 📦 Exe dosyası `dist/` klasöründe oluşturulur. Boyut: ~150-200 MB
4. Push edin (`git push origin feature/AmazingFeature`)
5. Pull Request açın

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakınız.

## 📧 İletişim

Sorularınız veya geri bildirimleriniz için issue açabilirsiniz.

---

⭐ Bu projeyi beğendiyseniz yıldız vermeyi unutmayın!
