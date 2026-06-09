# PROJECT PROGRESS SUMMARY: Reachy Mini AI Assistant

This file serves as a chronological log of all modifications, feature additions, and architectural updates, maintained automatically via the "Update-on-Change" protocol.

## Modification Log

- **2026-06-09**: 
  - **Component**: Architecture & DevSecOps
  - **Change**: Established 'PROJECT_WORKSPACE_ARCHITECTURE.md' and 'map_workspace.py'.
  - **Reason**: Defined the project's structural baseline and automated workspace mapping.

- **2026-06-09**: 
  - **Component**: Project Management
  - **Change**: Initialized 'SUMMARY.md' and activated the "Update-on-Change" DevSecOps protocol.
  - **Reason**: To ensure documentation and repository synchronization remain in lockstep with code changes.

- **2026-06-09**: 
  - **Component**: Perception & Kinematics (Healthcare Phase 1)
  - **Change**: Implemented 'patient_tracker.py' and integrated spatial tracking into 'test_reachy.py'.
  - **Reason**: To establish a local healthcare monitoring layer with reactive robot behaviors (active looking and alert retraction).

- **2026-06-09**: 
  - **Component**: Environment & Documentation
  - **Change**: Updated all operational guides and scripts to use the venv-relative path for 'reachy-mini-daemon'.
  - **Reason**: To resolve the 'CommandNotFound' error and ensure consistent execution across different shell environments.

- **2026-06-09**: 
  - **Component**: Vision & Perception (Healthcare Phase 2)
  - **Change**: Implemented 'webcam_tracker.py' (OpenCV/MediaPipe) and integrated TTS/Vision orchestration into 'test_reachy.py'.
  - **Reason**: To upgrade from mock telemetry to live pose estimation (Sleeping/Sitting/Standing) and distance-based patient monitoring.

- **2026-06-09**: 
  - **Component**: Dependencies (MediaPipe)
  - **Change**: Downgraded MediaPipe to version 0.10.13 to restore the legacy 'solutions' API on Python 3.12.
  - **Reason**: Resolved 'AttributeError: module mediapipe has no attribute solutions' caused by API removals in newer versions.

- **2026-06-09**: 
  - **Component**: Vision UI/UX (Healthcare Phase 2.5)
  - **Change**: Enhanced 'webcam_tracker.py' with a semi-transparent dashboard, state-based skeleton colors, pulsing red borders, and a blurred critical breach overlay.
  - **Reason**: To provide rich, high-alert visual feedback for local monitoring, improving situational awareness during safety events.

- **2026-06-09**: 
  - **Component**: Vision Robustness (Bug Fix)
  - **Change**: Added 2s camera warmup, implemented a 3s landmark disappearance grace period, and added a 'RECOVERY' state to 'webcam_tracker.py'.
  - **Reason**: Resolved immediate program termination on startup and allowed the robot to automatically resume monitoring if the patient returns to the frame.

- **2026-06-09**: 
  - **Component**: Control & Kinematics (Healthcare Phase 3)
  - **Change**: Implemented a Proportional (P) controller in 'test_reachy.py' for real-time head tracking based on normalized vision error (X, Y).
  - **Reason**: To enable smooth, continuous "look-at" behavior where the robot dynamically follows the patient's movements during monitoring.

- **2026-06-09**: 
  - **Component**: Kinematics & Safety
  - **Change**: Increased NEUTRAL_Z to 25mm and tightened joint limits (Yaw: 35, Pitch: 20) in 'test_reachy.py'.
  - **Reason**: Resolved 'IK error: Collision detected' by providing more physical clearance for the Orbita3D neck and preventing out-of-bounds trajectory requests.

- **2026-06-09**: 
  - **Component**: Networking & Communications (Healthcare Phase 2)
  - **Change**: Implemented 'network_alerts.py' with an asynchronous 'AlertDispatcher' class and integrated it into 'webcam_tracker.py'.
  - **Reason**: To enable non-blocking caregiver notifications via webhooks, ensuring external alerts are fired without interrupting the real-time robot control loop.

- **2026-06-09**: 
  - **Component**: Full-Stack IoT Ecosystem (Phase 3)
  - **Change**: Built a local FastAPI backend (`backend_server/app.py`) and a Vanilla JS frontend dashboard (`frontend_app/index.html`).
  - **Reason**: To replace third-party webhooks with a private, real-time monitoring solution using WebSockets for live telemetry and REST for remote commands.

- **2026-06-09**: 
  - **Component**: Telemetry Pipeline (Full-Stack Bridge)
  - **Change**: Established a real-time data bridge between the OpenCV vision loop and the React dashboard via a new `POST /api/internal/telemetry` endpoint and WebSocket broadcaster.
  - **Reason**: To ensure live posture and spatial data are visualized on the caregiver dashboard without blocking the robot's perception loop.

## Debugging & Verification Protocol
1.  **Backend Health**: `GET http://127.0.0.1:8000/api/health` should return 200 OK.
2.  **WebSocket Handshake**: Browser console should log "Handshake successful: WebSocket Link Active."
3.  **Latency Check**: Joint sliders in UI should reflect in backend logs within <100ms.

