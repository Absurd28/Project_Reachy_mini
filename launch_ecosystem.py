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
    print("      REACHY MINI: PROACTIVE AI ECOSYSTEM BOOT       ")
    print("=====================================================")
    
    # 1. FastAPI Backend (Telemetry Logs)
    launch_service("FastAPI Backend", [sys.executable, "start_backend.py"])
    time.sleep(2) 
    
    # 2. OpenCV Vision Loop
    launch_service("OpenCV Vision Loop", [sys.executable, "webcam_tracker.py"])
    
    # 3. Voice & NLP Monitor
    launch_service("Voice & NLP Monitor", [sys.executable, "voice_monitor.py"])
    
    # 4. Proactive Routine Manager (Phase 4)
    launch_service("Routine Manager", [sys.executable, "routine_manager.py"])
    
    print("\n[+] FULL SYSTEM BOOT COMPLETED.")
    print("[*] All services are running in their own windows.")
    print("[*] Proactive medication checks scheduled every 2 minutes.")
    
    time.sleep(5)
    sys.exit(0)
