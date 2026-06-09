# Reachy Mini: Voice-Controlled AI Simulation Project

This document serves as a persistent record of the development, architecture, and operational procedures for the Reachy Mini simulation environment.

## 1. Project Overview
The goal of this project was to establish a high-fidelity local development environment for the **Reachy Mini** (by Pollen Robotics) and implement an expressive, voice-controlled AI assistant within a simulated environment.

## 2. Technical Stack & Tools
- **Operating System**: Windows 10/11 (win32).
- **Core SDK**: `reachy-mini` (v1.7.1) with `[mujoco,dev]` extras.
- **Simulation Engine**: MuJoCo (Physics-based robot simulation).
- **Python Version**: 3.12 (managed via a local `venv`).
- **Voice Interface**:
    - **STT**: `SpeechRecognition` (using Google Web Speech API).
    - **TTS**: `pyttsx3` (using Windows SAPI5 native engine).
    - **Audio I/O**: `PyAudio`.
- **Communication**: REST API & WebSockets via the `reachy-mini-daemon`.

## 3. Milestones & Implementation Details

### A. Environment Setup
- Successfully installed system-level dependencies (Git, Git-LFS).
- Configured a virtual environment to isolate the robotics stack.
- Resolved SDK-specific flag changes (migrated from `--deactivate-audio` to `--no-media`).

### B. Kinematics & Motion Control
- **Orbita3D Neck Implementation**: Successfully mapped 6-DOF control (Roll, Pitch, Yaw + Z translation).
- **Retraction Logic**: Created `hide_in_shell()` and `emerge_from_shell()` functions utilizing the mechanical translation axis to protect the robot.
- **Safety Constraints**: Optimized the "Neutral" position to `Z=20mm` to prevent Inverse Kinematics (IK) collision errors during tilts.

### C. AI Assistant Features (`interactive_reachy.py`)
- **Idle Behavior**: Asynchronous "Breathing" loop that adds subtle micro-movements to the head and antennas to make the robot feel alive.
- **Intent Parser**: Maps natural language keywords (Hello, Tired, Happy, Look Around, Sleep) to complex robotic gestures.
- **Animation Styles**: Uses `minjerk` for smooth motion and `cartoon` for expressive overshooting/squash-and-stretch effects.
- **Auto-Power Save**: A background monitor that puts the robot into "Sleep" mode (retracted) after 60 seconds of inactivity.

## 4. Current File Structure
- `venv/`: Python virtual environment.
- `start_sim.sh`: Bash script to launch the simulation daemon.
- `test_reachy.py`: Script for basic hardware testing and animation sequences.
- `interactive_reachy.py`: The main Voice-Assistant application.
- `README.md`: Basic usage guide.
- `PROJECT_SUMMARY.md`: This detailed record.

## 5. Operational Steps (How to Run)

### Step 1: Start the Simulation Daemon (Terminal 1)
This window runs the robot's "brain" and physics.
```powershell
.\venv\Scripts\activate
.\venv\Scripts\reachy-mini-daemon --sim --scene minimal --no-media
```

### Step 2: Start the AI Assistant (Terminal 2)
This window runs the voice logic and controls the robot.
```powershell
.\venv\Scripts\activate
python interactive_reachy.py
```

### Step 3: Available Voice Commands
- **"Hello Reachy" / "Wake up"**: Wakes up and greets the user.
- **"Go to sleep" / "Hide"**: Retracts into the shell.
- **"Are you happy?"**: Expressive antenna wiggle and look-up.
- **"Look around"**: Scans the environment randomly.
- **"Listen to me"**: Curious head tilt.
- **"I'm tired"**: Empathetic sigh and lowered head.
- **"Status"**: Vocalizes the current neck height.
