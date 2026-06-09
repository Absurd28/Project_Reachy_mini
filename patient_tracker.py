import time
import random
import math

class PatientTracker:
    """
    Simulates a 2D spatial coordinate system for patient monitoring.
    States: SAFE, WARNING, EXIT_BREACH
    """
    def __init__(self, bed_center=(0.0, 0.0), warning_threshold=3.5, breach_threshold=4.5):
        self.bed_x, self.bed_y = bed_center
        self.warning_threshold = warning_threshold
        self.breach_threshold = breach_threshold
        self.current_state = 'SAFE'
        self.current_pos = (0.0, 0.0)

    def calculate_state(self, x, y):
        distance = math.sqrt((x - self.bed_x)**2 + (y - self.bed_y)**2)
        if distance >= self.breach_threshold:
            state = 'EXIT_BREACH'
        elif distance >= self.warning_threshold:
            state = 'WARNING'
        else:
            state = 'SAFE'
        return state, distance

    def stream_mock_telemetry(self):
        """
        Generator for realistic human movement patterns:
        1. Resting (minor noise)
        2. Walking (progressive movement)
        3. Distress (freeze/stop)
        """
        # Phase 1: Resting (10 steps)
        for _ in range(10):
            x = self.bed_x + random.uniform(-0.2, 0.2)
            y = self.bed_y + random.uniform(-0.2, 0.2)
            yield x, y
            time.sleep(0.5)

        # Phase 2: Walking toward door (coordinates increasing)
        curr_x, curr_y = self.bed_x, self.bed_y
        for i in range(20):
            curr_x += 0.3
            curr_y += 0.15
            yield curr_x, curr_y
            time.sleep(0.5)

        # Phase 3: Distress / Breach (freeze at breach location)
        final_x, final_y = curr_x, curr_y
        for _ in range(10):
            yield final_x, final_y
            time.sleep(0.5)

def get_tracking_angles(target_x, target_y):
    """
    Computes basic proportional angles for Reachy's head to 'look at' the target.
    Simplification: Map X to Yaw and Y to Pitch.
    """
    # Simple heuristic: 1 meter offset ~ 10 degrees
    yaw = math.degrees(math.atan2(target_x, 5.0))  # Assume robot is 5m away
    pitch = math.degrees(math.atan2(target_y, 5.0))
    return yaw, pitch
