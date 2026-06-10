import time
import threading
import numpy as np
from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose

class RobotController:
    """
    Hardware Execution Layer: Bridges high-level macros to the ReachyMini SDK.
    Uses a singleton-like pattern to manage the persistent connection to the daemon.
    """
    def __init__(self, host="127.0.0.1", port=8000):
        self.host = host
        self.port = port
        self.reachy = None
        self.is_connected = False
        self.neutral_z = 20.0 # Optimized Neutral Z from PROJECT_SUMMARY.md
        self.min_z = -40.0   # Defined as -0.04m in instructions
        
    def connect(self):
        try:
            print(f"[*] Connecting to Reachy Mini SDK at {self.host}:{self.port}...")
            # Initialize ReachyMini with the correct parameters
            self.reachy = ReachyMini(host=self.host, port=self.port, media_backend='no_media')
            
            # Implementation of Rule 1: Startup stiffening
            self.reachy.turn_on("head")
            self.reachy.turn_on("antennas")
            self.is_connected = True
            print("[+] Robot Hardware Layer: ONLINE & STIFF")
        except Exception as e:
            print(f"[!] Hardware Connection Failed: {e}")
            self.is_connected = False

    def disconnect(self):
        if self.reachy:
            try:
                self.reachy.turn_off("head")
                self.reachy.turn_off("antennas")
                print("[*] Robot Hardware Layer: RELEASED (COMPLIANT)")
            except:
                pass

    def _safe_goto(self, roll=0, pitch=0, yaw=0, z=None, antennas=[0, 0], duration=1.5):
        """Internal helper for safe, interpolated movement."""
        if not self.is_connected or not self.reachy:
            print("[!] Command ignored: Robot not connected.")
            return

        target_z = z if z is not None else self.neutral_z
        try:
            # Using official 'create_head_pose' and 'goto_target'
            pose = create_head_pose(roll=roll, pitch=pitch, yaw=yaw, z=target_z, degrees=True, mm=True)
            self.reachy.goto_target(head=pose, antennas=antennas, duration=duration)
        except Exception as e:
            print(f"[!] Kinematic Error: {e}")

    # --- Macro Sequences (Rule 2) ---

    def cmd_wake_up(self):
        """Move head pitch/roll/yaw to 0, Z-translation to default height, antennas straight up."""
        print("[CONTROL] Executing: WAKE_UP")
        self._safe_goto(roll=0, pitch=0, yaw=0, z=self.neutral_z, antennas=[0, 0], duration=2.0)

    def cmd_hide(self):
        """Set Z-translation to minimum (e.g., -40mm), pitch/roll/yaw to 0, antennas flat."""
        print("[CONTROL] Executing: HIDE")
        self._safe_goto(roll=0, pitch=0, yaw=0, z=self.min_z, antennas=[-0.5, -0.5], duration=2.0)

    def cmd_curious(self):
        """Set a slight head roll (e.g., 15 degrees) and raise one antenna while lowering the other."""
        print("[CONTROL] Executing: CURIOUS")
        self._safe_goto(roll=15, pitch=-5, yaw=0, z=self.neutral_z, antennas=[0.7, -0.3], duration=1.5)
        time.sleep(1.5)
        self._safe_goto(roll=0, pitch=0, yaw=0, duration=1.5)

    def cmd_scan(self):
        """Sequence a slow pan left (yaw 30), then right (yaw -30), then center."""
        print("[CONTROL] Executing: SCAN")
        # Pan Left
        self._safe_goto(yaw=30, duration=1.5)
        time.sleep(1.6)
        # Pan Right
        self._safe_goto(yaw=-30, duration=2.5)
        time.sleep(2.6)
        # Center
        self._safe_goto(yaw=0, duration=1.5)

    def cmd_stiff(self):
        if self.reachy: self.reachy.turn_on("head"); self.reachy.turn_on("antennas")
        print("[CONTROL] Motors: STIFF")

    def cmd_compliant(self):
        if self.reachy: self.reachy.turn_off("head"); self.reachy.turn_off("antennas")
        print("[CONTROL] Motors: COMPLIANT")

    def handle_macro(self, action_key):
        """Mapper for string-based commands from the dashboard."""
        action_map = {
            "wake_up": self.cmd_wake_up,
            "hide": self.cmd_hide,
            "curious": self.cmd_curious,
            "scan": self.cmd_scan,
            "STIFF": self.cmd_stiff,
            "COMPLIANT": self.cmd_compliant,
            "E-STOP": self.cmd_compliant
        }
        
        # Compatibility mapping for existing frontend keys
        compat_map = {
            "emerge_wakeup": "wake_up",
            "retract_hide": "hide",
            "force_hide": "hide",
            "trigger_wakeup": "wake_up",
            "curious_tilt": "curious",
            "scan_room": "scan"
        }
        
        target_key = compat_map.get(action_key, action_key)
        func = action_map.get(target_key)
        
        if func:
            func()
        else:
            print(f"[?] Unknown macro requested: {action_key}")
