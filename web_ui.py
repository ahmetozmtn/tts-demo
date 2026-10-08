#!/usr/bin/env python3
"""
EMA Lightning TTS - Modern Web Test Arayüzü
Tek bir dosyada çalışan, ek bağımlılık gerektirmeyen hafif web sunucusu.
"""

import http.server
import json
import os
import sys
import time
import urllib.parse
import warnings
warnings.filterwarnings("ignore")
import torch
from ema_lightning import EMA

HOST = "0.0.0.0"
PORT = 7860

def get_compatible_device():
    if torch.cuda.is_available():
        try:
            t = torch.zeros(1, device="cuda")
            del t
            return "cuda"
        except Exception:
            return "cpu"
    return "cpu"

DEVICE = get_compatible_device()
print(f"[*] EMA Lightning TTS yükleniyor (Cihaz: {DEVICE.upper()})...")
tts = EMA(device=DEVICE)
print(f"[✓] Model hazır! Web arayüzü başlatılıyor...")

os.makedirs("web_outputs", exist_ok=True)

HTML_PAGE = """<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EMA Lightning - Türkçe TTS</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #09090b;
            --surface: #121215;
            --surface-hover: #18181b;
            --border: #27272a;
            --border-subtle: #1f1f23;
            --text: #f4f4f5;
            --text-muted: #71717a;
            --btn-bg: #f4f4f5;
            --btn-text: #09090b;
            --btn-hover: #e4e4e7;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: var(--bg);
            color: var(--text);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            padding: 40px 16px;
            -webkit-font-smoothing: antialiased;
        }
        .container {
            width: 100%;
            max-width: 720px;
        }
        .header {
            margin-bottom: 24px;
        }
        .header-top {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 6px;
        }
        .header h1 {
            font-size: 1.25rem;
            font-weight: 600;
            letter-spacing: -0.02em;
            color: var(--text);
        }
        .pill {
            font-size: 0.75rem;
            font-family: 'JetBrains Mono', monospace;
            color: var(--text-muted);
            border: 1px solid var(--border);
            padding: 2px 8px;
            border-radius: 4px;
        }
        .desc {
            color: var(--text-muted);
            font-size: 0.875rem;
            line-height: 1.4;
        }
        .card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 20px;
        }
        label {
            display: block;
            font-size: 0.75rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-muted);
            margin-bottom: 8px;
        }
        textarea {
            width: 100%;
            height: 110px;
            background: var(--bg);
            border: 1px solid var(--border);
            border-radius: 6px;
            color: var(--text);
            font-family: inherit;
            font-size: 0.9375rem;
            line-height: 1.5;
            padding: 12px;
            resize: vertical;
            outline: none;
            transition: border-color 0.15s ease;
        }
        textarea:focus {
            border-color: #52525b;
        }
        .examples {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin: 12px 0 16px 0;
            align-items: center;
        }
        .examples-label {
            font-size: 0.75rem;
            color: var(--text-muted);
            margin-right: 2px;
        }
        .example-btn {
            background: transparent;
            border: 1px solid var(--border);
            color: #a1a1aa;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 0.8125rem;
            cursor: pointer;
            transition: all 0.15s ease;
        }
        .example-btn:hover {
            background: var(--surface-hover);
            color: var(--text);
            border-color: #3f3f46;
        }
        .controls {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            padding-top: 14px;
            border-top: 1px solid var(--border-subtle);
        }
        .slider-group {
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 0.875rem;
            color: var(--text-muted);
        }
        input[type="range"] {
            width: 140px;
            accent-color: #e4e4e7;
            cursor: pointer;
        }
        .speed-val {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.8125rem;
            color: var(--text);
            min-width: 40px;
        }
        .btn-submit {
            background: var(--btn-bg);
            color: var(--btn-text);
            font-family: inherit;
            font-weight: 500;
            font-size: 0.875rem;
            padding: 8px 18px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            transition: background-color 0.15s ease;
        }
        .btn-submit:hover {
            background: var(--btn-hover);
        }
        .btn-submit:disabled {
            opacity: 0.4;
            cursor: not-allowed;
        }
        .result-box {
            display: none;
            margin-top: 16px;
            padding-top: 16px;
            border-top: 1px solid var(--border);
        }
        audio {
            width: 100%;
            height: 38px;
            margin-top: 10px;
            filter: invert(0.9) hue-rotate(180deg);
            border-radius: 4px;
        }
        .stats {
            display: flex;
            gap: 12px;
            margin-top: 14px;
        }
        .stat-card {
            flex: 1;
            background: var(--bg);
            padding: 8px 12px;
            border-radius: 6px;
            border: 1px solid var(--border-subtle);
        }
        .stat-label {
            font-size: 0.6875rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }
        .stat-val {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.875rem;
            color: var(--text);
            margin-top: 2px;
        }
        .loading {
            display: none;
            font-size: 0.875rem;
            color: var(--text-muted);
            text-align: center;
            padding: 12px 0;
        }
        .footer {
            margin-top: 16px;
            display: flex;
            justify-content: space-between;
            font-size: 0.75rem;
            color: var(--text-muted);
        }
        .footer a {
            color: var(--text-muted);
            text-decoration: underline;
            text-underline-offset: 2px;
        }
        .footer a:hover {
            color: var(--text);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="header-top">
                <h1>EMA Lightning</h1>
                <span class="pill">""" + DEVICE.upper() + """ · 48 kHz</span>
            </div>
            <p class="desc">Hızlı ve kompakt Türkçe ses sentezi (8.6M parametre)</p>
        </div>

        <div class="card">
            <label for="text">Metin</label>
            <textarea id="text" placeholder="Seslendirilecek Türkçe metni girin...">15 Ekim 2026 Çarşamba günü saat 14:30'da, 1.250.000 TL tutarındaki ödemeniz hesabınıza yatırılacak.</textarea>

            <div class="examples">
                <span class="examples-label">Örnekler:</span>
                <button class="example-btn" onclick="setText('Merhaba, EMA Lightning Türkçe metin okuma modeli başarıyla çalışıyor.')">Selamlama</button>
                <button class="example-btn" onclick="setText('15 Ekim 2026 Çarşamba günü saat 14:30\'da, 1.250.000 TL tutarındaki ödemeniz hesabınıza yatırılacak.')">Tarih & Sayı</button>
                <button class="example-btn" onclick="setText('Sabahın erken saatlerinde liman henüz uyanmamıştı. Balıkçılar ağlarını sessizce topluyordu.')">Betimleme</button>
                <button class="example-btn" onclick="setText('Şu yoğurdu sarımsaklasak da mı saklasak, sarımsaklamasak da mı saklasak?')">Tekerleme</button>
            </div>

            <div class="controls">
                <div class="slider-group">
                    <span>Hız:</span>
                    <input type="range" id="speed" min="0.5" max="2.0" step="0.05" value="1.0" oninput="document.getElementById('speed-val').innerText = this.value + 'x'">
                    <span class="speed-val" id="speed-val">1.0x</span>
                </div>
                <button id="btn-submit" class="btn-submit" onclick="synthesize()">
                    Sentezle
                </button>
            </div>

            <div id="loading" class="loading">
                Sentezleniyor...
            </div>

            <div id="result" class="result-box">
                <label>Çıktı</label>
                <audio id="audio-player" controls autoplay></audio>
                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-label">Ses Süresi</div>
                        <div class="stat-val" id="stat-duration">-</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Sentez Süresi</div>
                        <div class="stat-val" id="stat-latency">-</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Örnekleme</div>
                        <div class="stat-val" id="stat-sr">48 kHz</div>
                    </div>
                </div>
            </div>
        </div>

        <div class="footer">
            <span>Model: <a href="https://huggingface.co/canberkkkkkk/ema-lightning" target="_blank">canberkkkkkk/ema-lightning</a></span>
            <span>Apache 2.0</span>
        </div>
    </div>

    <script>
        function setText(t) {
            document.getElementById('text').value = t;
        }

        async function synthesize() {
            const text = document.getElementById('text').value.trim();
            if (!text) return alert('Lütfen bir metin girin.');

            const speed = parseFloat(document.getElementById('speed').value);
            const btn = document.getElementById('btn-submit');
            const loading = document.getElementById('loading');
            const resultBox = document.getElementById('result');
            const player = document.getElementById('audio-player');

            btn.disabled = true;
            loading.style.display = 'block';
            resultBox.style.display = 'none';

            try {
                const res = await fetch('/api/tts', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({text: text, speed: speed})
                });
                const data = await res.json();
                if (data.error) throw new Error(data.error);

                player.src = data.audio_url + '?t=' + Date.now();
                document.getElementById('stat-duration').innerText = data.duration.toFixed(2) + 's';
                document.getElementById('stat-latency').innerText = data.latency.toFixed(2) + 's';
                resultBox.style.display = 'block';
            } catch (err) {
                alert('Hata: ' + err.message);
            } finally {
                btn.disabled = false;
                loading.style.display = 'none';
            }
        }
    </script>
</body>
</html>
"""

class TTSHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Clean logging
        sys.stderr.write(f"[{time.strftime('%H:%M:%S')}] {args[0]} {args[1]}\n")

    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        if url.path == "/" or url.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))
        elif url.path.startswith("/audio/"):
            filename = os.path.basename(url.path)
            filepath = os.path.join("web_outputs", filename)
            if os.path.exists(filepath):
                self.send_response(200)
                self.send_header("Content-Type", "audio/wav")
                self.send_header("Content-Length", str(os.path.getsize(filepath)))
                self.end_headers()
                with open(filepath, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/api/tts":
            content_len = int(self.headers.get("Content-Length", 0))
            post_body = self.rfile.read(content_len)
            try:
                data = json.loads(post_body.decode("utf-8"))
                text = data.get("text", "").strip()
                speed = float(data.get("speed", 1.0))
                if not text:
                    raise ValueError("Metin boş olamaz.")

                filename = f"speech_{int(time.time()*1000)}.wav"
                out_path = os.path.join("web_outputs", filename)

                t0 = time.time()
                speech = tts.say(text, speed=speed, path=out_path)
                latency = time.time() - t0

                resp = {
                    "audio_url": f"/audio/{filename}",
                    "duration": speech.duration,
                    "latency": latency,
                    "sample_rate": speech.sample_rate
                }
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(resp).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

def run_server():
    server = http.server.ThreadingHTTPServer((HOST, PORT), TTSHandler)
    print("=" * 60)
    print(f"🚀 EMA Lightning Web Test Ortamı Başlatıldı!")
    print(f"🌐 Tarayıcınızda açın: http://localhost:{PORT}")
    print("=" * 60)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nSunucu kapatıldı.")

if __name__ == "__main__":
    run_server()
