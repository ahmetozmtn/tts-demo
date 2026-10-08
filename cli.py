#!/usr/bin/env python3
"""
EMA Lightning TTS CLI Tool
Synthesize Turkish text to WAV audio files directly from the terminal.
"""

import argparse
import sys
import time
import subprocess
import warnings
warnings.filterwarnings("ignore")
import torch
from ema_lightning import EMA

def get_compatible_device(requested_device):
    if requested_device != "auto":
        return requested_device
    if torch.cuda.is_available():
        try:
            t = torch.zeros(1, device="cuda")
            del t
            return "cuda"
        except Exception:
            return "cpu"
    return "cpu"

def play_audio(filepath):
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
    print("[Uyarı] Ses oynatıcı bulunamadı (aplay/paplay/mpv/ffplay).")
    return False

def main():
    parser = argparse.ArgumentParser(description="EMA Lightning Türkçe TTS Komut Satırı Aracı")
    parser.add_argument("text", nargs="?", help="Sentezlenecek Türkçe metin")
    parser.add_argument("-o", "--output", default="output.wav", help="Çıktı WAV dosyası yolu (varsayılan: output.wav)")
    parser.add_argument("-s", "--speed", type=float, default=1.0, help="Konuşma hızı (0.25 - 4.0, varsayılan: 1.0)")
    parser.add_argument("-d", "--device", default="auto", choices=["auto", "cpu", "cuda"], help="Cihaz (varsayılan: auto)")
    parser.add_argument("-p", "--play", action="store_true", help="Üretim bittikten sonra sesi doğrudan oynat")
    parser.add_argument("-i", "--interactive", action="store_true", help="İnteraktif mod (sürekli metin girişi)")

    args = parser.parse_args()

    device = get_compatible_device(args.device)
    print(f"[*] EMA Lightning TTS yükleniyor (Cihaz: {device.upper()})...")
    tts = EMA(device=device)
    print("[✓] Model hazır!")

    if args.interactive or not args.text:
        print("\n--- İnteraktif Mod (Çıkmak için 'q' veya Ctrl+C) ---")
        idx = 1
        import os
        os.makedirs("outputs", exist_ok=True)
        try:
            while True:
                prompt_text = input(f"\n[{idx}] Okunacak metin: ").strip()
                if not prompt_text:
                    continue
                if prompt_text.lower() in ["q", "exit", "quit", "cikis"]:
                    print("Çıkılıyor.")
                    break
                out_path = f"outputs/interactive_{idx}.wav"
                t0 = time.time()
                speech = tts.say(prompt_text, speed=args.speed, path=out_path)
                elapsed = time.time() - t0
                print(f"    -> {speech.duration:.2f}s ses {elapsed:.2f} saniyede üretildi ({out_path})")
                play_audio(out_path)
                idx += 1
        except (KeyboardInterrupt, EOFError):
            print("\nÇıkış yapıldı.")
            sys.exit(0)
    else:
        import os
        out_dir = os.path.dirname(args.output)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        t0 = time.time()
        speech = tts.say(args.text, speed=args.speed, path=args.output)
        elapsed = time.time() - t0
        print(f"[✓] Tamamlandı: {speech.duration:.2f}s ses, {elapsed:.2f}s işlem süresi.")
        print(f"[✓] Kaydedildi: {args.output}")

        if args.play:
            print("[*] Ses çalınıyor...")
            play_audio(args.output)

if __name__ == "__main__":
    main()
