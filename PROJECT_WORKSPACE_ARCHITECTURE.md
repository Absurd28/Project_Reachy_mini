# PROJECT WORKSPACE ARCHITECTURE: Reachy Mini AI Assistant

This document provides a definitive architectural overview of the Reachy Mini robotics workspace, mapping its 21,000+ items into logical operational categories.

## 1. WORKSPACE TREE CONFIGURATION

The following conceptual tree illustrates the high-level organization of the project, isolating core source logic from the high-volume dependency noise.

```text
.
├── interactive_reachy.py       # Main HCI / Voice AI Engine
├── test_reachy.py              # Orchestration, Patient Monitoring & Vision Loop
├── webcam_tracker.py           # Live OpenCV/MediaPipe Pose Estimation
├── network_alerts.py           # Non-blocking Alert Dispatcher (Local Target)
├── backend_server/
│   └── app.py                  # FastAPI Edge Server (WebSockets & REST)
├── frontend_app/
│   └── index.html              # Local Caregiver Dashboard (Vanilla JS)
├── map_workspace.py            # Architectural Verification Script
├── PROJECT_SUMMARY.md          # Technical Log & Milestones
├── start_sim.sh                # Simulation Bootstrapper
│
├── venv/                       # [DEPENDENCY NOISE: ~21,000 files]
```

> **Note:** The vast majority of the 21,000+ items are housed within the `.venv/` and `.git/` directories, representing the Python runtime, simulation dependencies (MuJoCo, SDKs), and version history.

---

## 2. SOFTWARE DEVELOPMENT MODEL MAPPING

### **Paradigm: Full-Stack Robotics / Hardware-in-the-Loop (HiL)**
The project has evolved into a **Full-Stack Robotics** ecosystem. The Edge Server bridges the low-level kinematic control with a high-level, interactive web dashboard, enabling remote monitoring and teleoperation.

**Operational Responsibilities:**
- **Perception Layer:** Live Vision-Based Patient Tracking (OpenCV/MediaPipe).
- **Edge Communications:** FastAPI backend managing real-time WebSocket telemetry and incoming remote commands.
- **Remote Interface:** Interactive HTML5/JS dashboard for real-time status and control.
- **Execution Layer:** Smooth 6-DOF head tracking and safety retraction sequences.

---

## 3. CATEGORIZED FUNCTIONAL MAPPING

### Physics Simulation & Digital Twin Assets
- **Functional Role:** Handles rigid-body dynamics, joint limits, and environmental scene configuration.
- **Associated Sub-Categories & File Paths:**
    * *Simulation Meshes:* `venv/Lib/site-packages/reachy_mini/assets/` (STL/XML meshes).
    * *Robot Descriptions:* `venv/Lib/site-packages/reachy_mini/descriptions/` (URDF/MJCF configs).

### Kinematics & Full-Stack Communications
- **Functional Role:** Manages joint transformations and the bidirectional data flow between the robot and the caregiver.
- **Associated Sub-Categories & File Paths:**
    * *Edge Backend:* `backend_server/app.py` (FastAPI/WebSockets).
    * *Client Interface:* `frontend_app/index.html` (Native JS Dashboard).
    * *Kinematics Engines:* `venv/Lib/site-packages/reachy_mini/kinematics/` (IK solvers).

### Execution & Application Logic
- **Functional Role:** The high-level application layer that manages multimodal perception and robotic personality.
- **Associated Sub-Categories & File Paths:**
    * *AI Logic Engine:* `interactive_reachy.py` (Voice assistant).
    * *Vision & Control:* `test_reachy.py` / `webcam_tracker.py` (Vision loop & P-Controller).
    * *Alert Dispatcher:* `network_alerts.py` (Communication bridge).

---

## 4. ARCHITECTURAL VERIFICATION

The workspace integrity is verified using `map_workspace.py`, which programmatically categorizes the file distribution.

**Current Distribution Snapshot:**
- **Application Logic:** ~6 core scripts.
- **SDK & Simulation Core:** ~250 items.
- **Environment & Dependencies:** ~19,000 items.
- **System Records:** ~34 items.

*To re-verify the distribution, run:* `python map_workspace.py`
