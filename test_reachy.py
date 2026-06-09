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
NEUTRAL_Z = 25 # Increased from 20 to provide better clearance for extreme tilts

# Control Constants (P-Controller) - Tightened for safety
KP = 12.0  # Slightly reduced for more conservative tracking
YAW_LIMIT = 35 # Reduced from 45
PITCH_LIMIT = 20 # Reduced from 30

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
    """Phase 4: Real-Time Proportional Head Tracking."""
    print(f"Checking daemon status at {DEFAULT_HOST}:{DEFAULT_PORT}...")
    if not check_daemon_running():
        print("ERROR: reachy-mini-daemon is not running!")
        return

    tracker = WebcamTracker()
    
    try:
        with ReachyMini(host=DEFAULT_HOST, port=DEFAULT_PORT, media_backend='no_media') as mini:
            print("Healthcare Monitoring System Initialized. Real-time P-Control active.")
            move_head(mini, z=NEUTRAL_Z, duration=1.0)
            
            last_alert_time = 0
            curr_yaw, curr_pitch = 0.0, 0.0
            
            for frame, state, dist, alert, error in tracker.stream_vision_telemetry():
                error_x, error_y = error
                
                if alert == "BREACH":
                    speak("Critical Alert! Patient has disappeared.")
                    move_head(mini, roll=0, pitch=20, yaw=0, z=MIN_Z, duration=0.5)
                    curr_yaw, curr_pitch = 0.0, 0.0 # Reset targets
                
                elif alert == "RECOVERY":
                    speak("Patient detected. Resuming monitoring.")
                    move_head(mini, roll=0, pitch=0, yaw=0, z=NEUTRAL_Z, duration=1.0)
                
                elif alert == "WARNING":
                    if time.time() - last_alert_time > 5:
                        speak("Warning, patient is leaving the designated area.")
                        last_alert_time = time.time()
                
                # P-Controller Logic (Only during SAFE/WARNING and when patient is visible)
                if not tracker.is_breached and state != "NO_PATIENT":
                    # Update targets based on error and Kp
                    target_yaw = curr_yaw - (error_x * KP)
                    target_pitch = curr_pitch + (error_y * KP)
                    
                    # Clamp to safety limits
                    curr_yaw = np.clip(target_yaw, -YAW_LIMIT, YAW_LIMIT)
                    curr_pitch = np.clip(target_pitch, -PITCH_LIMIT, PITCH_LIMIT)
                    
                    print(f"[CONTROL] Err: ({error_x:.2f}, {error_y:.2f}) | Target RPY: (0, {curr_pitch:.1f}, {curr_yaw:.1f})")
                    
                    # Command head movement (non-blocking)
                    # Use small duration for smooth continuous tracking
                    move_head(mini, roll=0, pitch=curr_pitch, yaw=curr_yaw, z=NEUTRAL_Z, duration=0.1)

            print("Vision sequence terminated.")

    except KeyboardInterrupt:
        print("\nMonitoring stopped by user.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    run_vision_monitoring()
