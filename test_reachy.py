import time
import requests
import pyttsx3
import numpy as np
from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose
from webcam_tracker import WebcamTracker

# --- Constants for Reachy Mini ---
DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 8000
MIN_Z = 0   
MAX_Z = 35  
NEUTRAL_Z = 20 

# Initialize TTS
engine = pyttsx3.init()

def speak(text):
    """Vocalizes the given text using the Windows SAPI5 engine."""
    print(f"Reachy says: {text}")
    engine.say(text)
    engine.runAndWait()

def check_daemon_running(host=DEFAULT_HOST, port=DEFAULT_PORT):
    url = f"http://{host}:{port}/"
    try:
        response = requests.get(url, timeout=2)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def move_head(mini, roll=0, pitch=0, yaw=0, z=NEUTRAL_Z, duration=1.5):
    target_pose = create_head_pose(roll=roll, pitch=pitch, yaw=yaw, z=z, degrees=True, mm=True)
    mini.goto_target(head=target_pose, duration=duration)

def run_vision_monitoring():
    """Phase 3: Robust Vision Tracking with Recovery Logic."""
    print(f"Checking daemon status at {DEFAULT_HOST}:{DEFAULT_PORT}...")
    if not check_daemon_running():
        print("ERROR: reachy-mini-daemon is not running!")
        return

    tracker = WebcamTracker()
    
    try:
        with ReachyMini(host=DEFAULT_HOST, port=DEFAULT_PORT, media_backend='no_media') as mini:
            print("Healthcare Monitoring System Initialized.")
            move_head(mini, z=NEUTRAL_Z, duration=1.0)
            
            last_alert_time = 0
            
            for frame, state, dist, alert in tracker.stream_vision_telemetry():
                
                if alert == "BREACH":
                    speak("Critical Alert! Patient has disappeared from the tracking zone.")
                    move_head(mini, roll=0, pitch=20, yaw=0, z=MIN_Z, duration=0.5)
                
                elif alert == "RECOVERY":
                    speak("Patient detected. Resuming monitoring.")
                    move_head(mini, roll=0, pitch=0, yaw=0, z=NEUTRAL_Z, duration=1.0)
                
                elif alert == "WARNING":
                    if time.time() - last_alert_time > 5:
                        speak("Warning, patient is leaving the designated area.")
                        last_alert_time = time.time()
                    move_head(mini, roll=10, pitch=0, yaw=0, z=NEUTRAL_Z, duration=0.3)
                
                # Dynamic gaze (only if not currently breached)
                if not tracker.is_breached:
                    if state == "SITTING":
                        move_head(mini, pitch=10, z=NEUTRAL_Z, duration=0.8)
                    elif state == "STANDING":
                        move_head(mini, pitch=-5, z=NEUTRAL_Z, duration=0.8)
                    elif state == "SLEEPING":
                        move_head(mini, pitch=25, z=NEUTRAL_Z, duration=0.8)

            print("Vision sequence terminated.")

    except KeyboardInterrupt:
        print("\nMonitoring stopped by user.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    run_vision_monitoring()
