# Voice Modifier Web App

A simple web application to upload or record your voice, tweak pitch/speed, and download the transformed audio.  
Built with Flask and PyDub.

## Features
- Upload or record voice (supports `.wav`)
- Pitch shift (up/down semitones)
- Speed control (time-stretch)
- Optional robot (ring modulation) effect
- Download processed audio


## Tech Stack
- Backend: Flask, PyDub
- Frontend: HTML, CSS, JavaScript
- Audio Processing: PyDub, ffmpeg


## Project Structure
voice-modifier/
│── app.py # Flask backend
│── requirements.txt # Dependencies
│── static/ # CSS, JS, frontend assets
│── templates/ # HTML templates
│── uploads/ # Temporary uploaded files (ignored by git)
│── outputs/ # Processed audio files (ignored by git)
│── .gitignore # Ignored files/folders
│── README.md # Project documentation


## Setup Instructions
1. Clone repo
   in your bash
   git clone <your-repo-url>
   cd voice-modifier
2. Create virtual environment
   python -m venv .venv
   source .venv/bin/activate   # Mac/Linux
   .venv\Scripts\activate      # Windows
3. Install dependencies
   pip install -r requirements.txt
4. Run the app
   python app.py
Open the port in your browser

## Notes
- Only .wav files under 25 seconds are supported (due to processing limits).
- uploads/ and outputs/ are ignored in git (.gitignore).
