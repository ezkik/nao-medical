from flask import Flask, render_template, jsonify, request
from deep_translator import GoogleTranslator
import speech_recognition as sr
from gtts import gTTS
import openai
import os
from io import BytesIO
from pydub import AudioSegment
from pydub.playback import play

app = Flask(__name__)

# Configure OpenAI API Key
openai.api_key = "YOUR_OPENAI_API_KEY"

def transcribe_audio(file_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(file_path) as source:
        audio_data = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio_data)
    except sr.UnknownValueError:
        return "Could not understand audio."
    except sr.RequestError:
        return "API unavailable."

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400
    audio_file = request.files['audio']
    audio_path = "audio.wav"
    audio_file.save(audio_path)
    
    # Transcribe audio to text
    transcript = transcribe_audio(audio_path)
    
    # Enhanced transcription with OpenAI (optional for medical terminology)
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Improve the transcription for accuracy in medical terminology: {transcript}",
        max_tokens=100
    )
    enhanced_transcript = response.choices[0].text.strip()
    return jsonify({"transcript": enhanced_transcript})

@app.route('/translate', methods=['POST'])
def translate():
    data = request.get_json()
    text = data.get('text')
    target_language = data.get('target_language', 'en')
    translated_text = GoogleTranslator(source='auto', target=target_language).translate(text)
    return jsonify({"translated_text": translated_text})

@app.route('/speak', methods=['POST'])
def speak():
    data = request.get_json()
    text = data.get("text")
    tts = gTTS(text=text, lang="en")
    tts.save("translated_audio.mp3")
    audio_data = BytesIO()
    tts.write_to_fp(audio_data)
    audio_data.seek(0)
    return jsonify({"audio_url": "translated_audio.mp3"})

if __name__ == '__main__':
    app.run(debug=True)
