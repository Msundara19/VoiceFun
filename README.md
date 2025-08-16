# 🎙️ VoiceFun — Cartoonify My Voice (30–40 min project)

A tiny web app that transforms your speech with **pitch**, **speed**, and playful effects (Robot, Echo, Telephone). Perfect for a quick portfolio demo.

## ✨ What you’ll show off
- Real‑time audio manipulation (pitch shift, time‑stretch)
- Simple DSP effects in Python (ring modulation, echo, band‑pass)
- A clean web demo with Gradio

## 🚀 Quickstart

1. **Create and activate a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the app**
   ```bash
   python app.py
   ```
   Gradio will print a local URL (e.g., `http://127.0.0.1:7860`). Open it in your browser.

4. **Use it**
   - Record or upload a **short speech clip** (5–15s is great).
   - Tweak the **Pitch** (−12 to +12 semitones) and **Speed** (0.5×–2×).
   - Toggle **Robot**, **Echo**, **Telephone** for fun effects.
   - Click **Transform** → listen and **Download WAV**.

## 🧠 How it works
- **librosa** handles high‑quality **pitch shifting** and **time‑stretch**.
- **Robot** is **ring modulation** (multiply by a low‑frequency sine carrier).
- **Echo** is a simple feedback delay (ms + decay).
- **Telephone** is a **band‑pass filter** (≈300–3400 Hz) using `scipy.signal`.

## 📂 Repo layout
```
VoiceFun/
├─ app.py
├─ effects.py
├─ requirements.txt
└─ README.md
```

## 📝 Notes
- Works best on **mono** voice clips; the app converts to mono at 44.1 kHz.
- Keep inputs short for snappy processing.
- No external binaries required (ffmpeg not needed).

## 🔮 Extensions (if you have extra time)
- Add **formant shift** control (e.g., simple spectral envelope tilt).
- Export **MP3** as an option.
- Presets: *Chipmunk*, *Darth*, *Robot overlord* (just set pitch/speed/effects combos).
- Deploy on **Hugging Face Spaces** for an instant public demo.
```