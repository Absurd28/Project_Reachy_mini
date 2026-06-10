# PROJECT WORKSPACE ARCHITECTURE: Reachy Mini AI Assistant

This document provides a definitive architectural overview of the Reachy Mini robotics workspace, mapping its 21,000+ items into logical operational categories.

## 1. WORKSPACE TREE CONFIGURATION

The following conceptual tree illustrates the high-level organization of the project, isolating core source logic from the high-volume dependency noise.

```text
.
├── interactive_reachy.py       # Main HCI / Voice AI Engine
├── test_reachy.py              # Orchestration, Patient Monitoring & Vision Loop
├── webcam_tracker.py           # Live OpenCV/MediaPipe Pose Estimation
├── voice_monitor.py            # Continuous Voice Distress & NLP Monitor
├── network_alerts.py           # Non-blocking Alert Dispatcher (Local Target)
├── backend_server/
│   └── app.py                  # FastAPI Edge Server (WS/REST: Port 8001)
├── frontend_react/
│   └── src/App.jsx             # Caregiver Dashboard (Vite Port: 5173)
├── start_backend.py            # Unified Multi-Service System Launcher
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
    * *Client Interface:* `frontend_react/src/App.jsx` (React Dashboard).
    * *Kinematics Engines:* `venv/Lib/site-packages/reachy_mini/kinematics/` (IK solvers).

### Execution & Application Logic
- **Functional Role:** The high-level application layer that manages multimodal perception and robotic personality.
- **Associated Sub-Categories & File Paths:**
    * *AI Logic Engine:* `interactive_reachy.py` (Voice assistant).
    * *Audio Perception:* `voice_monitor.py` (Distress detection & TTS).
    * *Vision & Control:* `test_reachy.py` / `webcam_tracker.py` (Vision loop & P-Controller).
    * *Alert Dispatcher:* `network_alerts.py` (Communication bridge).

---

## 4. UTILITY SCRIPTS

### Unified System Launcher (`start_backend.py`)
- **Purpose**: A multi-process manager that boots the FastAPI backend, the OpenCV Vision Loop, and the Voice Monitor simultaneously in separate console windows.
- **Features**: Automatic port auditing (8001) and service orchestration.

## 5. ARCHITECTURAL VERIFICATION

The workspace integrity is verified using `map_workspace.py`, which programmatically categorizes the file distribution.

*To re-verify the distribution, run:* `python map_workspace.py`

---

---

## 6. NETWORK TOPOLOGY & PORTS

- **Official Reachy Daemon**: Port `8000` (SDK Communication)
- **Custom Edge FastAPI Server**: Port `8001` (REST & WebSockets)
- **Vite React Dev Server**: Port `5173` (Caregiver Dashboard)
- **Websocket Path**: `ws://127.0.0.1:8001/ws/telemetry`
- **CORS Whitelist**: `http://localhost:5173`, `http://127.0.0.1:5173`

## 7. DATA PIPELINE ARCHITECTURE

### Vision-to-Dashboard Bridge
The project uses an asynchronous "Push-then-Broadcast" pattern to deliver live telemetry:
1.  **Perception**: `webcam_tracker.py` captures posture and spatial data via OpenCV/MediaPipe.
2.  **Dispatch**: A non-blocking thread in the vision loop pushes a data dictionary (`x`, `y`, `posture`, `distance`) to `POST /api/internal/telemetry` every 100ms.
3.  **Broadcast**: The FastAPI backend iterates through the `connected_clients` set and broadcasts the raw payload directly using `client.send_json()`.
4.  **Visualization**: The React dashboard receives the raw telemetry object in its `onmessage` handler and updates the `telemetryState` hook for real-time rendering.
