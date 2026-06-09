import requests
import json
import threading
from datetime import datetime
import pyttsx3

class AlertDispatcher:
    """
    Handles non-blocking caregiver notifications via local FastAPI backend.
    Includes a fail-safe local TTS alert if network fails.
    """
    def __init__(self, webhook_url="http://127.0.0.1:8000/api/alerts"):
        self.webhook_url = webhook_url
        self.robot_id = "Reachy-Unit-01"
        self._tts_engine = pyttsx3.init()

    def _post_request(self, payload):
        try:
            # Simulation of network delay/request
            response = requests.post(self.webhook_url, json=payload, timeout=5)
            response.raise_for_status()
            print(f"[NETWORK] Caregiver alert dispatched successfully: {payload['event_type']}")
        except Exception as e:
            print(f"[OFFLINE] Network failure: {e}")
            # Local fallback alert
            self._tts_engine.say("Network disconnected. Engaging local alarm.")
            self._tts_engine.runAndWait()

    def send_caregiver_alert(self, event_type, severity, message):
        """Dispatches an alert in a background thread to prevent blocking the vision loop."""
        payload = {
            "timestamp": datetime.now().isoformat(),
            "robot_id": self.robot_id,
            "event_type": event_type,
            "severity": severity,
            "message": message
        }
        
        print(f"[DISPATCHER] Preparing {severity} alert: {event_type}")
        thread = threading.Thread(target=self._post_request, args=(payload,))
        thread.daemon = True
        thread.start()

if __name__ == "__main__":
    # Test script
    dispatcher = AlertDispatcher()
    dispatcher.send_caregiver_alert("TEST_EVENT", "WARNING", "System test sequence initiated.")
    import time
    time.sleep(2)
