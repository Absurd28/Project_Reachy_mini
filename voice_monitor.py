import speech_recognition as sr
import pyttsx3
import requests
import time
import json
import threading
from datetime import datetime

# --- Configuration ---
API_ALERT_URL = "http://127.0.0.1:8001/api/alerts"
DISTRESS_KEYWORDS = ["help", "uneasy", "nurse", "pain", "cannot move", "emergency", "reachy"]

class VoiceMonitor:
    def __init__(self):
        # Initialize TTS engine
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)
        self._tts_lock = threading.Lock()
        
        # Initialize Speech Recognition
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        
        self.is_running = True

    def speak(self, text):
        """Thread-safe Text-to-Speech."""
        with self._tts_lock:
            print(f"[*] Voice Monitor: {text}")
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()

    def trigger_alert(self, transcribed_text):
        """Sends distress alert to the FastAPI backend."""
        payload = {
            "timestamp": datetime.now().isoformat(),
            "robot_id": "REACHY_MINI_01",
            "event_type": "VOICE_DISTRESS",
            "severity": "CRITICAL",
            "message": f"Patient said: '{transcribed_text}'"
        }
        
        try:
            # Reachy acknowledges verbally
            self.speak("I heard you. Sending an emergency alert to the nurse now.")
            
            # Send alert to backend
            response = requests.post(API_ALERT_URL, json=payload, timeout=2)
            if response.status_code == 200:
                print("[+] Alert successfully dispatched to backend.")
            else:
                print(f"[!] Backend returned error: {response.status_code}")
        except Exception as e:
            print(f"[!] Failed to send alert: {e}")

    def listen_loop(self):
        """Continuous listening loop."""
        print("[*] Voice Distress Monitor: Active and listening...")
        
        with sr.Microphone() as source:
            # Calibration
            print("[*] Calibrating for ambient noise...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            while self.is_running:
                try:
                    print("[.] Listening...")
                    # Adjusting timeout/phrase_time_limit for responsiveness
                    audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=5)
                    
                    try:
                        # Use Google Speech Recognition (requires internet)
                        text = self.recognizer.recognize_google(audio).lower()
                        print(f"[USER]: {text}")
                        
                        # Check for distress keywords
                        if any(keyword in text for keyword in DISTRESS_KEYWORDS):
                            print(f"[!!!] DISTRESS DETECTED: {text}")
                            self.trigger_alert(text)
                            
                    except sr.UnknownValueError:
                        # Speech was unintelligible
                        pass
                    except sr.RequestError as e:
                        print(f"[!] API Request Error: {e}")
                        
                except sr.WaitTimeoutError:
                    # No speech detected in timeout period
                    continue
                except Exception as e:
                    print(f"[!] Listener Error: {e}")
                    time.sleep(1)

    def start(self):
        try:
            self.listen_loop()
        except KeyboardInterrupt:
            self.is_running = False
            print("[*] Voice Monitor shutting down.")

if __name__ == "__main__":
    monitor = VoiceMonitor()
    monitor.start()
