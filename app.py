from flask import Flask, render_template, jsonify, request
import speech_recognition as sr
import threading
import openai
from deep_translator import GoogleTranslator
from gtts import gTTS
from io import BytesIO
import os

app = Flask(__name__)

# Configure OpenAI API Key
openai.api_key = "YOUR_OPENAI_API_KEY"

# Initialize recognizer and microphone
recognizer = sr.Recognizer()
microphone = sr.Microphone()

# Global variables
listening = False
recognized_text = ""
audio_filename = "translated_audio.mp3"

# Function to recognize speech and update transcription
def listen_for_speech():
    global recognized_text, listening
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        while listening:
            try:
                print("Listening...")
                audio = recognizer.listen(source)
                recognized_text = recognizer.recognize_google(audio)
                print(f"Recognized: {recognized_text}")
            except sr.UnknownValueError:
                print("Could not understand audio.")
            except sr.RequestError:
                print("API unavailable.")
            except Exception as e:
                print(f"Error: {str(e)}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_listening', methods=['POST'])
def start_listening():
    global listening, recognized_text
    if not listening:
        listening = True
        recognized_text = ""  # Clear previous transcription
        threading.Thread(target=listen_for_speech, daemon=True).start()
        return jsonify({"status": "Listening started"})
    return jsonify({"status": "Already listening"})

@app.route('/stop_listening', methods=['POST'])
def stop_listening():
    global listening
    listening = False
    return jsonify({"status": "Listening stopped"})

@app.route('/transcribe', methods=['GET'])
def transcribe():
    # Return the most recent transcription
    return jsonify({"transcript": recognized_text})

@app.route('/translate', methods=['POST'])
def translate():
    data = request.get_json()
    text = data.get('text')
    # Set target language to Spanish ('es')
    target_language = 'es'  # Spanish
    translated_text = GoogleTranslator(source='auto', target=target_language).translate(text)
    return jsonify({"translated_text": translated_text})

@app.route('/speak', methods=['POST'])
def speak():
    global audio_filename
    data = request.get_json()
    text = data.get("text")
    tts = gTTS(text=text, lang="es")  # Set language to Spanish
    tts.save(audio_filename)
    
    # Ensure the path to the audio file is correct
    audio_url = os.path.join('static', audio_filename)  # save in the 'static' folder
    
    # Return the URL for the audio file
    return jsonify({"audio_url": audio_url})

if __name__ == '__main__':
    app.run(debug=True)
