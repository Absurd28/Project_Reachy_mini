import cv2
import mediapipe as mp
import numpy as np
import time
import math

class WebcamTracker:
    def __init__(self, warning_shoulder_width=0.15, breach_shoulder_width=0.08):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.mp_draw = mp.solutions.drawing_utils
        
        self.warning_shoulder_width = warning_shoulder_width
        self.breach_shoulder_width = breach_shoulder_width
        self.last_detection_time = time.time()
        self.disappearance_limit = 3.0 # seconds
        self.start_time = time.time()
        
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
        # Semi-transparent top panel
        cv2.rectangle(overlay, (0, 0), (w, 100), (40, 40, 40), -1)
        alpha = 0.6
        cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0, image)
        
        # Dashboard Text
        cv2.putText(image, f"STATE: {state}", (20, 40), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)
        cv2.putText(image, f"DIST HEURISTIC: {dist:.2f}", (20, 80), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)
        cv2.putText(image, f"LIMIT: {self.breach_shoulder_width:.2f}", (w - 220, 40), cv2.FONT_HERSHEY_DUPLEX, 0.8, (200, 200, 200), 1)
        
        if alert == "WARNING":
            # Flashing Text
            if int(time.time() * 4) % 2 == 0:
                cv2.putText(image, "APPROACHING EXIT", (w//2 - 100, 60), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 255), 2)

    def draw_pulsing_border(self, image):
        h, w, _ = image.shape
        # Sine wave pulse (0.0 to 1.0)
        pulse = (math.sin(time.time() * 10) + 1) / 2
        thickness = int(10 * pulse) + 2
        color = (0, 0, 255) # Red
        cv2.rectangle(image, (0, 0), (w, h), color, thickness)

    def draw_critical_breach(self, image):
        h, w, _ = image.shape
        # Blur the background
        image[:] = cv2.GaussianBlur(image, (25, 25), 0)
        # Darken
        overlay = image.copy()
        cv2.rectangle(overlay, (0, 0), (w, h), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.5, image, 0.5, 0, image)
        # Alert Text
        cv2.putText(image, "CRITICAL: PATIENT LOST", (w//2 - 250, h//2), cv2.FONT_HERSHEY_DUPLEX, 1.5, (0, 0, 255), 3)
        cv2.putText(image, "INITIATING EMERGENCY RETRACTION", (w//2 - 280, h//2 + 60), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)

    def stream_vision_telemetry(self):
        cap = cv2.VideoCapture(0)
        print("Advanced Vision Dashboard Active. Press 'q' to quit.")
        
        while cap.isOpened():
            success, image = cap.read()
            if not success: break

            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = self.pose.process(image_rgb)
            
            state, skeleton_color = "NO_PATIENT", (255, 255, 255)
            dist_val = 0.0
            alert_trigger = None

            if results.pose_landmarks:
                self.last_detection_time = time.time()
                landmarks = results.pose_landmarks.landmark
                state, skeleton_color = self.analyze_pose(landmarks)
                dist_val = self.get_distance_heuristic(landmarks)
                
                # Check for thresholds
                if dist_val < self.breach_shoulder_width:
                    alert_trigger = "BREACH"
                elif dist_val < self.warning_shoulder_width:
                    alert_trigger = "WARNING"
                
                # Custom Skeleton Color
                custom_style = self.mp_draw.DrawingSpec(color=skeleton_color, thickness=2, circle_radius=2)
                self.mp_draw.draw_landmarks(image, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS, 
                                            landmark_drawing_spec=custom_style, connection_drawing_spec=custom_style)
            else:
                if time.time() - self.last_detection_time > self.disappearance_limit:
                    state = "EXIT_BREACH"
                    alert_trigger = "BREACH"

            # Visual Enhancements
            self.draw_overlay_panel(image, state, dist_val, alert_trigger)
            
            if alert_trigger == "WARNING":
                self.draw_pulsing_border(image)
            
            if alert_trigger == "BREACH" or state == "EXIT_BREACH":
                self.draw_critical_breach(image)
                yield image, state, dist_val, alert_trigger
                # Show one final frame of the breach overlay before stopping the loop if necessary
                cv2.imshow('Reachy Mini Healthcare Vision', image)
                cv2.waitKey(2000) # Pause to let alert be seen
                break

            yield image, state, dist_val, alert_trigger

            cv2.imshow('Reachy Mini Healthcare Vision', image)
            if cv2.waitKey(5) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
