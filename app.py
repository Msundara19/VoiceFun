import gradio as gr
import os
from effects import load_audio, save_audio, apply_pipeline

OUTPUT_PATH = "output.wav"

def process(audio_file, pitch_semitones, speed, robot, robot_freq, echo, echo_delay, echo_decay, telephone):
    if audio_file is None:
        raise gr.Error("Please record or upload an audio clip first.")
    # gradio provides (sr, data) OR a filepath depending on version. We handle both.
    if isinstance(audio_file, dict) and "path" in audio_file:
        path = audio_file["path"]
    elif isinstance(audio_file, str):
        path = audio_file
    else:
        # Older format: (sr, np.array) -> save temp
        import soundfile as sf
        import numpy as np
        sr, data = audio_file
        path = "temp_input.wav"
        sf.write(path, data.astype("float32"), sr)

    y, sr = load_audio(path, target_sr=44100)
    y_out = apply_pipeline(
        y, sr,
        n_steps=pitch_semitones,
        rate=speed,
        use_robot=robot,
        robot_freq=robot_freq,
        use_echo=echo,
        echo_delay_ms=echo_delay,
        echo_decay=echo_decay,
        use_telephone=telephone
    )
    save_audio(y_out, sr, OUTPUT_PATH)
    return OUTPUT_PATH

with gr.Blocks(title="VoiceFun - Cartoonify My Voice") as demo:
    gr.Markdown("# 🎙️ VoiceFun — Cartoonify My Voice")
    gr.Markdown("Upload or record your voice, then tweak pitch, speed, and fun effects. Download your transformed voice!")

    with gr.Row():
        with gr.Column():
            audio_in = gr.Audio(sources=["microphone", "upload"], type="filepath", label="Input Audio")
            pitch = gr.Slider(-12, 12, value=0, step=1, label="Pitch shift (semitones)")
            speed = gr.Slider(0.5, 2.0, value=1.0, step=0.05, label="Speed (time-stretch)")

            robot = gr.Checkbox(False, label="Robot (ring modulation)")
            robot_freq = gr.Slider(10, 80, value=30, step=1, label="Robot frequency (Hz)")

            echo = gr.Checkbox(False, label="Echo")
            echo_delay = gr.Slider(50, 800, value=250, step=10, label="Echo delay (ms)")
            echo_decay = gr.Slider(0.1, 0.9, value=0.4, step=0.05, label="Echo decay")

            telephone = gr.Checkbox(False, label="Telephone (bandpass 300–3400 Hz)")

            run_btn = gr.Button("Transform ✨")

        with gr.Column():
            audio_out = gr.Audio(type="filepath", label="Transformed Audio")
            download = gr.File(label="Download WAV")

    def run_and_return(audio_file, pitch_semitones, speed, robot, robot_freq, echo, echo_delay, echo_decay, telephone):
        out = process(audio_file, pitch_semitones, speed, robot, robot_freq, echo, echo_delay, echo_decay, telephone)
        return out, out

    run_btn.click(
        fn=run_and_return,
        inputs=[audio_in, pitch, speed, robot, robot_freq, echo, echo_delay, echo_decay, telephone],
        outputs=[audio_out, download]
    )

if __name__ == "__main__":
    demo.launch()