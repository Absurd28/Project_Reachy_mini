import subprocess
import os
import sys
import time

def launch_service(name, cmd):
    """Launches a service as a background process in a new console window."""
    print(f"[*] Launching {name}...")
    try:
        # Use subprocess.Popen with NEW_CONSOLE to keep processes separate
        process = subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
        return process
    except Exception as e:
        print(f"[ERROR] Failed to launch {name}: {e}")
        return None

if __name__ == "__main__":
    # Ensure we are in the project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print("=====================================================")
    print("      REACHY MINI: MULTI-SERVICE ECOSYSTEM BOOT      ")
    print("=====================================================")
    
    # Unified Startup Sequence
    # Note: Backend is launched in a NEW console so its logs are separate from this manager
    launch_service("FastAPI Backend", [
        sys.executable, "start_backend.py"
    ])
    
    time.sleep(2) # Wait for backend port to be cleared and bound
    
    # OpenCV Vision Loop
    launch_service("OpenCV Vision Loop", [
        sys.executable, "webcam_tracker.py"
    ])
    
    # Voice Distress Monitor
    launch_service("Voice Distress Monitor", [
        sys.executable, "voice_monitor.py"
    ])
    
    print("\n[+] FULL SYSTEM BOOT COMPLETED.")
    print("[*] 1. Backend Server (Telemetry Logs)")
    print("[*] 2. Vision Tracker (Skeleton Visuals)")
    print("[*] 3. Voice Monitor (Distress Listening)")
    print("\n[*] All services are running in their own windows.")
    print("[*] You can safely close this Manager window.")
    
    time.sleep(5)
    sys.exit(0)
