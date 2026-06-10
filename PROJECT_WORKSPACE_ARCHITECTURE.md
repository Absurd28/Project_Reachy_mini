# PROJECT WORKSPACE ARCHITECTURE: Reachy Mini AI Assistant

This document provides a definitive architectural overview of the Reachy Mini robotics workspace, mapping its 38,000+ items into logical operational categories.

## 1. WORKSPACE TREE CONFIGURATION

```text
.
├── interactive_reachy.py       # Main HCI / Voice AI Engine
├── test_reachy.py              # Orchestration, Patient Monitoring & Vision Loop
├── webcam_tracker.py           # Live OpenCV/MediaPipe Pose Estimation
├── voice_monitor.py            # Continuous Voice Distress & NLP Monitor
├── nlp_parser.py               # Phase 4: Zero-Shot Intent Classifier (Edge-AI)
├── routine_manager.py          # Phase 4: Proactive Scheduler (Medication Checks)
├── network_alerts.py           # Non-blocking Alert Dispatcher (Local Target)
├── backend_server/
│   └── app.py                  # FastAPI Edge Server (WS/REST: Port 8001)
├── frontend_react/
│   └── src/App.jsx             # Caregiver Dashboard (Vite Port: 5173)
├── start_backend.py            # Dedicated Backend Launcher (Visible Logs)
├── launch_ecosystem.py         # Multi-Service Orchestrator (Full Boot)
├── map_workspace.py            # Architectural Verification Script
├── PROJECT_SUMMARY.md          # Technical Log & Milestones
├── start_sim.sh                # Simulation Bootstrapper
│
├── venv/                       # [DEPENDENCY NOISE: ~25,000 files]
```

---

## 2. SOFTWARE DEVELOPMENT MODEL MAPPING

### **Paradigm: Full-Stack Robotics / Hardware-in-the-Loop (HiL)**
The project has evolved into a **Proactive AI Ecosystem**. 

**Operational Responsibilities:**
- **Perception Layer:** Live Vision-Based Tracking & Voice distress detection.
- **Cognitive Layer:** Zero-shot NLP intent parsing for context-aware responses.
- **Behavioral Layer:** Proactive scheduling for medical routines and interactive feedback.
- **Edge Communications:** FastAPI managing real-time WebSocket telemetry.
- **Remote Interface:** Interactive dashboard for caregiver monitoring.

---

## 3. CATEGORIZED FUNCTIONAL MAPPING

### Cognitive & Behavioral Layer (Phase 4)
- **Functional Role:** Handles decision-making, scheduled routines, and natural language understanding.
- **Associated Sub-Categories & File Paths:**
    * *NLP Engine:* `nlp_parser.py` (Transformer-based classification).
    * *Scheduler:* `routine_manager.py` (Proactive medication checks).
    * *Intent Handling:* `voice_monitor.py` (Process speech to intent).

### Kinematics & Full-Stack Communications
- **Functional Role:** Manages joint transformations and bidirectional data flow.
- **Associated Sub-Categories & File Paths:**
    * *Edge Backend:* `backend_server/app.py` (FastAPI/WebSockets).
    * *Hardware Abstraction:* `backend_server/robot_controller.py` (SDK Bridge).

### Execution & Application Logic
- **Functional Role:** High-level application layer for multimodal perception.
- **Associated Sub-Categories & File Paths:**
    * *AI Logic Engine:* `interactive_reachy.py`.
    * *Vision & Control:* `webcam_tracker.py` / `test_reachy.py`.

---

## 4. UTILITY SCRIPTS

### Unified System Launcher (`launch_ecosystem.py`)
- **Purpose**: Boots the entire Phase 4 ecosystem including the Proactive Manager and NLP Monitor in separate persistent console windows.

## 5. NETWORK TOPOLOGY & PORTS

- **Official Reachy Daemon**: Port `8000` (SDK Communication)
- **Custom Edge FastAPI Server**: Port `8001` (REST & WebSockets)
- **Vite React Dev Server**: Port `5173` (Caregiver Dashboard)
- **Websocket Path**: `ws://127.0.0.1:8001/ws/telemetry`
