import numpy as np
import librosa
import soundfile as sf
from scipy.signal import butter, lfilter

def load_audio(audio_path, target_sr=None):
    y, sr = librosa.load(audio_path, sr=target_sr, mono=True)
    return y, sr

def save_audio(y, sr, out_path):
    sf.write(out_path, y, sr)

def normalize(y, peak=0.98):
    maxv = np.max(np.abs(y)) + 1e-9
    return y * (peak / maxv)

def pitch_and_speed(y, sr, n_steps=0.0, rate=1.0):
    # Pitch shift first, then time-stretch
    if n_steps != 0:
        y = librosa.effects.pitch_shift(y, sr, n_steps=n_steps)
    if rate != 1.0 and rate > 0:
        # Guard for extremely short signals
        if len(y) > sr * 0.1:
            y = librosa.effects.time_stretch(y, rate=rate)
    return y

def ring_modulation(y, sr, freq=30.0):
    # Robotize via ring modulation with a low-frequency carrier
    t = np.arange(len(y)) / sr
    carrier = np.sin(2 * np.pi * freq * t)
    return y * carrier

def echo(y, sr, delay_ms=250, decay=0.4):
    delay_samples = int(sr * (delay_ms / 1000.0))
    if delay_samples <= 0:
        return y
    out = np.copy(y)
    # One-tap feedback echo
    for i in range(delay_samples, len(y)):
        out[i] += decay * out[i - delay_samples]
    # Prevent clipping
    out = out / (1.0 + abs(decay))
    return out

def butter_bandpass(lowcut, highcut, fs, order=4):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

def telephone_effect(y, sr):
    # Narrowband bandpass ~300–3400 Hz
    b, a = butter_bandpass(300.0, 3400.0, sr, order=4)
    out = lfilter(b, a, y)
    return out

def apply_pipeline(y, sr, n_steps=0.0, rate=1.0,
                   use_robot=False, robot_freq=30.0,
                   use_echo=False, echo_delay_ms=250, echo_decay=0.4,
                   use_telephone=False):
    y_proc = pitch_and_speed(y, sr, n_steps=n_steps, rate=rate)

    if use_robot:
        y_proc = ring_modulation(y_proc, sr, freq=robot_freq)

    if use_echo:
        y_proc = echo(y_proc, sr, delay_ms=echo_delay_ms, decay=echo_decay)

    if use_telephone:
        y_proc = telephone_effect(y_proc, sr)

    y_proc = normalize(y_proc)
    return y_proc