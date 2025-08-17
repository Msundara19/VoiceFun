# app.py — multi-format audio support + clear errors
from flask import Flask, render_template, request, send_file, jsonify
from werkzeug.utils import secure_filename
import numpy as np
import librosa
import soundfile as sf
import os
import uuid

app = Flask(__name__)

# where uploads/outputs live
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# allow common formats; we'll decode with librosa (audioread) and always export WAV
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'm4a', 'ogg', 'flac'}
MAX_SECONDS = 25        # auto-trim for snappy processing
TARGET_SR = 44100       # resample target

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    try:
        if 'audio' not in request.files:
            return jsonify({"error": "No file part named 'audio' in request"}), 400
        file = request.files['audio']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        if not allowed_file(file.filename):
            return jsonify({"error": f"Unsupported format. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"}), 400

        # save upload
        safe_name = secure_filename(file.filename)
        ext = safe_name.rsplit('.', 1)[1].lower()
        input_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}.{ext}")
        file.save(input_path)

        # parameters
        try:
            pitch_shift = float(request.form.get('pitch', 0))
        except:
            pitch_shift = 0.0
        try:
            speed = float(request.form.get('speed', 1.0))
            if speed <= 0:
                speed = 1.0
        except:
            speed = 1.0

        # decode (supports mp3/m4a/ogg/wav/flac), mono + resample
        y, sr = librosa.load(input_path, sr=TARGET_SR, mono=True)

        # auto-trim for speed
        max_len = int(MAX_SECONDS * sr)
        if len(y) > max_len:
            y = y[:max_len]

        # process: pitch then time-stretch
        if pitch_shift != 0:
            y = librosa.effects.pitch_shift(y, sr=sr, n_steps=pitch_shift)
        if speed != 1.0 and len(y) > sr * 0.1:
            y = librosa.effects.time_stretch(y, rate=speed)

        # normalize a bit
        peak = np.max(np.abs(y)) + 1e-9
        y = (0.98 / peak) * y

        # export as WAV
        out_path = os.path.join(OUTPUT_FOLDER, f"{uuid.uuid4()}.wav")
        sf.write(out_path, y, sr)

        # send back as download
        return send_file(out_path, mimetype="audio/wav", as_attachment=True, download_name="voicefun_output.wav")

    except Exception as e:
        # return readable error to the page / devtools
        return jsonify({"error": f"{type(e).__name__}: {e}"}), 500

if __name__ == '__main__':
    # run local
    app.run(host="127.0.0.1", port=5000, debug=True)
