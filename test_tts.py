#!/usr/bin/env python3
"""
EMA Lightning TTS Test Script
Test Turkish text-to-speech generation with latency and RTF (Real-Time Factor) benchmarks.
"""

import sys
import time
import subprocess
import warnings
warnings.filterwarnings("ignore")
import torch
from ema_lightning import EMA

def get_compatible_device():
    """Detect if CUDA actually works for tensor operations or fallback to CPU."""
    if torch.cuda.is_available():
        try:
            test_tensor = torch.zeros(1, device="cuda")
            del test_tensor
            return "cuda"
        except Exception as e:
            print(f"[Bilgi] CUDA mevcut ancak mevcut PyTorch bu GPU mimarisini desteklemiyor ({e}).")
            print("[Bilgi] CPU moduna otomatik geçiş yapılıyor.")
            return "cpu"
    return "cpu"

def play_audio(filepath):
    """Attempt playback using system tools."""
    for player in ["aplay", "paplay", "mpv", "ffplay"]:
        try:
            if player == "aplay":
                subprocess.run(["aplay", "-q", filepath], check=True)
            elif player == "paplay":
                subprocess.run(["paplay", filepath], check=True)
            elif player == "mpv":
                subprocess.run(["mpv", "--no-video", filepath], check=True)
            elif player == "ffplay":
                subprocess.run(["ffplay", "-nodisp", "-autoexit", filepath], check=True)
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            continue
    print("[Uyarı] Ses çalacak oynatıcı bulunamadı (aplay/paplay/mpv/ffplay).")
    return False

def main():
    print("=" * 60)
    print("⚡ EMA Lightning Türkçe TTS Model Testi")
    print("=" * 60)

    device = get_compatible_device()
    print(f"[1/4] Model yükleniyor (Cihaz: {device.upper()})...")
    load_start = time.time()
    tts = EMA(device=device)
    load_time = time.time() - load_start
    print(f"      Model başarıyla yüklendi! ({load_time:.2f} saniye)")

    test_cases = [
        {
            "category": "Genel Selamlama",
            "text": "Merhaba! EMA Lightning Türkçe metin okuma modeli başarıyla çalışıyor.",
            "speed": 1.0,
            "filename": "output_selam.wav"
        },
        {
            "category": "Sayılar, Tarih ve Para Birimi (Normalizasyon Testi)",
            "text": "15 Ekim 2026 Çarşamba günü saat 14:30'da, 1.250.000 TL tutarındaki ödemeniz hesabınıza yatırılacak.",
            "speed": 1.0,
            "filename": "output_finans.wav"
        },
        {
            "category": "Edebi Cümle ve Betimleme",
            "text": "Sabahın erken saatlerinde liman henüz uyanmamıştı. Balıkçılar ağlarını sessizce topluyor, martılar ise teknelerin etrafında dönerek şanslarını deniyordu.",
            "speed": 1.0,
            "filename": "output_edebi.wav"
        },
        {
            "category": "Tekerleme / Artikülasyon Testi",
            "text": "Şu yoğurdu sarımsaklasak da mı saklasak, sarımsaklamasak da mı saklasak?",
            "speed": 1.0,
            "filename": "output_tekerleme.wav"
        },
        {
            "category": "Hızlı Konuşma Testi (1.25x)",
            "text": "Siparişiniz kargo firmasına teslim edilmiştir, en kısa sürede adresinize ulaşacaktır.",
            "speed": 1.25,
            "filename": "output_hizli.wav"
        }
    ]

    print("\n[2/4] Test cümleleri sentezleniyor...")
    print("-" * 60)

    out_dir = "outputs"
    import os
    os.makedirs(out_dir, exist_ok=True)

    total_synth_time = 0
    total_audio_duration = 0

    for idx, test in enumerate(test_cases, 1):
        print(f"\nTest {idx}: [{test['category']}]")
        print(f"Metin : \"{test['text']}\"")
        print(f"Hız   : {test['speed']}x")

        out_path = os.path.join(out_dir, test['filename'])
        t0 = time.time()
        speech = tts.say(test['text'], speed=test['speed'], path=out_path)
        elapsed = time.time() - t0

        rtf = elapsed / speech.duration if speech.duration > 0 else 0
        total_synth_time += elapsed
        total_audio_duration += speech.duration

        print(f"Sonuç : {speech.duration:.2f} sn ses üretildi.")
        print(f"Süre  : {elapsed:.2f} sn (RTF: {rtf:.2f}x - {'Gerçek zamandan hızlı' if rtf < 1 else 'Gerçek zamandan yavaş'})")
        print(f"Kayıt : {out_path}")

    print("\n" + "=" * 60)
    print("[3/4] Özet Performans İstatistikleri")
    print("=" * 60)
    avg_rtf = total_synth_time / total_audio_duration if total_audio_duration > 0 else 0
    print(f"Toplam Üretilen Ses  : {total_audio_duration:.2f} saniye")
    print(f"Toplam Sentez Süresi : {total_synth_time:.2f} saniye")
    print(f"Ortalama RTF Değeri  : {avg_rtf:.2f}")
    if avg_rtf < 1:
        speedup = 1 / avg_rtf
        print(f"Hızlanma Oranı       : Gerçek zamanın {speedup:.2f} katı hızında")
    else:
        print(f"Hızlanma Oranı       : Gerçek zamandan {avg_rtf:.2f} kat yavaş")

    print("\n[4/4] Ses Çalma Denemesi")
    if "--play" in sys.argv:
        print("İlk test sesi oynatılıyor...")
        play_audio(os.path.join(out_dir, test_cases[0]["filename"]))
    else:
        print(f"Sesleri dinlemek için 'aplay outputs/{test_cases[0]['filename']}' komutunu çalıştırabilir veya")
        print("testi doğrudan '--play' parametresiyle çalıştırabilirsiniz: python test_tts.py --play")

    print("\n✅ Test tamamlandı!")

if __name__ == "__main__":
    main()
