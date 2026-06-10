import psutil
import subprocess
import os
import sys
import time

def kill_process_on_port(port):
    """Identifies and terminates any process listening on the specified port."""
    print(f"[*] Auditing port {port} for zombie processes...")
    found = False
    for conn in psutil.net_connections(kind='inet'):
        if conn.laddr.port == port:
            try:
                proc = psutil.Process(conn.pid)
                print(f"[!] Found zombie process: {proc.name()} (PID: {conn.pid}) on port {port}")
                print(f"[*] Terminating PID {conn.pid}...")
                proc.terminate()
                proc.wait(timeout=3)
                print(f"[+] Successfully cleared port {port}.")
                found = True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired) as e:
                print(f"[ERROR] Could not terminate process {conn.pid}: {e}")
    
    if not found:
        print(f"[+] Port {port} is clear.")

def launch_service(name, cmd):
    """Launches a service as a background process."""
    print(f"[*] Launching {name}...")
    try:
        # Use subprocess.Popen for background execution
        process = subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
        return process
    except Exception as e:
        print(f"[ERROR] Failed to launch {name}: {e}")
        return None

if __name__ == "__main__":
    # Ensure we are in the project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # 1. Clear Port 8001
    kill_process_on_port(8001)
    time.sleep(1)
    
    # 2. Unified Startup Sequence
    services = []
    
    # A. FastAPI Backend
    services.append(launch_service("FastAPI Backend", [
        "uvicorn", "backend_server.app:app", "--host", "0.0.0.0", "--port", "8001"
    ]))
    
    # B. OpenCV Vision Loop (Webcam Tracker)
    services.append(launch_service("OpenCV Vision Loop", [
        sys.executable, "webcam_tracker.py"
    ]))
    
    # C. Voice Distress Monitor
    services.append(launch_service("Voice Distress Monitor", [
        sys.executable, "voice_monitor.py"
    ]))
    
    print("\n[+] FULL SYSTEM BOOT COMPLETED.")
    print("[*] All services are running in separate consoles.")
    print("[*] Press Ctrl+C in this window to exit (Note: Child processes must be closed manually).")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[!] Manager shutdown by user.")
