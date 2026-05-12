import os
import subprocess
from flask import Flask, request, jsonify, render_template, send_file
import whisper
from googletrans import Translator
from gtts import gTTS

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# AI models
model = whisper.load_model("base")
translator = Translator()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/process", methods=["POST"])
def process_video():
    try:
        video = request.files["video"]

        video_path = os.path.join(UPLOAD_FOLDER, "input.mp4")
        audio_path = os.path.join(UPLOAD_FOLDER, "audio.wav")
        voice_path = os.path.join(UPLOAD_FOLDER, "khmer.mp3")

        # save video
        video.save(video_path)

        # STEP 1: extract audio
        subprocess.run([
            "ffmpeg", "-y",
            "-i", video_path,
            "-ar", "16000",
            "-ac", "1",
            audio_path
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # STEP 2: speech to text
        result = model.transcribe(audio_path)
        text = result["text"]

        # STEP 3: translate to Khmer
        khmer_text = translator.translate(text, dest="km").text

        # STEP 4: text → Khmer AI voice
        tts = gTTS(text=khmer_text, lang="km")
        tts.save(voice_path)

        # STEP 5: cleanup input files
        if os.path.exists(video_path):
            os.remove(video_path)
        if os.path.exists(audio_path):
            os.remove(audio_path)

        return jsonify({
            "status": "success",
            "text": text,
            "khmer": khmer_text
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })


# audio endpoint
@app.route("/audio")
def audio():
    return send_file("uploads/khmer.mp3", mimetype="audio/mpeg")


if __name__ == "__main__":
    app.run()
