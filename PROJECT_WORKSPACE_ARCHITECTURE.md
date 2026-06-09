# PROJECT WORKSPACE ARCHITECTURE: Reachy Mini AI Assistant

This document provides a definitive architectural overview of the Reachy Mini robotics workspace, mapping its 21,000+ items into logical operational categories.

## 1. WORKSPACE TREE CONFIGURATION

The following conceptual tree illustrates the high-level organization of the project, isolating core source logic from the high-volume dependency noise.

```text
.
├── interactive_reachy.py       # Main HCI / Voice AI Engine
├── test_reachy.py              # Orchestration, Patient Monitoring & Vision Loop
├── webcam_tracker.py           # Live OpenCV/MediaPipe Pose Estimation
├── network_alerts.py           # Non-blocking Webhook Alert Dispatcher
├── patient_tracker.py          # Mock Spatial Perception (Deprecated)
├── map_workspace.py            # Architectural Verification Script
├── PROJECT_SUMMARY.md          # Technical Log & Milestones
├── start_sim.sh                # Simulation Bootstrapper
│
├── venv/                       # [DEPENDENCY NOISE: ~21,000 files]
```

> **Note:** The vast majority of the 21,000+ items are housed within the `.venv/` and `.git/` directories, representing the Python runtime, simulation dependencies (MuJoCo, SDKs), and version history.

---

## 2. SOFTWARE DEVELOPMENT MODEL MAPPING

### **Paradigm: Component-Based / Hardware-in-the-Loop (HiL) Simulation**
The project follows a **Hardware-in-the-Loop (HiL)** development model where the software logic (AI Assistant & Healthcare Monitor) interacts with a **Digital Twin** (MuJoCo Simulation) through a standardized communication bridge. 

**Operational Responsibilities:**
- **Perception Layer:** Voice capture, NLP intent parsing, and **Live Vision-Based Patient Tracking**.
- **Communications Layer:** External caregiver notifications via **Asynchronous Webhooks**.
- **Orchestration Layer:** Managing the state machine between "Idle", "Active", and **"Healthcare Alert"**.
- **Execution Layer:** Translating high-level intents into low-level joint trajectories.

---

## 3. CATEGORIZED FUNCTIONAL MAPPING

### Physics Simulation & Digital Twin Assets
- **Functional Role:** Handles rigid-body dynamics, joint limits, collision mesh rendering, and environmental scene configuration.
- **Associated Sub-Categories & File Paths:**
    * *Simulation Meshes:* `venv/Lib/site-packages/reachy_mini/assets/` (Contains `.stl` and `.xml` definitions for the robot body).
    * *Robot Descriptions:* `venv/Lib/site-packages/reachy_mini/descriptions/` (URDF and MJCF configuration files).

### Kinematics & Control Core
- **Functional Role:** Manages the mathematical transformation between Cartesian space (X, Y, Z) and Joint space (Roll, Pitch, Yaw). Handles trajectory smoothing and safety constraints.
- **Associated Sub-Categories & File Paths:**
    * *Kinematics Engines:* `venv/Lib/site-packages/reachy_mini/kinematics/` (Rust-optimized IK solvers).
    * *Motion Primitives:* `venv/Lib/site-packages/reachy_mini/motion/` (Animation styles like `minjerk` and `cartoon`).

### Execution & Communication Daemons
- **Functional Role:** Provides the runtime orchestration required to bridge the AI logic with the physics engine via REST/WebSockets.
- **Associated Sub-Categories & File Paths:**
    * *Background Runtimes:* `venv/Lib/site-packages/reachy_mini/daemon/` (Orchestrates the robot's "brain" process).
    * *Hardware Interface (IO):* `venv/Lib/site-packages/reachy_mini/io/` (Communication protocols for simulation and real hardware).

### Human-Computer Interaction (HCI), Perception & Comms Interface
- **Functional Role:** The high-level application layer that manages multimodal perception (STT, Live Computer Vision), personality modeling, output generation (TTS), and **External Alerting**.
- **Associated Sub-Categories & File Paths:**
    * *AI Logic Engine:* `interactive_reachy.py` (Main entry point for voice interaction).
    * *Vision Tracker:* `webcam_tracker.py` (Real-time OpenCV/MediaPipe pose estimation engine).
    * *Alert Dispatcher:* `network_alerts.py` (Asynchronous webhook engine for remote caregiver notification).
    * *Validation & Monitoring:* `test_reachy.py` (Couples vision logic with physical kinematic responses and TTS alerts).

---

## 4. ARCHITECTURAL VERIFICATION

The workspace integrity is verified using `map_workspace.py`, which programmatically categorizes the file distribution.

**Current Distribution Snapshot:**
- **Application Logic:** ~6 core scripts.
- **SDK & Simulation Core:** ~250 items.
- **Environment & Dependencies:** ~19,000 items.
- **System Records:** ~34 items.

*To re-verify the distribution, run:* `python map_workspace.py`
