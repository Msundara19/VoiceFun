
from flask import Flask, render_template, request, send_file, jsonify
import librosa
import soundfile as sf
import os
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    try:
        file = request.files['audio']
        pitch_shift = int(request.form.get('pitch', 0))
        speed = float(request.form.get('speed', 1.0))

        # Save uploaded file
        input_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}.wav")
        file.save(input_path)

        # Load and process audio
        y, sr = librosa.load(input_path, sr=None)
        if pitch_shift != 0:
            y = librosa.effects.pitch_shift(y, sr=sr, n_steps=pitch_shift)
        if speed != 1.0:
            y = librosa.effects.time_stretch(y, rate=speed)

        # Save output
        output_path = os.path.join(OUTPUT_FOLDER, f"{uuid.uuid4()}.wav")
        sf.write(output_path, y, sr)

        return send_file(output_path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
