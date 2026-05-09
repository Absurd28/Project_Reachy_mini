import time
import requests
import numpy as np
from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose

# --- Constants for Reachy Mini ---
DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 8000
MIN_Z = 0   # Retracted height (mm)
MAX_Z = 35  # Fully emerged height (mm)
NEUTRAL_Z = 30 # Default viewing height (mm)

def check_daemon_running(host=DEFAULT_HOST, port=DEFAULT_PORT):
    """Checks if the reachy-mini-daemon is alive via its REST API."""
    url = f"http://{host}:{port}/"
    try:
        response = requests.get(url, timeout=2)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def move_head(mini, roll=0, pitch=0, yaw=0, z=NEUTRAL_Z, duration=1.5):
    """
    Moves the 6-DOF head using Orbita3D neck kinematics.
    roll, pitch, yaw are in degrees.
    z is height in mm (0 to 35).
    """
    target_pose = create_head_pose(
        roll=roll, 
        pitch=pitch, 
        yaw=yaw, 
        z=z, 
        degrees=True, 
        mm=True
    )
    mini.goto_target(head=target_pose, duration=duration)
    # Note: we don't sleep here to allow for non-blocking command chaining if needed, 
    # but the duration parameter handles interpolation.

def hide_in_shell(mini):
    """Retracts the neck and aligns the head to hide inside the body opening."""
    print("Action: Retracting into shell...")
    # Align RPY to 0 and drop Z to minimum
    move_head(mini, roll=0, pitch=0, yaw=0, z=MIN_Z, duration=1.2)
    time.sleep(1.2)

def emerge_from_shell(mini):
    """Raises the neck to its default viewing height."""
    print("Action: Emerging from shell...")
    move_head(mini, roll=0, pitch=0, yaw=0, z=NEUTRAL_Z, duration=1.5)
    time.sleep(1.5)

def run_animation_sequence():
    # 1. Pre-flight check: Ensure daemon is reachable
    print(f"Checking daemon status at {DEFAULT_HOST}:{DEFAULT_PORT}...")
    if not check_daemon_running():
        print("ERROR: reachy-mini-daemon is not running!")
        print("Please run: reachy-mini-daemon --sim --scene minimal --no-media")
        return

    try:
        # 2. Connect to the robot
        with ReachyMini(host=DEFAULT_HOST, port=DEFAULT_PORT, media_backend='no_media') as mini:
            print("Connected. Starting animation loop. Press Ctrl+C to stop.")
            
            # Start in retracted state
            hide_in_shell(mini)
            
            while True:
                # a. Emerge from the shell
                emerge_from_shell(mini)
                
                # b. Scan the room (Smoothly varying pitch and yaw)
                print("Action: Scanning the room...")
                move_head(mini, yaw=30, pitch=-10, z=NEUTRAL_Z, duration=2.0)
                time.sleep(2.0)
                move_head(mini, yaw=-30, pitch=10, z=NEUTRAL_Z, duration=2.0)
                time.sleep(2.0)
                
                # c. Tilt head curiously (Roll)
                print("Action: Tilting head curiously...")
                move_head(mini, roll=15, pitch=0, yaw=0, z=NEUTRAL_Z, duration=1.0)
                time.sleep(1.0)
                move_head(mini, roll=-15, pitch=0, yaw=0, z=NEUTRAL_Z, duration=1.0)
                time.sleep(1.0)
                
                # Return to neutral for a second
                move_head(mini, roll=0, pitch=0, yaw=0, z=NEUTRAL_Z, duration=1.0)
                time.sleep(1.0)

                # d. Quickly retract back into the shell
                print("Action: Quick retraction!")
                move_head(mini, roll=0, pitch=0, yaw=0, z=MIN_Z, duration=0.6) # Faster duration
                time.sleep(2.0) # Stay hidden for 2 seconds

    except KeyboardInterrupt:
        print("\nAnimation stopped by user.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    run_animation_sequence()
