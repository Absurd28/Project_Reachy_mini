import speech_recognition as sr
import pyttsx3
import requests
import time
import json
import threading
from datetime import datetime
from nlp_parser import NLPIntentParser

# --- Configuration ---
API_ALERT_URL = "http://127.0.0.1:8001/api/alerts"
API_COMMAND_URL = "http://127.0.0.1:8001/api/commands"

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
        
        # Initialize Phase 4 NLP Parser
        self.nlp_parser = NLPIntentParser()
        
        self.is_running = True

    def speak(self, text):
        """Thread-safe Text-to-Speech."""
        with self._tts_lock:
            print(f"[*] Voice Monitor: {text}")
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()

    def send_alert(self, severity, event_type, message):
        """Helper to send alerts to backend."""
        payload = {
            "timestamp": datetime.now().isoformat(),
            "robot_id": "REACHY_MINI_01",
            "event_type": event_type,
            "severity": severity,
            "message": message
        }
        try:
            requests.post(API_ALERT_URL, json=payload, timeout=2)
        except Exception as e:
            print(f"[!] Failed to send alert: {e}")

    def send_command(self, command):
        """Helper to send robotic commands to backend."""
        try:
            requests.post(API_COMMAND_URL, json={"command": command}, timeout=2)
        except Exception as e:
            print(f"[!] Failed to send command: {e}")

    def process_speech(self, text):
        """
        Phase 4: Advanced NLP Intent Processing.
        """
        print(f"[*] Analyzing Intent: '{text}'")
        label, score = self.nlp_parser.parse_intent(text)
        print(f"[NLP] Top Intent: {label} (Confidence: {score:.2f})")

        # Threshold check
        if score < 0.5:
            print("[!] Confidence too low. Ignoring.")
            return

        if label == "medical distress":
            # Rule 4: Critical alert and TTS reassurance
            self.send_alert("CRITICAL", "VOICE_DISTRESS", f"Patient in distress: '{text}'")
            self.speak("I heard you. Sending an emergency alert to the nurse now.")
            self.send_command("curious") # Visual reaction

        elif label == "routine confirmation":
            # Rule 4: Log info alert and Nod
            self.send_alert("INFO", "ROUTINE_CONFIRM", f"Medication confirmed: '{text}'")
            self.speak("Excellent, logging that now.")
            self.send_command("nod") # Robotic nod

        elif label == "casual greeting":
            self.speak("Hello! I am Reachy, your assistant. How can I help you today?")
            self.send_command("wake_up")

    def listen_loop(self):
        print("[*] Voice Ecosystem: Active and listening...")
        with sr.Microphone() as source:
            print("[*] Calibrating...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            while self.is_running:
                try:
                    audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=5)
                    try:
                        text = self.recognizer.recognize_google(audio).lower()
                        print(f"[USER]: {text}")
                        self.process_speech(text)
                    except sr.UnknownValueError: pass
                    except sr.RequestError: print("[!] Google Speech API unreachable.")
                except sr.WaitTimeoutError: continue
                except Exception as e:
                    print(f"[!] Listener Error: {e}")
                    time.sleep(1)

    def start(self):
        try: self.listen_loop()
        except KeyboardInterrupt:
            self.is_running = False
            print("[*] Voice Monitor shutting down.")

if __name__ == "__main__":
    monitor = VoiceMonitor()
    monitor.start()
