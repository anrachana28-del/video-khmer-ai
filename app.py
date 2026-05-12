import os
import uuid
import subprocess
from flask import Flask, request, jsonify, render_template, send_file
import whisper
from deep_translator import GoogleTranslator
from gtts import gTTS

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ⚡ load model (Docker safe)
model = whisper.load_model("tiny")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/process", methods=["POST"])
def process_video():
    try:
        video = request.files["video"]
        file_id = str(uuid.uuid4())

        video_path = os.path.join(UPLOAD_FOLDER, f"{file_id}.mp4")
        audio_path = os.path.join(UPLOAD_FOLDER, f"{file_id}.wav")
        voice_path = os.path.join(UPLOAD_FOLDER, f"{file_id}.mp3")

        # Save video
        video.save(video_path)

        # Extract audio
        subprocess.run([
            "ffmpeg", "-y",
            "-i", video_path,
            "-ar", "16000",
            "-ac", "1",
            audio_path
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Speech to text
        result = model.transcribe(audio_path)
        text = result["text"]

        # Translate
        khmer_text = GoogleTranslator(
            source="auto",
            target="km"
        ).translate(text)

        # Voice output
        tts = gTTS(text=khmer_text, lang="en")
        tts.save(voice_path)

        # cleanup
        if os.path.exists(video_path):
            os.remove(video_path)
        if os.path.exists(audio_path):
            os.remove(audio_path)

        return jsonify({
            "text": text,
            "khmer": khmer_text,
            "audio_url": f"/audio/{file_id}"
        })

    except Exception as e:
        return jsonify({"error": str(e)})


@app.route("/audio/<file_id>")
def audio(file_id):
    path = os.path.join(UPLOAD_FOLDER, f"{file_id}.mp3")
    return send_file(path)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
