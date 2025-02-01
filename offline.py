import vosk
import pyttsx3
import sounddevice as sd
import numpy as np
import tempfile
import os
import wave
import threading
text_to_speech_lock = threading.Lock()

def text_to_speech(text):
    with text_to_speech_lock:  # Ensure only one thread uses pyttsx3 at a time
        try:
            print(f"Speaking: {text}")
            engine = pyttsx3.init()  # Reinitialize the engine for this call
            engine.say(text)
            engine.runAndWait()
            engine.stop()  # Clean up resources
        except Exception as e:
            print(f"Error in text_to_speech: {e}")

# Initialize the Vosk model
model = vosk.Model(r"D:\PRO\vosk-model-small-en-us-0.15\vosk-model-small-en-us-0.15")

# Function to convert speech to text
def speech_to_text():
    print("Please speak something...")
    fs = 16000  
    duration = 5  
    print(f"Recording for {duration} seconds...")
    
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()  
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_wav:
        temp_filename = temp_wav.name
        with wave.open(temp_filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  
            wf.setframerate(fs)
            wf.writeframes(audio.tobytes())

        print("Recognizing...")
        rec = vosk.KaldiRecognizer(model, fs)
        with wave.open(temp_filename, "rb") as wf:
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if rec.AcceptWaveform(data):
                    result = rec.Result()
                    print(f"You said: {result}")
                    break  
        try:
            os.remove(temp_filename)  
            print(f"Temporary file {temp_filename} deleted.")
        except Exception as e:
            print(f"Failed to delete file: {e}")
            return None

        if 'result' in locals():  
            return result
        else:
            print("Could not recognize the speech.")
            return None
        
        