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
    with text_to_speech_lock:  # التأكد من استخدام pyttsx3 بخيط واحد فقط في كل مرة
        try:
            print(f"Speaking: {text}")
            engine = pyttsx3.init()  # إعادة تهيئة المحرك لهذه المكالمة
            engine.say(text)
            engine.runAndWait()
            engine.stop()  # تنظيف الموارد
        except Exception as e:
            print(f"Error in text_to_speech: {e}")

# تهيئة نموذج Vosk
model = vosk.Model(r"D:\PRO\vosk-model-small-en-us-0.15\vosk-model-small-en-us-0.15")

def speech_to_text():
    print("Please speak something...")
    fs = 16000  # تردد العينة
    duration = 5  # مدة التسجيل بالثواني
    print(f"Recording for {duration} seconds...")
    
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()  # انتظار انتهاء التسجيل
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_wav:
        temp_filename = temp_wav.name
        with wave.open(temp_filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 2 بايت لكل عينة
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
            os.remove(temp_filename)  # حذف الملف المؤقت
            print(f"Temporary file {temp_filename} deleted.")
        except Exception as e:
            print(f"Failed to delete file: {e}")
            return None

        if 'result' in locals():  # إذا كان هناك نتيجة
            return result
        else:
            print("Could not recognize the speech.")
            return None