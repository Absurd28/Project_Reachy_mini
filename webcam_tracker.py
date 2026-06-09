import cv2
import mediapipe as mp
import numpy as np
import time
import math
import requests
import threading
from network_alerts import AlertDispatcher

class WebcamTracker:
    def __init__(self, warning_shoulder_width=0.15, breach_shoulder_width=0.08):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.mp_draw = mp.solutions.drawing_utils
        self.dispatcher = AlertDispatcher()
        
        self.warning_shoulder_width = warning_shoulder_width
        self.breach_shoulder_width = breach_shoulder_width
        self.last_detection_time = time.time()
        self.disappearance_limit = 3.0 # seconds
        self.is_breached = False
        
        # Telemetry Throttling
        self.last_push_time = 0
        self.push_interval = 0.1 # 100ms (10 FPS for telemetry)

    def _push_to_backend(self, payload):
        """Internal threaded POST to avoid blocking OpenCV."""
        try:
            # Use the standardized internal telemetry endpoint on port 8001
            requests.post("http://127.0.0.1:8001/api/internal/telemetry", json=payload, timeout=0.1)
        except Exception:
            pass # Silently fail to maintain vision loop stability

    def push_telemetry(self, x_val, y_val, current_posture, current_dist):
        """Throttled non-blocking telemetry dispatch (approx 10 FPS)."""
        now = time.time()
        if now - self.last_push_time > 0.1: # 100ms throttle
            payload = {
                'x': float(x_val), 
                'y': float(y_val), 
                'posture': str(current_posture), 
                'distance': float(current_dist)
            }
            # Dispatch in background thread to prevent camera stutter
            threading.Thread(target=self._push_to_backend, args=(payload,), daemon=True).start()
            self.last_push_time = now

    def analyze_pose(self, landmarks):
        try:
            shoulder_y = (landmarks[11].y + landmarks[12].y) / 2
            hip_y = (landmarks[23].y + landmarks[24].y) / 2
            knee_y = (landmarks[25].y + landmarks[26].y) / 2
            ankle_y = (landmarks[27].y + landmarks[28].y) / 2
            
            if abs(shoulder_y - ankle_y) < 0.2:
                return "SLEEPING", (255, 255, 0) # Cyan
            if abs(hip_y - knee_y) < 0.15 and shoulder_y < hip_y:
                return "SITTING", (0, 165, 255) # Orange
            return "STANDING", (0, 255, 0) # Green
        except Exception:
            return "UNKNOWN", (255, 255, 255)

    def get_distance_heuristic(self, landmarks):
        left_shoulder = landmarks[11]
        right_shoulder = landmarks[12]
        width = np.sqrt((left_shoulder.x - right_shoulder.x)**2 + (left_shoulder.y - right_shoulder.y)**2)
        return width

    def draw_overlay_panel(self, image, state, dist, alert):
        h, w, _ = image.shape
        overlay = image.copy()
        cv2.rectangle(overlay, (0, 0), (w, 100), (40, 40, 40), -1)
        alpha = 0.6
        cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0, image)
        
        cv2.putText(image, f"STATE: {state}", (20, 40), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)
        cv2.putText(image, f"DIST HEURISTIC: {dist:.2f}", (20, 80), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)
        
        if alert == "WARNING":
            if int(time.time() * 4) % 2 == 0:
                cv2.putText(image, "APPROACHING EXIT", (w//2 - 100, 60), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 255), 2)

    def draw_pulsing_border(self, image):
        h, w, _ = image.shape
        pulse = (math.sin(time.time() * 10) + 1) / 2
        thickness = int(10 * pulse) + 2
        cv2.rectangle(image, (0, 0), (w, h), (0, 0, 255), thickness)

    def draw_critical_breach(self, image):
        h, w, _ = image.shape
        overlay = image.copy()
        cv2.rectangle(overlay, (0, 0), (w, h), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.5, image, 0.5, 0, image)
        cv2.putText(image, "ALERT: PATIENT LOST", (w//2 - 200, h//2), cv2.FONT_HERSHEY_DUPLEX, 1.2, (0, 0, 255), 2)
        cv2.putText(image, "WAITING FOR RE-DETECTION...", (w//2 - 180, h//2 + 50), cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), 1)

    def stream_vision_telemetry(self):
        cap = cv2.VideoCapture(0)
        print("Initializing Camera hardware...")
        time.sleep(2.0) # Warmup delay
        
        self.last_detection_time = time.time()
        self.is_breached = False

        while cap.isOpened():
            success, image = cap.read()
            if not success: continue

            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = self.pose.process(image_rgb)
            
            state, skeleton_color = "NO_PATIENT", (255, 255, 255)
            dist_val = 0.0
            error_x, error_y = 0.0, 0.0
            alert_trigger = None

            if results.pose_landmarks:
                if self.is_breached:
                    alert_trigger = "RECOVERY"
                    self.is_breached = False
                
                self.last_detection_time = time.time()
                landmarks = results.pose_landmarks.landmark
                
                # Tracking point: Midpoint between shoulders for stability
                track_point_x = (landmarks[11].x + landmarks[12].x) / 2
                track_point_y = (landmarks[11].y + landmarks[12].y) / 2
                error_x = track_point_x - 0.5
                error_y = track_point_y - 0.5

                state, skeleton_color = self.analyze_pose(landmarks)
                dist_val = self.get_distance_heuristic(landmarks)
                
                if dist_val < self.breach_shoulder_width:
                    alert_trigger = "BREACH"
                    self.is_breached = True
                elif dist_val < self.warning_shoulder_width:
                    alert_trigger = "WARNING"
                
                custom_style = self.mp_draw.DrawingSpec(color=skeleton_color, thickness=2, circle_radius=2)
                self.mp_draw.draw_landmarks(image, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS, 
                                            landmark_drawing_spec=custom_style, connection_drawing_spec=custom_style)
            else:
                missing_duration = time.time() - self.last_detection_time
                if missing_duration > self.disappearance_limit:
                    if not self.is_breached:
                        alert_trigger = "BREACH"
                        self.is_breached = True
                        # Dispatch Network Alert (Non-blocking)
                        self.dispatcher.send_caregiver_alert(
                            event_type="EXIT_BREACH",
                            severity="CRITICAL",
                            message="Patient has left the tracking zone or disappeared."
                        )
                    state = "EXIT_BREACH"
                else:
                    state = f"SEARCHING ({self.disappearance_limit - missing_duration:.1f}s)"

            self.draw_overlay_panel(image, state, dist_val, alert_trigger)
            
            if alert_trigger == "WARNING":
                self.draw_pulsing_border(image)
            
            if self.is_breached or state == "EXIT_BREACH":
                self.draw_critical_breach(image)

            # --- NEW: PUSH TELEMETRY TO DASHBOARD ---
            self.push_telemetry(error_x, error_y, state, dist_val)

            yield image, state, dist_val, alert_trigger, (error_x, error_y)

            cv2.imshow('Reachy Mini Healthcare Vision', image)
            if cv2.waitKey(5) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
