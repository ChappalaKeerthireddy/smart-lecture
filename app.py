import subprocess
from flask import Flask, render_template, request, jsonify
import wikipediaapi
import os
from flask_cors import CORS
from summarize import summarize_text_from_file
import speech_recognition as sr
from pydub import AudioSegment
import requests

app = Flask(__name__)
CORS(app)

wiki_wiki = wikipediaapi.Wikipedia(
    language='en',
    extract_format=wikipediaapi.ExtractFormat.WIKI,
    user_agent='SmartLecture/1.0 (https://yourwebsite.com; your_email@example.com)'
)

def get_wikipedia_link(topic):
    """Fetch Wikipedia page link for the given topic."""
    print(f"DEBUG: Searching Wikipedia for topic: {topic}")

    if not topic or len(topic) < 3:
        print("DEBUG: Invalid topic for Wikipedia search.")
        return None

    page = wiki_wiki.page(topic)

    if page.exists():
        print(f"DEBUG: Wikipedia page found: {page.fullurl}")
        return page.fullurl
    else:
        print(f"DEBUG: Wikipedia page NOT found for '{topic}'. Redirecting to search results...")
        return f"https://en.wikipedia.org/wiki/Special:Search?search={topic.replace(' ', '_')}"

def extract_topic(summary):
    """Extract a meaningful topic from the summary."""
    print("DEBUG: Extracting topic from summary.")
    
    sentences = summary.split('.')
    
    for sentence in sentences:
        words = sentence.split()
        if 2 < len(words) < 10:
            return sentence.strip()

    return ' '.join(summary.split()[:3])

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload-audio", methods=["POST"])
def upload_audio():
    try:
        if "audio" not in request.files:
            return jsonify({"error": "No audio file uploaded"}), 400

        audio_file = request.files["audio"]
        file_path = "uploaded_audio.wav"
        audio_file.save(file_path)

        # Convert audio to WAV format if needed
        audio = AudioSegment.from_file(file_path)
        audio = audio.set_frame_rate(16000).set_channels(1)
        audio.export(file_path, format="wav")

        recognizer = sr.Recognizer()
        with sr.AudioFile(file_path) as source:
            audio_data = recognizer.record(source)

            try:
                transcription = recognizer.recognize_google(audio_data)
            except sr.UnknownValueError:
                return jsonify({"error": "Speech Recognition could not understand the audio"}), 400
            except sr.RequestError as e:
                return jsonify({"error": f"Google API request failed: {e}"}), 500

        with open("transcription.txt", "w") as file:
            file.write(transcription)

        os.remove(file_path)

        return jsonify({"transcription": transcription})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/summarize", methods=["POST"])
def summarize():
    try:
        print("DEBUG: Summarization endpoint called.")

        if not os.path.exists("transcription.txt") or os.stat("transcription.txt").st_size == 0:
            print("DEBUG: Transcription file is missing or empty.")
            return jsonify({"error": "No transcription available for summarization."}), 400

        with open("transcription.txt", "r") as file:
            transcription = file.read().strip()

        if not transcription:
            print("DEBUG: Transcription is empty.")
            return jsonify({"error": "Transcription is empty. Cannot summarize."}), 400

        print("DEBUG: Transcription content:", transcription)

        summary = summarize_text_from_file("transcription.txt")

        if not summary or "Error" in summary:
            print("DEBUG: Summarization failed.")
            return jsonify({"error": "Failed to generate summary."}), 500

        print("DEBUG: Summary generated:", summary)

        topic = extract_topic(summary)
        print("DEBUG: Extracted topic:", topic)

        wiki_link = get_wikipedia_link(topic)

        if not wiki_link:
            print("DEBUG: No Wikipedia page found.")
            wiki_link = "https://en.wikipedia.org/wiki/Special:Search?search=" + topic.replace(" ", "_")

        print("DEBUG: Wikipedia link:", wiki_link)

        return jsonify({"summary": summary, "wiki_link": wiki_link})
    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
