import schedule
import time
import requests
import threading

API_COMMAND_URL = "http://127.0.0.1:8001/api/commands"

def medication_check():
    """
    Proactive task: Triggers the robot to search for the patient and check medication status.
    """
    print(f"[*] [ROUTINE] Triggering medication check...")
    try:
        payload = {"command": "trigger_proactive_search"}
        response = requests.post(API_COMMAND_URL, json=payload, timeout=5)
        if response.status_code == 200:
            print("[+] Routine Task: 'trigger_proactive_search' successfully dispatched.")
        else:
            print(f"[!] Routine Task Failed: {response.status_code}")
    except Exception as e:
        print(f"[!] Routine Network Error: {e}")

def run_scheduler():
    print("[*] Proactive Routine Manager: Running...")
    
    # Schedule a medication check every 2 minutes for testing
    schedule.every(2).minutes.do(medication_check)
    
    # Initial trigger for demonstration
    medication_check()

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    run_scheduler()
