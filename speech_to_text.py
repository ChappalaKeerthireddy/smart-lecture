import speech_recognition as sr

def record_audio():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Recording... Speak now.")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        print("Recording complete.")
        return audio

def transcribe_audio(audio):
    recognizer = sr.Recognizer()
    try:
        transcription = recognizer.recognize_google(audio)
        with open("transcription.txt", "w") as file:
            file.write(transcription)
        print("Transcription saved successfully.")
    except sr.UnknownValueError:
        print("Could not understand audio")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")

if __name__ == "__main__":
    audio = record_audio()
    transcribe_audio(audio)
