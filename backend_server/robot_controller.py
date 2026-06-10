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
        self.neutral_z = 25.0 # mm
        self.min_z = 0.0      # mm
        
        # Internal state to track current manual targets
        self.current_state = {
            "roll": 0.0,
            "pitch": 0.0,
            "yaw": 0.0,
            "z": self.neutral_z,
            "antennas": [0.0, 0.0] # Radians
        }
        
        self.last_move_time = 0
        self._move_lock = threading.Lock()
        
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
        """Internal helper for safe movement. If duration is 0, uses immediate set_target."""
        if not self.is_connected or not self.reachy:
            return

        target_z = z if z is not None else self.neutral_z
        try:
            # Reachy Mini coordinate system: X-forward, Y-left, Z-up
            # Head translation is on the Z axis.
            pose = create_head_pose(x=0, y=0, z=target_z, roll=roll, pitch=pitch, yaw=yaw, degrees=True, mm=True)
            
            if duration <= 0.05:
                # Use immediate, non-blocking target setting for tracking
                self.reachy.set_target(head=pose, antennas=antennas)
            else:
                # Use interpolated task-space movement for macros
                self.reachy.goto_target(head=pose, antennas=antennas, duration=duration, method=method)
        except Exception as e:
            print(f"[!] Kinematic Error: {e}")

    def move_joint(self, joint_name, value):
        """
        Updates the target state and commands immediate movement.
        """
        if not self.is_connected: return

        # Update internal state
        if joint_name == "neck_roll":
            self.current_state["roll"] = float(value)
        elif joint_name == "neck_pitch":
            self.current_state["pitch"] = float(value)
        elif joint_name == "neck_yaw":
            self.current_state["yaw"] = float(value)
        elif joint_name == "neck_height":
            self.current_state["z"] = float(value)
        elif joint_name == "l_antenna":
            self.current_state["antennas"][1] = np.deg2rad(float(value))
        elif joint_name == "r_antenna":
            self.current_state["antennas"][0] = np.deg2rad(float(value))
        
        # Throttling to 40Hz to prevent network saturation, but using non-blocking set_target
        now = time.time()
        if now - self.last_move_time < 0.025:
            return
        
        with self._move_lock:
            self.last_move_time = now
            # Use duration=0 for real-time tracking (uses set_target)
            self._safe_goto(
                roll=self.current_state["roll"],
                pitch=self.current_state["pitch"],
                yaw=self.current_state["yaw"],
                z=self.current_state["z"],
                antennas=self.current_state["antennas"],
                duration=0
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
        self.sync_state_from_macro(0, 0, 0, self.neutral_z, [0, 0])
        self._safe_goto(roll=0, pitch=0, yaw=0, z=self.neutral_z, antennas=[0, 0], duration=1.5)

    def cmd_hide(self):
        print("[CONTROL] Executing: HIDE")
        self.sync_state_from_macro(0, 0, 0, self.min_z, [-0.5, -0.5])
        self._safe_goto(roll=0, pitch=0, yaw=0, z=self.min_z, antennas=[-0.5, -0.5], duration=1.5)

    def cmd_curious(self):
        print("[CONTROL] Executing: CURIOUS")
        self.sync_state_from_macro(15, -5, 0, self.neutral_z, [0.7, -0.3])
        self._safe_goto(roll=15, pitch=-5, yaw=0, z=self.neutral_z, antennas=[0.7, -0.3], duration=1.2)
        time.sleep(1.2)
        self.sync_state_from_macro(0, 0, 0, self.neutral_z, [0, 0])
        self._safe_goto(roll=0, pitch=0, yaw=0, duration=1.0)

    def cmd_scan(self):
        print("[CONTROL] Executing: SCAN")
        self._safe_goto(yaw=30, duration=1.2)
        time.sleep(1.3)
        self._safe_goto(yaw=-30, duration=2.0)
        time.sleep(2.1)
        self.sync_state_from_macro(0, 0, 0, self.neutral_z, [0, 0])
        self._safe_goto(yaw=0, duration=1.2)

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
        
        if func:
            func()
        else:
            print(f"[?] Unknown macro requested: {action_key}")
