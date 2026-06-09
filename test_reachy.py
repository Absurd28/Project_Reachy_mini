import time
import requests
import numpy as np
from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose
from patient_tracker import PatientTracker, get_tracking_angles

# --- Constants for Reachy Mini ---
DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 8000
MIN_Z = 0   # Retracted height (mm)
MAX_Z = 35  # Fully emerged height (mm)
NEUTRAL_Z = 20 # Optimized safety-tuned height

def check_daemon_running(host=DEFAULT_HOST, port=DEFAULT_PORT):
    """Checks if the reachy-mini-daemon is alive via its REST API."""
    url = f"http://{host}:{port}/"
    try:
        response = requests.get(url, timeout=2)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def move_head(mini, roll=0, pitch=0, yaw=0, z=NEUTRAL_Z, duration=1.5):
    """Moves the 6-DOF head using Orbita3D neck kinematics."""
    target_pose = create_head_pose(
        roll=roll, 
        pitch=pitch, 
        yaw=yaw, 
        z=z, 
        degrees=True, 
        mm=True
    )
    mini.goto_target(head=target_pose, duration=duration)

def run_patient_monitoring():
    """Runs the Phase 1: Patient Perception & Tracking Simulation."""
    print(f"Checking daemon status at {DEFAULT_HOST}:{DEFAULT_PORT}...")
    if not check_daemon_running():
        print("ERROR: reachy-mini-daemon is not running!")
        return

    tracker = PatientTracker()
    
    try:
        with ReachyMini(host=DEFAULT_HOST, port=DEFAULT_PORT, media_backend='no_media') as mini:
            print("Healthcare Monitoring Layer Active. Tracking Patient...")
            
            # Start in neutral position
            move_head(mini, z=NEUTRAL_Z, duration=1.0)
            
            for x, y in tracker.stream_mock_telemetry():
                state, dist = tracker.calculate_state(x, y)
                yaw, pitch = get_tracking_angles(x, y)
                
                print(f"[TELEMETRY] Pos: ({x:.2f}, {y:.2f}) | Dist: {dist:.2f}m | State: {state}")
                
                if state == 'EXIT_BREACH':
                    print("!!! ALERT: BREACH DETECTED !!!")
                    # Warning Gesture: Drop antennas (if applicable in sim) and retract
                    # Since we can't directly control antennas easily in this SDK snippet, 
                    # we focus on the quick retraction alert.
                    move_head(mini, roll=0, pitch=20, yaw=0, z=MIN_Z, duration=0.5)
                    break 
                
                elif state == 'WARNING':
                    # Look at target but with slight "concern" (faster movements or slight roll)
                    move_head(mini, roll=5, pitch=pitch, yaw=yaw, z=NEUTRAL_Z, duration=0.3)
                
                else:
                    # Normal smooth tracking
                    move_head(mini, roll=0, pitch=pitch, yaw=yaw, z=NEUTRAL_Z, duration=0.5)

            print("Monitoring sequence complete.")

    except KeyboardInterrupt:
        print("\nMonitoring stopped by user.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    run_patient_monitoring()
