# app.py — WAV-only, fast, with extra effects
from flask import Flask, render_template, request, send_file, jsonify
from werkzeug.utils import secure_filename
import numpy as np
import librosa
import soundfile as sf
from scipy.signal import butter, lfilter
import os, uuid

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'wav'}      # keep WAV-only for reliability/speed
TARGET_SR = 44100                 # resample target

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ---------- DSP helpers ----------
def normalize(y, peak=0.98):
    m = float(np.max(np.abs(y)) + 1e-9)
    return y * (peak / m)

def ring_modulation(y, sr, freq=30.0):
    t = np.arange(len(y)) / sr
    return y * np.sin(2*np.pi*freq*t)

def butter_bandpass(low, high, fs, order=4):
    nyq = 0.5 * fs
    b, a = butter(order, [low/nyq, high/nyq], btype='band')
    return b, a

def telephone_effect(y, sr):
    b, a = butter_bandpass(300.0, 3400.0, sr, order=4)
    return lfilter(b, a, y)

def echo(y, sr, delay_ms=250, decay=0.4):
    d = int(sr * (delay_ms/1000.0))
    if d <= 0: return y
    out = np.copy(y)
    for i in range(d, len(out)):
        out[i] += decay * out[i-d]
    return out / (1.0 + abs(decay))

# ---------------------------------

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    try:
        if 'audio' not in request.files:
            return jsonify({"error": "No file field named 'audio'."}), 400
        file = request.files['audio']
        if file.filename == '':
            return jsonify({"error": "No file selected."}), 400
        if not allowed_file(file.filename):
            return jsonify({"error": "Only .wav accepted (use ≤25s for speed)."}), 400

        safe = secure_filename(file.filename)
        in_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}_{safe}")
        file.save(in_path)

        # UI params
        pitch = float(request.form.get('pitch', 0))
        speed = float(request.form.get('speed', 1.0))
        max_seconds = float(request.form.get('trim', 25))

        use_robot = (request.form.get('robot') == 'on')
        robot_freq = float(request.form.get('robot_freq', 30))
        use_echo = (request.form.get('echo') == 'on')
        echo_delay = float(request.form.get('echo_delay', 250))
        echo_decay = float(request.form.get('echo_decay', 0.4))
        use_tel = (request.form.get('telephone') == 'on')

        # Load mono + resample
        y, sr = librosa.load(in_path, sr=TARGET_SR, mono=True)

        # Auto-trim
        max_len = int(max_seconds * sr)
        if len(y) > max_len:
            y = y[:max_len]

        # Core processing
        if pitch != 0:
            y = librosa.effects.pitch_shift(y, sr=sr, n_steps=pitch)
        if speed != 1.0 and len(y) > sr * 0.1:
            y = librosa.effects.time_stretch(y, rate=speed)

        # Effects (optional)
        if use_robot:
            y = ring_modulation(y, sr, freq=robot_freq)
        if use_echo:
            y = echo(y, sr, delay_ms=echo_delay, decay=echo_decay)
        if use_tel:
            y = telephone_effect(y, sr)

        y = normalize(y)
        out_path = os.path.join(OUTPUT_FOLDER, f"{uuid.uuid4()}.wav")
        sf.write(out_path, y, sr)
        return send_file(out_path, mimetype="audio/wav", as_attachment=True, download_name="voicefun_output.wav")

    except Exception as e:
        return jsonify({"error": f"{type(e).__name__}: {e}"}), 500

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000, debug=True)
