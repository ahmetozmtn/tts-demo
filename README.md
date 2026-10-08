# ⚡ EMA Lightning - Türkçe TTS Test & Web Arayüzü

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-green.svg)](https://opensource.org/licenses/Apache-2.0)
[![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20Model-canberkkkkkk%2Fema--lightning-yellow)](https://huggingface.co/canberkkkkkk/ema-lightning)
[![Audio Quality](https://img.shields.io/badge/Audio-48%20kHz%20Studio-purple.svg)](#)

[canberkkkkkk/ema-lightning](https://huggingface.co/canberkkkkkk/ema-lightning) Türkçe Text-to-Speech (Metin-Ses Dönüştürme) modelini test etmek, karşılaştırmalı performans ölçümleri (RTF) almak ve modern bir web/terminal arayüzü üzerinden hızlıca kullanmak için geliştirilmiş açık kaynaklı test ortamı.

---

## ✨ Özellikler

- **8.6M Parametre / ~34 MB:** Son derece hafif ve kompakt mimari (5.6M Flow-matching DiT akustik model + 3.0M HiFi-GAN 48 kHz vocoder).
- **Gerçek Zamandan Hızlı (RTF < 0.5):** Modern GPU'larda saniyeler yerine milisaniyeler içinde ses üretir; ortalama bir CPU üzerinde bile gerçek konuşma hızının **2 ila 4 katı hızında** çalışır.
- **Akıllı Metin Normalizasyonu:** [normalizer-tr](https://github.com/erdemtuna/normalizer-tr) desteği ile para birimleri (`1.250.000 TL`), tarihler (`15 Ekim 2026`), saatler (`14:30`) ve kısaltmalar telaffuza uygun şekilde otomatik dönüştürülür.
- **Otomatik Donanım Algılama:** Sistemdeki GPU uyumluluğunu (CUDA compute capability) kontrol eder; modern kartlarda CUDA hızlandırmasını kullanırken eski mimarilerde hatasız biçimde kararlı CPU moduna geçer.
- **Minimalist Web Arayüzü (`web_ui.py`):** Harici framework bağımlılığı olmadan (sıfır ek kütüphane) çalışan sade ve modern web paneli.
- **Gelişmiş CLI & İnteraktif Mod (`cli.py`):** Terminalden tek komutla veya interaktif sohbet şeklinde metin seslendirme.
- **Benchmark Test Paketi (`test_tts.py`):** Selamlama, finans, edebiyat ve tekerleme senaryolarını test edip gecikme ve RTF (Real-Time Factor) analizi sunar.

---

## 🚀 Hızlı Başlangıç

### 1. Depoyu Klonlayın
```bash
git clone https://github.com/ahmetozmtn/tts-demo.git
cd tts-demo
```

### 2. Sanal Ortam Oluşturun ve Bağımlılıkları Yükleyin
```bash
python3 -m venv .venv
source .venv/bin/activate

# Pip ile yükleme:
pip install -r requirements.txt

# veya UV ile hızlı yükleme:
# uv pip install -r requirements.txt
```

> **Not:** Model ağırlıkları ilk çalıştırmada Hugging Face Hub üzerinden otomatik olarak indirilir (~34 MB) ve yerel önbelleğe alınır.

---

## 🖥️ Kullanım Yolları

### 1. Modern Web Arayüzü
Tarayıcı üzerinden metin girmek, konuşma hızını ayarlamak ve sesleri dinleyip indirmek için:
```bash
python web_ui.py
```
Sunucu başladığında tarayıcınızdan **`http://localhost:7860`** adresine gidin.

---

### 2. Komut Satırı Aracı (CLI)
Terminal üzerinden doğrudan metin dönüştürmek için:

```bash
# Metni ses dosyasına dönüştür
python cli.py "Merhaba dünya, nasılsınız?" -o merhaba.wav

# Sentezleyip hemen hoparlörden dinle (aplay / paplay / mpv / ffplay ile)
python cli.py "Siparişiniz yola çıkmıştır." --play

# Konuşma hızını değiştir (ör. 1.25x hızlı)
python cli.py "Biraz acelem var." -s 1.25 -o hizli.wav --play

# İnteraktif mod (yazdıkça anında seslendirir)
python cli.py -i
```

---

### 3. Benchmark ve Doğrulama Testi
Modelin metin normalizasyonunu, telaffuz doğruluğunu ve sisteminizdeki işlem hızını test etmek için:

```bash
python test_tts.py

# Test sonunda üretilen sesi hoparlörden dinlemek için:
python test_tts.py --play
```

Tüm üretilen test sesleri otomatik olarak `outputs/` klasörüne kaydedilir.

---

## 📊 Örnek Performans Sonuçları (CPU Üzerinde)

*Test Ortamı: Standart 2-çekirdekli taşınabilir CPU (torch 2.x, CPU Modu)*

| Test Senaryosu | Metin Örneği | Ses Süresi | Sentez Süresi | RTF Değeri | Durum |
|---|---|---|---|---|---|
| **Genel Selamlama** | "Merhaba! EMA Lightning..." | 3.92 sn | 1.06 sn | **0.27** | 3.7x gerçek zamandan hızlı |
| **Tarih & Finans** | "15 Ekim 2026 ... 1.250.000 TL..." | 8.56 sn | 4.92 sn | **0.57** | 1.7x gerçek zamandan hızlı |
| **Edebi Betimleme** | "Sabahın erken saatlerinde liman..." | 8.28 sn | 3.67 sn | **0.44** | 2.3x gerçek zamandan hızlı |
| **Tekerleme** | "Şu yoğurdu sarımsaklasak da..." | 4.12 sn | 1.93 sn | **0.47** | 2.1x gerçek zamandan hızlı |
| **Hızlı Konuşma (1.25x)** | "Siparişiniz kargo firmasına..." | 3.76 sn | 1.03 sn | **0.27** | 3.7x gerçek zamandan hızlı |
| **TOPLAM / ORTALAMA** | *5 test senaryosu* | **28.64 sn** | **12.61 sn** | **0.44** | **~2.3x Hızlanma** |

---

## 📂 Proje Yapısı

```text
tts-demo/
├── cli.py             # Esnek komut satırı aracı ve interaktif terminal modu
├── web_ui.py          # Sıfır bağımlılıklı, minimalist web test arayüzü
├── test_tts.py        # Benchmark ve test senaryosu çalıştırıcısı
├── requirements.txt   # Gerekli Python bağımlılıkları
├── pyproject.toml     # Standart Python paket yapılandırması
├── .gitignore         # Gereksiz ve geçici dosyaların engellenmesi
├── LICENSE            # Apache 2.0 Lisansı
└── README.md          # Proje dokümantasyonu
```

---

## ⚖️ Lisans ve Atıflar

- Bu test projesi ve model ağırlıkları **Apache License 2.0** kapsamında lisanslanmıştır.
- Model Mimarisi & Ağırlıkları: **[Canberk Aslan](https://huggingface.co/canberkkkkkk)** ([EMA Lightning Hugging Face](https://huggingface.co/canberkkkkkk/ema-lightning))
- Türkçe Metin Frontend: **[Erdem Tuna](https://github.com/erdemtuna)** ([normalizer-tr](https://github.com/erdemtuna/normalizer-tr))
