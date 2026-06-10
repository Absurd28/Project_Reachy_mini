import time
import threading
import numpy as np
from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose

class RobotController:
    """
    Hardware Execution Layer: Bridges high-level macros to the ReachyMini SDK.
    Optimized for smooth, responsive manual control and accurate kinematics.
    """
    def __init__(self, host="127.0.0.1", port=8000):
        self.host = host
        self.port = port
        self.reachy = None
        self.is_connected = False
        self.neutral_z = 20.0 # Standard Neutral
        self.min_z = 0.0      # Mechanical bottom
        
        # Internal state to track current manual targets
        self.current_state = {
            "roll": 0.0,
            "pitch": 0.0,
            "yaw": 0.0,
            "z": 20.0,
            "antennas": [0.0, 0.0] 
        }
        
        self.last_move_time = 0
        self._lock = threading.Lock()
        
    def connect(self):
        try:
            print(f"[*] Connecting to Reachy Mini SDK at {self.host}:{self.port}...")
            self.reachy = ReachyMini(host=self.host, port=self.port, media_backend='no_media')
            self.reachy.enable_motors() 
            self.is_connected = True
            print("[+] Robot Hardware Layer: ONLINE & STIFF")
        except Exception as e:
            print(f"[!] Hardware Connection Failed: {e}")
            self.is_connected = False

    def disconnect(self):
        if self.reachy:
            try:
                self.reachy.disable_motors()
                print("[*] Robot Hardware Layer: RELEASED (COMPLIANT)")
            except:
                pass

    def _safe_goto(self, roll=0, pitch=0, yaw=0, z=None, antennas=[0, 0], duration=1.0, method="minjerk"):
        """Internal helper for safe movement using verified goto_target."""
        if not self.is_connected or not self.reachy:
            return

        target_z = z if z is not None else self.current_state["z"]
        try:
            pose = create_head_pose(x=0, y=0, z=target_z, roll=roll, pitch=pitch, yaw=yaw, degrees=True, mm=True)
            self.reachy.cancel_move()
            self.reachy.goto_target(head=pose, antennas=antennas, duration=max(0.1, duration), method=method)
        except Exception as e:
            print(f"[!] Kinematic/SDK Error: {e}")

    def move_joint(self, joint_name, value):
        if not self.is_connected: return
        with self._lock:
            if joint_name == "neck_roll": self.current_state["roll"] = float(value)
            elif joint_name == "neck_pitch": self.current_state["pitch"] = float(value)
            elif joint_name == "neck_yaw": self.current_state["yaw"] = float(value)
            elif joint_name == "neck_height": self.current_state["z"] = np.clip(float(value), 0, 35)
            elif joint_name == "l_antenna": self.current_state["antennas"][1] = np.deg2rad(float(value))
            elif joint_name == "r_antenna": self.current_state["antennas"][0] = np.deg2rad(float(value))
            
            now = time.time()
            if now - self.last_move_time < 0.1: return
            self.last_move_time = now
            self._safe_goto(
                roll=self.current_state["roll"], pitch=self.current_state["pitch"], 
                yaw=self.current_state["yaw"], z=self.current_state["z"],
                antennas=self.current_state["antennas"], duration=0.2
            )

    # --- Macro Sequences ---

    def sync_state_from_macro(self, roll, pitch, yaw, z, antennas):
        self.current_state["roll"] = roll
        self.current_state["pitch"] = pitch
        self.current_state["yaw"] = yaw
        self.current_state["z"] = z
        self.current_state["antennas"] = list(antennas)

    def cmd_wake_up(self):
        print("[CONTROL] Executing: WAKE_UP")
        with self._lock:
            self.sync_state_from_macro(0, 0, 0, 20.0, [0, 0])
            self._safe_goto(roll=0, pitch=0, yaw=0, z=20.0, antennas=[0, 0], duration=1.5)

    def cmd_hide(self):
        print("[CONTROL] Executing: HIDE")
        with self._lock:
            self.sync_state_from_macro(0, 0, 0, 0.0, [-0.5, -0.5])
            self._safe_goto(roll=0, pitch=0, yaw=0, z=0.0, antennas=[-0.5, -0.5], duration=1.5)

    def cmd_curious(self):
        print("[CONTROL] Executing: CURIOUS")
        with self._lock:
            self.sync_state_from_macro(15, -5, 0, 20.0, [0.7, -0.3])
            self._safe_goto(roll=15, pitch=-5, yaw=0, z=20.0, antennas=[0.7, -0.3], duration=1.2)
        time.sleep(1.3)
        with self._lock:
            self.sync_state_from_macro(0, 0, 0, 20.0, [0, 0])
            self._safe_goto(roll=0, pitch=0, yaw=0, duration=1.0)

    def cmd_scan(self):
        print("[CONTROL] Executing: SCAN")
        with self._lock: self._safe_goto(yaw=30, duration=1.2)
        time.sleep(1.3)
        with self._lock: self._safe_goto(yaw=-30, duration=2.0)
        time.sleep(2.1)
        with self._lock:
            self.sync_state_from_macro(0, 0, 0, 20.0, [0, 0])
            self._safe_goto(yaw=0, duration=1.2)

    def cmd_nod(self):
        """Positive confirmation behavior (Nod)."""
        print("[CONTROL] Executing: NOD")
        with self._lock:
            self._safe_goto(pitch=15, duration=0.4)
            time.sleep(0.5)
            self._safe_goto(pitch=-5, duration=0.4)
            time.sleep(0.5)
            self._safe_goto(pitch=0, duration=0.4)

    def cmd_stiff(self):
        if self.reachy: self.reachy.enable_motors()
        print("[CONTROL] Motors: STIFF")

    def cmd_compliant(self):
        if self.reachy: self.reachy.disable_motors()
        print("[CONTROL] Motors: COMPLIANT")

    def handle_macro(self, action_key):
        action_map = {
            "wake_up": self.cmd_wake_up,
            "hide": self.cmd_hide,
            "curious": self.cmd_curious,
            "scan": self.cmd_scan,
            "nod": self.cmd_nod,
            "STIFF": self.cmd_stiff,
            "COMPLIANT": self.cmd_compliant,
            "E-STOP": self.cmd_compliant
        }
        
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
        if func: func()
        else: print(f"[?] Unknown macro requested: {action_key}")
