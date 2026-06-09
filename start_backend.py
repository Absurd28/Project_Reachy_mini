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

def launch_backend():
    """Launches the FastAPI backend using uvicorn."""
    print("[*] Launching Reachy Mini Communication Center...")
    cmd = [
        "uvicorn", 
        "backend_server.app:app", 
        "--host", "0.0.0.0", 
        "--port", "8000", 
        "--reload"
    ]
    
    try:
        # Use subprocess.run to maintain console output
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n[!] Backend shutdown by user.")
    except Exception as e:
        print(f"[ERROR] Failed to launch backend: {e}")

if __name__ == "__main__":
    # Ensure we are in the project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # 1. Clear Port 8000
    kill_process_on_port(8000)
    
    # 2. Brief wait for OS to release socket
    time.sleep(1)
    
    # 3. Launch Server
    launch_backend()
