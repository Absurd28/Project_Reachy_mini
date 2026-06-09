import cv2
import mediapipe as mp
import numpy as np
import time

class WebcamTracker:
    def __init__(self, warning_shoulder_width=0.15):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.mp_draw = mp.solutions.drawing_utils
        
        self.warning_shoulder_width = warning_shoulder_width
        self.last_detection_time = time.time()
        self.disappearance_limit = 3.0 # seconds
        
    def analyze_pose(self, landmarks):
        """
        Determines state based on landmark Y-coordinates.
        Indices: Shoulder(11,12), Hip(23,24), Knee(25,26), Ankle(27,28)
        """
        try:
            shoulder_y = (landmarks[11].y + landmarks[12].y) / 2
            hip_y = (landmarks[23].y + landmarks[24].y) / 2
            knee_y = (landmarks[25].y + landmarks[26].y) / 2
            ankle_y = (landmarks[27].y + landmarks[28].y) / 2
            
            # 1. Sleeping Check: Horizontal alignment (Head vs Ankle)
            if abs(shoulder_y - ankle_y) < 0.2:
                return "SLEEPING"
            
            # 2. Sitting Check: Vertical distance between hip and knee is small
            # but shoulders are clearly above hips
            if abs(hip_y - knee_y) < 0.15 and shoulder_y < hip_y:
                return "SITTING"
                
            # 3. Standing Check: Vertical alignment
            return "STANDING"
        except Exception:
            return "UNKNOWN"

    def get_distance_heuristic(self, landmarks):
        """Calculates distance based on shoulder pixel width."""
        left_shoulder = landmarks[11]
        right_shoulder = landmarks[12]
        # Euclidean distance in normalized coordinates
        width = np.sqrt((left_shoulder.x - right_shoulder.x)**2 + (left_shoulder.y - right_shoulder.y)**2)
        return width

    def stream_vision_telemetry(self):
        cap = cv2.VideoCapture(0)
        
        print("Vision Engine Active. Press 'q' in the window to quit.")
        
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                break

            # Convert to RGB for MediaPipe
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = self.pose.process(image_rgb)
            
            state = "NO_PATIENT"
            dist_val = 0.0
            alert_trigger = None

            if results.pose_landmarks:
                self.last_detection_time = time.time()
                landmarks = results.pose_landmarks.landmark
                
                state = self.analyze_pose(landmarks)
                dist_val = self.get_distance_heuristic(landmarks)
                
                # Check for Warning (Patient walking away)
                if dist_val < self.warning_shoulder_width:
                    alert_trigger = "WARNING"
                
                # Draw skeleton
                self.mp_draw.draw_landmarks(image, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
            else:
                # Check for Breach (Disappearance)
                if time.time() - self.last_detection_time > self.disappearance_limit:
                    state = "EXIT_BREACH"
                    alert_trigger = "BREACH"

            # Overlay Data
            cv2.putText(image, f"State: {state}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(image, f"Dist Heuristic: {dist_val:.2f}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            
            yield image, state, dist_val, alert_trigger

            cv2.imshow('Reachy Mini Healthcare Vision', image)
            if cv2.waitKey(5) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
